#!/usr/bin/env bash
# Install the Troll Library skills into one or more harness skill directories.
set -euo pipefail

src="$(cd "$(dirname "$0")" && pwd)/skills"
mode=link
targets=()

usage() {
  cat <<'EOF'
usage: install.sh [--copy] [--uninstall] [--target DIR]...

  (no flags)      install into every harness dir found on this machine
  --target DIR    install into DIR (repeatable)
  --copy          copy skill directories instead of symlinking them
  --uninstall     remove only what this repo installed, from the same targets
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --copy) mode=copy; shift ;;
    --uninstall) mode=uninstall; shift ;;
    --target) [ $# -ge 2 ] || { echo "install: --target needs a directory" >&2; exit 2; }; targets+=("$2"); shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "install: unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ ${#targets[@]} -eq 0 ]; then
  for candidate in "$HOME/.omp/agent/skills" "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.agents/skills"; do
    [ -d "$(dirname "$candidate")" ] && targets+=("$candidate")
  done
  [ ${#targets[@]} -gt 0 ] || targets=("$HOME/.agents/skills")
fi

is_ours() {
  if [ -L "$1" ]; then
    case "$(readlink "$1")" in "$src"/*) return 0 ;; esac
  fi
  [ -f "$1/.troll-library" ] && return 0
  return 1
}

for target in "${targets[@]}"; do
  mkdir -p "$target"

  if [ "$mode" = uninstall ]; then
    for path in "$target"/*; do
      [ -e "$path" ] || [ -L "$path" ] || continue
      if is_ours "$path"; then
        rm -rf "$path"
        echo "removed $(basename "$path") from $target"
      fi
    done
    continue
  fi

  for dir in "$src"/*/; do
    name="$(basename "$dir")"
    dest="$target/$name"
    if [ -L "$dest" ] && ! is_ours "$dest"; then
      echo "skip: foreign symlink exists: $dest"
      continue
    fi
    if [ -e "$dest" ] && [ ! -L "$dest" ] && [ ! -f "$dest/.troll-library" ]; then
      echo "skip: authored skill exists: $dest"
      continue
    fi
    rm -rf "$dest"
    if [ "$mode" = copy ]; then
      cp -R "$dir" "$dest"
      : > "$dest/.troll-library"
      echo "copied $name -> $target"
    else
      ln -sfn "$dir" "$dest"
      echo "linked $name -> $target"
    fi
  done
done

echo "restart the harness so it rediscovers skills"

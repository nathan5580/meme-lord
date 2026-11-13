#!/usr/bin/env bash
set -euo pipefail

src="$(cd "$(dirname "$0")" && pwd)/skills"
dest="$HOME/.omp/agent/skills"
mkdir -p "$dest"

if [ "${1:-}" = "--uninstall" ]; then
  for path in "$dest"/*; do
    [ -L "$path" ] || continue
    case "$(readlink "$path")" in
      "$src"/*) rm "$path"; echo "unlinked $(basename "$path")" ;;
    esac
  done
  echo "restart the session so OMP rediscovers skills"
  exit 0
fi

for dir in "$src"/*/; do
  name="$(basename "$dir")"
  if [ -e "$dest/$name" ] && [ ! -L "$dest/$name" ]; then
    echo "skip: authored skill exists: $name"
    continue
  fi
  ln -sfn "$dir" "$dest/$name"
  echo "linked $name"
done

echo "restart the session so OMP rediscovers skills"

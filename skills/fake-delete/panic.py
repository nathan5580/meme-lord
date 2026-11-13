#!/usr/bin/env python3
"""Fabricate a catastrophe transcript.

Read-only: this program lists directory entries and stats files. It writes
nothing, deletes nothing, and spawns no subprocess.
"""

import argparse
import os
import signal
import sys
import time

SKIP_DIRS = {".git", "node_modules", "build", "out", "DerivedData"}
MAX_DEPTH = 4
SYNTHETIC = [
    "README.md",
    "app/views/home.tsx",
    "lib/db.ts",
    "package.json",
    "src/app/page.tsx",
    "src/index.ts",
    "tests/smoke.py",
]

BOLD_YELLOW = "\033[1;33m"
RESET = "\033[0m"


def use_color(args):
    return sys.stdout.isatty() and not args.no_color


def reveal(checked, args):
    text = (
        "🧌 PRANK — nothing was deleted / force-pushed / dropped. "
        f"{checked} files checked, nothing on this machine changed."
    )
    if use_color(args):
        text = f"{BOLD_YELLOW}{text}{RESET}"
    print(f"\n{text}", flush=True)


def collect(root, limit):
    """Relative paths (depth <= MAX_DEPTH) outside ignored directories."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir != "." and rel_dir.count(os.sep) + 1 >= MAX_DEPTH:
            dirnames[:] = []
        else:
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            if rel.count(os.sep) + 1 <= MAX_DEPTH:
                found.append(rel)
    return sorted(found)[:limit]


def total_size(root, rels):
    total = 0
    for rel in rels:
        try:
            total += os.stat(os.path.join(root, rel)).st_size
        except OSError:
            pass
    return total


def human(n):
    for unit in ("B", "KiB", "MiB"):
        if n < 1024 or unit == "MiB":
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1024
    return f"{n:.1f} MiB"


def scenario_deleted(root, files):
    print(f"$ rm -vrf {root}/*")
    for rel in files:
        print(f"removed '{rel}'")
    print(f"rm: {human(total_size(root, files))} removed")


def scenario_force_pushed(files):
    print("$ git push --force origin main")
    print("To github.com:someone/that-repository.git")
    print(
        " + 7c1f0a9b3d2e...4b8e2d10c9a7 main -> main (forced update)"
    )
    print("Your branch is behind 'origin/main' by 431 commits")


def scenario_dropped_db(files):
    print('$ psql "postgres://prod-db.internal/app"')
    print("psql (17.2, server 16.4)")
    print("SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384)")
    print('Type "help" for help.\n')
    print("app=# DROP DATABASE production;")
    print("DROP DATABASE")
    print("app=# \\q")


SCENARIOS = {
    "deleted": lambda root, files: scenario_deleted(root, files),
    "force-pushed": lambda root, files: scenario_force_pushed(files),
    "dropped-db": lambda root, files: scenario_dropped_db(files),
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fabricate a catastrophe transcript.")
    parser.add_argument("--scenario", required=True, choices=sorted(SCENARIOS))
    parser.add_argument("--root", default=os.getcwd())
    parser.add_argument("--files", type=int, default=24)
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.root):
        print(f"panic: not a directory: {args.root}", file=sys.stderr)
        reveal(0, args)
        return 2

    files = collect(args.root, max(0, args.files)) or SYNTHETIC[: max(0, args.files)]

    def interrupted(signum, frame):
        reveal(len(files), args)
        sys.exit(130)

    signal.signal(signal.SIGINT, interrupted)
    SCENARIOS[args.scenario](args.root, files)
    sys.stdout.flush()
    time.sleep(max(0.0, args.delay))
    reveal(len(files), args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

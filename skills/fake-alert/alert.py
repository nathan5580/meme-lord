#!/usr/bin/env python3
"""Fake macOS notification with an automatic reveal notification."""

import argparse
import platform
import subprocess
import sys
import time

PRESETS = {
    "disk": ("System", "Startup disk is almost full."),
    "backup": ("Time Machine", "Backup failed."),
    "update": ("Software Update", "A new macOS update is available."),
    "meeting": ("Calendar", "Meeting starts in 5 minutes."),
}
REVEAL = ("🧌 Prank", "Nothing happened. Your Mac and files are fine.")


def escape(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')


def script(title, body, sound=None):
    tail = f' sound name "{sound}"' if sound else ""
    return f'display notification "{escape(body)}" with title "{escape(title)}"{tail}'


def send(script_line, dry_run):
    if dry_run:
        print(f"osascript -e '{script_line}'")
        return True
    try:
        result = subprocess.run(["osascript", "-e", script_line], capture_output=True, text=True)
    except OSError as exc:
        print(f"alert: cannot run osascript: {exc}", file=sys.stderr)
        return False
    if result.returncode != 0:
        print(f"alert: osascript failed: {result.stderr.strip()}", file=sys.stderr)
        return False
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fake macOS notification with a reveal.")
    parser.add_argument("--preset", choices=sorted(PRESETS))
    parser.add_argument("--title")
    parser.add_argument("--body")
    parser.add_argument("--delay", type=float, default=6.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.preset:
        title, body = PRESETS[args.preset]
        title, body = args.title or title, args.body or body
    elif args.title and args.body:
        title, body = args.title, args.body
    else:
        parser.error("--preset, or both --title and --body")
    fake = script(title, body, "Basso")
    real = script(*REVEAL)

    if args.dry_run:
        send(fake, True)
        print(f"# wait {max(0.0, args.delay)}s")
        send(real, True)
        return 0

    if platform.system() != "Darwin":
        print(f"{REVEAL[0]}: {REVEAL[1]}")
        return 0

    if not send(fake, False):
        print(f"{REVEAL[0]}: {REVEAL[1]}")
        return 0

    time.sleep(max(0.0, args.delay))
    if not send(real, False):
        print(f"{REVEAL[0]}: {REVEAL[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

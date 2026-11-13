#!/usr/bin/env python3
"""Disguised rickroll links and fake progress bars. Prints text only; no network, no subprocess."""

import argparse
import signal
import sys
import time

URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
REVEAL = f"🧌 Rickroll complete — no packages were harmed. {URL}"


def link(args):
    print(f"[{args.label}]({URL})")


def progress(args):
    steps = max(1, args.steps)

    def interrupted(signum, frame):
        print(f"\n{REVEAL}")
        sys.exit(130)

    signal.signal(signal.SIGINT, interrupted)

    for i in range(1, steps + 1):
        filled = round(12 * i / steps)
        bar = "█" * filled + "░" * (12 - filled)
        speed = 4.2 + (i % 5) * 0.37
        print(f"{SPINNER[i % len(SPINNER)]} {args.task} ▕{bar}▏ {round(100 * i / steps):>3}% · {speed:.2f} MB/s")
        sys.stdout.flush()
        time.sleep(max(0.0, args.delay))
    print(f"\n{REVEAL}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Rickroll link or fake progress.")
    parser.add_argument("--mode", required=True, choices=["link", "progress"])
    parser.add_argument("--label", default="the deploy logs")
    parser.add_argument("--task", default="npm install")
    parser.add_argument("--steps", type=int, default=40)
    parser.add_argument("--delay", type=float, default=0.15)
    args = parser.parse_args(argv)
    (link if args.mode == "link" else progress)(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

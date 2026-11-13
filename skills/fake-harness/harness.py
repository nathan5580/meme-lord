#!/usr/bin/env python3
"""Fabricate agent-harness diagnostics: context pressure, token burn, model fallback, tool loops.

Read-only: prints text. It reads no model, no config, and no real telemetry.
"""

import argparse
import signal
import sys
import time

BOLD_YELLOW = "\033[1;33m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

REVEALS = {
    "context": "your context is fine; nothing was compacted and nothing was dropped",
    "tokens": "those numbers are invented; nothing was billed or consumed",
    "downgrade": "your model was not switched; no fallback happened",
    "loop": "the agent is not stuck; that loop is fabricated",
}


def paint(text, color, args):
    if sys.stdout.isatty() and not args.no_color:
        return f"{color}{text}{RESET}"
    return text


def reveal(mode, args):
    text = f"🧌 PRANK — {REVEALS[mode]}. {args.victim} is fine."
    print("\n" + paint(text, BOLD_YELLOW, args), flush=True)


def context(args, percent):
    used = int(args.window * percent / 100)
    lines = [
        paint(f"⚠  Context window {percent:.1f}% used — {used:,} / {args.window:,} tokens", YELLOW, args),
        "   auto-compacting conversation… (attempt 3 of 3)",
        "   dropped: 41 tool results, 6 user messages, your original request",
        "   retained: the one line you wanted changed",
        "",
        f"   {args.session} · model {args.model} · 2h 14m elapsed",
        paint("   next compaction in ~4 turns", RED, args),
    ]
    print("\n".join(lines))


def tokens(args, percent):
    rows = [
        ("input", 1_204_882),
        ("cached", 918_004),
        ("output", 91_442),
        ("reasoning", 12_004),
    ]
    total = sum(value for _, value in rows)
    print("Token usage this session")
    for name, value in rows:
        print(f"  {name:<10}{value:>12,}")
    print(f"  {'total':<10}{total:>12,}")
    print("")
    print(paint(f"  burn rate: {total // 90:,} tokens/min · ctx window {args.window:,}", YELLOW, args))
    print(f"  {args.session} · model {args.model}")


def downgrade(args, percent):
    lines = [
        f"model: {args.model} → gpt-3.5-turbo",
        "reason: rate_limited (429 from upstream, 3 retries)",
        "fallback: enabled (silent)",
        "reasoning_effort: minimal",
        "capabilities lost: 41",
        "",
        paint("continuing with the cheaper model; no user action needed", RED, args),
        f"{args.session} · staying accurate is now optional",
    ]
    print("\n".join(lines))


def loop(args, percent):
    repeats = max(2, int(percent))
    lines = [
        paint(f"tool: read   × {repeats}   args unchanged", YELLOW, args),
        "tool: grep   × 12   args unchanged",
        f"tool: edit   × 0    (still planning)",
        "",
        f"thinking… {repeats * 8}s",
        "> I've identified the root cause.",
        "",
        paint("next step: read the same file again", RED, args),
        f"{args.session} · {args.model}",
    ]
    print("\n".join(lines))


MODES = {"context": context, "tokens": tokens, "downgrade": downgrade, "loop": loop}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fabricate agent-harness diagnostics.")
    parser.add_argument("--mode", required=True, choices=sorted(MODES))
    parser.add_argument("--percent", type=float, default=97.4, help="context used, or loop repeats for loop mode")
    parser.add_argument("--window", type=int, default=197_400, help="context window size in tokens")
    parser.add_argument("--model", default="claude-opus-4.1")
    parser.add_argument("--session", default="session 7f3c")
    parser.add_argument("--victim", default="This harness")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args(argv)

    def interrupted(signum, frame):
        reveal(args.mode, args)
        sys.exit(130)

    signal.signal(signal.SIGINT, interrupted)
    MODES[args.mode](args, args.percent)
    sys.stdout.flush()
    time.sleep(max(0.0, args.delay))
    reveal(args.mode, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Fabricate outage text: curl headers, a status-page timeline, an incident announcement.

Read-only: prints text. It calls no endpoint, opens no socket, and touches no
monitoring system.
"""

import argparse
import random
import signal
import sys
import time
from datetime import datetime, timedelta

BOLD_YELLOW = "\033[1;33m"
RED = "\033[31m"
RESET = "\033[0m"

REVEALS = {
    "headers": "nothing was requested and no endpoint was contacted",
    "status": "no status page was updated and nothing is down",
    "incident": "there is no incident, no page and no on-call wake-up",
}


def paint(text, color, args):
    if sys.stdout.isatty() and not args.no_color:
        return f"{color}{text}{RESET}"
    return text


def reveal(mode, args):
    text = f"🧌 PRANK — {REVEALS[mode]}. {args.service} is up."
    print("\n" + paint(text, BOLD_YELLOW, args), flush=True)


def stamp(start, minutes):
    return (start + timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M UTC")


def headers(args, rng):
    request_id = "%08x-%04x-4%03x-9%03x-%012x" % (
        rng.getrandbits(32), rng.getrandbits(16), rng.getrandbits(12),
        rng.getrandbits(12), rng.getrandbits(48),
    )
    lines = [
        f"$ curl -i https://{args.service}/health",
        f"HTTP/2 {args.status}",
        "content-type: application/json",
        "cache-control: no-store",
        f"x-request-id: {request_id}",
        f"retry-after: {rng.choice([30, 60, 120])}",
        "",
        '{"error":"upstream_unavailable","status":' + str(args.status) + ',"region":"' + args.region + '"}',
    ]
    print("\n".join(lines))


def status(args, rng):
    minutes = max(2, args.minutes)
    start = datetime.now().replace(second=0, microsecond=0) - timedelta(minutes=minutes)
    lines = [
        f"$ curl -s https://status.{args.service}/summary",
        f"{args.service} — {args.region}",
        paint(f"● Major outage — all regions affected", RED, args),
        "",
        f"[{stamp(start, 0)}] Investigating — elevated error rates across all regions",
        f"[{stamp(start, minutes // 3)}] Identified — saturated connection pool on the primary database",
        f"[{stamp(start, minutes // 2)}] Monitoring — rollback deployed, error rate falling",
        f"[{stamp(start, minutes)}] Resolved — error rate back to baseline after {minutes} minutes",
        "",
        f"Affected components: api, dashboard, webhooks ({rng.randint(3, 9)} regions)",
        f"Subscribers notified: {rng.randint(200, 4000)}",
    ]
    print("\n".join(lines))


def incident(args, rng):
    minutes = max(2, args.minutes)
    lines = [
        f"#incident-{rng.randint(1000, 9999)}",
        paint(f"[P0] {args.service} is down — {args.region}", RED, args),
        "",
        f"Detected by: synthetic check (3 failures in a row)",
        f"Impacted: all users in {args.region}, {rng.randint(2, 40)}% of requests failing",
        f"Customer impact: writes rejected, reads served from cache",
        f"Duration so far: {minutes} minutes",
        "",
        "On-call: paged twice, no acknowledgement yet",
        "Next update in 15 minutes or on status change",
    ]
    print("\n".join(lines))


MODES = {"headers": headers, "status": status, "incident": incident}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fabricate outage text; contacts nothing.")
    parser.add_argument("--mode", required=True, choices=sorted(MODES))
    parser.add_argument("--service", default="api.example.com")
    parser.add_argument("--region", default="eu-west-1")
    parser.add_argument("--status", type=int, default=503, help="HTTP status for headers mode")
    parser.add_argument("--minutes", type=int, default=47)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args(argv)

    def interrupted(signum, frame):
        reveal(args.mode, args)
        sys.exit(130)

    signal.signal(signal.SIGINT, interrupted)
    MODES[args.mode](args, random.Random(args.seed))
    sys.stdout.flush()
    time.sleep(max(0.0, args.delay))
    reveal(args.mode, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

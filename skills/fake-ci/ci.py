#!/usr/bin/env python3
"""Fabricate a CI failure log.

Read-only: walks the repo for test-file names and prints text. It runs no
pipeline, calls no API, and spawns no subprocess.
"""

import argparse
import os
import random
import signal
import sys
import time

SKIP_DIRS = {".git", "node_modules", "build", "out", "DerivedData", "dist", "troll-out"}
TEST_HINTS = ("test_", "_test.", ".test.", ".spec.", "/tests/", "/Tests/")
FALLBACK_TESTS = [
    "tests/test_parser.py::test_nested_quotes",
    "tests/test_checkout.py::test_rounding",
    "src/api/client.test.ts::retries on 503",
    "Tests/AppTests/OrderTests.swift::testReconnect",
]
RUN_URL = "https://github.com/{repo}/actions/runs/{run_id}"

BOLD_YELLOW = "\033[1;33m"
RED = "\033[31m"
RESET = "\033[0m"


def paint(text, color, args):
    if sys.stdout.isatty() and not args.no_color:
        return f"{color}{text}{RESET}"
    return text


def reveal(checked, args, mode):
    files = f"{checked} test file{'s' if checked != 1 else ''}"
    text = f"🧌 PRANK — no pipeline ran, nothing failed, {files} on this machine are untouched."
    if mode == "jenkins":
        text = f"🧌 PRANK — no Jenkins call was made and nothing failed; {files} untouched."
    elif mode == "gitlab":
        text = f"🧌 PRANK — no GitLab job ran and nothing failed; {files} untouched."
    print("\n" + paint(text, BOLD_YELLOW, args), flush=True)


def find_tests(root, limit=8):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            rel = os.path.relpath(os.path.join(dirpath, name), root)
            if rel.startswith(".."):
                continue
            haystack = "/" + rel.replace(os.sep, "/")
            if any(hint in haystack for hint in TEST_HINTS):
                found.append(rel.replace(os.sep, "/"))
        if len(found) >= limit:
            break
    return sorted(found)[:limit]


def failure_line(test):
    if test.endswith(".py") or "::" in test:
        return f"FAILED {test} - AssertionError: expected 2, got 3"
    if ".ts" in test:
        return f"FAILED {test}: expect(received).toBe(expected) // 2 !== 3"
    return f"FAILED {test}: XCTAssertEqual failed: (\"2\") is not equal to (\"3\")"


def actions(args, test, run_id, sha):
    job = args.job or "test (ubuntu-latest)"
    stamp = "2026-11-13T10:14:"
    lines = [
        f"$ gh run view {run_id} --log-failed",
        f"{job}\tSet up job\t{stamp}02.004Z Current runner version: '2.320.0'",
        f"{job}\tSet up job\t{stamp}02.881Z Operating System: Ubuntu 24.04.1 LTS",
        f"{job}\tRun actions/checkout@v4\t{stamp}09.120Z Syncing repository: {args.repo}",
        f"{job}\tRun actions/setup-python@v5\t{stamp}14.556Z Successfully set up Python 3.12.7",
        f"{job}\tRun pytest -q\t{stamp}19.771Z .......F.......",
        f"{job}\tRun pytest -q\t{stamp}31.204Z {failure_line(test)}",
        f"{job}\tRun pytest -q\t{stamp}31.288Z 1 failed, 14 passed in 11.43s",
        f"{job}\tPost Run actions/checkout@v4\t{stamp}33.002Z Post job cleanup.",
        f"{job}\tComplete job\t{stamp}34.118Z Cleaning up orphan processes",
        "",
        paint(f"##[error]Process completed with exit code 1.", RED, args),
        "",
        f"{sha}  {args.branch}  {RUN_URL.format(repo=args.repo, run_id=run_id)}",
        "1 failed job · 14 passed tests · 1 annotation",
    ]
    print("\n".join(lines))


def jenkins(args, test, run_id, sha):
    job = args.job or "app_main"
    lines = [
        f"Started by user nate",
        "[Pipeline] Start of Pipeline",
        "[Pipeline] node",
        f"Running on linux-x86-8 in /var/jenkins/workspace/{job}",
        "[Pipeline] stage",
        "[Pipeline] { (Build)",
        "+ make build",
        "building 41 files…",
        "[Pipeline] }",
        "[Pipeline] { (Test)",
        "+ pytest -q",
        ".......F.......",
        failure_line(test),
        "1 failed, 14 passed in 11.43s",
        "[Pipeline] }",
        "[Pipeline] // node",
        "[Pipeline] End of Pipeline",
        paint("ERROR: script returned exit code 1", RED, args),
        "Finished: FAILURE",
        f"Build #{run_id} · {args.branch} · {sha}",
    ]
    print("\n".join(lines))


def gitlab(args, test, run_id, sha):
    job = args.job or "test"
    lines = [
        "Running with gitlab-runner 17.4.0 (b92ee590)",
        f"  on docker-medium-3 a1b2c3d4, system ID: s_41f0",
        'Preparing the "docker" executor',
        "Using Docker executor with image python:3.12-slim ...",
        "Pulling docker image python:3.12-slim ...",
        "Using docker image sha256:4d1f0c2ab4ef for python:3.12-slim ...",
        "$ pytest -q",
        ".......F.......",
        failure_line(test),
        "1 failed, 14 passed in 11.43s",
        paint("ERROR: Job failed: exit code 1", RED, args),
        "",
        f"Job #{run_id} · {job} · {args.branch} · {sha}",
    ]
    print("\n".join(lines))


MODES = {"actions": actions, "jenkins": jenkins, "gitlab": gitlab}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fabricate a CI failure log.")
    parser.add_argument("--mode", required=True, choices=sorted(MODES))
    parser.add_argument("--repo", default="acme/app")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--job", help="job name shown in the log")
    parser.add_argument("--test", help="failing test name; defaults to one found in this repo")
    parser.add_argument("--root", default=os.getcwd())
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)
    tests = find_tests(args.root) if os.path.isdir(args.root) else []
    test = args.test or (rng.choice(tests) if tests else rng.choice(FALLBACK_TESTS))
    sha = "%07x" % rng.getrandbits(28)

    def interrupted(signum, frame):
        reveal(len(tests), args, args.mode)
        sys.exit(130)

    signal.signal(signal.SIGINT, interrupted)
    MODES[args.mode](args, test, rng.randint(1000, 9999), sha)
    sys.stdout.flush()
    time.sleep(max(0.0, args.delay))
    reveal(len(tests), args, args.mode)
    return 0


if __name__ == "__main__":
    sys.exit(main())

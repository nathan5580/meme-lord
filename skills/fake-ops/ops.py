#!/usr/bin/env python3
"""Fabricate deploy, benchmark and docker-build console output.

Read-only: prints text. It runs no kubectl, docker or benchmark, contacts no
cluster or daemon, and spawns no subprocess.
"""

import argparse
import random
import signal
import sys
import time

BOLD_YELLOW = "\033[1;33m"
RED = "\033[31m"
RESET = "\033[0m"

REVEALS = {
    "deploy": "nothing was deployed, no cluster was contacted",
    "bench": "no benchmark ran; those numbers are invented",
    "docker": "no image was built and no Docker daemon was touched",
}


def paint(text, color, args):
    if sys.stdout.isatty() and not args.no_color:
        return f"{color}{text}{RESET}"
    return text


def reveal(mode, args):
    text = f"🧌 PRANK — {REVEALS[mode]}. Everything still runs exactly as it did before."
    print("\n" + paint(text, BOLD_YELLOW, args), flush=True)


def deploy(args, rng):
    app = args.app
    replicas = max(1, args.replicas)
    pod = lambda suffix: f"{app}-7d9f8c6b5d-{suffix}"
    restarts = rng.randint(9, 24)
    lines = [
        f"$ kubectl rollout status deployment/{app} --timeout=90s",
        f'Waiting for deployment "{app}" rollout to finish: {replicas - 1} out of {replicas} new replicas have been updated...',
        f'Waiting for deployment "{app}" rollout to finish: 1 old replicas are pending termination...',
        paint(f'error: deployment "{app}" exceeded its progress deadline', RED, args),
        "",
        f"$ kubectl get pods -l app={app}",
        f"{'NAME':<27}READY   STATUS             RESTARTS        AGE",
        f"{pod('2xk4l'):<27}0/1     CrashLoopBackOff   {restarts} (41s ago)   6m12s",
        f"{pod('9m2pq'):<27}0/1     CrashLoopBackOff   {restarts} (38s ago)   6m12s",
        f"{pod('t8wvz'):<27}1/1     Running            0               6m40s",
        "",
        f"$ kubectl logs {pod('2xk4l')} --tail=2",
        "Starting container process…",
        paint("Error: connect ECONNREFUSED 127.0.0.1:5432", RED, args),
        "",
        f"$ kubectl rollout undo deployment/{app}",
        f'deployment.apps/{app} rolled back',
    ]
    print("\n".join(lines))


def bench(args, rng):
    before = 1.9 + rng.random()
    factor = rng.choice([21.84, 41.7, 412.9, 4.2])
    after = before * factor
    lines = [
        f"$ hyperfine '{args.before}' '{args.after}' --warmup 3",
        f"Benchmark 1: {args.before}",
        f"  Time (mean ± σ):      {before:.3f} s ±  0.043 s    [User: {before * 0.91:.3f} s, System: 0.061 s]",
        f"  Range (min … max):    {before - 0.05:.3f} s …  {before + 0.09:.3f} s    10 runs",
        "",
        f"Benchmark 2: {args.after}",
        f"  Time (mean ± σ):     {after:.3f} s ±  {after * 0.02:.3f} s    [User: {after * 0.98:.3f} s, System: 0.402 s]",
        f"  Range (min … max):   {after * 0.97:.3f} s … {after * 1.03:.3f} s    10 runs",
        "",
        "Summary",
        paint(f"  {args.after} ran {factor:.2f} ± 0.62 times slower than {args.before}", RED, args),
        "",
        "$ git log --oneline -1",
        "a41c9f2 perf: cache the hot path",
    ]
    print("\n".join(lines))


def docker(args, rng):
    tag = args.image
    lines = [
        f"$ docker build -t {tag} .",
        "[+] Building 42.1s (14/19)  docker:desktop-linux",
        " => [internal] load build definition from Dockerfile                0.0s",
        " => => transferring dockerfile: 512B                               0.0s",
        " => [internal] load metadata for docker.io/library/node:22-alpine  1.2s",
        " => [builder 1/8] FROM docker.io/library/node:22-alpine            3.4s",
        " => [builder 4/8] COPY package.json package-lock.json ./           0.1s",
        " => [builder 5/8] RUN npm ci                                       31.7s",
        paint(" => => # npm error code EUSAGE", RED, args),
        "",
        paint(" => ERROR [builder 5/8] RUN npm ci", RED, args),
        "------",
        " > [builder 5/8] RUN npm ci:",
        "0.412 npm error `npm ci` can only install packages when your",
        "0.412 npm error package.json and package-lock.json are in sync.",
        "0.431 npm error Missing: typescript@5.6.3 from lock file",
        "------",
        paint('ERROR: failed to solve: process "/bin/sh -c npm ci" did not complete successfully: exit code: 1', RED, args),
        "",
        f"# image {tag}:latest still points at the last successful build",
    ]
    print("\n".join(lines))


MODES = {"deploy": deploy, "bench": bench, "docker": docker}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fabricate deploy, bench or docker output.")
    parser.add_argument("--mode", required=True, choices=sorted(MODES))
    parser.add_argument("--app", default="api", help="deployment name for deploy mode")
    parser.add_argument("--replicas", type=int, default=3)
    parser.add_argument("--image", default="app", help="image tag for docker mode")
    parser.add_argument("--before", default="./before", help="baseline binary for bench mode")
    parser.add_argument("--after", default="./after", help="candidate binary for bench mode")
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

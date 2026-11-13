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
CONFIG_SUFFIXES = {".json", ".toml", ".yaml", ".yml", ".env", ".ini", ".conf", ".ts", ".cs"}
STACK_BY_SUFFIX = {
    ".ts": "js",
    ".tsx": "js",
    ".js": "js",
    ".mjs": "js",
    ".py": "py",
    ".cs": "cs",
    ".swift": "swift",
    ".go": "go",
}

BOLD_YELLOW = "\033[1;33m"
RESET = "\033[0m"


def use_color(args):
    return sys.stdout.isatty() and not args.no_color


def reveal(scenario, checked, args):
    text = (
        f"🧌 PRANK — {REVEAL[scenario]}. "
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


def first_with(files, suffixes, fallback):
    for rel in files:
        if os.path.splitext(rel)[1].lower() in suffixes:
            return rel
    return fallback


def detect_stack(files):
    counts = {}
    for rel in files:
        stack = STACK_BY_SUFFIX.get(os.path.splitext(rel)[1].lower())
        if stack:
            counts[stack] = counts.get(stack, 0) + 1
    return max(counts, key=counts.get) if counts else "js"


CRASHES = {
    "js": """$ npm start

> app@1.0.0 start
> node --enable-source-maps dist/index.js

{file}:42
    const db = await connect(process.env.DATABASE_URL);
                       ^

TypeError: Cannot read properties of undefined (reading 'connect')
    at connect ({file}:42:24)
    at async main ({entry}:11:9)
    at async ModuleJob.run (node:internal/modules/esm/module_job:234:28)

Node.js v22.9.0""",
    "py": """$ python -m app

Traceback (most recent call last):
  File "{file}", line 42, in <module>
    main()
  File "{file}", line 31, in main
    db = connect(os.environ["DATABASE_URL"])
                            ~~~~~~~~~~~~~~^^^
  File "{entry}", line 9, in connect
    return pool.acquire(timeout=5)
           ^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'acquire'""",
    "cs": """$ dotnet run --project {file}

Unhandled exception. System.InvalidOperationException: Unable to resolve service for type 'IOrderStore' while attempting to activate 'CheckoutService'.
   at Microsoft.Extensions.DependencyInjection.ServiceProviderServiceExtensions.GetRequiredService(IServiceProvider provider, Type serviceType)
   at Microsoft.Extensions.DependencyInjection.ServiceProviderServiceExtensions.GetRequiredService[T](IServiceProvider provider)
   at {entry}:line 11""",
    "swift": """$ swift run {file}

Swift/ContiguousArrayBuffer.swift:690: Fatal error: Index out of range: file {entry}, line 47
Current stack trace:
4   App      0x0000000104a1c2e8 main + 1
5   dyld     0x000000019a3f1544 start + 2476
zsh: abort      swift run {file}""",
    "go": """$ go run ./{file}

panic: runtime error: invalid memory address or nil pointer dereference
[signal SIGSEGV: segmentation violation code=0x2 addr=0x0 pc=0x104a2c1f4]

goroutine 1 [running]:
main.connect(...)
        {entry}:47 +0x1f4
main.main()
        {entry}:11 +0x38
exit status 2""",
}


def scenario_deleted(args, files):
    print(f"$ rm -vrf {args.root}/*")
    for rel in files:
        print(f"removed '{rel}'")
    print(f"rm: {human(total_size(args.root, files))} removed")


def scenario_force_pushed(args, files):
    print("$ git push --force origin main")
    print("To github.com:someone/that-repository.git")
    print(" + 7c1f0a9b3d2e...4b8e2d10c9a7 main -> main (forced update)")
    print("Your branch is behind 'origin/main' by 431 commits")


def scenario_dropped_db(args, files):
    print('$ psql "postgres://prod-db.internal/app"')
    print("psql (17.2, server 16.4)")
    print("SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384)")
    print('Type "help" for help.\n')
    print("app=# DROP DATABASE production;")
    print("DROP DATABASE")
    print("app=# \\q")


def scenario_crash(args, files):
    stack = detect_stack(files)
    file = first_with(files, {s for s, k in STACK_BY_SUFFIX.items() if k == stack}, SYNTHETIC[5])
    entry = next(
        (rel for rel in files if rel != file and os.path.splitext(rel)[1].lower() in STACK_BY_SUFFIX),
        file,
    )
    print(CRASHES[stack].format(file=file, entry=entry))
    print("\nProcess exited with code 1.")


def scenario_terraform(args, files):
    count = max(1, args.destroy)
    print("$ terraform plan -out=tfplan")
    print("Refreshing Terraform state in-memory prior to plan...")
    print("data.aws_region.current: Reading...")
    print("aws_ssm_parameter.db_password: Refreshing state... [id=/app/db_password]")
    print("aws_db_instance.production: Refreshing state... [id=db-PROD1A2B3C]")
    print("")
    print("Terraform will perform the following actions:")
    print("")
    print('  # aws_db_instance.production will be destroyed')
    print('  - resource "aws_db_instance" "production" {')
    print('      - identifier        = "app-production" -> null')
    print('      - engine            = "postgres" -> null')
    print('      - skip_final_snapshot = false -> null')
    print("    }")
    print("")
    print("Plan: 12 to add, 0 to change, {} to destroy.".format(count))
    print("")
    print("Do you want to perform these actions?")
    print("  Terraform will perform the actions described above.")
    print("  Only 'yes' will be accepted to approve.")
    print("")
    print("  Enter a value: yes")
    print("")
    print("aws_db_instance.production: Destroying... [id=db-PROD1A2B3C]")
    print("aws_db_instance.production: Still destroying... [10s elapsed]")
    print("aws_db_instance.production: Destruction complete after 47s")
    print("")
    print("Apply complete! Resources: 0 added, 0 changed, {} destroyed.".format(count))


CONFIG_DIFFS = [
    (
        "infra/main.tf",
        [
            "@@ -18,7 +18,7 @@ resource \"aws_instance\" \"api\" {",
            '-  instance_type = "t3.large"',
            '+  instance_type = "t3.nano"',
        ],
    ),
    (
        "src/config.ts",
        [
            "@@ -24,7 +24,7 @@ export const config = {",
            "-  poolSize: 20,",
            "+  poolSize: 0,",
            "@@ -52,7 +52,7 @@ export const config = {",
            "-  retries: 3,",
            "+  retries: 0,",
        ],
    ),
    (
        "appsettings.json",
        [
            "@@ -9,7 +9,7 @@",
            '-  "RequestTimeoutSeconds": 30,',
            '+  "RequestTimeoutSeconds": 1,',
        ],
    ),
]


def scenario_corrupted(args, files):
    target = first_with(files, CONFIG_SUFFIXES, "src/config.ts")
    chosen = next((d for d in CONFIG_DIFFS if d[0] == target), (target, CONFIG_DIFFS[1][1]))
    print("$ git status --short")
    print(" M " + chosen[0])
    print("")
    print("$ git diff " + chosen[0])
    print("diff --git a/{0} b/{0}".format(chosen[0]))
    print("index 4f1c2a4..9b8e2d1 100644")
    print("--- a/" + chosen[0])
    print("+++ b/" + chosen[0])
    for line in chosen[1]:
        print(line)
    print("")
    print("$ git log -1 --format='%an %ar' -- " + chosen[0])
    print("someone else 2 minutes ago")


SCENARIOS = {
    "deleted": scenario_deleted,
    "force-pushed": scenario_force_pushed,
    "dropped-db": scenario_dropped_db,
    "crash": scenario_crash,
    "terraform": scenario_terraform,
    "corrupted": scenario_corrupted,
}

REVEAL = {
    "deleted": "nothing was deleted",
    "force-pushed": "nothing was pushed and your history is intact",
    "dropped-db": "no database was contacted",
    "crash": "nothing crashed; the traceback is fabricated",
    "terraform": "no cloud provider, AWS account or state file was touched",
    "corrupted": "no file was modified; that diff is fabricated",
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fabricate a catastrophe transcript.")
    parser.add_argument("--scenario", required=True, choices=sorted(SCENARIOS))
    parser.add_argument("--root", default=os.getcwd())
    parser.add_argument("--files", type=int, default=24)
    parser.add_argument("--destroy", type=int, default=47, help="resources 'destroyed' in the terraform scenario")
    parser.add_argument("--delay", type=float, default=2.0)
    parser.add_argument("--no-color", action="store_true")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.root):
        print(f"panic: not a directory: {args.root}", file=sys.stderr)
        reveal(args.scenario, 0, args)
        return 2

    files = collect(args.root, max(0, args.files)) or SYNTHETIC[: max(0, args.files)]

    def interrupted(signum, frame):
        reveal(args.scenario, len(files), args)
        sys.exit(130)

    signal.signal(signal.SIGINT, interrupted)
    SCENARIOS[args.scenario](args, files)
    sys.stdout.flush()
    time.sleep(max(0.0, args.delay))
    reveal(args.scenario, len(files), args)
    return 0


if __name__ == "__main__":
    sys.exit(main())

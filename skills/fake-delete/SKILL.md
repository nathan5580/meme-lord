---
name: fake-delete
description: "Use for catastrophe prank requests: deleted files, a force-push, a dropped database, a startup crash, a terraform destroy plan or a silent config corruption, with a guaranteed per-scenario reveal; never touches files, clusters or databases."
---

# Fake delete

1. Load the `troll-protocol` skill first (`../troll-protocol/SKILL.md` if your harness has no skill loader).
2. Pick a scenario:

| Scenario | Bit | Reveal says |
|---|---|---|
| `deleted` | `rm -vrf` over the real file list, with a real size | nothing was deleted |
| `force-pushed` | 431 commits behind a forced update | nothing was pushed, history intact |
| `dropped-db` | `DROP DATABASE production` then quiet | no database was contacted |
| `crash` | startup traceback in the repo's own language | nothing crashed, traceback fabricated |
| `terraform` | plan destroying 47 resources, then "yes" | no cloud provider or state file touched |
| `corrupted` | `git diff` with two silent config edits | no file was modified |

3. From this skill's directory, run it against the repo the victim will recognise:

```bash
python3 panic.py --scenario deleted --delay 2
python3 panic.py --scenario crash --delay 2
python3 panic.py --scenario terraform --destroy 47
```

4. Paste the transcript, optionally add one line of prose panic.
5. Always show the reveal line; the script prints it itself, worded for the scenario.

`--root` picks the directory to describe, `--files N` caps how many real paths appear, `--destroy N` sets the terraform body count, `--no-color` strips ANSI for pasting into chat.

## Worked example

```text
$ python3 panic.py --scenario deleted --files 4 --delay 1
$ rm -vrf /Users/home/RiderProjects/troll/*
removed 'README.md'
removed 'install.sh'
removed 'skills/fake-delete/panic.py'
removed 'tests/smoke.py'
rm: 41.2 KiB removed

🧌 PRANK — nothing was deleted. 4 files checked, nothing on this machine changed.
```

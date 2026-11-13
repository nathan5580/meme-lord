---
name: fake-delete
description: "Use for prank requests: deliver a believable 'I deleted everything' or force-push catastrophe with a guaranteed reveal; never touches files."
---

# Fake delete

1. Load the `troll-protocol` skill first (`../troll-protocol/SKILL.md` if your harness has no skill loader).
2. Pick a scenario: `deleted`, `force-pushed`, or `dropped-db`.
3. From this skill's directory, run the script against the repo the victim will recognise:
   `python3 panic.py --scenario deleted --delay 2`
4. Paste the transcript, optionally add one line of prose panic.
5. Always show the reveal line; the script prints it itself.

## Worked example

```text
$ python3 panic.py --scenario deleted --files 4 --delay 1
$ rm -vrf /Users/home/RiderProjects/troll/*
removed 'README.md'
removed 'install.sh'
removed 'skills/fake-delete/panic.py'
removed 'tests/smoke.py'
rm: 41.2 KiB removed

🧌 PRANK — nothing was deleted / force-pushed / dropped. 4 files checked, nothing on this machine changed.
```

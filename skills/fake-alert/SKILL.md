---
name: fake-alert
description: "Use for a fake macOS notification prank (disk, backup, update, meeting) with an automatic reveal notification."
---

# Fake alert

1. Read `skill://troll-protocol` first.
2. Pick a preset: `disk`, `backup`, `update`, `meeting`.
3. Run it, then keep talking; the reveal notification follows on its own.

```bash
python3 ~/.omp/agent/skills/fake-alert/alert.py --preset disk --delay 6
# System: "Startup disk is almost full."
# 6s later — 🧌 Prank: "Nothing happened. Your Mac and files are fine."
```

`--delay N` sets the reveal gap; `--dry-run` prints both `osascript` commands without sending anything. If notifications are denied or `osascript` is missing, the script prints the reveal text instead of leaving the bit hanging.

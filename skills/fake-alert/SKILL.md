---
name: fake-alert
description: "Use for a fake macOS notification prank (disk, backup, update, meeting) with an automatic reveal notification."
---

# Fake alert

1. Load the `troll-protocol` skill first (`../troll-protocol/SKILL.md` if your harness has no skill loader).
2. Pick a preset: `disk`, `backup`, `update`, `meeting`.
3. From this skill's directory, run it and keep talking; the reveal notification follows on its own.

```bash
python3 alert.py --preset disk --delay 6
# System: "Startup disk is almost full."
# 6s later — 🧌 Prank: "Nothing happened. Your Mac and files are fine."

python3 alert.py --title "iCloud" --body "Storage sync paused." --delay 4
```

`--delay N` sets the reveal gap; `--dry-run` prints both `osascript` commands without sending anything. If notifications are denied or `osascript` is missing, the script prints the reveal text instead of leaving the bit hanging.

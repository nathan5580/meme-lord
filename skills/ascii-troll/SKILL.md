---
name: ascii-troll
description: "Use when a text-only joke lands better than a card: block banners, cow speech bubbles, and static ASCII art for terminals and commit messages."
---

# ASCII troll

1. Load the `troll-protocol` skill first (`../troll-protocol/SKILL.md` if your harness has no skill loader).
2. Pick a mode. Output is plain text, so it survives terminals, commit messages, PR comments and CI logs. Nothing here claims damage, so no reveal line is needed.

```bash
# block banner (run from this skill's directory)
python3 ascii.py --mode banner --text "TROLLED"
python3 ascii.py --mode banner --text "ship it" --char "█"

# cow says it for you
python3 ascii.py --mode cow --text "should have read the migration docs"

# static art
python3 ascii.py --mode art --name shrug
python3 ascii.py --mode art --name skull
```

Art names: `shrug`, `tableflip`, `unflip`, `skull`, `thumbs`, `fine`, `troll`. Banner supports A–Z, 0–9 and `! ? . , - : ' *`.

Rewriting a real terminal line? Keep the jokey line out of CI logs and incident channels — plain text travels further than a PNG.

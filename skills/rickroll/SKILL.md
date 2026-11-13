---
name: rickroll
description: "Use when the user asks for a rickroll or a hidden gag link: disguised links, fake build/download progress, guaranteed reveal."
---

# Rickroll

1. Load the `troll-protocol` skill first (`../troll-protocol/SKILL.md` if your harness has no skill loader).

**Disguised link** — prints a Markdown link whose label hides the video (run from this skill's directory):

```bash
python3 rickroll.py --mode link --label "the deploy logs"
# [the deploy logs](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
```

**Fake progress** — a plausible build/download that ends in the reveal:

```bash
python3 rickroll.py --mode progress --task "npm install" --steps 40 --delay 0.15
```

Paste the output as-is. The progress mode self-reveals; the link mode needs the reveal in the same message.

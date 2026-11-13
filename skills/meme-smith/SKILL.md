---
name: meme-smith
description: "Use when a meme would land: render classic Impact memes, fake tweets, fake terminal transcripts, or chat bubbles to PNG."
---

# Meme smith

1. Read `skill://troll-protocol` first.
2. Pick the style that fits the bit; keep captions short (one idea per card).
3. Run the script, then show the printed PNG path so the user can forward it.

```bash
# classic: needs an image; output keeps the source size
python3 ~/.omp/agent/skills/meme-smith/memegen.py --style classic \
  --image /path/to/shot.png --top "one does not simply" --bottom "explain the codebase"

# fake tweet
python3 ~/.omp/agent/skills/meme-smith/memegen.py --style tweet \
  --text "my code compiles on the first try" --name "Dev" --handle @dev --verified

# fake terminal transcript ("\n" separates lines; "$" lines are coloured)
python3 ~/.omp/agent/skills/meme-smith/memegen.py --style terminal \
  --text '$ npm test\n42 failing, 0 passing' --title "zsh — 80×24"

# chat bubble
python3 ~/.omp/agent/skills/meme-smith/memegen.py --style chat \
  --side right --name Me --text "did you push the force push"
```

Default output is `./troll-out/<style>-<time>.png`; `--out PATH` overrides it. If a screenshot is at hand, `--style classic` on it is usually funnier than a synthetic card.

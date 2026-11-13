---
name: brutal-roast
description: "Use when the user asks to be roasted or wants playful insults: evidence-based roasts mined from the repo's git history, TODOs, and tests."
---

# Brutal roast

1. Read `skill://troll-protocol` first.
2. Gather facts with read-only commands, one per bullet:

- `git shortlog -sn` — who carried the repo
- `git log --oneline -20` — commit message quality
- `rg -c "TODO|FIXME" --glob '!node_modules'` — debt markers
- test files vs source files — `rg --files -g '*.test.*' -g '*_test.*' | wc -l` against `rg --files -g '*.ts' -g '*.cs' -g '*.swift' | wc -l`
- `git status --short | wc -l` — uncommitted chaos
- `du -sh */ | sort -h | tail -3` — where the bytes went

3. Write roasts. Each cites the exact number it mocks, one joke per fact, at most 6 roasts. No traits, appearance, family, or a person's real mistakes — the repo is the target.
4. Offer `meme-smith --style tweet` for the best line.

## Worked examples

- Fact: `git log` shows 14 of the last 20 commits are `fix`. Roast: "you don't have a commit history, you have 14 autosaves that each promised to be the last one."
- Fact: 61 TODOs across 9 files. Roast: "61 TODOs, and the oldest one is old enough to have its own TODO."
- Fact: 3 test files, 118 source files. Roast: "a test suite so small it qualifies as a rumour."

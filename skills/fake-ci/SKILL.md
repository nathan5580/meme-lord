---
name: fake-ci
description: "Use when a fake CI failure would land: GitHub Actions, Jenkins or GitLab logs with a failing test, always self-revealing; never runs a pipeline or calls an API."
---

# Fake CI

1. Load the `troll-protocol` skill first (`../troll-protocol/SKILL.md` if your harness has no skill loader).
2. Pick a provider: `actions`, `jenkins`, or `gitlab`.
3. From this skill's directory, run it against the repo the victim will recognise — the failing test name is taken from their real test files:

```bash
python3 ci.py --mode actions --repo acme/app --delay 1
python3 ci.py --mode jenkins --job app_main
python3 ci.py --mode gitlab --test "tests/test_parser.py::test_nested_quotes"
```

`--test` overrides the discovered name, `--seed` makes a run reproducible, `--delay N` sets how long the reveal waits. Output is text only; nothing is executed and no API is called.

Pair it with `meme-smith --style ci` when the bit lives in a screenshot instead of a log.

Never paste the log into a channel where a false failure would trigger a real response.

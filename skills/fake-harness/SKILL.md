---
name: fake-harness
description: "Use for agent-native pranks: fake context-window pressure, token burn, silent model downgrade, or a tool-call loop, printed as harness output with an automatic reveal."
---

# Fake harness

The prank for people who stare at an agent all day. Four modes, all text, all self-revealing.

1. Load the `troll-protocol` skill first (`../troll-protocol/SKILL.md` if your harness has no skill loader).
2. Pick a mode and run it from this skill's directory:

```bash
python3 harness.py --mode context --percent 97.4 --delay 1
python3 harness.py --mode tokens
python3 harness.py --mode downgrade --model claude-opus-4.1
python3 harness.py --mode loop --percent 41
```

| Mode | Bit |
|---|---|
| `context` | window at 97% and "your original request" already dropped |
| `tokens` | absurd session token burn table |
| `downgrade` | silent fallback from a frontier model to `gpt-3.5-turbo` |
| `loop` | the agent rereading the same file 41 times and calling it insight |

`--percent` is the context percentage (or loop repeats), `--window` the fake window size, `--victim` the noun in the reveal line. The reveal states nothing was compacted, billed, switched, or looped.

Best delivered as one message with the block quoted, then the reveal underneath. Do not run it against a harness that is mid-incident.

---
name: fake-ops
description: "Use for fake ops panic: a stuck kubectl rollout, a benchmark that got 42x slower, or a broken docker build, printed as console output with an automatic reveal; touches no cluster, daemon or benchmark."
---

# Fake ops

1. Load the `troll-protocol` skill first (`../troll-protocol/SKILL.md` if your harness has no skill loader).
2. Pick a mode: `deploy`, `bench`, or `docker`.
3. From this skill's directory, run it and paste the block:

```bash
python3 ops.py --mode deploy --app api --replicas 3 --delay 1
python3 ops.py --mode bench --before ./v1 --after ./v2
python3 ops.py --mode docker --image acme/app
```

Every mode ends with the reveal. Output is text only: no cluster, no Docker daemon, no benchmark binary is contacted or executed — the commands in the transcript are fictional.

Funniest pairings: `deploy` with a calm status-page line from `fake-outage`, or `bench` right after a commit message that says "perf: cache the hot path".

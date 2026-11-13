---
name: fake-outage
description: "Use for a fake incident bit: believable 5xx headers, a status-page timeline or a P0 announcement, plus a status meme card; contacts no endpoint or monitoring system."
---

# Fake outage

1. Load the `troll-protocol` skill first (`../troll-protocol/SKILL.md` if your harness has no skill loader).
2. Pick a piece, or stack two of them:

```bash
python3 outage.py --mode headers  --service api.example.com --status 503   # fabricated curl -i
python3 outage.py --mode status   --service api.example.com --minutes 47   # status-page timeline
python3 outage.py --mode incident --service checkout --region eu-west-1    # P0 announcement
```

3. Add the status card when the bit lives in a screenshot:

```bash
python3 ../meme-smith/memegen.py --style tweet \
  --text "Investigating — elevated error rates in all regions. Next update in 30 minutes." \
  --name "Acme Status" --handle @acmestatus
```

Every mode ends with the reveal: nothing was requested, no status page changed, no on-call was paged. `--minutes` sets the fake duration, `--seed` keeps a run reproducible.

Never call a real endpoint, `kubectl`, or `ssh`, and never post the status line where a real incident channel would respond to it.

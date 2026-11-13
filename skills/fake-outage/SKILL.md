---
name: fake-outage
description: "Use for a fake incident bit: believable 5xx/status-page panic composed from prose and meme cards, never real monitoring."
---

# Fake outage

1. Load the `troll-protocol` skill first (`../troll-protocol/SKILL.md` if your harness has no skill loader).
2. Compose the bit from three pieces, then end with the reveal.

**1. Fabricated `curl -i`** (text only; nothing is called):

```text
$ curl -i https://api.example.com/health
HTTP/2 503
content-type: application/json
retry-after: 120
x-request-id: 8f1c2a4e-0b7d-4a11-9d3f-6c5e8b2a7f01

{"error":"upstream_unavailable","status":503}
```

**2. Status page line:**

```text
[2026-11-13 14:02 UTC] Investigating — elevated error rates (all regions)
```

**3. Status card** (from this skill's directory):

```bash
python3 ../meme-smith/memegen.py --style tweet \
  --text "Investigating — elevated error rates in all regions. Next update in 30 minutes." \
  --name "Acme Status" --handle @acmestatus
```

Reveal: `🧌 prank — nothing actually happened` in the same message. Never call a real endpoint, `kubectl`, or `ssh`.

---
name: troll-protocol
description: "Load before any prank: reveal contract, banned claims, kill switch, and the no-real-damage floor for the troll skills."
---

# Prank safety floor

- **Reveal contract:** If the bit asserts loss, damage, or a live incident, the same assistant message must contain `🧌 prank — nothing actually happened` or the script itself must produce the reveal. Otherwise reveal within two assistant turns. Scripts always self-reveal.
- **No real damage:** No `rm`, `mv`, `truncate`, `git reset/clean`, DB connections, or writes outside the meme output directory. Prank payloads are text, PNGs, and notifications only. Printed commands are fictional; never execute them.
- **Banned claims:** Money, accounts or transfers; health or medical matters; legal, police or immigration; a live security breach or compromised account; employment status; fabricated misconduct of a real person.
- **Banned targets:** Protected traits, appearance, family, grief, addiction, and a person's real mistakes. Roasts cite repo facts, not the person.
- **Distress stop:** On “is this real”, “stop”, “not funny”, or visible panic, reveal and drop the bit immediately; no follow-up joke.
- **Never autonomously send:** Produce artifacts for the user to forward. No email, DM, or API posting.
- **Scope:** One prank per session unless the user asks for another. Never put prank output in CI/automation output or a shared incident channel where a false deleted line could trigger a real response.
- **Kill switch:** “no more pranks” or “normal mode” ends pranking for the session.

## Fake-delete delivery

```text
$ rm -vrf /example/*
removed 'src/index.ts'
removed 'README.md'
removed 'app/views/home.tsx'
removed 'tests/example.py'
🧌 prank — nothing actually happened
```

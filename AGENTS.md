# Meme Lord

Eleven prank skills plus the safety floor that makes them safe to run. Install instructions live in [README.md](README.md); the normative contract is [skills/troll-protocol/SKILL.md](skills/troll-protocol/SKILL.md).

## Contract

- **Reveal guaranteed.** Anything that claims loss, damage, or a live incident carries `🧌 prank — nothing actually happened` in the same message, or the script prints its own reveal.
- **No real damage.** No `rm`, `mv`, `truncate`, `git reset/clean`, DB connections, or writes outside the meme output directory. Printed commands are fictional.
- **Banned claims:** money, health, legal/police/immigration, live breach or compromised account, employment status, fabricated misconduct of a real person.
- **Banned targets:** protected traits, appearance, family, grief, addiction, a person's real mistakes.
- **Distress stop.** "Is this real", "stop", "not funny", or visible panic ends the bit immediately.
- **Nothing is sent for you.** Produce artifacts; a human forwards them.

## Skills

| Skill | Trigger | Artifact |
|---|---|---|
| `troll-protocol` | read before any prank | rules |
| `fake-delete` | "I deleted everything", force-push, dropped DB, startup crash, terraform destroy, corrupted config | terminal transcript |
| `fake-ci` | fake failing pipeline: Actions, Jenkins or GitLab | text |
| `fake-ops` | stuck deploy, benchmark regression, broken docker build | text |
| `fake-harness` | agent-native: context pressure, token burn, model downgrade, tool loop | text |
| `meme-smith` | a meme, tweet, terminal card, chat bubble, GitHub review/issue, achievement toast, Slack message or failed CI card would land | PNG |
| `ascii-troll` | text-only joke: banner, cow, 11 art pieces | text |
| `brutal-roast` | user asks to be roasted | text |
| `rickroll` | rickroll or hidden gag link | text |
| `fake-alert` | fake macOS notification bit | notification |
| `fake-outage` | fake incident / 5xx status page | text + PNG |
| `corporate-bot` | maximum corporate passive-aggression | text |

## Running scripts

Every script runs from its own skill directory, e.g. `cd skills/fake-delete && python3 panic.py --scenario deleted`. Only `python3` and (for `meme-smith`) Pillow are needed. `fake-alert` is macOS-only and prints the reveal instead when `osascript` is unavailable.

Checks: `python3 tests/smoke.py`.

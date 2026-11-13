# Troll Library

A pack of eight [OMP](https://github.com/nathan5580) skills for running harmless social pranks on a workstation: the "I deleted everything" bit, generated memes, evidence-based roasts, rickrolls, fake macOS notifications, fabricated incidents, and corporate passive-aggression. Every output is local text, a PIL-rendered PNG, or an `osascript` notification. Nothing in this repo deletes, moves, or writes to your files.

## Install

```bash
git clone https://github.com/nathan5580/troll-library.git
cd troll-library
bash install.sh          # symlinks skills/ into ~/.omp/agent/skills
```

Authored skills already in `~/.omp/agent/skills` are never overwritten. Restart the OMP session so it rediscovers skills.

## Uninstall

```bash
bash install.sh --uninstall   # removes only symlinks pointing into this repo
```

## Skills

| Skill | What it does | Artifact |
|---|---|---|
| `troll-protocol` | Safety floor every other skill reads first | rules |
| `fake-delete` | Believable `rm` / force-push / `DROP DATABASE` catastrophe | terminal transcript |
| `meme-smith` | Classic Impact memes, fake tweets, terminal cards, chat bubbles | PNG |
| `brutal-roast` | Roasts built from git history, TODOs, and test counts | text |
| `rickroll` | Disguised links and fake build/download progress | text |
| `fake-alert` | Fake macOS notifications with an automatic reveal | notification |
| `fake-outage` | Fabricated `curl`, status-page line, and status card | text + PNG |
| `corporate-bot` | Passive-aggressive compliance-bot rewrites | text |

## Try one

```bash
python3 skills/fake-delete/panic.py --scenario deleted --files 6 --delay 2
python3 skills/meme-smith/memegen.py --style tweet --text "my code compiles" --name Dev --handle @dev
python3 skills/rickroll/rickroll.py --mode progress --task "npm install" --steps 20
python3 skills/fake-alert/alert.py --preset disk --delay 4
```

Run the checks: `python3 tests/smoke.py` (requires Pillow).

## Safety

- **No real damage.** No `rm`, `mv`, `truncate`, `git reset/clean`, DB connections, or writes outside the meme output directory. Printed commands are fictional.
- **Reveal guaranteed.** Scripts print `🧌 PRANK — …` themselves; prose bits carry the reveal in the same message.
- **Distress stop.** "Is this real", "stop", or visible panic ends the bit immediately.
- **No banned claims or targets:** money, health, legal, security breaches, employment, protected traits, family, grief, or a person's real mistakes.
- **Nothing is sent for you.** You forward the artifact.

## License

MIT — see [LICENSE](LICENSE).

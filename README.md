# Troll Library

A pack of eight agent skills for harmless social pranks: the "I deleted everything" bit, generated memes, evidence-based roasts, rickrolls, fake macOS notifications, fabricated incidents, and corporate passive-aggression. Every output is local text, a PIL-rendered PNG, or an `osascript` notification. Nothing in this repo deletes, moves, or writes to your files.

Works wherever an agent can read files and run `python3`: OMP, Claude Code, Codex, Cursor, Copilot, Gemini CLI, or anything that reads `AGENTS.md`. Skills follow the common `SKILL.md` convention (`name` + `description` frontmatter), so skill-aware harnesses discover them and the rest can read them as plain Markdown.

## Install

```bash
git clone https://github.com/nathan5580/troll-library.git
cd troll-library
bash install.sh                                     # every harness dir it finds on this machine
```

| Harness | Install |
|---|---|
| OMP | `omp plugin marketplace add nathan5580/troll-library` then `omp plugin install troll-library@troll-library` |
| Claude Code | `/plugin marketplace add nathan5580/troll-library` then `/plugin install troll-library@troll-library` |
| Any harness with a skills dir | `bash install.sh --target ~/.claude/skills` (repeatable; `--copy` for real copies instead of symlinks) |
| Cursor, Copilot, Gemini CLI, other agents | point them at `AGENTS.md` in this repo, or copy `skills/` into their skills directory |
| Anything else | read `skills/troll-protocol/SKILL.md` first, then the skill you want |

Auto-detected targets: `~/.omp/agent/skills` (OMP), `~/.claude/skills` (Claude Code), `~/.codex/skills` (Codex), `~/.agents/skills` (universal). Authored skills and foreign symlinks are never overwritten; existing installs of this pack are refreshed.

Uninstall: `bash install.sh --uninstall` removes only what this repo installed, from the same targets.

Requirements: `python3` 3.10+. `meme-smith` also needs Pillow (`pip install pillow`). `fake-alert` is macOS-only and degrades to printed text elsewhere.

## Skills

| Skill | What it does | Artifact |
|---|---|---|
| `troll-protocol` | Safety floor every other skill reads first | rules |
| `fake-delete` | Believable `rm` / force-push / `DROP DATABASE` catastrophe | terminal transcript |
| `meme-smith` | Impact memes, fake tweets, terminal cards, chat bubbles | PNG |
| `brutal-roast` | Roasts built from git history, TODOs and test counts | text |
| `rickroll` | Disguised links and fake build progress | text |
| `fake-alert` | Fake macOS notifications with an automatic reveal | notification |
| `fake-outage` | Fabricated `curl`, status page and status card | text + PNG |
| `corporate-bot` | Passive-aggressive compliance rewrites | text |

## Try one

Run each script from its own skill directory.

```bash
python3 panic.py --scenario deleted --files 6 --delay 2                             # skills/fake-delete
python3 memegen.py --style tweet --text "my code compiles" --name Dev --handle @dev # skills/meme-smith
python3 rickroll.py --mode progress --task "npm install" --steps 20                 # skills/rickroll
python3 alert.py --preset disk --delay 4                                            # skills/fake-alert
```

Checks: `python3 tests/smoke.py` from the repo root (needs Pillow).

## Safety

- **No real damage.** No `rm`, `mv`, `truncate`, `git reset/clean`, DB connections, or writes outside the meme output directory. Printed commands are fictional.
- **Reveal guaranteed.** Scripts print `🧌 PRANK — …` themselves; prose bits carry the reveal in the same message.
- **Distress stop.** "Is this real", "stop", or visible panic ends the bit immediately.
- **No banned claims or targets:** money, health, legal, security breaches, employment, protected traits, family, grief, or a person's real mistakes.
- **Nothing is sent for you.** You forward the artifact.

Full contract: [`skills/troll-protocol/SKILL.md`](skills/troll-protocol/SKILL.md).

## License

MIT — see [LICENSE](LICENSE).

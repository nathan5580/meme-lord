# Meme Lord

[![test](https://github.com/nathan5580/meme-lord/actions/workflows/test.yml/badge.svg)](https://github.com/nathan5580/meme-lord/actions/workflows/test.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![release](https://img.shields.io/github/v/release/nathan5580/meme-lord)](https://github.com/nathan5580/meme-lord/releases)

Eleven agent skills for harmless social pranks: the "I deleted everything" bit, a startup crash, a terraform destroy plan, generated meme cards, fake CI and deploy logs, fake harness telemetry, ASCII banners, evidence-based roasts, rickrolls, fake macOS notifications, fabricated incidents, and corporate passive-aggression.

Everything runs locally. Prank payloads are text, PIL-rendered PNGs, and `osascript` notifications. No script deletes, moves, or writes to your files, and every script prints its own reveal, worded for the scenario it faked.

Works wherever an agent can read files and run `python3`: **OMP**, **Claude Code**, **Codex**, **Cursor**, **Copilot**, **Gemini CLI**, or anything that reads `AGENTS.md`. Skills use the common `SKILL.md` convention (`name` + `description` frontmatter), so skill-aware harnesses discover them and the rest read them as plain Markdown.

## Install

```bash
git clone https://github.com/nathan5580/meme-lord.git && cd meme-lord
bash install.sh        # every harness skill dir found on this machine
```

| Harness | Install |
|---|---|
| OMP | `omp plugin marketplace add nathan5580/meme-lord` → `omp plugin install troll-library@troll-library` |
| Claude Code | `/plugin marketplace add nathan5580/meme-lord` → `/plugin install troll-library@troll-library` |
| Any harness with a skills dir | `bash install.sh --target ~/.claude/skills` (repeatable, `--copy` for real copies) |
| Cursor, Copilot, Gemini CLI, other agents | point them at `AGENTS.md`, or copy `skills/` into their skills directory |
| Anything else | read `skills/troll-protocol/SKILL.md`, then the skill you want |

Auto-detected targets: `~/.omp/agent/skills`, `~/.claude/skills`, `~/.codex/skills`, `~/.agents/skills`. Authored skills and foreign symlinks are never overwritten; existing installs of this pack are refreshed in place. `bash install.sh --uninstall` removes only what this repo installed.

Requirements: `python3` 3.10+. `meme-smith` also needs Pillow. `fake-alert` is macOS-only and prints the reveal instead when `osascript` is missing.

## Skills

| Skill | What it does | Artifact |
|---|---|---|
| `troll-protocol` | Safety floor every other skill reads first | rules |
| `fake-delete` | Catastrophe transcripts: `rm`, force-push, `DROP DATABASE`, crash, terraform destroy, silent config corruption | text |
| `fake-ci` | Failing GitHub Actions, Jenkins or GitLab logs, failing test taken from the victim's repo | text |
| `fake-ops` | Stuck `kubectl` rollout, 42× benchmark regression, broken docker build | text |
| `fake-harness` | Agent-native: context at 97%, token burn, silent model downgrade, tool-call loop | text |
| `meme-smith` | Nine card styles: impact, tweet, terminal, chat, GitHub review and issue, achievement toast, Slack, failed CI | PNG |
| `ascii-troll` | Block banners, cow speech bubbles, 11 art pieces | text |
| `brutal-roast` | Roasts built from git history, TODOs and test counts | text |
| `rickroll` | Disguised links and fake build progress | text |
| `fake-alert` | Fake macOS notifications (presets or custom) with an automatic reveal | notification |
| `fake-outage` | Fabricated `curl` headers, status-page timeline, P0 announcement, plus a status card | text + PNG |
| `corporate-bot` | Passive-aggressive compliance rewrites | text |

## Demo

Cards rendered by `meme-smith` — nothing below is a screenshot of a real service:

![fake tweet card](docs/demo-tweet.png)

![fake terminal card](docs/demo-terminal.png)

![chat bubble card](docs/demo-chat.png)

![GitHub review card](docs/demo-review.png)

![failed CI card](docs/demo-ci.png)

![achievement toast](docs/demo-achievement.png)

`ascii-troll` for places a PNG cannot go:

```text
#### ###. .##. #... #... #### ###.
.#.. #..# #..# #... #... #... #..#
.#.. ###. #..# #... #... ###. #..#
.#.. #.#. #..# #... #... #... #..#
.#.. #..# .##. #### #### #### ###.

 ________________________________________
/ should have read the migration docs    \
\ before dropping the column             /
 ----------------------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
```

`fake-delete` — the headline bit, with the reveal attached:

```text
$ rm -vrf /Users/you/project/*
removed 'README.md'
removed 'install.sh'
removed 'skills/fake-delete/panic.py'
removed 'tests/smoke.py'
rm: 41.2 KiB removed

🧌 PRANK — nothing was deleted. 4 files checked, nothing on this machine changed.
```

`fake-ci` — a failed pipeline that never ran:

```text
$ gh run view 7890 --log-failed
test (ubuntu-latest)	Run pytest -q	2026-11-13T10:14:19.771Z .......F.......
test (ubuntu-latest)	Run pytest -q	2026-11-13T10:14:31.204Z FAILED tests/test_parser.py::test_nested_quotes
##[error]Process completed with exit code 1.

🧌 PRANK — no pipeline ran, nothing failed, 1 test file on this machine is untouched.
```

`fake-harness` — the prank aimed at agents themselves:

```text
⚠  Context window 97.4% used — 192,267 / 197,400 tokens
   auto-compacting conversation… (attempt 3 of 3)
   dropped: 41 tool results, 6 user messages, your original request
   retained: the one line you wanted changed

🧌 PRANK — your context is fine; nothing was compacted and nothing was dropped.
```

## Try one

Run each script from its own skill directory.

```bash
python3 panic.py --scenario deleted --files 6 --delay 2                              # skills/fake-delete
python3 panic.py --scenario crash                                               # skills/fake-delete
python3 panic.py --scenario terraform --destroy 47                               # skills/fake-delete
python3 ci.py --mode actions --repo acme/app                                     # skills/fake-ci
python3 ops.py --mode deploy --app api                                           # skills/fake-ops
python3 outage.py --mode status --service api.example.com                        # skills/fake-outage
python3 harness.py --mode context --percent 97.4                                 # skills/fake-harness
python3 memegen.py --style review --name octocat-bot --text "this will not scale"  # skills/meme-smith
python3 memegen.py --style ci --title acme/app --text "FAILED tests/test_x.py"     # skills/meme-smith
python3 ascii.py --mode banner --text "TROLLED"                                      # skills/ascii-troll
python3 rickroll.py --mode progress --task "npm install" --steps 20                  # skills/rickroll
python3 alert.py --preset disk --delay 4                                             # skills/fake-alert
```

## The safety floor

`skills/troll-protocol/SKILL.md` is normative for every skill in the pack.

- **Reveal guaranteed** — anything claiming loss, damage, or a live incident carries `🧌 prank — nothing actually happened` in the same message, or the script prints it.
- **No real damage** — no `rm`, `mv`, `truncate`, `git reset/clean`, DB connections, or writes outside the meme output directory.
- **Banned claims** — money, health, legal/police/immigration, live breach or compromised account, employment status, fabricated misconduct of a real person.
- **Banned targets** — protected traits, appearance, family, grief, addiction, a person's real mistakes.
- **Distress stop** — "is this real", "stop", "not funny", or visible panic ends the bit immediately.
- **Nothing is sent for you** — the agent produces artifacts; a human forwards them.

## Layout

```text
skills/<skill>/SKILL.md      skill instructions (frontmatter: name, description)
skills/<skill>/*.py          stdlib scripts (Pillow only for memegen.py)
tests/smoke.py               every script plus an install/uninstall round trip
install.sh                   multi-harness installer
.claude-plugin/              plugin + marketplace manifests (OMP, Claude Code)
.cursor/rules/               Cursor rule mirroring the floor
AGENTS.md, CLAUDE.md         entry points for harnesses without a skill loader
```

## Contributing

`python3 tests/smoke.py` must pass before a PR. CI runs it on Ubuntu and macOS. New pranks belong behind the floor: self-revealing or paired with a reveal, no real-world harm, no real endpoint calls.

## License

MIT — see [LICENSE](LICENSE).

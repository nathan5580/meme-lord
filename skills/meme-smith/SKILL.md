---
name: meme-smith
description: "Use when a meme would land: render classic Impact memes, fake tweets, terminal transcripts, chat bubbles, GitHub reviews and issues, Xbox achievements, Slack messages or failed CI cards to PNG."
---

# Meme smith

1. Load the `troll-protocol` skill first (`../troll-protocol/SKILL.md` if your harness has no skill loader).
2. Pick the style that fits the bit; keep captions short (one idea per card).
3. From this skill's directory, run the script; then show the printed PNG path so the user can forward it.

| Style | Needs | Use for |
|---|---|---|
| `classic` | `--image` | Impact captions on a screenshot |
| `tweet` | `--text` | fake tweet from a person or a status bot |
| `terminal` | `--text` | shell transcript card (dark, `$` lines green) |
| `chat` | `--text` | one chat bubble, `--side left\|right` |
| `review` | `--text` | GitHub review: red "requested changes" or `--approved` green |
| `issue` | `--title` | closed-as-not-planned issue with `--labels bug,P1` |
| `achievement` | `--text` | Xbox toast, `--score 50G`, `--title` overline |
| `slack` | `--text` | Slack message with reactions, `--handle #incidents` |
| `ci` | `--text` | failed GitHub Actions card, `--title repo --name branch` |

```bash
# classic: needs an image; output keeps the source size
python3 memegen.py --style classic \
  --image /path/to/shot.png --top "one does not simply" --bottom "explain the codebase"

# fake tweet
python3 memegen.py --style tweet \
  --text "my code compiles on the first try" --name "Dev" --handle @dev --verified

# terminal / chat
python3 memegen.py --style terminal --text '$ npm test\n42 failing, 0 passing' --title "zsh — 80×24"
python3 memegen.py --style chat --side right --name Me --text "did you push the force push"

# review, with a code line
python3 memegen.py --style review --name octocat-bot --handle @reviewer \
  --text "Have you considered that this cannot scale?" \
  --code "for (const row of rows) { await query(row); }"

# issue / achievement / slack / ci
python3 memegen.py --style issue --title "App crashes on startup" --labels "bug,P1,wontfix"
python3 memegen.py --style achievement --text "Deleted production" --score 50G
python3 memegen.py --style slack --name Dev --handle "#incidents" --text "did you push the force push" --likes 12
python3 memegen.py --style ci --title acme/app --bottom "test (ubuntu-latest)" --text "FAILED tests/test_parser.py::test_nested_quotes"
```

Cards render at 1080 px wide. Default output is `./troll-out/<style>-<time>.png`; `--out PATH` overrides it. If a screenshot is at hand, `--style classic` on it is usually funnier than a synthetic card.

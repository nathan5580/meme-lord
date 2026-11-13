#!/usr/bin/env python3
"""One runnable check for every script in the pack. Exits 1 naming the first failure."""

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
failures = []


def script(rel, *args, **kwargs):
    return subprocess.run([PY, str(ROOT / rel), *args], capture_output=True, text=True, **kwargs)


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(name, fn):
    try:
        fn()
    except AssertionError as exc:
        failures.append(name)
        print(f"FAIL {name}: {exc}")
    else:
        print(f"PASS {name}")


def panic_cases(tmp):
    sentinel = tmp / "keep.txt"
    sentinel.write_text("still here\n")
    (tmp / "src").mkdir(exist_ok=True)
    (tmp / "src" / "a.py").write_text("print(1)\n")

    def deleted():
        result = script("skills/fake-delete/panic.py", "--scenario", "deleted", "--root", str(tmp), "--files", "3", "--delay", "0")
        assert result.returncode == 0, result.stderr
        assert "PRANK" in result.stdout, result.stdout
        assert "removed 'src/a.py'" in result.stdout, result.stdout
        assert sentinel.exists(), "sentinel was deleted"

    def force_pushed():
        result = script("skills/fake-delete/panic.py", "--scenario", "force-pushed", "--root", str(tmp), "--delay", "0")
        assert result.returncode == 0, result.stderr
        assert "forced update" in result.stdout and "PRANK" in result.stdout, result.stdout
        assert sentinel.exists(), "sentinel was deleted"

    def dropped_db():
        result = script("skills/fake-delete/panic.py", "--scenario", "dropped-db", "--root", str(tmp), "--delay", "0")
        assert result.returncode == 0, result.stderr
        assert "DROP DATABASE" in result.stdout and "PRANK" in result.stdout, result.stdout
        assert sentinel.exists(), "sentinel was deleted"

    def bad_root():
        result = script("skills/fake-delete/panic.py", "--scenario", "deleted", "--root", "/nonexistent", "--delay", "0")
        assert result.returncode == 2, result.returncode
        output = result.stdout + result.stderr
        assert "/nonexistent" in output and "PRANK" in output, output
        assert "Traceback" not in output, output

    def crash():
        result = script("skills/fake-delete/panic.py", "--scenario", "crash", "--root", str(tmp), "--delay", "0")
        assert result.returncode == 0, result.stderr
        assert "nothing crashed" in result.stdout, result.stdout
        assert "Traceback" in result.stdout or "TypeError" in result.stdout, result.stdout
        assert sentinel.exists(), "sentinel was deleted"

    def terraform():
        result = script("skills/fake-delete/panic.py", "--scenario", "terraform", "--destroy", "3", "--delay", "0")
        assert result.returncode == 0, result.stderr
        assert "3 to destroy" in result.stdout and "3 destroyed" in result.stdout, result.stdout
        assert "no cloud provider" in result.stdout, result.stdout

    def corrupted():
        result = script("skills/fake-delete/panic.py", "--scenario", "corrupted", "--root", str(tmp), "--delay", "0")
        assert result.returncode == 0, result.stderr
        assert "fabricated" in result.stdout and "@@" in result.stdout, result.stdout
        assert sentinel.exists(), "sentinel was deleted"

    def every_scenario():
        scenarios = sorted(load("skills/fake-delete/panic.py", "panic").SCENARIOS)
        assert len(scenarios) == 6, scenarios
        for scenario in scenarios:
            result = script("skills/fake-delete/panic.py", "--scenario", scenario, "--root", str(tmp), "--delay", "0")
            assert result.returncode == 0, (scenario, result.stderr)
            assert "🧌 PRANK" in result.stdout, (scenario, result.stdout[-300:])
        assert sentinel.exists(), "sentinel was deleted"

    for name, fn in [
        ("panic deleted", deleted),
        ("panic force-pushed", force_pushed),
        ("panic dropped-db", dropped_db),
        ("panic crash", crash),
        ("panic terraform", terraform),
        ("panic corrupted", corrupted),
        ("panic every scenario reveals", every_scenario),
        ("panic bad root", bad_root),
    ]:
        check(name, fn)


def meme_cases(tmp):
    def card(style, *extra):
        out = tmp / f"{style}.png"
        result = script("skills/meme-smith/memegen.py", "--style", style, *extra, "--out", str(out))
        assert result.returncode == 0, result.stderr
        img = Image.open(out)
        assert len(img.convert("RGB").getcolors(maxcolors=1_000_000) or [1]) > 1, "blank image"

    def classic():
        source = tmp / "base.png"
        Image.new("RGB", (400, 400), (20, 90, 160)).save(source)
        out = tmp / "classic.png"
        result = script("skills/meme-smith/memegen.py", "--style", "classic", "--image", str(source), "--top", "one does not simply", "--out", str(out))
        assert result.returncode == 0, result.stderr
        assert Image.open(out).size == (400, 400), "classic changed the source size"

    def classic_long_caption():
        source = tmp / "base.png"
        out = tmp / "classic-long.png"
        top = "one does not simply write a caption far too long for a tiny image and expect it to fit"
        result = script("skills/meme-smith/memegen.py", "--style", "classic", "--image", str(source), "--top", top, "--bottom", "and yet here we are", "--out", str(out))
        assert result.returncode == 0, result.stderr
        img = Image.open(out).convert("RGB")
        assert img.size == (400, 400), img.size
        white = sum(count for count, color in img.getcolors(maxcolors=1_000_000) if sum(color) > 700)
        assert white > 2000, f"caption barely rendered ({white} light pixels)"

    def missing_image():
        result = script("skills/meme-smith/memegen.py", "--style", "classic")
        assert result.returncode == 2 and "--image" in result.stderr, result.stderr

    def review_states():
        bad, good = tmp / "review-bad.png", tmp / "review-good.png"
        for out, extra in ((bad, []), (good, ["--approved"])):
            result = script("skills/meme-smith/memegen.py", "--style", "review", "--text", "this will not scale", "--code", "retry();", *extra, "--out", str(out))
            assert result.returncode == 0, result.stderr
        assert bad.read_bytes() != good.read_bytes(), "approved and requested-changes cards are identical"

    def styles_match_renderers():
        names = sorted(load("skills/meme-smith/memegen.py", "memegen").RENDERERS)
        assert names == ["achievement", "chat", "ci", "classic", "issue", "review", "slack", "terminal", "tweet"], names

    check("meme tweet", lambda: card("tweet", "--text", "my code compiles on the first try", "--name", "Dev", "--handle", "@dev"))
    check("meme terminal", lambda: card("terminal", "--text", "$ npm test\n42 failing"))
    check("meme chat", lambda: card("chat", "--side", "right", "--text", "did you push the force push"))
    check("meme review", lambda: card("review", "--text", "this will not scale", "--code", "retry();"))
    check("meme issue", lambda: card("issue", "--title", "crashes on startup", "--labels", "bug,P1,wontfix"))
    check("meme achievement", lambda: card("achievement", "--text", "Deleted production", "--score", "50G"))
    check("meme slack", lambda: card("slack", "--text", "did you push the force push", "--handle", "#incidents", "--likes", "12"))
    check("meme ci", lambda: card("ci", "--title", "acme/app", "--name", "main", "--text", "FAILED tests/test_parser.py::test_nested_quotes"))
    check("meme review states differ", review_states)
    check("meme nine styles", styles_match_renderers)
    check("meme classic", classic)
    check("meme classic long caption", classic_long_caption)
    check("meme missing image", missing_image)


def rickroll_cases():
    def link():
        result = script("skills/rickroll/rickroll.py", "--mode", "link")
        assert result.returncode == 0, result.stderr
        assert "watch?v=dQw4w9WgXcQ" in result.stdout, result.stdout

    def progress():
        result = script("skills/rickroll/rickroll.py", "--mode", "progress", "--steps", "4", "--delay", "0")
        assert result.returncode == 0, result.stderr
        assert "Rickroll complete" in result.stdout, result.stdout
        assert "100%" in result.stdout, result.stdout

    check("rickroll link", link)
    check("rickroll progress", progress)


def alert_cases():
    def presets():
        for preset in ("disk", "backup", "update", "meeting"):
            result = script("skills/fake-alert/alert.py", "--preset", preset, "--dry-run")
            assert result.returncode == 0, result.stderr
            assert result.stdout.count("display notification") == 2, result.stdout
            assert "Nothing happened" in result.stdout, result.stdout

    def custom():
        result = script("skills/fake-alert/alert.py", "--title", "iCloud", "--body", "Storage sync paused.", "--dry-run")
        assert result.returncode == 0, result.stderr
        assert 'title "iCloud"' in result.stdout, result.stdout
        assert result.stdout.count("display notification") == 2, result.stdout

    def missing_text():
        result = script("skills/fake-alert/alert.py", "--dry-run")
        assert result.returncode == 2 and "--preset" in result.stderr, result.stderr

    check("alert dry-run presets", presets)
    check("alert custom text", custom)
    check("alert missing preset", missing_text)


def ascii_cases():
    def banner():
        result = script("skills/ascii-troll/ascii.py", "--mode", "banner", "--text", "TROLLED")
        assert result.returncode == 0, result.stderr
        rows = result.stdout.rstrip("\n").split("\n")
        assert len(rows) == 5, rows
        assert all("#" in row for row in rows), rows
        assert rows[0].split(" ")[0] == "####", "T glyph wrong: " + rows[0]

    def unknown_char():
        result = script("skills/ascii-troll/ascii.py", "--mode", "banner", "--text", "a~b")
        assert result.returncode == 0, result.stderr
        assert "###." in result.stdout, result.stdout

    def cow():
        result = script("skills/ascii-troll/ascii.py", "--mode", "cow", "--text", "read the migration docs")
        assert result.returncode == 0, result.stderr
        assert "read the migration docs" in result.stdout, result.stdout
        assert "(oo)" in result.stdout, result.stdout

    def art():
        result = script("skills/ascii-troll/ascii.py", "--mode", "art", "--name", "skull")
        assert result.returncode == 0, result.stderr
        assert "() ()" in result.stdout, result.stdout

    def bad_art():
        result = script("skills/ascii-troll/ascii.py", "--mode", "art", "--name", "nope")
        assert result.returncode == 2, result.returncode

    check("ascii banner", banner)
    check("ascii unknown char", unknown_char)
    check("ascii cow", cow)
    check("ascii art", art)
    check("ascii bad art name", bad_art)


def ci_cases():
    def mode(name, expect):
        result = script("skills/fake-ci/ci.py", "--mode", name, "--delay", "0", "--seed", "1")
        assert result.returncode == 0, result.stderr
        assert expect in result.stdout, result.stdout
        assert "🧌 PRANK" in result.stdout, result.stdout

    def explicit_test():
        result = script("skills/fake-ci/ci.py", "--mode", "actions", "--test", "tests/test_parser.py::test_nested_quotes", "--delay", "0")
        assert result.returncode == 0, result.stderr
        assert "tests/test_parser.py::test_nested_quotes" in result.stdout, result.stdout

    def every_mode():
        modes = sorted(load("skills/fake-ci/ci.py", "ci").MODES)
        assert modes == ["actions", "gitlab", "jenkins"], modes
        for name in modes:
            result = script("skills/fake-ci/ci.py", "--mode", name, "--delay", "0")
            assert result.returncode == 0, (name, result.stderr)
            assert "test file" in result.stdout, (name, result.stdout[-300:])

    check("ci actions", lambda: mode("actions", "gh run view"))
    check("ci jenkins", lambda: mode("jenkins", "Finished: FAILURE"))
    check("ci gitlab", lambda: mode("gitlab", "ERROR: Job failed"))
    check("ci explicit test", explicit_test)
    check("ci every mode reveals", every_mode)


def ops_cases():
    def mode(name, expect):
        result = script("skills/fake-ops/ops.py", "--mode", name, "--delay", "0", "--seed", "1")
        assert result.returncode == 0, result.stderr
        assert expect in result.stdout, result.stdout
        assert "🧌 PRANK" in result.stdout, result.stdout

    def replicas():
        result = script("skills/fake-ops/ops.py", "--mode", "deploy", "--app", "billing", "--replicas", "5", "--delay", "0")
        assert result.returncode == 0, result.stderr
        assert "deployment/billing" in result.stdout and "billing-7d9f8c6b5d" in result.stdout, result.stdout

    check("ops deploy", lambda: mode("deploy", "CrashLoopBackOff"))
    check("ops bench", lambda: mode("bench", "times slower"))
    check("ops docker", lambda: mode("docker", "failed to solve"))
    check("ops deploy naming", replicas)


def outage_cases():
    def mode(name, expect):
        result = script("skills/fake-outage/outage.py", "--mode", name, "--delay", "0", "--seed", "1")
        assert result.returncode == 0, result.stderr
        assert expect in result.stdout, result.stdout
        assert "🧌 PRANK" in result.stdout, result.stdout

    def status_code():
        result = script("skills/fake-outage/outage.py", "--mode", "headers", "--status", "502", "--delay", "0")
        assert result.returncode == 0, result.stderr
        assert "HTTP/2 502" in result.stdout and '"status":502' in result.stdout, result.stdout

    check("outage headers", lambda: mode("headers", "HTTP/2 503"))
    check("outage status", lambda: mode("status", "Major outage"))
    check("outage incident", lambda: mode("incident", "[P0]"))
    check("outage status code", status_code)


def harness_cases():
    def mode(name, expect):
        result = script("skills/fake-harness/harness.py", "--mode", name, "--delay", "0")
        assert result.returncode == 0, result.stderr
        assert expect in result.stdout, result.stdout
        assert "🧌 PRANK" in result.stdout, result.stdout

    def percent():
        result = script("skills/fake-harness/harness.py", "--mode", "context", "--percent", "99.9", "--delay", "0")
        assert result.returncode == 0, result.stderr
        assert "99.9% used" in result.stdout, result.stdout

    def loop_repeats():
        result = script("skills/fake-harness/harness.py", "--mode", "loop", "--percent", "7", "--delay", "0")
        assert result.returncode == 0, result.stderr
        assert "read   × 7" in result.stdout, result.stdout

    check("harness context", lambda: mode("context", "compacting"))
    check("harness tokens", lambda: mode("tokens", "Token usage"))
    check("harness downgrade", lambda: mode("downgrade", "rate_limited"))
    check("harness loop", lambda: mode("loop", "read the same file again"))
    check("harness percent", percent)
    check("harness loop repeats", loop_repeats)


def pack_cases(tmp):
    def frontmatter():
        for skill_dir in sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir()):
            text = (skill_dir / "SKILL.md").read_text()
            assert text.startswith("---\n"), f"{skill_dir.name}: no frontmatter"
            head = text.split("---\n")[1]
            fields = dict(line.split(": ", 1) for line in head.strip().split("\n") if ": " in line)
            assert fields.get("name") == skill_dir.name, f"{skill_dir.name}: name is {fields.get('name')}"
            assert len(fields.get("description", "")) > 20, f"{skill_dir.name}: thin description"

    def plugin_lists_every_skill():
        import json
        listed = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["skills"]
        on_disk = {f"./skills/{p.name}" for p in (ROOT / "skills").iterdir() if p.is_dir()}
        assert set(listed) == on_disk, (sorted(set(listed) - on_disk), sorted(on_disk - set(listed)))

    def every_art():
        names = sorted(load("skills/ascii-troll/ascii.py", "ascii_troll").ART)
        assert len(names) >= 11, names
        for name in names:
            result = script("skills/ascii-troll/ascii.py", "--mode", "art", "--name", name)
            assert result.returncode == 0, (name, result.stderr)
            assert result.stdout.strip(), (name, "empty art")

    def scripts_are_readonly():
        banned = ("os.remove(", "shutil.rmtree(", "os.rename(", "os.unlink(", "import urllib", "import requests", "import socket")
        for script_path in sorted((ROOT / "skills").glob("*/*.py")):
            source = script_path.read_text()
            for word in banned:
                assert word not in source, f"{script_path.name} references {word}"
            if script_path.name != "alert.py":
                assert "import subprocess" not in source, f"{script_path.name} spawns subprocesses"

    def memegen_writes_only_out():
        out = tmp / "only-out" / "card.png"
        result = script("skills/meme-smith/memegen.py", "--style", "slack", "--text", "hi", "--out", str(out))
        assert result.returncode == 0, result.stderr
        assert out.exists(), result.stdout

    check("pack frontmatter", frontmatter)
    check("pack plugin manifest", plugin_lists_every_skill)
    check("pack ascii art", every_art)
    check("pack scripts readonly", scripts_are_readonly)
    check("pack memegen out path", memegen_writes_only_out)


def install_cases(tmp):
    def roundtrip():
        target = tmp / "harness-skills"
        (target / "authored-skill").mkdir(parents=True)
        (target / "authored-skill" / "SKILL.md").write_text("mine\n")

        def install(*extra):
            result = subprocess.run(["bash", str(ROOT / "install.sh"), "--target", str(target), *extra], capture_output=True, text=True)
            assert result.returncode == 0, result.stderr
            return result

        install()
        entries = sorted(p.name for p in target.iterdir())
        expected = len([p for p in (ROOT / "skills").iterdir() if p.is_dir()]) + 1
        assert len(entries) == expected, entries
        assert all((target / name).is_symlink() for name in entries if name != "authored-skill"), entries

        install("--copy")
        assert (target / "fake-delete" / ".troll-library").exists(), "copy marker missing"
        assert (target / "fake-delete" / "panic.py").exists(), "copy missing script"

        install("--uninstall")
        assert [p.name for p in target.iterdir()] == ["authored-skill"], "uninstall left files or ate the authored skill"
        assert (target / "authored-skill" / "SKILL.md").read_text() == "mine\n", "authored skill was modified"

    check("install round trip", roundtrip)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        panic_cases(tmp)
        meme_cases(tmp)
        pack_cases(tmp)
        install_cases(tmp)
    rickroll_cases()
    alert_cases()
    ascii_cases()
    ci_cases()
    ops_cases()
    outage_cases()
    harness_cases()
    if failures:
        print(f"\n{len(failures)} failed: {', '.join(failures)}")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

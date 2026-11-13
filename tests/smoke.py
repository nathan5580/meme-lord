#!/usr/bin/env python3
"""One runnable check for every script in the pack. Exits 1 naming the first failure."""

import os
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

    for name, fn in [
        ("panic deleted", deleted),
        ("panic force-pushed", force_pushed),
        ("panic dropped-db", dropped_db),
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

    check("meme tweet", lambda: card("tweet", "--text", "my code compiles on the first try", "--name", "Dev", "--handle", "@dev"))
    check("meme terminal", lambda: card("terminal", "--text", "$ npm test\n42 failing"))
    check("meme chat", lambda: card("chat", "--side", "right", "--text", "did you push the force push"))
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
        install_cases(tmp)
    rickroll_cases()
    alert_cases()
    ascii_cases()
    if failures:
        print(f"\n{len(failures)} failed: {', '.join(failures)}")
        return 1
    print("\nall checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

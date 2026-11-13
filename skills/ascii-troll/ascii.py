#!/usr/bin/env python3
"""ASCII trolling: block banners, cow speech bubbles, and static art. Prints text only."""

import argparse
import sys
import textwrap

GLYPHS = {
    "A": (".##.", "#..#", "####", "#..#", "#..#"),
    "B": ("###.", "#..#", "###.", "#..#", "###."),
    "C": (".###", "#...", "#...", "#...", ".###"),
    "D": ("###.", "#..#", "#..#", "#..#", "###."),
    "E": ("####", "#...", "###.", "#...", "####"),
    "F": ("####", "#...", "###.", "#...", "#..."),
    "G": (".###", "#...", "#.##", "#..#", ".###"),
    "H": ("#..#", "#..#", "####", "#..#", "#..#"),
    "I": ("###.", ".#..", ".#..", ".#..", "###."),
    "J": ("..##", "...#", "...#", "#..#", ".##."),
    "K": ("#..#", "#.#.", "##..", "#.#.", "#..#"),
    "L": ("#...", "#...", "#...", "#...", "####"),
    "M": ("#..#", "####", "####", "#..#", "#..#"),
    "N": ("#..#", "##.#", "#.##", "#..#", "#..#"),
    "O": (".##.", "#..#", "#..#", "#..#", ".##."),
    "P": ("###.", "#..#", "###.", "#...", "#..."),
    "Q": (".##.", "#..#", "#..#", "#.#.", ".#.#"),
    "R": ("###.", "#..#", "###.", "#.#.", "#..#"),
    "S": (".###", "#...", ".##.", "...#", "###."),
    "T": ("####", ".#..", ".#..", ".#..", ".#.."),
    "U": ("#..#", "#..#", "#..#", "#..#", ".##."),
    "V": ("#..#", "#..#", "#..#", ".##.", ".##."),
    "W": ("#..#", "#..#", "####", "####", "#..#"),
    "X": ("#..#", "#..#", ".##.", "#..#", "#..#"),
    "Y": ("#..#", "#..#", ".##.", ".#..", ".#.."),
    "Z": ("####", "...#", ".##.", "#...", "####"),
    "0": (".##.", "#.##", "#..#", "##.#", ".##."),
    "1": (".#..", "##..", ".#..", ".#..", "###."),
    "2": ("###.", "...#", ".##.", "#...", "####"),
    "3": ("###.", "...#", ".##.", "...#", "###."),
    "4": ("#..#", "#..#", "####", "...#", "...#"),
    "5": ("####", "#...", "###.", "...#", "###."),
    "6": (".##.", "#...", "###.", "#..#", ".##."),
    "7": ("####", "...#", "..#.", ".#..", ".#.."),
    "8": (".##.", "#..#", ".##.", "#..#", ".##."),
    "9": (".##.", "#..#", ".###", "...#", ".##."),
    " ": ("....", "....", "....", "....", "...."),
    "!": ("..#.", "..#.", "..#.", "....", "..#."),
    "?": ("###.", "...#", ".##.", "....", ".##."),
    ".": ("....", "....", "....", "....", "..#."),
    ",": ("....", "....", "....", "..#.", ".#.."),
    "-": ("....", "....", "####", "....", "...."),
    ":": ("....", "..#.", "....", "..#.", "...."),
    "'": ("..#.", "..#.", "....", "....", "...."),
    "*": ("#..#", ".##.", "####", ".##.", "#..#"),
}

ART = {
    "shrug": r"""
  ¯\_(ツ)_/¯
""",
    "tableflip": r"""
  (╯°□°)╯︵ ┻━┻
""",
    "unflip": r"""
  ┬─┬ノ( º _ ºノ)
""",
    "skull": r"""
        _____
       /     \
      | () () |
       \  ^  /
        |||||
        |||||
""",
    "thumbs": r"""
       _,--._
    .-'      `-.
   /            \
   |  _    _    |
   | / \  / \   |
   | \_/  \_/   |
    \          /
     `-.____.-'
""",
    "fine": r"""
   ______________
  /  THIS IS FINE \
 |  ______________ |
 | |              | |
 | |   [] [] []   | |
 | |______________| |
 |__________________|
""",
    "troll": r'''
      .-"""-.
     /  _  _  \
    |  (o)(o)  |
    |     ^    |
    \  \___/   /
     '-.___.-'
     /  | |  \
''',
}

COW = r"""
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\
                ||----w |
                ||     ||
"""


def banner(text, block="#"):
    rows = ["", "", "", "", ""]
    for i, chunk in enumerate(text.upper()):
        glyph = GLYPHS.get(chunk, GLYPHS["?"])
        for r in range(5):
            rows[r] += glyph[r].replace("#", block) + ("" if i == len(text) - 1 else " ")
    return "\n".join(row.rstrip() for row in rows)


def cow(text, width=38):
    lines = textwrap.wrap(text or "moo", width) or [""]
    out = [" " + "_" * (width + 2)]
    for i, line in enumerate(lines):
        pad = line.ljust(width)
        if i == 0 and len(lines) > 1:
            out.append(f"/ {pad} \\")
        elif i == len(lines) - 1 and len(lines) > 1:
            out.append(f"\\ {pad} /")
        else:
            out.append(f"| {pad} |")
    out.append(" " + "-" * (width + 2))
    return "\n".join(out) + COW.rstrip("\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description="ASCII trolling: banners, cow, art.")
    parser.add_argument("--mode", required=True, choices=["banner", "cow", "art"])
    parser.add_argument("--text", default="")
    parser.add_argument("--char", default="#", help="fill character for banner mode")
    parser.add_argument("--name", choices=sorted(ART), help="art piece")
    args = parser.parse_args(argv)

    if args.mode == "banner":
        if not args.text:
            parser.error("--mode banner needs --text")
        print(banner(args.text, args.char))
    elif args.mode == "cow":
        print(cow(args.text))
    else:
        if not args.name:
            parser.error(f"--mode art needs --name ({', '.join(sorted(ART))})")
        print(ART[args.name].strip("\n"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

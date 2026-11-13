#!/usr/bin/env python3
"""Render prank cards to PNG: classic memes, fake tweets, terminal transcripts, chat bubbles."""

import argparse
import os
import sys
import time

from PIL import Image, ImageDraw, ImageFont

FONT_CHAINS = {
    "impact": [
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "/System/Library/Fonts/Supplemental/Arial Black.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "mono": [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    ],
    "ui": [
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "ui_bold": [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
}

_cache = {}


def font(kind, size):
    key = (kind, size)
    if key not in _cache:
        for path in FONT_CHAINS[kind]:
            if os.path.exists(path):
                _cache[key] = ImageFont.truetype(path, size)
                break
        else:
            _cache[key] = ImageFont.load_default(size=size)
    return _cache[key]


def hard_split(word, fnt, max_width):
    parts, cur = [], ""
    for ch in word:
        if cur and fnt.getlength(cur + ch) > max_width:
            parts.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        parts.append(cur)
    return parts


def wrap(text, fnt, max_width):
    lines = []
    for para in text.replace("\\n", "\n").split("\n"):
        cur = ""
        for word in para.split():
            chunks = [word] if fnt.getlength(word) <= max_width else hard_split(word, fnt, max_width)
            for i, chunk in enumerate(chunks):
                candidate = f"{cur} {chunk}" if cur else chunk
                if not cur or fnt.getlength(candidate) <= max_width:
                    cur = candidate
                else:
                    lines.append(cur)
                    cur = chunk
                if i < len(chunks) - 1:
                    lines.append(cur)
                    cur = ""
        if cur:
            lines.append(cur)
    return lines or [""]


def out_path(args):
    path = args.out or f"troll-out/{args.style}-{int(time.time())}.png"
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    return os.path.abspath(path)


def render_classic(args):
    if not args.image:
        print("memegen: --style classic needs --image", file=sys.stderr)
        return 2
    try:
        img = Image.open(args.image).convert("RGB")
    except OSError as exc:
        print(f"memegen: cannot read image {args.image}: {exc}", file=sys.stderr)
        return 2

    width, height = img.size
    max_width = width - 80
    size = max(28, width // 12)
    while size > 16:
        fnt = font("impact", size)
        lines = wrap(args.top.upper(), fnt, max_width) + wrap(args.bottom.upper(), fnt, max_width)
        if len(lines) * int(size * 1.1) <= height * 0.5:
            break
        size -= 2

    fnt = font("impact", size)
    line_height = int(size * 1.1)
    top_lines = wrap(args.top.upper(), fnt, max_width)
    bottom_lines = wrap(args.bottom.upper(), fnt, max_width)
    draw = ImageDraw.Draw(img)

    y = 24
    for line in top_lines:
        draw.text((width / 2, y), line, font=fnt, fill="white", stroke_width=4, stroke_fill="black", anchor="mt")
        y += line_height

    y = height - 24 - line_height * len(bottom_lines)
    for line in bottom_lines:
        draw.text((width / 2, y), line, font=fnt, fill="white", stroke_width=4, stroke_fill="black", anchor="mt")
        y += line_height

    path = out_path(args)
    img.save(path)
    print(path)
    return 0


def render_tweet(args):
    width = 1080
    pad, body_size, body_lh = 56, 46, 58
    text_c, secondary, accent, border = "#0f1419", "#536471", "#1d9bf0", "#cfd9de"
    name = args.name or "Display Name"
    handle = args.handle or "@user"

    f_name, f_handle = font("ui_bold", 40), font("ui", 34)
    f_body, f_foot = font("ui", body_size), font("ui", 34)
    lines = wrap(args.text, f_body, width - 2 * pad)
    height = pad + 96 + 40 + len(lines) * body_lh + 100

    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width - 1, height - 1], outline=border, width=2)

    draw.ellipse([pad, pad, pad + 96, pad + 96], fill=accent)
    draw.text((pad + 96 + 24, pad), name, font=f_name, fill=text_c)
    handle_x = pad + 96 + 24
    draw.text((handle_x, pad + 52), handle, font=f_handle, fill=secondary)
    if args.verified:
        badge_x = handle_x + f_handle.getlength(handle) + 12
        draw.ellipse([badge_x, pad + 56, badge_x + 24, pad + 80], fill=accent)
        draw.line([badge_x + 6, pad + 68, badge_x + 11, pad + 74], fill="#ffffff", width=3)
        draw.line([badge_x + 11, pad + 74, badge_x + 19, pad + 62], fill="#ffffff", width=3)

    y = pad + 96 + 40
    for line in lines:
        draw.text((pad, y), line, font=f_body, fill=text_c)
        y += body_lh

    footer = f"{args.replies} replies    {args.retweets} reposts    {args.likes} likes"
    draw.text((pad, height - 100 + 40), footer, font=f_foot, fill=secondary)

    path = out_path(args)
    img.save(path)
    print(path)
    return 0


def render_terminal(args):
    width = 1080
    pad, chrome, lh = 40, 64, 44
    f_mono, f_title = font("mono", 30), font("ui", 28)
    lines = wrap(args.text, f_mono, width - 2 * pad)
    height = chrome + pad + len(lines) * lh + pad

    img = Image.new("RGB", (width, height), "#0d1117")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width, chrome], fill="#161b22")
    for i, color in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        cx = 32 + i * 32
        draw.ellipse([cx - 7, 25, cx + 7, 39], fill=color)
    draw.text((120, 32), args.title or "zsh — 80×24", font=f_title, fill="#8b949e", anchor="lm")

    y = chrome + pad
    for line in lines:
        draw.text((pad, y), line, font=f_mono, fill="#7ee787" if line.startswith("$") else "#c9d1d9")
        y += lh

    path = out_path(args)
    img.save(path)
    print(path)
    return 0


def render_chat(args):
    width = 1080
    body_size, bubble_pad_x, bubble_pad_y, radius = 42, 32, 28, 28
    f_body, f_name = font("ui", body_size), font("ui", 30)
    bubble_max = 800
    lines = wrap(args.text, f_body, bubble_max - 2 * bubble_pad_x)
    bubble_h = 2 * bubble_pad_y + len(lines) * 54
    height = 40 + 30 + bubble_h + 40

    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    bubble_w = min(bubble_max, int(max(f_body.getlength(line) for line in lines)) + 2 * bubble_pad_x)
    x = 60 if args.side == "left" else width - 60 - bubble_w
    top = 70

    draw.text((x, 32), args.name or "Me", font=f_name, fill="#8e8e93")
    draw.rounded_rectangle([x, top, x + bubble_w, top + bubble_h], radius=radius, fill="#e9e9eb")
    y = top + bubble_pad_y
    for line in lines:
        draw.text((x + bubble_pad_x, y), line, font=f_body, fill="#111111")
        y += 54

    path = out_path(args)
    img.save(path)
    print(path)
    return 0


RENDERERS = {
    "classic": render_classic,
    "tweet": render_tweet,
    "terminal": render_terminal,
    "chat": render_chat,
}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Render prank cards to PNG.")
    parser.add_argument("--style", required=True, choices=sorted(RENDERERS))
    parser.add_argument("--image")
    parser.add_argument("--top", default="")
    parser.add_argument("--bottom", default="")
    parser.add_argument("--text", default="")
    parser.add_argument("--name")
    parser.add_argument("--handle")
    parser.add_argument("--likes", type=int, default=42)
    parser.add_argument("--retweets", type=int, default=7)
    parser.add_argument("--replies", type=int, default=3)
    parser.add_argument("--verified", action="store_true")
    parser.add_argument("--title")
    parser.add_argument("--side", choices=["left", "right"], default="left")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    if args.style != "classic" and not args.text:
        parser.error(f"--style {args.style} needs --text")
    return RENDERERS[args.style](args)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Render prank cards to PNG: classic memes, fake tweets, terminal transcripts, chat bubbles."""

import argparse
import math
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


def save(img, args):
    path = out_path(args)
    img.save(path)
    print(path)
    return 0


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

    return save(img, args)


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

    return save(img, args)


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

    return save(img, args)


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

    return save(img, args)


def tick(draw, x, y, radius=13, color="#1a7f37"):
    draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)
    draw.line([x - 6, y, x - 1, y + 5], fill="#ffffff", width=3)
    draw.line([x - 1, y + 5, x + 6, y - 5], fill="#ffffff", width=3)


def cross(draw, x, y, radius=13, color="#cf222e"):
    draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)
    draw.line([x - 5, y - 5, x + 5, y + 5], fill="#ffffff", width=3)
    draw.line([x - 5, y + 5, x + 5, y - 5], fill="#ffffff", width=3)


def render_review(args):
    width, pad, lh = 1080, 48, 52
    text_c, secondary, border, code_bg = "#1f2328", "#656d76", "#d0d7de", "#f6f8fa"
    name = args.name or "reviewer-bot"
    handle = args.handle or ""
    state = "approved these changes" if args.approved else "requested changes"
    state_c = "#1a7f37" if args.approved else "#cf222e"
    f_name, f_body, f_small, f_code = font("ui_bold", 32), font("ui", 36), font("ui", 26), font("mono", 28)

    lines = wrap(args.text or "This will not scale.", f_body, width - 2 * pad - 120)
    code_lines = wrap(args.code, f_code, width - 2 * pad - 64) if args.code else []
    body_y = pad + 112
    code_y = body_y + len(lines) * lh + 20
    code_h = 32 + len(code_lines) * 40 if code_lines else 0
    height = code_y + code_h + 96

    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([1, 1, width - 2, height - 2], radius=14, outline=border, width=2)
    draw.ellipse([pad, pad, pad + 68, pad + 68], fill="#8250df")
    draw.text((pad + 34, pad + 34), name[0].upper(), font=f_name, fill="#ffffff", anchor="mm")
    draw.text((pad + 92, pad + 2), name, font=f_name, fill=text_c)
    handle_x = pad + 92 + f_name.getlength(name) + 14
    draw.text((handle_x, pad + 8), handle, font=f_small, fill=secondary)
    draw.text((pad + 92, pad + 46), state, font=f_small, fill=state_c)

    y = body_y
    for line in lines:
        draw.text((pad, y), line, font=f_body, fill=text_c)
        y += lh
    if code_lines:
        draw.rounded_rectangle([pad, code_y, width - pad, code_y + code_h], radius=10, fill=code_bg)
        y = code_y + 16
        for line in code_lines:
            draw.text((pad + 24, y), line, font=f_code, fill=text_c)
            y += 40
    draw.text((pad, height - 62), "View reviewed changes", font=f_small, fill="#0969da")
    return save(img, args)


def render_issue(args):
    width, pad = 1080, 48
    text_c, secondary, border = "#1f2328", "#656d76", "#d0d7de"
    f_title, f_body, f_small, f_chip = font("ui_bold", 44), font("ui", 34), font("ui", 26), font("ui_bold", 24)
    title_lines = wrap(args.title or "App crashes on startup", f_title, width - 2 * pad)
    body_lines = wrap(args.text or "Reproduced on a clean checkout.", f_body, width - 2 * pad)
    labels = [s.strip() for s in (args.labels or "bug").split(",") if s.strip()]

    meta_y = pad + len(title_lines) * 56 + 12
    body_y = meta_y + 128
    height = body_y + len(body_lines) * 48 + 72

    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([1, 1, width - 2, height - 2], radius=14, outline=border, width=2)

    y = pad
    for line in title_lines:
        draw.text((pad, y), line, font=f_title, fill=text_c)
        y += 56

    state = "Closed as not planned"
    pill_w = int(f_small.getlength(state)) + 44
    draw.rounded_rectangle([pad, meta_y, pad + pill_w, meta_y + 40], radius=20, fill="#8250df")
    draw.text((pad + 22, meta_y + 20), state, font=f_small, fill="#ffffff", anchor="lm")
    author = args.name or "octocat"
    draw.text((pad + pill_w + 18, meta_y + 20), f"{author} opened this issue", font=f_small, fill=secondary, anchor="lm")

    x = pad
    for label in labels:
        w = int(f_chip.getlength(label)) + 32
        draw.rounded_rectangle([x, meta_y + 54, x + w, meta_y + 94], radius=16, fill="#ddf4ff")
        draw.text((x + 16, meta_y + 74), label, font=f_chip, fill="#0969da", anchor="lm")
        x += w + 12

    y = body_y
    for line in body_lines:
        draw.text((pad, y), line, font=f_body, fill=text_c)
        y += 48
    return save(img, args)


def render_achievement(args):
    width, pad = 1080, 40
    height = 260
    img = Image.new("RGB", (width, height), "#0b0b0b")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([8, 8, width - 9, height - 9], radius=30, fill="#141414", outline="#2a2a2a", width=3)

    cx, cy, r = pad + 76, height // 2, 52
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#107c10")
    points = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        radius = 32 if i % 2 == 0 else 14
        points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    draw.polygon(points, fill="#e6f4e6")

    f_small, f_score = font("ui", 26), font("ui_bold", 34)
    tx = cx + r + 36
    room = width - pad - tx
    size = 46
    while size > 22 and font("ui_bold", size).getlength(args.text or "Deleted production") > room:
        size -= 2
    draw.text((tx, cy - 62), args.title or "Achievement Unlocked", font=f_small, fill="#9d9d9d")
    draw.text((tx, cy - 26), args.text or "Deleted production", font=font("ui_bold", size), fill="#ffffff")
    draw.text((tx, cy + 32), args.score or "50G", font=f_score, fill="#ffd700")
    return save(img, args)


def render_slack(args):
    width, pad = 1080, 48
    text_c, secondary, border = "#1d1c1d", "#616061", "#dddddd"
    f_name, f_body, f_small = font("ui_bold", 32), font("ui", 36), font("ui", 26)
    name = args.name or "Dev"
    channel = args.handle or "#general"

    lines = wrap(args.text or "did you push the force push", f_body, width - 2 * pad - 112)
    body_y = pad + 56
    react_y = body_y + len(lines) * 50 + 20
    height = react_y + 48 + pad

    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([1, 1, width - 2, height - 2], radius=14, outline=border, width=2)
    draw.rounded_rectangle([pad, pad, pad + 80, pad + 80], radius=16, fill="#4a154b")
    draw.text((pad + 40, pad + 40), name[:2].upper(), font=f_name, fill="#ffffff", anchor="mm")
    draw.text((pad + 104, pad + 2), name, font=f_name, fill=text_c)
    meta_x = pad + 104 + f_name.getlength(name) + 16
    draw.text((meta_x, pad + 8), f"2:14 PM · {channel}", font=f_small, fill=secondary)

    y = body_y
    for line in lines:
        draw.text((pad + 104, y), line, font=f_body, fill=text_c)
        y += 50

    x = pad + 104
    for label, count in ((":+1:", args.likes), (":tada:", max(1, args.likes // 4))):
        text = f"{label} {count}"
        w = int(f_small.getlength(text)) + 36
        draw.rounded_rectangle([x, react_y, x + w, react_y + 42], radius=21, fill="#f4f4f4", outline="#e8e8e8", width=2)
        draw.text((x + 18, react_y + 21), text, font=f_small, fill="#1d6fd8", anchor="lm")
        x += w + 12
    return save(img, args)


def render_ci(args):
    width, pad = 1080, 48
    text_c, secondary, border, fail_c = "#1f2328", "#656d76", "#d0d7de", "#cf222e"
    f_title, f_row, f_small, f_mono = font("ui_bold", 34), font("ui", 30), font("ui", 25), font("mono", 26)
    repo, branch = args.title or "acme/app", args.name or "main"
    job = args.bottom or "test (ubuntu-latest)"
    step_lines = wrap(args.text or "AssertionError: expected 200, got 500", f_mono, width - 2 * pad - 88)

    top = pad
    run_y = top + 56
    jobs_y = run_y + 56
    box_y = jobs_y + 100
    box_h = 32 + len(step_lines) * 38
    foot_y = box_y + box_h + 28
    height = foot_y + 28 + pad

    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([1, 1, width - 2, height - 2], radius=14, outline=border, width=2)
    draw.text((pad, top), repo, font=f_title, fill=text_c)
    draw.text((width - pad, top + 8), branch, font=f_small, fill=secondary, anchor="rt")

    cross(draw, pad + 14, run_y + 16, 15, fail_c)
    draw.text((pad + 40, run_y), "Failed", font=f_row, fill=fail_c)
    draw.text((width - pad, run_y + 6), "4m 12s", font=f_small, fill=secondary, anchor="rt")

    tick(draw, pad + 12, jobs_y + 12, 12)
    draw.text((pad + 40, jobs_y), "build (ubuntu-latest)", font=f_small, fill=text_c)
    draw.text((width - pad, jobs_y + 6), "1m 04s", font=f_small, fill=secondary, anchor="rt")
    cross(draw, pad + 12, jobs_y + 60, 12, fail_c)
    draw.text((pad + 40, jobs_y + 48), job, font=f_small, fill=text_c)
    draw.text((width - pad, jobs_y + 54), "3m 08s", font=f_small, fill=secondary, anchor="rt")

    draw.rounded_rectangle([pad, box_y, width - pad, box_y + box_h], radius=10, fill="#fff1f0")
    draw.rectangle([pad, box_y, pad + 4, box_y + box_h], fill=fail_c)
    y = box_y + 16
    for line in step_lines:
        draw.text((pad + 32, y), line, font=f_mono, fill="#82071e")
        y += 38

    draw.text((pad, foot_y), "Run failed · 1 annotation · logs retained for 90 days", font=f_small, fill=secondary)
    return save(img, args)


RENDERERS = {
    "classic": render_classic,
    "review": render_review,
    "issue": render_issue,
    "achievement": render_achievement,
    "slack": render_slack,
    "ci": render_ci,
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
    parser.add_argument("--code", help="monospace line shown in the review card")
    parser.add_argument("--labels", help="comma-separated labels for the issue card")
    parser.add_argument("--score", help="points badge for the achievement card")
    parser.add_argument("--approved", action="store_true", help="review card says approved instead of requested changes")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    if args.style in {"tweet", "terminal", "chat"} and not args.text:
        parser.error(f"--style {args.style} needs --text")
    return RENDERERS[args.style](args)


if __name__ == "__main__":
    sys.exit(main())

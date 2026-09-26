#!/usr/bin/env python3
"""Slate card renderer. Deterministic: same input always produces the same PNG."""
import json, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(ROOT, "fonts")
W, H = 1080, 1350
MARGIN = 112

BG = (14, 15, 17)
INK = (233, 231, 226)
DIM = (122, 126, 133)
RULE = (70, 74, 80)

CFG = json.load(open(os.path.join(ROOT, "config.json")))


def _f(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def _tracked(d, xy, text, font, fill, track=0.0):
    x, y = xy
    for c in text:
        d.text((x, y), c, font=font, fill=fill)
        x += d.textlength(c, font=font) + track
    return x


def _wrap(d, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def _fit(d, text, max_w, max_h, start=84, min_size=44, ratio=1.26):
    """Shrink until the wrapped block fits. Long lines get smaller type, never clipped."""
    size = start
    while size > min_size:
        f = _f("inter-latin-600-normal.ttf", size)
        lines = _wrap(d, text, f, max_w)
        lh = int(size * ratio)
        if len(lines) * lh <= max_h and all(
            d.textlength(l, font=f) <= max_w for l in lines
        ):
            return f, lines, lh
        size -= 2
    f = _f("inter-latin-600-normal.ttf", min_size)
    return f, _wrap(d, text, f, max_w), int(min_size * ratio)


def render(text, index, path=None):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    lab = _f("inter-latin-500-normal.ttf", 21)
    _tracked(d, (MARGIN, 96), CFG["account_name"], lab, DIM, track=5.5)

    num = f"{index:03d}"
    num_w = sum(d.textlength(c, font=lab) + 3 for c in num) - 3
    _tracked(d, (W - MARGIN - num_w, 96), num, lab, DIM, track=3)

    f, lines, lh = _fit(d, text, W - 2 * MARGIN, 640)
    y = (H - len(lines) * lh) / 2 - 40
    for ln in lines:
        d.text((MARGIN, y), ln, font=f, fill=INK)
        y += lh

    d.line([(MARGIN, H - 190), (MARGIN + 70, H - 190)], fill=RULE, width=2)
    _tracked(d, (MARGIN, H - 158), CFG["footer_label"],
             _f("inter-latin-400-normal.ttf", 19), DIM, track=4)

    if path:
        img.save(path, "PNG", optimize=True)
    return img


if __name__ == "__main__":
    import sys
    render(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 1, "preview.png")
    print("wrote preview.png")

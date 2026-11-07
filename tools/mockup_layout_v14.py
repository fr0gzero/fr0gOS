#!/usr/bin/env python3
"""fr0gOS v1.3 r07 layout options for MK4-2 (HDZero 50x18): three ways to space the same elements.

usage: mockup_layout_v14.py <BTFL_000.bmp> <frog_charmap.h> <out.png>
"""
import re
import sys
from PIL import Image, ImageDraw

FONT, CHARMAP, OUT = sys.argv[1:4]
font = Image.open(FONT).convert("RGB")
GW, GH = font.width // 16, font.height // 32
TRANS = (127, 127, 127)
hdr = open(CHARMAP).read()
G = {m[0]: int(m[1], 16) for m in re.findall(r"#define FROG_GLYPH_(\w+)\s+0x([0-9A-F]+)", hdr)}
maps = {}
for name in ("Amber", "Red"):
    body = re.search(r"frog%sMap\[64\] = \{([^}]*)\}" % name, hdr).group(1)
    maps[name] = [int(v, 16) for v in re.findall(r"0x([0-9A-F]{2})", body)]
N, W_, C = 0, 1, 2
L, R = 0, 49


def g(s, sev=N):
    out = []
    for ch in s:
        c = ord(ch)
        if sev and 0x20 <= c <= 0x5F:
            c = maps["Amber" if sev == W_ else "Red"][c - 0x20] or c
        out.append(c)
    return out


def scene(w, h, pic_w):
    bg = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(bg)
    x0 = (w - pic_w) // 2
    for y in range(h):
        t = y / h
        col = (int(70 + 60 * (1 - t)), int(82 + 50 * (1 - t)), int(96 + 40 * (1 - t))) if t < 0.55 else (int(58 + 30 * t), int(48 + 22 * t), int(40 + 10 * t))
        d.line([(x0, y), (x0 + pic_w, y)], fill=col)
    d.rectangle([x0 + pic_w * 0.62, h * 0.18, x0 + pic_w * 0.9, h * 0.55], fill=(205, 205, 190))
    d.rectangle([x0 + pic_w * 0.1, h * 0.6, x0 + pic_w * 0.45, h * 0.95], fill=(92, 60, 42))
    return bg


def panel(items):
    cols, rows = 50, 18
    img = scene(cols * GW, rows * GH, rows * GH * 4 // 3)
    px, fpx = img.load(), font.load()
    for x, y, codes, right in items:
        if right:
            x = x + 1 - len(codes)
        for i, code in enumerate(codes):
            gx, gy = (code % 16) * GW, (code // 16) * GH
            for yy in range(GH):
                for xx in range(GW):
                    p = fpx[gx + xx, gy + yy]
                    if p != TRANS:
                        px[(x + i) * GW + xx, y * GH + yy] = p
    return img


def quad(rows_left, rows_right, frog_at):
    """rows_*: dict name -> row. Values are a mid-flight frame."""
    it = []
    fx, fy = frog_at
    it.append((fx, fy, [G["FROG_IDLE"]], fx > 25))
    lv = {"feed1": g("ANGLE"), "feed2": g("PUNCH", W_), "vbat": g("3.71V"), "mah": g("135") + [0x07], "amp": g("6.81A"),
          "lq": g("LQ100"), "rate": g("F1000"), "ch": g("R8"), "pwr": g("200MW")}
    rv = {"craft": g("MK4-2"), "time": g("01:17"), "arm": g("ARMED"), "mode": g("ACRO"), "air": g("AIR"),
          "thrl": g("THR"), "thr": g("47.1%"), "rpml": g("RPM"), "rpm": g("33370", W_), "gf": g("1.0G"),
          "core": g("C69"), "fl": g("#2")}
    for k, y in rows_left.items():
        it.append((L, y, lv[k], False))
    for k, y in rows_right.items():
        it.append((R, y, rv[k], True))
    return panel(it)


OPTIONS = [
    ("A  MIRRORED  -  both sides share one grid: groups start on rows 0 / 4 / 9 / 13",
     dict(feed1=1, feed2=2, vbat=4, mah=5, amp=6, lq=9, rate=10, ch=13, pwr=14),
     dict(craft=0, time=1, arm=4, mode=5, air=6, thrl=9, thr=10, rpml=11, rpm=12, gf=13, core=14, fl=15),
     (0, 0)),
    ("B  EYE LINE  -  the numbers you read sit in the middle third, corners stay quiet",
     dict(feed1=1, feed2=2, vbat=6, mah=7, amp=8, lq=10, rate=11, ch=13, pwr=14),
     dict(craft=0, time=2, arm=5, mode=6, air=7, thrl=9, thr=10, rpml=11, rpm=12, gf=13, core=15, fl=16),
     (2, 16)),
    ("C  CORNERS  -  groups anchored to the four corners, the middle of the bars left open for the frog",
     dict(feed1=1, feed2=2, vbat=3, mah=4, amp=5, lq=13, rate=14, ch=15, pwr=16),
     dict(craft=0, time=1, arm=3, mode=4, air=5, thrl=9, thr=10, rpml=11, rpm=12, gf=13, core=15, fl=16),
     (47, 7)),
]

W = 1100
shots = [(t, quad(l, r, f)) for t, l, r, f in OPTIONS]
scaled = [(t, im.resize((W, int(im.height * W / im.width)), Image.LANCZOS)) for t, im in shots]
H = sum(im.height + 34 for _, im in scaled) + 40
sheet = Image.new("RGB", (W + 40, H), (16, 16, 16))
d = ImageDraw.Draw(sheet)
y = 14
for t, im in scaled:
    d.text((20, y), t, fill=(230, 230, 230))
    sheet.paste(im, (20, y + 18))
    y += im.height + 34
d.text((20, y - 6), "MK4-2 v1.3 r07 options. Warnings slot sits under the timer (empty here). The frog hops between free spots; shown at one of them.", fill=(170, 170, 170))
sheet.save(OUT)
print("ok", sheet.size)

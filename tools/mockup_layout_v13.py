#!/usr/bin/env python3
"""fr0gOS layout proposal (v1.3): priority-ordered layout for MK51, MK42 (HDZero) and MK41 (analog).

usage: mockup_layout_v13.py <BTFL_000.bmp> <frog_charmap.h> <pcface fontmap.js> <out.png>
"""
import re
import sys
from PIL import Image, ImageDraw

FONT, CHARMAP, FONTMAP, OUT = sys.argv[1:5]
font = Image.open(FONT).convert("RGB")
GW, GH = font.width // 16, font.height // 32
TRANS = (127, 127, 127)
GHOST = (110, 110, 110)
hdr = open(CHARMAP).read()
G = {m[0]: int(m[1], 16) for m in re.findall(r"#define FROG_GLYPH_(\w+)\s+0x([0-9A-F]+)", hdr)}
maps = {}
for name in ("Amber", "Red"):
    body = re.search(r"frog%sMap\[64\] = \{([^}]*)\}" % name, hdr).group(1)
    maps[name] = [int(v, 16) for v in re.findall(r"0x([0-9A-F]{2})", body)]
vga = {}
for line in open(FONTMAP, encoding="utf-8"):
    m = re.search(r"\[((?:0x[0-9a-f]{2},?\s*){16})\].*\((\d+)\)\s*$", line)
    if m:
        vga[int(m.group(2))] = [int(b, 16) for b in re.findall(r"0x[0-9a-f]{2}", m.group(1))]
N, W_, C = 0, 1, 2


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


def hd_panel(items):
    cols, rows = 50, 18
    img = scene(cols * GW, rows * GH, rows * GH * 4 // 3)
    px, fpx = img.load(), font.load()
    for x, y, codes, right, ghost in items:
        if right:
            x = x + 1 - len(codes)
        for i, code in enumerate(codes):
            gx, gy = (code % 16) * GW, (code // 16) * GH
            for yy in range(GH):
                for xx in range(GW):
                    p = fpx[gx + xx, gy + yy]
                    if p == TRANS:
                        continue
                    if ghost and p != (0, 0, 0):
                        p = GHOST
                    px[(x + i) * GW + xx, y * GH + yy] = p
    return img


def analog_panel(items):
    cw, ch, cols, rows = 12, 18, 30, 13
    img = scene(cols * cw, rows * ch, cols * cw)
    px = img.load()
    for x, y, text, right, ghost in items:
        if right:
            x = x + 1 - len(text)
        colour = GHOST if ghost else (240, 240, 240)
        for i, c in enumerate(text):
            ox, oy = (x + i) * cw + 2, y * ch + 1
            if ord(c) < 0x20:
                sym = font.crop(((ord(c) % 16) * GW, (ord(c) // 16) * GH, (ord(c) % 16 + 1) * GW, (ord(c) // 16 + 1) * GH)).resize((cw - 2, ch - 2), Image.NEAREST)
                sp = sym.load()
                for yy in range(sym.height):
                    for xx in range(sym.width):
                        q = sp[xx, yy]
                        if q != TRANS:
                            px[ox - 1 + xx, oy + yy] = (0, 0, 0) if q == (0, 0, 0) else colour
                continue
            rows16 = vga[ord(c)]
            on = {(xx, yy) for yy in range(16) for xx in range(8) if (rows16[yy] >> (7 - xx)) & 1}
            for (xx, yy) in on:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if (xx + dx, yy + dy) not in on:
                            X, Y = ox + xx + dx, oy + yy + dy
                            if 0 <= X < img.width and 0 <= Y < img.height:
                                px[X, Y] = (0, 0, 0)
            for (xx, yy) in on:
                px[ox + xx, oy + yy] = colour
    return img.resize((img.width * 3, img.height * 3), Image.NEAREST)


L, R = 0, 49


def hd_quad(name, cam):
    it = [
        # identity
        (L, 0, g("FR0G") + [G["CURSOR"]], False, False), (R, 0, [G["FROG_IDLE"]] + g(name), True, False),
        # POWER (left top, eye line): the number a whoop pilot reads most
        (L, 2, g("3.62V"), False, False), (L, 3, g("54%") + [G["BATT0"] + 2], False, False),
        (L, 4, g("212") + [0x07], False, False), (L, 5, g("4.32A"), False, False),
        # LINKS (left middle): control link then video link
        (L, 7, g("LQ100"), False, False), (L, 8, g("-41"), False, False), (L, 9, g("F1000"), False, False),
        (L, 10, g("R8"), False, False), (L, 11, g("200MW"), False, False),
        # TIME + ALERTS (right top, eye line)
        (R, 2, g("01:47"), True, False), (R, 3, g("LAND!"), True, True),
        # STATE (right middle): what the switches say
        (R, 5, g("[ARM]"), True, False), (R, 6, g("ACRO"), True, False), (R, 7, g("AIR"), True, False),
        # PERFORMANCE (right lower middle): fast-moving fun numbers
        (R, 9, [0x04] + g("38%"), True, False), (R, 10, g("38K"), True, False), (R, 11, g("2.1G", W_), True, False),
        # SYSTEM (right bottom): slow, glance only when curious
        (R, 13, g("E48"), True, False), (R, 14, g("C52"), True, False), (R, 16, g("#127"), True, False),
    ]
    # VIDEO (left bottom): static reference
    it += [(L, 13, g("HDZRO"), False, False)] + [(L, 14 + i, g(t), False, False) for i, t in enumerate(cam)]
    return hd_panel(it)


p51 = hd_quad("MK51", ["540P", "90FPS", "CROP"])
p42 = hd_quad("MK42", ["720P", "60FPS", "4:3"])
p41 = analog_panel([
    (0, 0, "FR0G_", False, False), (29, 0, "MK41", True, False),
    (0, 1, "3.82V", False, False), (0, 2, "78%", False, False),
    (0, 4, "LQ99", False, False), (0, 5, "F1000", False, False), (0, 6, "R8", False, False), (0, 7, "200MW", False, False),
    (0, 10, "ANT", False, False), (0, 11, "NTSC", False, False), (0, 12, "16:9", False, False),
    (29, 1, "01:23", True, False), (29, 2, "LAND!", True, True),
    (29, 4, "SAFE", True, False), (29, 5, "ACRO", True, False), (29, 6, "AIR", True, False),
    (29, 8, "\x04" + "45%", True, False), (29, 9, "38K", True, False), (29, 10, "2.1G", True, False),
    (29, 12, "#127", True, False)])

W = 1100
panels = [("MK51  HDZero  540P90 crop", p51), ("MK42  HDZero  720P60 4:3", p42), ("MK41  analog  NTSC 16:9 (mono, font approximate)", p41)]
scaled = [(t, im.resize((W, int(im.height * W / im.width)), Image.LANCZOS)) for t, im in panels]
H = sum(im.height + 34 for _, im in scaled) + 40
sheet = Image.new("RGB", (W + 40, H), (16, 16, 16))
d = ImageDraw.Draw(sheet)
y = 14
for t, im in scaled:
    d.text((20, y), t, fill=(230, 230, 230))
    sheet.paste(im, (20, y + 18))
    y += im.height + 34
d.text((20, y - 6), "fr0gOS v1.3 layout proposal. Grey = warning slot (empty until something is wrong). 2.1G shown amber: G heat colours.", fill=(170, 170, 170))
sheet.save(OUT)
print("ok", sheet.size)

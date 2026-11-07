#!/usr/bin/env python3
"""Render what the goggles should show, using the real font BMP and the fr0gOS charmap.

usage: preview_osd.py <BTFL_000.bmp> <out.png>
"""
import sys
from PIL import Image, ImageDraw

FONT, OUT = sys.argv[1:3]
font = Image.open(FONT).convert("RGB")
GW, GH = font.width // 16, font.height // 32
COLS, ROWS = 50, 18
TRANS = (127, 127, 127)

AMBER = {c: 0xD0 + i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-!%:")}
RED_SLOTS = (list(range(0x60, 0x70)) + [0x77] + list(range(0x80, 0x8A)) +
             list(range(0x90, 0x97)) + [0x98, 0x99] + list(range(0x9B, 0xA0)))
RED = {c: RED_SLOTS[i] for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-!%:")}
FROG, BLINK, CROAK, CURSOR, S1, S2, S3 = range(0xF9, 0x100)
BATT = 0x11
MAH = 0x07


def amber(s): return [AMBER.get(c, ord(c)) for c in s]
def red(s): return [RED.get(c, ord(c)) for c in s]
def g(s): return [ord(c) for c in s]


def background():
    W, H = COLS * GW, ROWS * GH
    bg = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(bg)
    pic_w = H * 4 // 3
    x0 = (W - pic_w) // 2
    for y in range(H):  # sky to ground, like a living room shot
        t = y / H
        col = (int(70 + 60 * (1 - t)), int(82 + 50 * (1 - t)), int(96 + 40 * (1 - t))) if t < 0.55 else (int(58 + 30 * t), int(48 + 22 * t), int(40 + 10 * t))
        d.line([(x0, y), (x0 + pic_w, y)], fill=col)
    d.rectangle([x0 + pic_w * 0.62, H * 0.18, x0 + pic_w * 0.9, H * 0.55], fill=(205, 205, 190))
    d.rectangle([x0 + pic_w * 0.1, H * 0.6, x0 + pic_w * 0.45, H * 0.95], fill=(92, 60, 42))
    return bg


def compose(cells, title):
    img = background()
    px = img.load()
    fpx = font.load()
    for (x, y, codes, right) in cells:
        if right:
            x = x + 1 - len(codes)
        for i, code in enumerate(codes):
            gx, gy = (code % 16) * GW, (code // 16) * GH
            for yy in range(GH):
                for xx in range(GW):
                    p = fpx[gx + xx, gy + yy]
                    if p != TRANS:
                        px[(x + i) * GW + xx, y * GH + yy] = p
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, len(title) * 8 + 10, 14], fill=(0, 0, 0))
    d.text((5, 2), title, fill=(255, 255, 255))
    return img


L, R = 0, 49


def flight(frog=FROG, warn=None, volt=None, batt=None, lq=None):
    c = [(L, 0, g("FR0G") + [CURSOR], False), (R, 0, [frog] + g("MK51"), True),
         (L, 2, volt or g("3.98V"), False), (L, 3, g("4.32A"), False), (L, 4, g("212") + [MAH], False),
         (L, 5, batt or (g("62%") + [BATT + 2]), False),
         (L, 7, lq or g("LQ100"), False), (L, 8, g("-41"), False), (L, 9, g("F1000"), False),
         (L, 13, g("540P"), False), (L, 14, g("90FPS"), False), (L, 15, g("CROP"), False),
         (R, 2, g("01:47"), True), (R, 3, g("38%"), True),
         (R, 7, g("[ARM]"), True), (R, 8, g("ACRO"), True), (R, 9, g("AIRON"), True),
         (R, 13, g("C52"), True), (R, 14, g("R8"), True), (R, 15, g("200MW"), True)]
    if warn:
        c.append((R, 16, warn, True))
    return c


frames = [
    ("1. cruising: calm green", flight()),
    ("2. LOWV decoding in", flight(frog=CROAK, warn=[S2] + amber("O") + [S3, ord("#")], volt=amber("3.34V"), batt=amber("21%") + [BATT + 1])),
    ("3. LOWV locked, amber", flight(frog=CROAK, warn=amber("LOWV"), volt=amber("3.34V"), batt=amber("21%") + [BATT + 1])),
    ("4. LAND! critical, red", flight(frog=CROAK, warn=red("LAND!"), volt=red("3.18V"), batt=red("6%") + [BATT + 0], lq=red("LQ38"))),
]

boot = [(13, 4, list(range(0xA0, 0xB8)), False), (13, 5, list(range(0xB8, 0xD0)), False),
        (14, 7, g("FR0GOS V1.1 R02   MK51"), False),
        (14, 8, g("CPU  G474 C41 ..... OK"), False),
        (14, 9, g("GYRO .............. OK"), False),
        (14, 10, g("RX   ............") + amber("WAIT"), False),
        (14, 11, g("VTX  R8 200 ....... OK"), False),
        (14, 12, g("ESC  4/4 ...........") + [ord("/")], False),
        (L, 0, g("FR0G") + [CURSOR], False), (R, 0, [FROG] + g("MK51"), True),
        (L, 9, amber("SCAN") + [ord("/")], False), (R, 7, g("SAFE"), True)]
arm = [(0, 8, ([S1, ord("%"), S3, ord("7"), S2, ord(" "), S1, ord("X"), S3] * 6)[:50], False),
       (0, 9, ([S3, ord(" "), S2, ord("@"), S1, ord("="), S2, ord("<"), S3] * 6)[:50], False),
       (12, 3, [S2], False), (40, 14, [ord("#")], False), (31, 5, [S1], False),
       (23, 9, g("[A") + [S2, S3] + g("]"), False)]

imgs = [compose(c, t) for t, c in frames] + [compose(boot, "5. boot: checks tick in"), compose(arm, "6. arming glitch sweep")]
W, H = imgs[0].size
sheet = Image.new("RGB", (W * 2 + 30, H * 3 + 40), (18, 18, 18))
for i, im in enumerate(imgs):
    sheet.paste(im, (10 + (i % 2) * (W + 10), 10 + (i // 2) * (H + 10)))
sheet = sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS)
sheet.save(OUT)
print("ok", sheet.size)

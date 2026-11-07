#!/usr/bin/env python3
"""FrogOS v1.2 preview sheet: HISCORE.EXE, battery noise stages, Matrix rain, frog moods, arm hop.

Mirrors the firmware layouts (osd.c / osd_elements.c) with the real HDZero hacker font.
usage: preview_v12.py <BTFL_000.bmp> <frog_charmap.h> <out.png>
"""
import random
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
NORMAL, WARN, CRIT = 0, 1, 2
rnd = random.Random(7)


def colour(c, sev):
    if sev == NORMAL or not (0x20 <= c <= 0x5F):
        return c
    m = maps["Amber" if sev == WARN else "Red"][c - 0x20]
    return m or c


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


class Screen:
    def __init__(self, cols=50, rows=18):
        self.cols, self.rows = cols, rows
        self.cells = {}

    def write(self, x, y, codes):
        for i, c in enumerate(codes):
            if 0 <= x + i < self.cols and 0 <= y < self.rows and c != 0x20:
                self.cells[(x + i, y)] = c

    def text(self, x, y, s, sev=NORMAL):
        self.write(x, y, [colour(ord(ch), sev) for ch in s])

    def render(self):
        img = scene(self.cols * GW, self.rows * GH, self.rows * GH * 4 // 3)
        px, fpx = img.load(), font.load()
        for (x, y), code in self.cells.items():
            gx, gy = (code % 16) * GW, (code // 16) * GH
            for yy in range(GH):
                for xx in range(GW):
                    p = fpx[gx + xx, gy + yy]
                    if p != TRANS:
                        px[x * GW + xx, y * GH + yy] = p
        return img


def noise(hd=True):
    r = rnd.getrandbits(16)
    if hd and r & 1:
        return G["SCRAMBLE1"] + (r >> 1) % 3
    return ord("#%&*+=?@$/\\<>XZ0123456789"[(r >> 2) % 25])


def cnoise(sev):
    return colour(ord(rnd.choice("%!0123456789XZAEKQ")), sev)


def bar_cell(s, bar=6):
    col = rnd.randrange(bar * 2)
    return (col if col < bar else s.cols - bar * 2 + col), rnd.randrange(s.rows)


def score_line(s, x, y, label, value, sev=NORMAL):
    s.text(x, y, (label + "." * 18)[:18] + " ")
    s.text(x + 19, y, value, sev)


def hiscore(ms, cols=50, rows=18):
    """frogDrawHiScore() with a new G record"""
    s = Screen(cols, rows)
    x = cols // 2 - 13
    lines = 1 + 3 + 3 + 1 + 1 + 2 + 1
    tight_b = lines > rows
    lines -= tight_b
    tight_f = lines > rows
    lines -= tight_f
    y = max(0, (rows - lines) // 2)
    s.text(x, y, "C:\\FR0G> HISCORE.EXE")
    y += 2
    hop = (ms // 150) % 3
    fr = G["FROG_CROAK"] if (ms // 300) % 2 else G["FROG_IDLE"]
    left = [fr if k == hop else 0x20 for k in range(3)]
    chase = [NORMAL, WARN, CRIT]
    mid = [colour(ord(c), chase[(i + ms // 80) % 3]) if c != " " else 0x20 for i, c in enumerate("NEW HIGH SCORE")]
    b = left + [0x20] + mid + [0x20] + left[::-1]
    s.write(cols // 2 - len(b) // 2, y, b)
    for _ in range(6):
        cx, cy = bar_cell(s)
        s.write(cx, cy, [colour(ord(rnd.choice("X.!%")), rnd.choice([WARN, CRIT]))])
    y += 1 if tight_b else 2
    flash = WARN if (ms // 250) % 2 else CRIT
    score_line(s, x, y, "BEST G", "4.6G", flash); y += 1
    score_line(s, x, y, "  THIS FLIGHT", "4.6G"); y += 1
    score_line(s, x, y, "  OLD RECORD", "3.9G"); y += 1
    score_line(s, x, y, "BEST LAP", "--.--"); y += 1
    y += 0 if tight_f else 1
    score_line(s, x, y, "FLIGHTS", "#128"); y += 1
    score_line(s, x, y, "AIR TIME", "6H12M"); y += 1
    s.write(x, y, [ord(c) for c in "C:\\FR0G> "] + [G["CURSOR"]])
    return s


def flight_osd(s, frog, vbat, batt, warn=None, warn_sev=NORMAL):
    s.write(0, 0, [ord(c) for c in "FR0G"] + [G["CURSOR"]])
    s.write(49 - 4, 0, [frog] + [ord(c) for c in "MK51"])
    s.text(0, 2, vbat, warn_sev)
    s.write(0, 5, [ord(c) for c in batt] + [G["BATT0"] + 1])
    for i, t in enumerate(["01:47"]):
        s.text(50 - len(t), 2, t)
    s.text(45, 7, "[ARM]")
    s.text(46, 8, "ACRO")
    if warn:
        s.text(50 - len(warn), 16, warn, warn_sev)


def stage(name):
    """noise first (it is first in osdElementDisplayOrder), then the telemetry writes over it"""
    s = Screen()
    red = lambda: G["RSCRAMBLE1"] + rnd.randrange(3) if rnd.random() < .5 else cnoise(CRIT)
    spec = {"SAG": (3, noise, G["FROG_IDLE"], "3.52V", "61%", None, NORMAL),
            "LOW": (6, lambda: cnoise(WARN), G["FROG_SWEAT1"], "3.46V", "18%", "LOWV", WARN),
            "LAND": (10, red, G["FROG_SWEAT2"], "3.27V", "6%", "LAND!", CRIT),
            "DEAD": (14, red, G["FROG_SWEAT1"], "2.98V", "0%", "LAND!", CRIT)}[name]
    n, gen, frog, vbat, batt, warn, sev = spec
    for _ in range(n):
        s.write(*bar_cell(s), [gen()])
    flight_osd(s, frog, vbat, batt, warn, sev)
    return s


def rain():
    s = Screen()
    bar = 6
    heads = [rnd.randrange(-4, 22) for _ in range(12)]
    lens = [rnd.randrange(3, 8) for _ in range(12)]
    for i in range(12):
        x = i if i < bar else s.cols - bar * 2 + i
        for d in range(lens[i]):
            y = heads[i] - d
            if 0 <= y < s.rows:
                c = (G["SCRAMBLE1"] + rnd.randrange(3)) if d >= 2 else ord(rnd.choice("0123456789ABCDEFXZ$#"))
                s.write(x, y, [c])
    return s


def hop(ms):
    s = Screen(50, 3)
    home = 49 - 4
    s.text(home + 1, 0, "MK51")
    t = min(ms - 360, 480)
    fx = home * t // 480
    phase = (t * 8 // 480) % 2
    landed = t >= 480
    fy = 0 if (landed or phase == 0) else 1
    s.write(fx, fy, [G["FROG_IDLE"] if (landed or fy == 1) else G["FROG_CROAK"]])
    s.text(23, 2, "[ARM]")
    return s


def strip():
    names = [("IDLE", "FROG_IDLE"), ("BLINK", "FROG_BLINK"), ("CROAK warn", "FROG_CROAK"), ("SWEAT low batt", "FROG_SWEAT1"),
             ("SWEAT", "FROG_SWEAT2"), ("FLIP upside down", "FROG_FLIP"), ("SQUASH high G", "FROG_SQUASH1"), ("SQUASH", "FROG_SQUASH2")]
    k = 4
    img = Image.new("RGB", (len(names) * (GW * k + 40), GH * k + 30), (0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, (label, key) in enumerate(names):
        code = G[key]
        cell = font.crop(((code % 16) * GW, (code // 16) * GH, (code % 16 + 1) * GW, (code // 16 + 1) * GH))
        cell = cell.resize((GW * k, GH * k), Image.NEAREST)
        cell.putdata([(0, 0, 0) if p == TRANS else p for p in list(cell.getdata())])
        img.paste(cell, (20 + i * (GW * k + 40), 4))
        d.text((20 + i * (GW * k + 40), GH * k + 10), label, fill=(220, 220, 220))
    return img


W = 1100
panels = [("HISCORE.EXE  - new G record (BEST LAP is a placeholder for the lap timer): banner decodes, colours chase, frogs hop, fireworks in the bars", hiscore(1500).render()),
          ("HISCORE.EXE on analog (30x13, compact; mono on the goggles)", hiscore(1500, 30, 13).render())]
sheet_parts = [(t, im.resize((W, int(im.height * W / im.width)), Image.LANCZOS)) for t, im in panels]
stages = [stage(n).render() for n in ("SAG", "LOW", "LAND", "DEAD")]
half = W // 2 - 6
st = [(n, im.resize((half, int(im.height * half / im.width)), Image.LANCZOS)) for n, im in zip(
    ["SAG  - green, under load", "LOW  - amber, sweating frog", "LAND - red", "DEAD - red flood"], stages)]
rainimg = rain().render()
hops = [hop(ms).render() for ms in (420, 560, 700, 900)]
H = sum(im.height + 34 for _, im in sheet_parts) + 2 * (st[0][1].height + 30) + 30 + int(rainimg.height * W / rainimg.width) + 40 \
    + 4 * (int(hops[0].height * W / hops[0].width) + 6) + 40 + strip().height + 80
sheet = Image.new("RGB", (W + 40, H), (16, 16, 16))
d = ImageDraw.Draw(sheet)
y = 14
for t, im in sheet_parts:
    d.text((20, y), t, fill=(230, 230, 230))
    sheet.paste(im, (20, y + 18))
    y += im.height + 34
d.text((20, y), "Battery noise in the black bars, escalating: SAG -> LOW -> LAND -> DEAD", fill=(230, 230, 230))
y += 18
for i, (t, im) in enumerate(st):
    x = 20 + (i % 2) * (half + 12)
    sheet.paste(im, (x, y))
    d.text((x + 4, y + im.height - 14), t, fill=(255, 255, 255))
    if i % 2:
        y += im.height + 12
y += 6
d.text((20, y), "Matrix rain screensaver (5 s disarmed and still; any stick brings the OSD back)", fill=(230, 230, 230))
r = rainimg.resize((W, int(rainimg.height * W / rainimg.width)), Image.LANCZOS)
sheet.paste(r, (20, y + 18))
y += r.height + 34
d.text((20, y), "Arm: after the glitch sweep the frog hops along the top bar and lands by the craft name", fill=(230, 230, 230))
y += 18
for im in hops:
    h = im.resize((W, int(im.height * W / im.width)), Image.LANCZOS)
    sheet.paste(h, (20, y))
    y += h.height + 6
y += 14
d.text((20, y), "Frog moods (HD)", fill=(230, 230, 230))
sheet.paste(strip(), (20, y + 18))
sheet.save(OUT)
print("ok", sheet.size)

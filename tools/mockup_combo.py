#!/usr/bin/env python3
"""fr0gOS r16 combo meter mockup: the left bar during a flurry of events (mirrors the firmware logic).

usage: mockup_combo.py <frog_charmap.h> <frog_anim.h> <out.gif>
"""
import os
import re
import sys
import random
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_hop as HP  # noqa: E402

CHARMAP, ANIMH, OUT = sys.argv[1:4]
hdr = open(CHARMAP).read()
MAPS = {n: [int(v, 16) for v in re.findall(r"0x([0-9A-F]{2})", re.search(r"frog%sMap\[64\] = \{([^}]*)\}" % n, hdr).group(1))] for n in ("Amber", "Red")}
G_SCR = [0xFD, 0xFE, 0xFF]
G_RSCR = [0x1D, 0x1E, 0x1F]
IDLE = int(re.search(r"#define FROG_G_IDLE\s+0x([0-9A-F]+)", open(ANIMH).read()).group(1), 16)
N, W, C = 0, 1, 2
HOLD, OUT_MS, GAP = 4000, 300, 5000
WINDOW = HOLD + OUT_MS + GAP
COLS_SHOWN = 14


def col(c, sev):
    if sev and 0x20 <= c <= 0x5F:
        return MAPS["Amber" if sev == W else "Red"][c - 0x20] or c
    return c


def noise(sev):
    return random.choice(G_RSCR if sev == C else G_SCR)


# events: (time s, text, severity)
EVENTS = [(1.0, "ARMED", N), (2.0, "PUNCH", W), (3.2, "FLIP", N), (4.6, "ROLL", N), (6.5, "ANGLE", N), (8.0, "ACRO", N),
          (9.0, "SPIN", N), (10.0, "PUNCH", W), (10.8, "FLIP", N), (11.6, "ROLL", N), (12.5, "SPIN", N), (13.4, "PUNCH", W),
          (14.3, "3.6G!", W), (15.2, "FLIP", N), (16.0, "RECRD", C), (25.5, "ANGLE", N)]
END = 28.0

feed = []            # newest first: dict(text, sev, at)
combo = 0
combo_last = combo_bump = combo_end = 0
combo_final = 0
frames, durs = [], []
ev_i = 0
t_ms = 0
while t_ms < END * 1000:
    while ev_i < len(EVENTS) and EVENTS[ev_i][0] * 1000 <= t_ms:
        _, text, sev = EVENTS[ev_i]
        ev_i += 1
        # combo (as frogComboEvent)
        if text != "ARMED":
            if combo and t_ms - combo_last <= WINDOW:
                combo = min(99, combo + 1)
                combo_bump = t_ms
                combo_end = 0
            else:
                if combo >= 2:
                    combo_final, combo_end = combo, t_ms
                combo = 1
            combo_last = t_ms
        feed.insert(0, dict(text=text, sev=sev, at=t_ms))
        feed = feed[:5]
    if combo and t_ms - combo_last > WINDOW:
        if combo >= 2:
            combo_final, combo_end = combo, t_ms
        combo = 0

    img = HP.BASE.copy()
    # clear the left rows 0-6 (the base scene has a static feed in it)
    for r in range(0, 7):
        for x in range(0, 6):
            img.paste((0, 0, 0), (x * HP.FGW, r * HP.FGH, (x + 1) * HP.FGW, (r + 1) * HP.FGH))
    HP.put(img, 4, 0, HP.glyph(IDLE))
    for row, ev in enumerate(feed, start=1):
        age = t_ms - ev["at"]
        if age >= HOLD + OUT_MS:
            continue
        for i, ch in enumerate(ev["text"]):
            if age < 60 * i + 150:
                g = noise(ev["sev"])                     # types in through glyphs
            elif age >= HOLD + 50 * i:
                g = noise(ev["sev"]) if age < HOLD + 50 * i + 120 else 0x20   # disintegrates
            else:
                g = col(ord(ch), ev["sev"])
            HP.put(img, i, row, HP.glyph(g))
    # combo line (as frogComboLine)
    n = combo if combo >= 2 else (combo_final if combo_end and t_ms - combo_end < 400 else 0)
    if n >= 2:
        txt = ("X%d!" if n >= 10 else "X%d") % n
        sev = C if n >= 10 else W if n >= 5 else N
        ending = combo < 2
        tt = (t_ms - combo_end) if ending else (t_ms - combo_bump if combo_bump else 260)
        for i, ch in enumerate(txt):
            scr = (tt >= 80 * i) if ending else (tt < 260 - 50 * i)
            HP.put(img, i, 6, HP.glyph(noise(sev) if scr else col(ord(ch), sev)))
    crop = img.crop((0, 0, COLS_SHOWN * HP.FGW, img.height)).resize((COLS_SHOWN * HP.FGW // 2, img.height // 2), Image.LANCZOS)
    canvas = Image.new("RGB", (crop.width, crop.height + 22), (16, 16, 16))
    canvas.paste(crop, (0, 0))
    d = ImageDraw.Draw(canvas)
    left = max(0, (WINDOW - (t_ms - combo_last)) / 1000) if combo else 0
    d.text((6, crop.height + 5), "t %4.1fs   combo %s   chain alive %.1fs" % (t_ms / 1000, combo if combo >= 2 else "-", left), fill=(150, 240, 170))
    frames.append(canvas)
    durs.append(50)
    t_ms += 50

# merge identical frames
out_f, out_d = [frames[0]], [durs[0]]
for f, d_ in zip(frames[1:], durs[1:]):
    if f.tobytes() == out_f[-1].tobytes():
        out_d[-1] += d_
    else:
        out_f.append(f)
        out_d.append(d_)
out_f[0].save(OUT, save_all=True, append_images=out_f[1:], duration=out_d, loop=0)
print(len(out_f), "frames", os.path.getsize(OUT) // 1024, "KB")

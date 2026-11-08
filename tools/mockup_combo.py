#!/usr/bin/env python3
"""fr0gOS r28 combo meter mockup (4 s chain, 5-cell time-left meter under the count, COMBO burns down from X5, crash breaks it): the left bar during a flurry of events (mirrors the firmware logic).

usage: mockup_combo.py <frog_charmap.h> <frog_anim.h> <out.gif>
"""
import os
import re
import sys
import random
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_hop as HP  # noqa: E402

# r17 layout C left side: feed 1-5, combo 6-7, blank 8, power 9-11, links 13-16
HP.LEFT = {9: "3.71V", 10: "135\x07", 11: "6.81A", 13: "LQ100", 14: "F1000", 15: "R8", 16: "200MW"}
HP.BASE = HP.scene()

CHARMAP, ANIMH, OUT = sys.argv[1:4]
hdr = open(CHARMAP).read()
MAPS = {n: [int(v, 16) for v in re.findall(r"0x([0-9A-F]{2})", re.search(r"frog%sMap\[64\] = \{([^}]*)\}" % n, hdr).group(1))] for n in ("Amber", "Red")}
G_SCR = [0xFD, 0xFE, 0xFF]
G_RSCR = [0x1D, 0x1E, 0x1F]
IDLE = int(re.search(r"#define FROG_G_IDLE\s+0x([0-9A-F]+)", open(ANIMH).read()).group(1), 16)
N, W, C = 0, 1, 2
HOLD, OUT_MS = 7000, 300
WINDOW = 4000
CRASH_MS = 1500
COLS_SHOWN = 9


def col(c, sev):
    if sev and 0x20 <= c <= 0x5F:
        return MAPS["Amber" if sev == W else "Red"][c - 0x20] or c
    return c


def noise(sev):
    return random.choice(G_RSCR if sev == C else G_SCR)


# events: (time s, text, severity)
EVENTS = [(1.0, "ARMED", N), (2.0, "PUNCH", W), (3.6, "FLIP", N), (5.4, "ROLL", N), (6.8, "ORBIT", N), (8.5, "ZOOM", W),
          (10.0, "SPIN", N), (11.4, "LOOP", N), (13.0, "CRASH", C), (16.0, "PUNCH", W), (17.5, "FLIP", N), (19.0, "PERCH", N),
          (20.5, "TRIPY", W), (22.0, "ROLL", N)]
END = 30.0

feed = []            # newest first: dict(text, sev, at)
combo = 0
combo_last = combo_bump = combo_end = 0
combo_final = 0
word_at = 0
crash_at = None
frames, durs = [], []
ev_i = 0
t_ms = 0
while t_ms < END * 1000:
    while ev_i < len(EVENTS) and EVENTS[ev_i][0] * 1000 <= t_ms:
        _, text, sev = EVENTS[ev_i]
        ev_i += 1
        # combo (as frogComboEvent)
        if text == "CRASH":
            if combo >= 2:
                combo_final, crash_at, combo_end = combo, t_ms, 0
            combo = 0
        elif text != "ARMED":
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
        if text == "CRASH":     # r26: a crash wipes everything under it, top to bottom
            for i, ev in enumerate(feed[1:], start=1):
                if t_ms - ev["at"] < HOLD:
                    ev["at"] = t_ms - HOLD + 90 * (i - 1)
    if combo and t_ms - combo_last > WINDOW:
        if combo >= 2:
            combo_final, combo_end = combo, t_ms
        combo = 0

    img = HP.BASE.copy()
    # clear the left rows 0-6 (the base scene has a static feed in it)
    for r in range(0, 8):
        for x in range(0, 9):
            img.paste((0, 0, 0), (x * HP.FGW, r * HP.FGH, (x + 1) * HP.FGW, (r + 1) * HP.FGH))
    HP.put(img, 4, 0, HP.glyph(IDLE))
    for row, ev in enumerate(feed, start=1):
        age = t_ms - ev["at"]
        if age >= HOLD + OUT_MS:
            continue
        for i, ch in enumerate(ev["text"]):
            if age < 250 + 45 * i:
                g = noise(ev["sev"])                     # types in through glyphs
            elif age >= HOLD + 50 * i:
                g = noise(ev["sev"]) if age < HOLD + 50 * i + 120 else 0x20   # disintegrates
            else:
                g = col(ord(ch), ev["sev"])
            HP.put(img, i, row, HP.glyph(g))
    # combo lines (as frogComboLine / frogComboCrashLine)
    if crash_at is not None and t_ms - crash_at < CRASH_MS:
        ct = t_ms - crash_at
        num = ("X%d!" if combo_final >= 10 else "X%d") % combo_final
        if ct < 350:
            off = 1 if (ct // 60) % 2 else 0
            for i, ch in enumerate(num):
                HP.put(img, i + off, 6, HP.glyph(col(ord(ch), C)))
        elif ct < 800:
            for i, ch in enumerate(num):
                at = 350 + 70 * i
                if ct < at:
                    HP.put(img, i, 6, HP.glyph(col(ord(ch), C)))
                elif ct < at + 110:
                    HP.put(img, i, 6, HP.glyph(noise(C)))
        if 420 <= ct < 900:
            for i in range(len(num)):
                at = 420 + 70 * i
                if at <= ct < at + 240:
                    HP.put(img, i, 7, HP.glyph(noise(C)))
        elif ct >= 900:
            tw, hold = ct - 900, CRASH_MS - 900
            outT = tw - (hold - 400)
            for i, ch in enumerate("BREAK"):
                if outT >= 0 and outT >= 45 * i + 150:
                    continue
                g = noise(C) if ((outT >= 0 and outT >= 45 * i) or tw < 250 + 45 * i) else col(ord(ch), C)
                HP.put(img, i, 7, HP.glyph(g))
        word_at = 0
    else:
        n = combo if combo >= 2 else (combo_final if combo_end and t_ms - combo_end < 400 else 0)
        if n >= 2:
            txt = ("X%d!" if n >= 10 else "X%d") % n
            sev = C if n >= 10 else W if n >= 5 else N
            ending = combo < 2
            tt = (t_ms - combo_end) if ending else (t_ms - combo_bump if combo_bump else 260)
            for i, ch in enumerate(txt):
                scr = (tt >= 80 * i) if ending else (tt < 260 - 50 * i)
                HP.put(img, i, 6, HP.glyph(noise(sev) if scr else col(ord(ch), sev)))
            left = WINDOW - (t_ms - combo_last)
            cells = 0 if left <= 0 else min(5, -(-left // (WINDOW // 5)))
            ms = C if left < 1000 else sev
            if n >= 5:
                if not word_at:
                    word_at = t_ms
                tw = (t_ms - combo_end) if ending else (t_ms - word_at)
                word = "COMBO" if ending else "COMBO"[:cells]
                for i, ch in enumerate(word):
                    scr = (tw >= 80 * i) if ending else (tw < 260 - 50 * i)
                    HP.put(img, i, 7, HP.glyph(noise(sev) if scr else col(ord(ch), ms if tw >= 260 and not ending else sev)))
            else:
                word_at = 0
                if not ending:
                    for i in range(cells):
                        HP.put(img, i, 7, HP.glyph(col(ord("="), ms)))
        else:
            word_at = 0
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

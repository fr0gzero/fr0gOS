#!/usr/bin/env python3
"""Event animations for the activity feed (FLIP / ROLL / SPIN / PUNCH / CRASH / big G / RECRD / ARMED / SAFE /
mode change / warnings), on the Big Eyes base. Reuses the main set's frames wherever it can.

usage: frog_events.py <out dir>
"""
import hashlib
import math
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_anim as A  # noqa: E402
from frog_anim import IDLE, BLINK, SMILE, FLIPPED, dos, outline1, scale, shift, rot, W, H, TOP, BODY, FEET, frog  # noqa: E402
from frog_dos import WHITE, RED, CYAN, LIGHT  # noqa: E402

YELLOW, AMBER = (255, 220, 60), (255, 168, 0)


def draw(src, fn):
    im = src.copy()
    fn(ImageDraw.Draw(im))
    return im


import frog_dos as FD  # noqa: E402
FD.PAL["Y"] = YELLOW

# ---- new DOS poses ----
X_EYES = frog(eyes="GKGGGGKG", top=[".KK..KK.", "GGKGGKGG"])                       # dizzy X eyes
STAR_EYES = dos([".YY..YY.", "GYYGGYYG", "GGYGGYGG"] + BODY + ["GKKKKKKG"] + FEET)
ALERT = dos([".WW..WW.", "GWWGGWWG", "GWKGGKWG", "GGGGGGGG", "GGKKKKGG", "GGGGGGGG", ".GGGGGG.", "G..GG..G"])   # standing tall
SLEEPY = frog(eyes="GKKGGKKG", top=[".GG..GG.", "GGGGGGGG"], mouth="GGGKKGGG")
SIDE_L = dos([".WW.....", "GWWGG...", "KWGGGGG.", "GGGGGGGG", "GGGGGGGG", "KKKGGGG.", ".GGGGGG.", "GG.GG..."])
BACK = dos([".GG..GG.", "GGGGGGGG", "GGGGGGGG", "GDGGGGDG", "GGDDDDGG", "GGGGGGGG", ".GGGGGG.", "GG.GG.GG"])
SIDE_R = SIDE_L.transpose(Image.FLIP_LEFT_RIGHT)


def speed(src, n, lean=0):
    im = shift(src, 0)
    im = im.transform(im.size, Image.AFFINE, (1, -0.25 * lean, 6 * lean, 0, 1, 0), resample=Image.NEAREST) if lean else im
    d = ImageDraw.Draw(im)
    for i in range(n):
        y = 18 + i * 8
        d.line([0, y, 6 + 3 * i, y], fill=LIGHT)
    return outline1(im)


def burst(src, r, col):
    def f(d):
        for a in range(0, 360, 30):
            x1 = 18 + int(r * 0.5 * math.cos(math.radians(a)))
            y1 = 38 + int(r * 0.3 * math.sin(math.radians(a)))
            x2 = 18 + int(r * math.cos(math.radians(a)))
            y2 = 38 + int(r * 0.6 * math.sin(math.radians(a)))
            d.line([x1, y1, x2, y2], fill=col)
    return draw(src, f)


def stars(src, phase):
    def f(d):
        for k in range(3):
            a = phase + k * 2.1
            x, y = 18 + int(13 * math.cos(a)), 12 + int(4 * math.sin(a))
            d.line([x - 1, y, x + 1, y], fill=YELLOW)
            d.line([x, y - 1, x, y + 1], fill=YELLOW)
    return draw(src, f)


def sparkle(src, k):
    def f(d):
        pts = [(4, 10), (31, 8), (2, 34), (33, 30), (10, 4), (26, 2), (6, 46), (30, 46)]
        for i, (x, y) in enumerate(pts):
            if (i + k) % 2 == 0:
                s = 2 if (i + k) % 4 == 0 else 1
                d.line([x - s, y, x + s, y], fill=YELLOW if i % 3 else WHITE)
                d.line([x, y - s, x, y + s], fill=YELLOW if i % 3 else WHITE)
    return draw(src, f)


SPIN = [rot(IDLE, -a) for a in (22, 45, 67, 90, 112, 135, 157)]            # same frames the flip already uses

EVENTS = {
    "trick_flip_roll": ("FLIP / ROLL  - a full trick: rolls over and back, using the flip frames (no new glyphs)",
                        [(IDLE, 200)] + [(f, 50) for f in SPIN] + [(FLIPPED, 120)] + [(f, 50) for f in reversed(SPIN)] + [(SMILE, 600), (IDLE, 300)]),
    "trick_spin": ("SPIN  - yaw spin: front, side, back, side, front",
                   [(IDLE, 200)] + [(f, 90) for f in (SIDE_L, BACK, SIDE_R, IDLE, SIDE_L, BACK, SIDE_R)] + [(IDLE, 500)]),
    "punch": ("PUNCH  - leans into it, speed lines streak past",
              [(IDLE, 250), (scale(IDLE, 0.9, 1.12), 70), (speed(IDLE, 2, 1), 80), (speed(IDLE, 4, 1), 80), (speed(IDLE, 3, 1), 80),
               (speed(IDLE, 1, 0), 80), (IDLE, 500)]),
    "big_g": ("3.6G!  - squashes flat (the squash frames, no new glyphs)",
              [(IDLE, 250), (scale(IDLE, 1.1, 0.85), 60), (scale(IDLE, 1.2, 0.7), 60), (scale(IDLE, 1.24, 0.64), 400),
               (scale(IDLE, 1.1, 0.88), 60), (scale(IDLE, 0.94, 1.08), 60), (IDLE, 400)]),
    "crash": ("CRASH  - splats with an impact burst, then sits there dizzy with stars going round",
              [(IDLE, 200), (burst(scale(IDLE, 1.3, 0.55), 14, AMBER), 90), (burst(scale(IDLE, 1.3, 0.55), 20, RED), 90),
               (scale(X_EYES, 1.15, 0.8), 150)] + [(stars(X_EYES, p), 140) for p in (0, 1.0, 2.0, 3.0, 4.0, 5.0)] + [(IDLE, 400)]),
    "record": ("RECRD / NEW HIGH SCORE  - star eyes and a gold sparkle burst",
               [(IDLE, 250), (STAR_EYES, 200)] + [(sparkle(STAR_EYES, k), 110) for k in range(6)] + [(SMILE, 600)]),
    "armed": ("ARMED  - snaps to attention, eyes wide", [(IDLE, 300), (ALERT, 600), (IDLE, 300)]),
    "safe": ("SAFE  - relaxes, sleepy eyes", [(IDLE, 300), (BLINK, 150), (SLEEPY, 900), (IDLE, 300)]),
    "mode": ("MODE CHANGE (ANGLE / HORZN / ACRO / AIR)  - a little hop in place",
             [(IDLE, 250), (scale(IDLE, 1.1, 0.85), 60), (scale(IDLE, 0.94, 1.08), 60), (shift(IDLE, -5), 90), (shift(IDLE, -2), 60),
              (scale(IDLE, 1.08, 0.9), 60), (IDLE, 400)]),
    "warning": ("WARNINGS (RXLOS / FSAFE / LQ!)  - the signal glitch (no new glyphs)", A.ANIMS["glitch"][1]),
}


def to_rgb(im, s=4):
    cell = Image.new("RGB", (W, H), (0, 0, 0))
    cell.paste(im, (0, 0), im)
    return cell.resize((W * s, H * s), Image.NEAREST)


def key(im):
    cell = Image.new("RGB", (W, H), (0, 0, 0))
    cell.paste(im, (0, 0), im)
    return hashlib.md5(cell.tobytes()).hexdigest()


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    base = {key(f) for _, (_, fr) in A.ANIMS.items() for f, _ in fr}
    new = set()
    S, LABEL = 5, 34
    reel, durs = [], []
    for k, (title, fr) in EVENTS.items():
        for f, _ in fr:
            if key(f) not in base:
                new.add(key(f))
        name = title.split("  -")[0]
        for f, ms in fr:
            c = Image.new("RGB", (W * S, H * S + LABEL), (16, 16, 16))
            c.paste(to_rgb(f, S), (0, LABEL))
            ImageDraw.Draw(c).text((8, 10), name, fill=(120, 240, 150))
            reel.append(c)
            durs.append(ms)
    reel[0].save(os.path.join(out, "frog_events_showreel.gif"), save_all=True, append_images=reel[1:], duration=durs, loop=0, disposal=2)
    print(f"base set {len(base)} glyphs, events add {len(new)}, total {len(base | new)} (about 104 free once the logo goes)")
    # sheet
    sc, per = 2, 14
    cw = W * sc + 8
    rows = []
    for k, (title, fr) in EVENTS.items():
        for j in range(0, len(fr), per):
            rows.append((title if j == 0 else "", fr[j:j + per]))
    rowh = H * sc + 34
    sh = Image.new("RGB", (per * cw + 40, len(rows) * rowh + 20), (16, 16, 16))
    dd = ImageDraw.Draw(sh)
    y = 8
    for title, fr in rows:
        if title:
            dd.text((20, y), title, fill=(230, 230, 230))
        for i, (im, ms) in enumerate(fr):
            sh.paste(to_rgb(im, sc), (20 + i * cw, y + 14))
            dd.text((20 + i * cw, y + 15 + H * sc), f"{ms}ms", fill=(140, 140, 140))
        y += rowh
    sh.save(os.path.join(out, "frog_events_sheet.png"))

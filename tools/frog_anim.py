#!/usr/bin/env python3
"""fr0gOS frog animations on the chosen base (BIGGER EYES). DOS pixels at rest, full resolution in motion.
Writes one animated GIF per animation (real timing, 4x) plus a contact sheet.

usage: frog_anim.py <out dir>
"""
import math
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_dos as FD  # noqa: E402
from frog_dos import W, H, dos, outline1, scatter, shift, WHITE, BLACK, RED, CYAN, LIGHT  # noqa: E402
from frog_dos2 import rot, scale, beam_in, glitch_rgb  # noqa: E402

FD.PAL.update({"D": (30, 128, 62), "L": (150, 255, 170)})

TOP = [".WW..WW.", "GWWGGWWG"]
BODY = ["GGGGGGGG", "GKGGGGKG"]
FEET = [".GGGGGG.", "GG.GG.GG"]


def frog(eyes="GWKGGKWG", mouth="GGKKKKGG", top=None, body=None, feet=None):
    return dos((top or TOP) + [eyes] + (body or BODY) + [mouth] + (feet or FEET))


IDLE = frog()
BLINK = frog(eyes="GKKGGKKG", top=[".GG..GG.", "GGGGGGGG"])
LOOK_L = frog(eyes="GKWGGKWG")
LOOK_R = frog(eyes="GWKGGWKG")
LOOK_UP = frog(eyes="GWWGGWWG", top=[".WW..WW.", "GWKGGKWG"])
SMILE = frog(mouth="GKKKKKKG", body=["GGGGGGGG", "KGGGGGGK"])
FLIPPED = frog().rotate(180)
FLIP_L = LOOK_L.rotate(180)
FLIP_R = LOOK_R.rotate(180)
KICK = dos(["G.GG.G.G", ".GGGGGG.", "GGKKKKGG", "GKGGGGKG", "GGGGGGGG", "GWKGGKWG", "GWWGGWWG", ".WW..WW."])
ARMS = dos(["G......G", "GWW..WWG", "GWWGGWWG", "GWKGGKWG", "GGGGGGGG", "GKGGGGKG", "GGKRRKGG", ".GGGGGG.", "GG.GG.GG"])
ARMS_L = dos(["G.......", "GWW..WWG", "GWWGGWWG", "GWKGGKWG", "GGGGGGGG", "GKGGGGKG", "GGKRRKGG", ".GGGGGGG", "GG.GG.GG"])
ARMS_R = dos([".......G", "GWW..WWG", "GWWGGWWG", "GWKGGKWG", "GGGGGGGG", "GKGGGGKG", "GGKRRKGG", "GGGGGGG.", "GG.GG.GG"])


def bang(im, big):
    im = im.copy()
    d = ImageDraw.Draw(im)
    bb = im.getbbox()
    top = (bb[1] if bb else 20) - (12 if big else 10)
    d.rectangle([16, top, 19, top + (7 if big else 5)], fill=RED)
    d.rectangle([16, top + (9 if big else 7), 19, top + (10 if big else 8)], fill=RED)
    return outline1(im)


def white_flash(src):
    im = outline1(src.copy())
    px = im.load()
    for y in range(H):
        for x in range(W):
            if px[x, y][3] and px[x, y][:3] == BLACK:
                px[x, y] = WHITE + (255,)
    return im


def peek(t, look=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    src = look or IDLE
    im.paste(src, (int(-16 + 16 * t), 0), src)
    return im


def crt(t):
    """CRT power-on: a bright line at the frog's middle opens up to reveal it"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s_, d_ = IDLE.load(), im.load()
    mid, half = 27, int(t * 16)
    for y in range(H):
        for x in range(W):
            if abs(y - mid) <= half and s_[x, y][3]:
                d_[x, y] = s_[x, y]
    if t < 1:
        dr = ImageDraw.Draw(im)
        w = int(17 * min(1.0, 0.15 + t * 3))
        dr.line([18 - w, mid, 17 + w, mid], fill=WHITE)
        if t < 0.08:
            dr.point((18, mid), fill=WHITE)
    return im


def croak_a(k):
    """A: eyes squeeze shut, body swells, mouth pops open and a light ring bursts out"""
    if k == 0:
        return IDLE
    if k == 1:
        return scale(BLINK, 1.06, 0.94)
    if k == 2:
        return scale(BLINK, 1.14, 1.05)
    o = frog(mouth="GGKRRKGG", body=["GGGGGGGG", "GKGKKGKG"])
    o = scale(o, 1.1, 1.04)
    d = ImageDraw.Draw(o)
    r = 6 + (k - 3) * 5
    d.ellipse([18 - r, 30 - r * 0.7, 18 + r, 30 + r * 0.7], outline=LIGHT)
    return o


def croak_b(k):
    """B: a DOS-pixel throat sac inflates under the chin in steps (stays on the font grid), then pops"""
    sacs = [None, ["..L..L..", ".GLLLLG."], ["..LLLL..", "GLLLLLLG"], [".LLLLLL.", "GLLLLLLG"]]
    if k == 0 or k >= 5:
        return IDLE
    if k == 4:
        im = IDLE.copy()
        d = ImageDraw.Draw(im)
        for a in range(0, 360, 45):
            d.point((18 + int(11 * math.cos(math.radians(a))), 42 + int(5 * math.sin(math.radians(a)))), fill=WHITE)
        return im
    sac = sacs[k]
    return dos(TOP + ["GWKGGKWG"] + BODY + ["GGKKKKGG"] + [sac[0], sac[1]] + ["GG.GG.GG"])


ANIMS = {
    "rest": ("REST  - idle, blink, look left, look right, look up, smile (DOS pixels)",
             [(IDLE, 1600), (BLINK, 140), (IDLE, 1200), (LOOK_L, 700), (IDLE, 250), (LOOK_R, 700), (IDLE, 400),
              (LOOK_UP, 600), (IDLE, 500), (SMILE, 900)]),
    "teleport_out": ("TELEPORT OUT  - 1.4 s: pixels scatter and burn out red",
                     [(IDLE, 300)] + [(scatter(IDLE, t, seed=5, tint=RED), 140) for t in (0.08, 0.18, 0.3, 0.42, 0.55, 0.68, 0.82, 0.96)] + [(Image.new("RGBA", (W, H)), 400)]),
    "teleport_in": ("TELEPORT IN  - 1.7 s: scan beam draws it in, white flash, settles to DOS",
                    [(Image.new("RGBA", (W, H)), 300)] + [(beam_in(IDLE, t), 110) for t in [i / 11 for i in range(12)]] +
                    [(white_flash(IDLE), 120), (IDLE, 1000)]),
    "flip": ("FLIP  - spins at full res, rocks on its back, then holds (1 s+) looking around and kicking",
             [(IDLE, 300)] + [(rot(IDLE, -a), 60) for a in (22, 45, 67, 90, 112, 135, 157)] +
             [(rot(FLIPPED, 12), 110), (rot(FLIPPED, -9), 110), (rot(FLIPPED, 5), 110), (FLIPPED, 500), (FLIP_L, 450), (FLIP_R, 450),
              (KICK, 150), (FLIPPED, 150), (KICK, 150), (FLIPPED, 600)]),
    "low_battery": ("LOW BATTERY  - crouch, launch, arms waving at the top with a pulsing red !, squash landing, bounce (loops)",
                    [(bang(shift(ARMS, 8), False), 220), (bang(shift(scale(ARMS, 1.06, 0.9), 8), False), 80),
                     (bang(shift(scale(ARMS, 1.12, 0.8), 8), False), 80), (bang(shift(scale(ARMS, 0.9, 1.15), 8), False), 60),
                     (bang(shift(scale(ARMS, 0.94, 1.08), 4), False), 60), (bang(shift(ARMS_L, 1), True), 70),
                     (bang(shift(ARMS, -2), True), 90), (bang(shift(ARMS_R, -2), True), 90), (bang(shift(ARMS_L, 1), True), 70),
                     (bang(shift(scale(ARMS, 0.94, 1.08), 4), False), 60), (bang(shift(scale(ARMS, 1.15, 0.78), 8), False), 90),
                     (bang(shift(scale(ARMS, 1.05, 0.95), 7), False), 80)]),
    "squash": ("SQUASH  - pulling high G: flattens, holds, springs back",
               [(IDLE, 400), (scale(IDLE, 1.1, 0.85), 60), (scale(IDLE, 1.2, 0.7), 60), (scale(IDLE, 1.24, 0.64), 500),
                (scale(IDLE, 1.1, 0.88), 60), (scale(IDLE, 0.94, 1.08), 60), (IDLE, 500)]),
    "glitch": ("SIGNAL GLITCH  - every now and then, and on RXLOS: splits into red/cyan and tears",
               [(IDLE, 1200), (glitch_rgb(IDLE, 1), 60), (glitch_rgb(IDLE, 3), 60), (shift(glitch_rgb(IDLE, 2), 2), 60),
                (glitch_rgb(IDLE, 1), 60), (IDLE, 800)]),
    "peekaboo": ("PEEKABOO  - idle: slides out of the edge, looks around, ducks back",
                 [(peek(0.0), 400), (peek(0.25), 120), (peek(0.5), 120), (peek(0.75, LOOK_L), 400), (peek(1.0, LOOK_R), 500),
                  (peek(1.0, IDLE), 300), (peek(0.75), 120), (peek(0.5), 120), (peek(0.2), 120), (peek(0.0), 600)]),
    "boot": ("BOOT  - the frog does the boot: a white line opens out like an old CRT turning on, the frog appears and blinks",
             [(crt(t), ms) for t, ms in ((0.0, 300), (0.04, 80), (0.1, 80), (0.2, 80), (0.35, 80), (0.55, 80), (0.8, 80), (1.0, 500))] +
             [(BLINK, 140), (IDLE, 300), (SMILE, 900)]),
}


def to_rgb(im, s=4):
    cell = Image.new("RGB", (W, H), (0, 0, 0))
    cell.paste(im, (0, 0), im)
    return cell.resize((W * s, H * s), Image.NEAREST)


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    total = 0
    for key, (title, frames) in ANIMS.items():
        imgs = [to_rgb(f) for f, _ in frames]
        imgs[0].save(os.path.join(out, f"frog_{key}.gif"), save_all=True, append_images=imgs[1:],
                     duration=[ms for _, ms in frames], loop=0, disposal=2)
        total += len(frames)
        print(f"{key:13s} {len(frames):2d} frames {sum(ms for _, ms in frames) / 1000:.1f} s")
    # contact sheet
    sc = 2
    per = 14
    cw = W * sc + 8
    rows = []
    for key, (title, frames) in ANIMS.items():
        for j in range(0, len(frames), per):
            rows.append((title if j == 0 else "", frames[j:j + per]))
    rowh = H * sc + 34
    sh = Image.new("RGB", (per * cw + 40, len(rows) * rowh + 20), (16, 16, 16))
    d = ImageDraw.Draw(sh)
    y = 8
    for title, fr in rows:
        if title:
            d.text((20, y), title, fill=(230, 230, 230))
        for i, (im, ms) in enumerate(fr):
            sh.paste(to_rgb(im, sc), (20 + i * cw, y + 14))
            d.text((20 + i * cw, y + 15 + H * sc), f"{ms}ms", fill=(140, 140, 140))
        y += rowh
    sh.save(os.path.join(out, "frog_animations_sheet.png"))
    print("total frames", total)

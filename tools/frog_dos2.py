#!/usr/bin/env python3
"""DOS frog v2: longer teleport, more rest poses, longer flip, an intricate low-battery jump,
a new croak and six new ideas. Same rule: DOS pixels at rest, full resolution while moving.

usage: frog_dos2.py <out.png>
"""
import math
import os
import random
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frog_dos import (W, H, GREEN, LIGHT, DARK, WHITE, BLACK, RED, CYAN, dos, outline1, scatter, shift)  # noqa: E402

AMBER = (255, 168, 0)
PINK = (255, 120, 170)
YELLOW = (255, 220, 60)

R = {   # DOS-pixel rest poses (8 wide)
    "idle":    [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"],
    "blink":   [".GG..GG.", "GKKGGKKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"],
    "look up": [".GG..GG.", "GKWGGKWG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"],
    "wink":    [".GG..GG.", "GKKGGWKG", "GGGGGGGG", "KGGGGGGK", "GKKKKKKG", ".GGGGGG.", "GG.GG.GG"],
    "yawn 1":  [".GG..GG.", "GKKGGKKG", "GGGGGGGG", "GGGKKGGG", "GGKRRKGG", ".GGKKGG.", "GG.GG.GG"],
    "yawn 2":  [".GG..GG.", "GKKGGKKG", "GGGKKGGG", "GGKRRKGG", "GGKRRKGG", ".GGKKGG.", "GG.GG.GG"],
    "tongue":  [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKRRKGG", ".GGGRGG.", "GG.GRRGG"],
    "tap 1":   [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"],
    "tap 2":   [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGGG", "GG.GG..."],
    "breathe": [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", "GGGGGGGG", "GG.GG.GG"],
    "flipped": ["GG.GG.GG", ".GGGGGG.", "GGKKKKGG", "GKGGGGKG", "GGGGGGGG", "GWKGGWKG", ".GG..GG."],
    "flip L":  ["GG.GG.GG", ".GGGGGG.", "GGKKKKGG", "GKGGGGKG", "GGGGGGGG", "WKGGWKGG", ".GG..GG."],
    "flip R":  ["GG.GG.GG", ".GGGGGG.", "GGKKKKGG", "GKGGGGKG", "GGGGGGGG", "GGWKGGWK", ".GG..GG."],
    "flip kick": ["G.GG.G.G", ".GGGGGG.", "GGKKKKGG", "GKGGGGKG", "GGGGGGGG", "GWKGGWKG", ".GG..GG."],
    "arms up": ["G......G", "G.G..G.G", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKRRKGG", ".GGGGGG.", "GG.GG.GG"],
    "arms L":  ["G.......", "G.G..G.G", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKRRKGG", ".GGGGGGG", "GG.GG.GG"],
    "arms R":  [".......G", "G.G..G.G", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKRRKGG", "GGGGGGG.", "GG.GG.GG"],
}


def F(name, **kw):
    return dos(R[name], **kw)


def rot(src, deg, dy=0):
    big = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    big.paste(src, (W // 2, H // 2 + dy), src)
    r = big.rotate(deg, resample=Image.NEAREST, center=(W, H))
    return r.crop((W // 2, H // 2, W // 2 + W, H // 2 + H))


def scale(src, sx, sy, anchor_bottom=True):
    """squash and stretch at full resolution"""
    bbox = src.getbbox()
    part = src.crop(bbox)
    nw, nh = max(1, int(part.width * sx)), max(1, int(part.height * sy))
    part = part.resize((nw, nh), Image.NEAREST)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x = (W - nw) // 2
    y = bbox[3] - nh if anchor_bottom else (H - nh) // 2
    out.paste(part, (x, y), part)
    return out


def beam_in(src, t, width=1.0):
    """scan beam sweeping down, drawing the frog in, with a red/cyan double line and sparkle"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    yl = int(12 + t * 36)
    s, d = src.load(), img.load()
    for y in range(H):
        for x in range(W):
            if s[x, y][3] and y < yl:
                d[x, y] = s[x, y]
    dr = ImageDraw.Draw(img)
    half = int(17 * width)
    dr.line([18 - half, yl, 17 + half, yl], fill=CYAN)
    dr.line([18 - half, yl + 1, 17 + half, yl + 1], fill=RED)
    for i in range(3):
        sx = 18 + int(math.sin(t * 20 + i * 2.1) * 14)
        dr.point((sx, yl - 1), fill=WHITE)
    return img


def pillar(t):
    """vertical light pillar that opens up then narrows (pre-beam)"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w = max(1, int(1 + 7 * math.sin(math.pi * t)))
    for y in range(4, 50):
        c = RED if (y + int(t * 10)) // 2 % 2 else CYAN
        d.line([18 - w // 2, y, 18 + w // 2, y], fill=c)
    return img


def glitch_rgb(src, off):
    """chromatic split: red shifted left, cyan shifted right"""
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s = src.load()
    o = out.load()
    for y in range(H):
        for x in range(W):
            if s[x, y][3] and s[x, y][:3] != BLACK:
                if 0 <= x - off < W:
                    o[x - off, y] = RED + (255,)
                if 0 <= x + off < W:
                    o[x + off, y] = CYAN + (255,)
    for y in range(H):
        for x in range(W):
            if s[x, y][3] and s[x, y][:3] != BLACK and (y // 3) % 4:
                o[x, y] = s[x, y]
    return out


def overlay(src, draw_fn):
    img = src.copy()
    draw_fn(ImageDraw.Draw(img))
    return img


def frames():
    idle = F("idle")
    S = {}
    S["REST POSES  (DOS pixels; it cycles through these when nothing's happening)"] = [
        (n, F(n)) for n in ("idle", "blink", "look up", "wink", "yawn 1", "yawn 2", "tongue", "tap 1", "tap 2", "breathe")]

    out = [("rest", idle)] + [(f"out {i + 1}", scatter(idle, t, seed=5, tint=RED)) for i, t in enumerate((0.08, 0.18, 0.3, 0.42, 0.55, 0.68, 0.82, 0.96))]
    S["TELEPORT OUT  (8 frames, full res: pixels scatter and burn out red)"] = out

    tin = [(f"pillar {i + 1}", pillar(t)) for i, t in enumerate((0.1, 0.3, 0.5, 0.7, 0.9))]
    tin += [(f"conv {i + 1}", scatter(idle, t, seed=9, tint=CYAN)) for i, t in enumerate((0.95, 0.8, 0.65, 0.5, 0.35, 0.2))]
    tin += [(f"beam {i + 1}", beam_in(idle, t)) for i, t in enumerate((0.05, 0.18, 0.31, 0.44, 0.57, 0.7, 0.83, 0.96))]
    tin += [("flash", outline1(overlay(idle, lambda d: None)).copy()), ("rest", idle)]
    flash = tin[-2][1].load()
    for y in range(H):
        for x in range(W):
            if flash[x, y][3] and flash[x, y][:3] == BLACK:
                flash[x, y] = WHITE + (255,)
    S["TELEPORT IN  (21 frames, full res: light pillar, pixels converge, scan beam draws it in, white flash, DOS)"] = tin

    S["CROAK v2  (full res: puffs up round, cheeks out, mouth pops open, sound bars, settles)"] = [
        ("rest", idle), ("inhale", scale(idle, 1.0, 0.92)), ("puff 1", scale(idle, 1.08, 1.04)), ("puff 2", scale(idle, 1.16, 1.08)),
        ("pop!", overlay(scale(F("yawn 2"), 1.12, 1.06), lambda d: [d.line([2, 26, 2, 30], fill=LIGHT), d.line([33, 26, 33, 30], fill=LIGHT),
                                                                     d.line([0, 24, 0, 32], fill=LIGHT), d.line([35, 24, 35, 32], fill=LIGHT)])),
        ("bars", overlay(F("yawn 2"), lambda d: [d.line([1, 25, 1, 31], fill=LIGHT), d.line([34, 25, 34, 31], fill=LIGHT)])),
        ("deflate", scale(idle, 1.04, 0.98)), ("rest", idle)]

    S["FLIP  (full res spin in 22.5 deg steps, rocks on its back, then DOS: looks around, kicks)"] = (
        [(f"{a}", rot(idle, -a)) for a in (0, 22, 45, 67, 90, 112, 135, 157)] +
        [("rock -10", rot(F("flipped"), 10)), ("rock +10", rot(F("flipped"), -10)), ("flipped", F("flipped")),
         ("look L", F("flip L")), ("look R", F("flip R")), ("kick", F("flip kick"))])

    lb = [("rest", F("arms up")), ("crouch 1", scale(F("arms up"), 1.06, 0.9)), ("crouch 2", scale(F("arms up"), 1.12, 0.8)),
          ("launch", scale(F("arms up"), 0.9, 1.15)), ("rise 1", shift(scale(F("arms up"), 0.94, 1.08), -4)),
          ("rise 2", shift(F("arms L"), -8)), ("apex !", shift(F("arms up"), -11)), ("apex !!", shift(F("arms R"), -11)),
          ("fall 1", shift(F("arms L"), -8)), ("fall 2", shift(scale(F("arms up"), 0.94, 1.08), -4)),
          ("land", scale(F("arms up"), 1.15, 0.78)), ("bounce", shift(scale(F("arms up"), 1.05, 0.95), -1)), ("rest", F("arms up"))]
    def bang(im, big):
        d = ImageDraw.Draw(im)
        bb = im.getbbox()
        top = (bb[1] if bb else 20) - (12 if big else 10)
        d.rectangle([16, top, 19, top + (7 if big else 5)], fill=RED)
        d.rectangle([16, top + (9 if big else 7), 19, top + (10 if big else 8)], fill=RED)
        return outline1(im)
    S["LOW BATTERY JUMP  (13 frames: crouch, launch stretch, arms waving at the apex with a pulsing red !, squash landing, bounce)"] = [
        (n, bang(im.copy(), "!" in n)) for n, im in lb]

    # ---- six new ideas ----
    S["IDEA 1  SIGNAL GLITCH  (RXLOS / LQ drop: the frog splits into red/cyan channels and tears)"] = [
        ("ok", idle), ("split 1", glitch_rgb(idle, 1)), ("split 2", glitch_rgb(idle, 3)), ("tear", shift(glitch_rgb(idle, 2), 2)), ("split 1", glitch_rgb(idle, 1)), ("ok", idle)]

    def keyboard(d, frame):
        d.rectangle([4, 44, 31, 49], fill=DARK)
        for i in range(6):
            d.rectangle([6 + i * 4, 45, 7 + i * 4, 46], fill=GREEN if i != frame % 6 else WHITE)
        d.rectangle([10, 47, 25, 48], fill=GREEN)
    typ = [(f"type {i + 1}", outline1(overlay(shift(F("idle"), -6), lambda d, i=i: keyboard(d, i)))) for i in range(4)]
    S["IDEA 2  TYPING  (when a new message hits the event log, the frog types it on a tiny DOS keyboard)"] = typ

    S["IDEA 3  BACKFLIP  (new G record: a full 360 at full res, lands with star sparkles)"] = (
        [(f"{a}", shift(rot(idle, a), -int(10 * math.sin(math.radians(a / 2))))) for a in (0, 45, 90, 135, 180, 225, 270, 315, 360)] +
        [("stars", outline1(overlay(idle, lambda d: [d.point((p), fill=YELLOW) for p in ((4, 18), (31, 16), (8, 12), (28, 22))])))])

    def peek(t):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        im.paste(idle, (int(-14 + 14 * t), 0), idle)
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 3, H], fill=(0, 0, 0, 0))
        return im
    S["IDEA 4  PEEKABOO  (idle: hides at the screen edge and peeks out sideways)"] = [(f"peek {i + 1}", peek(t)) for i, t in enumerate((0.2, 0.5, 0.7, 0.5, 0.2))]

    def fly(fx, fy, look, tongue=False):
        im = dos(R["look up"] if look == "up" else R["idle"])
        d = ImageDraw.Draw(im)
        d.point((fx, fy), fill=BLACK)
        d.point((fx - 1, fy - 1), fill=WHITE)
        d.point((fx + 1, fy - 1), fill=WHITE)
        if tongue:
            d.line([18, 33, fx, fy], fill=PINK, width=2)
        return im
    S["IDEA 5  FLY HUNT  (a fly buzzes around in full res, eyes track it, tongue SNAP, gulp)"] = [
        ("fly", fly(30, 8, "up")), ("buzz", fly(8, 12, "up")), ("buzz", fly(26, 4, "up")), ("buzz", fly(14, 14, "up")),
        ("SNAP", fly(14, 14, "up", True)), ("gulp", F("blink")), ("smug", F("wink"))]

    def crt(t):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        s, d = idle.load(), im.load()
        mid = 30
        half = int(t * 26)
        for y in range(H):
            for x in range(W):
                if abs(y - mid) <= half and s[x, y][3]:
                    d[x, y] = s[x, y]
        dr = ImageDraw.Draw(im)
        if t < 1:
            dr.line([18 - int(16 * min(1, t * 3)), mid, 17 + int(16 * min(1, t * 3)), mid], fill=WHITE)
        return im
    S["IDEA 6  CRT POWER-ON  (boot: a white line opens out like an old monitor turning on, the frog appears)"] = [
        (f"crt {i + 1}", crt(t)) for i, t in enumerate((0.05, 0.15, 0.3, 0.5, 0.75, 1.0))]
    return S


def sheet(out):
    S = frames()
    sc = 3
    per = 11
    cw = W * sc + 12
    rows = []
    for title, fr in S.items():
        chunks = [fr[i:i + per] for i in range(0, len(fr), per)]
        for j, c in enumerate(chunks):
            rows.append((title if j == 0 else "", c))
    rowh = H * sc + 40
    sh = Image.new("RGB", (per * cw + 40, len(rows) * rowh + 20), (16, 16, 16))
    d = ImageDraw.Draw(sh)
    y = 8
    for title, fr in rows:
        if title:
            d.text((20, y), title, fill=(230, 230, 230))
        for i, (lab, im) in enumerate(fr):
            cell = Image.new("RGB", (W, H), (0, 0, 0))
            cell.paste(im, (0, 0), im)
            sh.paste(cell.resize((W * sc, H * sc), Image.NEAREST), (20 + i * cw, y + 14))
            d.text((20 + i * cw, y + 15 + H * sc), lab, fill=(150, 150, 150))
        y += rowh
    sh.save(out)
    print("ok", sh.size, sum(len(v) for v in S.values()), "frames")


if __name__ == "__main__":
    sheet(sys.argv[1])

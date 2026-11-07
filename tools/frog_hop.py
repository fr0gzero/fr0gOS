#!/usr/bin/env python3
"""Cell-to-cell hopping. The frog sits on a 'ledge' (5th character in from the edge, on the empty row above a
group of readouts). It moves by hopping sideways one character at a time; to change side or row it hops off
the outer edge of the screen and wraps around, coming in from the far edge on the new row.

A hop between two cells is drawn as a pair of glyphs per frame (the frog straddles the boundary), so a hop is
6 glyphs for each direction, and the wraparound reuses them (one half of the pair is just off-screen).

usage: frog_hop.py <out dir>
"""
import math
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frog_anim import IDLE, BLINK, SMILE, scale, W, H  # noqa: E402
from frog_events import SLEEPY  # noqa: E402

FONT = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts", "hdzero-hacker", "BTFL_FHD_000.bmp")).convert("RGB")
FGW, FGH = FONT.width // 16, FONT.height // 32
COLS, ROWS = 50, 18
TS = (0.25, 0.5, 0.75)


def hop_pair(t, direction):
    """frog in mid-hop across two cells: returns (from_cell, to_cell) glyph images"""
    canvas = Image.new("RGBA", (W * 2, H), (0, 0, 0, 0))
    lift = int(-14 * math.sin(math.pi * t))
    src = scale(IDLE, 0.92, 1.1) if t != 0.5 else IDLE
    x = int(W * t) if direction > 0 else W - int(W * t)
    canvas.paste(src, (x, lift), src)
    left, right = canvas.crop((0, 0, W, H)), canvas.crop((W, 0, W * 2, H))
    return (left, right) if direction > 0 else (right, left)


HOP_R = [hop_pair(t, +1) for t in TS]
HOP_L = [hop_pair(t, -1) for t in TS]
CROUCH = scale(IDLE, 1.1, 0.85)
LAND = scale(IDLE, 1.08, 0.9)

LEFT = {1: "ANGLE", 2: "PUNCH", 7: "3.71V", 8: "135\x07", 9: "6.81A", 13: "LQ100", 14: "F1000", 15: "R8", 16: "200MW"}
RIGHT = {0: "MK4-2", 1: "01:17", 3: "ARMED", 4: "ACRO", 5: "AIR", 12: "THR", 13: "47.1%", 14: "RPM", 15: "33370", 16: "1.0G"}


def scene():
    img = Image.new("RGB", (COLS * FGW, ROWS * FGH), (0, 0, 0))
    d = ImageDraw.Draw(img)
    pic_w = ROWS * FGH * 4 // 3
    x0 = (img.width - pic_w) // 2
    for y in range(img.height):                       # picture in the middle, black bars either side
        t = y / img.height
        col = (int(70 + 60 * (1 - t)), int(82 + 50 * (1 - t)), int(96 + 40 * (1 - t))) if t < 0.55 else (int(58 + 30 * t), int(48 + 22 * t), int(40 + 10 * t))
        d.line([(x0, y), (x0 + pic_w, y)], fill=col)
    for rows, right in ((LEFT, False), (RIGHT, True)):
        for r, txt in rows.items():
            x = (COLS - len(txt)) if right else 0
            for i, ch in enumerate(txt):
                put(img, x + i, r, glyph(ord(ch)))
    return img


def glyph(c):
    g = FONT.crop(((c % 16) * FGW, (c // 16) * FGH, (c % 16 + 1) * FGW, (c // 16 + 1) * FGH)).convert("RGBA")
    px = g.load()
    for y in range(FGH):
        for x in range(FGW):
            if px[x, y][:3] == (127, 127, 127):
                px[x, y] = (0, 0, 0, 0)
    return g


def put(img, col, row, g):
    if 0 <= col < COLS and 0 <= row < ROWS:
        img.paste(g, (col * FGW, row * FGH), g)


BASE = scene()
frames, durs = [], []


def frame(cells, ms):
    """cells: list of (col, row, glyph)"""
    im = BASE.copy()
    for c, r, g in cells:
        put(im, c, r, g)
    frames.append(im.resize((im.width // 2, im.height // 2), Image.NEAREST))
    durs.append(ms)


def sit(c, r, ms, pose=IDLE):
    frame([(c, r, pose)], ms)


def hop(c, r, direction):
    """one hop from (c, r) to (c + direction, r); cells off-screen are simply not drawn"""
    sit(c, r, 70, CROUCH)
    pairs = HOP_R if direction > 0 else HOP_L
    for a, b in pairs:
        frame([(c, r, a), (c + direction, r, b)], 60)
    sit(c + direction, r, 70, LAND)




def ledge(row, right):
    """the frog's ledge on `row`: the inner edge of the readout directly under it (stops over its first letter)"""
    below = (RIGHT if right else LEFT).get(row + 1, "")
    n = len(below) or 5
    return COLS - n if right else n - 1


# the tour: ledge on the left (above the power group) -> wrap -> ledge on the right (above the performance group)
if __name__ == "__main__":
    L_LEDGE, R_LEDGE = ledge(6, False), ledge(11, True)
    sit(L_LEDGE, 6, 900)
    sit(L_LEDGE, 6, 140, BLINK)
    sit(L_LEDGE, 6, 700)
    for c in range(L_LEDGE, 0, -1):    # hop out along the empty row to the screen edge
        hop(c, 6, -1)
    hop(0, 6, -1)                       # off the left edge...
    frame([], 250)
    hop(50, 11, -1)                     # ...and in from the right edge, one row group further down
    for c in range(49, R_LEDGE, -1):
        hop(c, 11, -1)
    sit(R_LEDGE, 11, 800)
    # mode change: a little hop in place on the ledge
    for f, ms in ((CROUCH, 60), (scale(IDLE, 0.94, 1.08), 60), (IDLE.transform(IDLE.size, Image.AFFINE, (1, 0, 0, 0, 1, 5)), 90), (LAND, 60)):
        sit(R_LEDGE, 11, ms, f)
    sit(R_LEDGE, 11, 600, SMILE)
    sit(R_LEDGE, 11, 1200, SLEEPY)

    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    frames[0].save(os.path.join(out, "frog_hop_tour.gif"), save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)
    # glyph sheet for the hop
    sh = Image.new("RGB", (8 * (W * 3 + 10) + 20, 2 * (H * 3 + 30) + 30), (16, 16, 16))
    dd = ImageDraw.Draw(sh)
    for row, (name, pairs) in enumerate((("hop right: from-cell | to-cell, three steps", HOP_R), ("hop left (and the wraparound)", HOP_L))):
        y = 10 + row * (H * 3 + 30)
        dd.text((10, y), name, fill=(220, 220, 220))
        x = 10
        for a, b in pairs:
            for g in (a, b) if name.startswith("hop right") else (b, a):
                cell = Image.new("RGB", (W, H), (0, 0, 0))
                cell.paste(g, (0, 0), g)
                sh.paste(cell.resize((W * 3, H * 3), Image.NEAREST), (x, y + 14))
                x += W * 3 + 2
            x += 14
    sh.save(os.path.join(out, "frog_hop_glyphs.png"))
    print("tour", len(frames), "frames", round(sum(durs) / 1000, 1), "s; hop glyphs: 12 (6 each way)")

#!/usr/bin/env python3
"""Preview sheet for the new frog animations (teleport, croak, flip look-around) and low-battery options.

usage: preview_frog_options.py <out.png>
"""
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_art as A  # noqa: E402

TRANS, BLACK = (127, 127, 127), (0, 0, 0)
GW, GH, K = 24, 36, 2
SCALE = 4


def grid(rows):
    rows = [r.ljust(8, ".") for r in rows]
    pad = (16 - len(rows)) // 2
    g = [[None] * 8 for _ in range(16)]
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            g[y + pad][x] = A.PAL.get(ch)
    return g


def cell(rows):
    art = grid(rows)
    W, H = 10, 18
    big = [[None] * W for _ in range(H)]
    for y in range(16):
        for x in range(8):
            if art[y][x] is not None:
                big[y + 1][x + 1] = art[y][x]
    img = Image.new("RGB", (GW, GH), BLACK)
    px = img.load()
    ox, oy = (GW - W * K) // 2, (GH - H * K) // 2
    for y in range(H):
        for x in range(W):
            c = big[y][x]
            if c is None and any(0 <= y + dy < H and 0 <= x + dx < W and big[y + dy][x + dx] not in (None, BLACK)
                                 for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                c = BLACK
            if c is not None:
                for yy in range(K):
                    for xx in range(K):
                        px[ox + x * K + xx, oy + y * K + yy] = c
    return img.resize((GW * SCALE, GH * SCALE), Image.NEAREST)


T = A.TELEPORT
rows = [
    ("TELEPORT ARRIVE - 1.4 s at the new spot: spark, beam, scan rings, scanlines, hologram, flash, frog",
     [("spark", T[0]), ("beam", T[1]), ("rings", T[2]), ("scanlines", T[3]), ("hologram", T[4]), ("flash", T[5]), ("frog", A.IDLE)]),
    ("TELEPORT LEAVE - 0.45 s at the old spot (arrive frames backwards), then 0.15 s of nothing",
     [("frog", A.IDLE), ("hologram", T[4]), ("rings", T[2]), ("spark", T[0])]),
    ("CROAK - loops while a warning is up: throat swells, balloons, ribbit with sound rings",
     [("idle", A.IDLE), ("swell", A.CROAK[0]), ("bigger", A.CROAK[1]), ("balloon", A.CROAK[2]), ("ribbit!", A.CROAK[3])]),
    ("FLIP - stays at least 1 s, looks around and kicks its legs",
     [("on its back", A.FLIP), ("look left", A.FLIP_LOOK_L), ("look right", A.FLIP_LOOK_R), ("kick", A.FLIP_KICK)]),
]
for name, frames in A.SWEAT_OPTIONS.items():
    rows.append(("LOW BATTERY option " + name, [(f"frame {i + 1}", f) for i, f in enumerate(frames)]))

CW = GW * SCALE + 40
W = 7 * CW + 40
H = len(rows) * (GH * SCALE + 56) + 20
sheet = Image.new("RGB", (W, H), (16, 16, 16))
d = ImageDraw.Draw(sheet)
y = 10
for title, frames in rows:
    d.text((20, y), title, fill=(230, 230, 230))
    for i, (lab, art) in enumerate(frames):
        x = 20 + i * CW
        sheet.paste(cell(art), (x, y + 16))
        d.text((x, y + 18 + GH * SCALE), lab, fill=(160, 160, 160))
    y += GH * SCALE + 56
sheet.save(sys.argv[1])
print("ok", sheet.size)

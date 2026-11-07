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


def grid(rows, w=8, h=16):
    rows = [r.ljust(w, ".") for r in rows]
    pad = (h - len(rows)) // 2
    g = [[None] * w for _ in range(h)]
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            g[y + pad][x] = A.PAL.get(ch)
    return g


def cell(rows, k=K):
    w = max(len(r) for r in rows)
    w = 8 if w <= 8 else w
    h = 16 if k == 2 else 34
    art = grid(rows, w, h)
    W, H = w + 2, h + 2
    big = [[None] * W for _ in range(H)]
    for y in range(h):
        for x in range(w):
            if art[y][x] is not None:
                big[y + 1][x + 1] = art[y][x]
    img = Image.new("RGB", (GW, GH), BLACK)
    px = img.load()
    ox, oy = (GW - W * k) // 2, (GH - H * k) // 2
    for y in range(H):
        for x in range(W):
            c = big[y][x]
            if c is None and any(0 <= y + dy < H and 0 <= x + dx < W and big[y + dy][x + dx] not in (None, BLACK)
                                 for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                c = BLACK
            if c is not None:
                for yy in range(k):
                    for xx in range(k):
                        px[ox + x * k + xx, oy + y * k + yy] = c
    return img.resize((GW * SCALE, GH * SCALE), Image.NEAREST)


rows = [
    ("LOW BATTERY - hops to the voltage readout and jumps at it, arms up, red !  (loops while LOW / LAND / DEAD)",
     [("crouch", A.LOWBATT[0]), ("jump !", A.LOWBATT[1]), ("falling", A.LOWBATT[2]), ("land", A.LOWBATT[3])]),
    ("TELEPORT with red - arrive (leave is the same frames backwards)",
     [(n, f) for n, f in zip(["spark", "beam", "rings", "scanlines", "hologram", "red flash"], A.TELEPORT_RED)] + [("frog", A.IDLE)]),
]
for name, frames in A.CUTE.items():
    rows.append(("CUTE option: " + name, [(f"frame {i + 1}", f) for i, f in enumerate(frames)]))
rows.append(("DETAIL - left: today (8x16 grid, every pixel doubled). right: same size at full resolution (20x16, 1:1)",
             [("today", A.IDLE), ("full res", ("HIRES", A.HIRES_IDLE))]))

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
        img = cell(art[1], 1) if isinstance(art, tuple) else cell(art)
        sheet.paste(img, (x, y + 16))
        d.text((x, y + 18 + GH * SCALE), lab, fill=(160, 160, 160))
    y += GH * SCALE + 56
sheet.save(sys.argv[1])
print("ok", sheet.size)

#!/usr/bin/env python3
"""The fr0gOS mascot as a FIXED multi-cell sprite: a smiling frog with FPV goggles on its head, drawn across a
2x2 (or 3x3) block of goggle-font cells. It stays put in that block and animates in place (blink, look, wink,
and trick reactions) instead of hopping around. Mega Drive shading.

usage: frog_grid.py <out.png> [cells=2]
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_megadrive as M  # noqa: E402

_anim = len(sys.argv) > 1 and sys.argv[1] == "anim"
CELLS = int(sys.argv[3]) if _anim and len(sys.argv) > 3 else (int(sys.argv[2]) if not _anim and len(sys.argv) > 2 else 2)
# one goggle-font FHD cell is 18x27 sprite units at PX=2; a CELLS x CELLS block scales that up
M.GW, M.GH = 18 * CELLS, 27 * CELLS
F = M.GW / 36.0       # coords below are authored on a 36x54 frame (the 2x2 size), scaled to the block


def R(*v):
    return [int(round(c * F)) for c in v]


def eye(s, box, look, lid=0):
    """big frog eye: white ball + black pupil; lid 0 open, 1 blink (closed curve), 2 X (crash)"""
    x0, y0, x1, y1 = box
    if lid == 2:
        s.shape("E", lambda d: d.ellipse(R(x0, y0, x1, y1), fill=1))
        s.ink(lambda d: (d.line(R(x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=1, width=max(1, int(F))),
                         d.line(R(x0 + 1, y1 - 1, x1 - 1, y0 + 1), fill=1, width=max(1, int(F)))))
    elif lid == 1:
        s.ink(lambda d: d.arc(R(x0, y0 + 1, x1, y1 + 1), 200, 340, fill=1, width=max(1, int(F))))
    else:
        s.shape("E", lambda d: d.ellipse(R(x0, y0, x1, y1), fill=1))
        cx = (x0 + x1) / 2 + look * 2.0
        cy = (y0 + y1) / 2 + 1
        r = (x1 - x0) * 0.26
        s.ink(lambda d: d.ellipse(R(cx - r, cy - r, cx + r, cy + r), fill=1))
        s.shape("E", lambda d: d.ellipse(R(cx - r + 0.5, cy - r + 0.5, cx - r + 1.5, cy - r + 1.5), fill=1))


def mascot(pose):
    s = M.Sprite()
    look = {"lookL": -1, "lookR": 1}.get(pose, 0)
    lid = 1 if pose == "blink" else (2 if pose == "crash" else 0)
    # --- head fills the frame ---
    s.shape("G", lambda d: d.ellipse(R(2, 12, 34, 52), fill=1))
    s.shape("G", lambda d: (d.ellipse(R(0, 26, 11, 49), fill=1), d.ellipse(R(25, 26, 36, 49), fill=1)))      # cheeks
    # --- FPV box goggles across the forehead, above the eyes, strap round the sides ---
    s.shape("D", lambda d: (d.rounded_rectangle(R(0, 13, 6, 20), int(2 * F), fill=1), d.rounded_rectangle(R(30, 13, 36, 20), int(2 * F), fill=1)))  # strap
    s.shape("S", lambda d: d.rounded_rectangle(R(5, 2, 31, 15), int(3 * F), fill=1))                              # body
    s.shape("K", lambda d: d.rounded_rectangle(R(7, 5, 29, 13), int(2 * F), fill=1))                              # bezel
    s.shape("C", lambda d: d.rectangle(R(9, 7, 27, 10), fill=1))                                            # lens screen
    s.shape("B", lambda d: d.rectangle(R(9, 10, 27, 11), fill=1))                                           # lower band
    s.ink(lambda d: d.line(R(18, 5, 18, 13), fill=1, width=max(1, int(F))))                                 # two-lens divider
    s.shape("Y", lambda d: (d.rectangle(R(10, -1, 12, 2), fill=1), d.rectangle(R(24, -1, 26, 2), fill=1)))   # antennas
    s.shape("E", lambda d: d.rectangle(R(11, 7, 13, 9), fill=1))                                            # lens glint
    # --- eyes, below the goggles ---
    eye(s, [6, 17, 16, 29], look, lid)
    eye(s, [20, 17, 30, 29], look, 1 if pose == "wink" else lid)
    # --- mouth ---
    if pose == "crash":
        s.ink(lambda d: d.arc(R(12, 44, 24, 50), 190, 350, fill=1, width=max(1, int(F))))                   # frown
    elif pose in ("grin", "flip"):
        s.ink(lambda d: d.chord(R(10, 33, 26, 47), 10, 170, fill=1))
        s.shape("E", lambda d: d.rectangle(R(13, 39, 23, 41), fill=1))
    else:
        s.ink(lambda d: d.arc(R(9, 32, 27, 48), 20, 160, fill=1, width=max(1, int(F))))
        s.ink(lambda d: d.arc(R(10, 31, 26, 47), 30, 150, fill=1, width=max(1, int(F))))
    # blush
    s.shape("P", lambda d: (d.ellipse(R(3, 31, 8, 36), fill=1), d.ellipse(R(28, 31, 33, 36), fill=1)))
    return s.render()


FRAMES = ["idle", "blink", "lookL", "lookR", "wink", "grin", "flip", "crash"]

if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "anim":
    # fixed-in-place animation: the frog sits in its block and plays idle business + a trick reaction
    out = sys.argv[2]
    fr = {p: mascot(p) for p in FRAMES}
    w, h = fr["idle"].size
    seq = ([("idle", 1400), ("blink", 120), ("idle", 1600), ("lookL", 500), ("idle", 300), ("lookR", 500),
            ("idle", 900), ("blink", 120), ("idle", 700), ("wink", 420), ("idle", 1300), ("grin", 700),
            ("idle", 600), ("flip", 800), ("idle", 1000), ("blink", 120), ("idle", 1400),
            ("crash", 1300), ("blink", 160), ("idle", 1200)])
    PADX, PADY, LBL = 18, 14, 30
    W, H = w + PADX * 2, h + PADY + LBL
    frames, durs = [], []
    for name, ms in seq:
        canvas = Image.new("RGB", (W, H), (0, 0, 0))
        canvas.paste(fr[name], (PADX, PADY), fr[name])
        dd = ImageDraw.Draw(canvas)
        try:
            nf = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 20)
        except Exception:
            nf = None
        # a little blue nameplate under him, like the OSD
        dd.rectangle([PADX, PADY + h + 4, PADX + 64, PADY + h + 24], fill=(22, 54, 201))
        dd.text((PADX + 6, PADY + h + 5), "MK42", fill=(255, 212, 0), font=nf)
        frames.append(canvas)
        durs.append(ms)
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)
    print("anim", out, W, H)
    sys.exit(0)

cells = [mascot(p) for p in FRAMES]
big = cells[0].width * (3 if CELLS == 2 else 2)
cols, pad, lblh, gap = 4, 18, 22, 22
cw, chh = big + gap, big + lblh + cells[0].height + 14
sheet = Image.new("RGB", (pad * 2 + cols * cw - gap, pad * 2 + 26 + 2 * chh), (18, 20, 24))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 22)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
except Exception:
    font = small = None
d.text((pad, pad - 4), f"fr0gOS mascot - fixed {CELLS}x{CELLS} block, animates in place", fill=(200, 230, 210), font=font)
for i, (c, name) in enumerate(zip(cells, FRAMES)):
    cx = pad + (i % cols) * cw
    cy = pad + 26 + (i // cols) * chh
    sheet.paste(c.resize((big, big), Image.NEAREST), (cx, cy))
    sheet.paste(c, (cx, cy + big + 6))          # actual size
    d.text((cx + c.width + 8, cy + big + 6 + c.height // 2 - 8), name, fill=(150, 200, 170), font=small)
sheet.save(sys.argv[1])
print("ok cell", cells[0].size)

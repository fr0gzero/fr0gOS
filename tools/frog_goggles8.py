#!/usr/bin/env python3
"""Eight variations on the fr0gOS mascot: a smiling frog face with FPV goggles on its forehead.
Mega Drive shading (three tones, top-left light, black outline) on the 18x27 grid (2x on the 36x54 cell).

usage: frog_goggles8.py <out.png>
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frog_megadrive import Sprite  # noqa: E402


def peye(s, box, look=1):
    """one front eye: white ball + black pupil"""
    s.shape("E", lambda d: d.ellipse(box, fill=1))
    cx = (box[0] + box[2]) // 2 + look
    cy = (box[1] + box[3]) // 2
    s.ink(lambda d: d.rectangle([cx, cy, cx + 1, cy + 1], fill=1))


def twin_goggle(s, x0=3, y0=1):
    s.shape("D", lambda d: (d.rectangle([x0 - 3, y0 + 7, x0 - 1, y0 + 11], fill=1), d.rectangle([x0 + 11, y0 + 7, x0 + 13, y0 + 11], fill=1)))
    s.shape("S", lambda d: d.rounded_rectangle([x0, y0, x0 + 11, y0 + 7], 2, fill=1))
    s.shape("K", lambda d: d.rounded_rectangle([x0 + 1, y0 + 2, x0 + 10, y0 + 6], 1, fill=1))
    s.shape("C", lambda d: d.rectangle([x0 + 2, y0 + 3, x0 + 9, y0 + 5], fill=1))
    s.ink(lambda d: d.line([x0 + 5, y0 + 2, x0 + 5, y0 + 6], fill=1))
    s.shape("Y", lambda d: (d.rectangle([x0 + 2, y0 - 2, x0 + 3, y0], fill=1), d.rectangle([x0 + 8, y0 - 2, x0 + 9, y0], fill=1)))
    s.shape("E", lambda d: d.point((x0 + 3, y0 + 3), fill=1))


def box_goggle(s):   # single wide HDZero-box screen
    s.shape("D", lambda d: (d.rectangle([0, 8, 2, 12], fill=1), d.rectangle([15, 8, 17, 12], fill=1)))
    s.shape("S", lambda d: d.rounded_rectangle([2, 1, 15, 8], 2, fill=1))
    s.shape("K", lambda d: d.rounded_rectangle([3, 3, 14, 7], 1, fill=1))
    s.shape("C", lambda d: d.rectangle([4, 4, 13, 6], fill=1))
    s.shape("B", lambda d: d.rectangle([4, 6, 13, 6], fill=1))
    s.shape("Y", lambda d: d.rectangle([8, -1, 9, 1], fill=1))
    s.shape("E", lambda d: d.point((5, 4), fill=1))


def visor_goggle(s):  # slim sunglasses-style visor pushed up
    s.shape("D", lambda d: (d.rectangle([0, 7, 2, 10], fill=1), d.rectangle([15, 7, 17, 10], fill=1)))
    s.shape("K", lambda d: d.rounded_rectangle([2, 3, 15, 7], 2, fill=1))
    s.shape("C", lambda d: d.line([4, 4, 13, 4], fill=1, width=1))
    s.shape("E", lambda d: d.point((5, 4), fill=1))


def aviator_goggle(s):  # two round lenses + strap
    s.shape("D", lambda d: d.rectangle([0, 6, 17, 7], fill=1))
    for cx in (5, 12):
        s.shape("S", lambda d, cx=cx: d.ellipse([cx - 3, 2, cx + 3, 8], fill=1))
        s.shape("C", lambda d, cx=cx: d.ellipse([cx - 2, 3, cx + 2, 7], fill=1))
        s.ink(lambda d, cx=cx: d.ellipse([cx - 2, 3, cx + 2, 7], outline=1))
    s.shape("E", lambda d: (d.point((4, 4), fill=1), d.point((11, 4), fill=1)))


def head(s, shape):
    if shape == "round":
        s.shape("G", lambda d: d.ellipse([1, 7, 16, 26], fill=1))
        s.shape("G", lambda d: (d.ellipse([0, 13, 6, 24], fill=1), d.ellipse([11, 13, 17, 24], fill=1)))
    elif shape == "wide":
        s.shape("G", lambda d: d.rounded_rectangle([0, 8, 17, 26], 7, fill=1))
    elif shape == "tall":
        s.shape("G", lambda d: d.ellipse([2, 6, 15, 26], fill=1))
    elif shape == "squish":
        s.shape("G", lambda d: d.ellipse([0, 11, 17, 26], fill=1))


def smile(s, kind):
    if kind == "wide":
        s.ink(lambda d: d.arc([4, 14, 14, 23], 15, 165, fill=1))
        s.ink(lambda d: d.arc([4, 14, 14, 23], 25, 155, fill=1))
    elif kind == "grin":
        s.ink(lambda d: d.chord([4, 15, 14, 23], 10, 170, fill=1))
        s.shape("E", lambda d: d.rectangle([6, 19, 12, 20], fill=1))
    elif kind == "small":
        s.ink(lambda d: d.arc([6, 16, 12, 21], 20, 160, fill=1))
    elif kind == "smirk":
        s.ink(lambda d: d.arc([6, 16, 13, 21], 10, 110, fill=1))


def blush(s):
    s.shape("P", lambda d: (d.ellipse([2, 17, 4, 19], fill=1), d.ellipse([13, 17, 15, 19], fill=1)))


def make(i):
    s = Sprite()
    if i == 0:   # round, twin-lens, wide smile (baseline refined)
        head(s, "round"); twin_goggle(s); peye(s, [3, 9, 7, 14]); peye(s, [10, 9, 14, 14]); smile(s, "wide"); blush(s)
    elif i == 1:   # bug-eyes on top, goggle strap across, big grin
        head(s, "squish")
        for bx in ([2, 7, 7, 13], [10, 7, 15, 13]):
            s.shape("G", lambda d, bx=bx: d.ellipse([bx[0] - 1, bx[1] - 3, bx[2] + 1, bx[3] - 3], fill=1)); peye(s, bx, 0)
        s.shape("K", lambda d: d.rectangle([0, 6, 17, 8], fill=1))
        s.shape("C", lambda d: d.rectangle([2, 6, 15, 7], fill=1))
        smile(s, "grin")
    elif i == 2:   # wide head, single box goggle, grin
        head(s, "wide"); box_goggle(s); peye(s, [3, 10, 7, 15]); peye(s, [10, 10, 14, 15]); smile(s, "grin"); blush(s)
    elif i == 3:   # cool, slim visor, smirk, narrow eyes
        head(s, "round"); visor_goggle(s)
        s.shape("E", lambda d: (d.rectangle([4, 10, 7, 12], fill=1), d.rectangle([11, 10, 14, 12], fill=1)))
        s.ink(lambda d: (d.point((6, 11), fill=1), d.point((12, 11), fill=1)))
        smile(s, "smirk")
    elif i == 4:   # cute, big eyes, small twin goggle, small smile
        head(s, "round"); twin_goggle(s, 4, 1)
        peye(s, [2, 9, 8, 15], 1); peye(s, [10, 9, 16, 15], 1); smile(s, "small"); blush(s)
    elif i == 5:   # aviator round goggles
        head(s, "round"); aviator_goggle(s); peye(s, [3, 10, 7, 15]); peye(s, [10, 10, 14, 15]); smile(s, "wide"); blush(s)
    elif i == 6:   # tall head, twin goggle high, happy
        head(s, "tall"); twin_goggle(s, 3, 0); peye(s, [4, 10, 8, 15]); peye(s, [10, 10, 14, 15]); smile(s, "wide")
    elif i == 7:   # wide squish, box goggle, huge grin, antennas
        head(s, "squish"); box_goggle(s); peye(s, [2, 11, 7, 16]); peye(s, [10, 11, 15, 16]); smile(s, "grin"); blush(s)
    return s.render()


NAMES = ["round+twin", "bug-eyes", "wide+box", "cool visor", "cute", "aviator", "tall", "squish grin"]
cells = [make(i) for i in range(8)]
big = cells[0].width * 4
cols, pad, gap, lblh = 4, 18, 26, 22
cw, ch = big + gap, big + lblh + 34
sheet = Image.new("RGB", (pad * 2 + cols * cw - gap, pad * 2 + 24 + 2 * ch), (18, 20, 24))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 22)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
except Exception:
    font = small = None
d.text((pad, pad - 2), "fr0gOS mascot - 8 variations (smiling frog, FPV goggles on forehead)", fill=(200, 230, 210), font=font)
for i, (c, name) in enumerate(zip(cells, NAMES)):
    cx = pad + (i % cols) * cw
    cy = pad + 24 + (i // cols) * ch
    sheet.paste(c.resize((big, big), Image.NEAREST), (cx, cy))
    sheet.paste(c, (cx + big - c.width, cy + big + 4))
    d.text((cx, cy + big + c.height + 6), f"{i + 1} {name}", fill=(150, 200, 170), font=small)
sheet.save(sys.argv[1])
print("ok", cells[0].size)

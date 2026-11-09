#!/usr/bin/env python3
"""fr0gOS mascot: a smiling frog face with FPV box goggles pushed up on the forehead.
Mega Drive style - three-tone shading lit top-left, bold black outline - on the 18x27 sprite grid
(2x pixels on the 36x54 FHD goggle-font cell). Frames: idle, blink, wink, grin.

usage: frog_goggles.py <out.png>
"""
import os
import sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frog_megadrive import Sprite, eyes  # noqa: E402


def mascot(pose):
    s = Sprite()
    # --- head: big friendly green frog face, wide cheeks ---
    s.shape("G", lambda d: d.ellipse([1, 7, 16, 26], fill=1))
    s.shape("G", lambda d: d.ellipse([0, 13, 6, 24], fill=1))
    s.shape("G", lambda d: d.ellipse([11, 13, 17, 24], fill=1))

    # --- FPV box goggles, pushed up on the forehead ---
    s.shape("D", lambda d: (d.rectangle([0, 8, 2, 12], fill=1), d.rectangle([15, 8, 17, 12], fill=1)))   # strap around the sides
    s.shape("S", lambda d: d.rounded_rectangle([3, 1, 14, 8], 2, fill=1))                                 # goggle body
    s.shape("K", lambda d: d.rounded_rectangle([4, 3, 13, 7], 1, fill=1))                                 # bezel
    s.shape("C", lambda d: d.rectangle([5, 4, 12, 6], fill=1))                                            # lens screen (cyan)
    s.shape("B", lambda d: d.rectangle([5, 6, 12, 6], fill=1))                                            # lower lens band (blue)
    s.ink(lambda d: d.line([8, 3, 8, 7], fill=1))                                                          # two-lens divider
    s.shape("Y", lambda d: (d.rectangle([5, -1, 6, 1], fill=1), d.rectangle([11, -1, 12, 1], fill=1)))     # antenna nubs
    s.shape("E", lambda d: d.point((6, 4), fill=1))                                                        # lens glint

    # --- eyes (below the goggles, so they read as pushed up) ---
    if pose == "blink":
        s.ink(lambda d: (d.arc([3, 10, 8, 15], 200, 340, fill=1), d.arc([9, 10, 14, 15], 200, 340, fill=1)))
    else:
        eyes(s, [3, 9, 7, 14], [10, 9, 14, 14], 1)
        if pose == "wink":
            s.shape("G", lambda d: d.rectangle([10, 9, 14, 14], fill=1))        # cover right eye
            s.ink(lambda d: d.arc([10, 10, 14, 15], 200, 340, fill=1))          # ...with a closed curve

    # --- big smile ---
    if pose == "grin":
        s.ink(lambda d: d.chord([4, 15, 14, 23], 10, 170, fill=1))
        s.shape("E", lambda d: d.rectangle([6, 19, 12, 20], fill=1))            # teeth line
    else:
        s.ink(lambda d: d.arc([4, 14, 14, 23], 15, 165, fill=1))
        s.ink(lambda d: d.arc([4, 14, 14, 23], 25, 155, fill=1))               # thicken the smile
    # rosy cheeks
    s.shape("P", lambda d: (d.ellipse([2, 17, 4, 19], fill=1), d.ellipse([13, 17, 15, 19], fill=1)))
    return s.render()


FRAMES = ["idle", "blink", "wink", "grin"]
cells = [mascot(p) for p in FRAMES]
PX = cells[0].width // 18

pad, gap, lblh = 16, 24, 22
big = cells[0].width * 4
sheet = Image.new("RGB", (pad * 2 + len(cells) * (big + gap) - gap + 220, pad * 2 + lblh + big + 60), (18, 20, 24))
from PIL import ImageDraw, ImageFont
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 22)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
except Exception:
    font = small = None
d.text((pad, pad - 2), "fr0gOS mascot - smiling frog, FPV goggles on the forehead", fill=(200, 230, 210), font=font)
x = pad
for c, name in zip(cells, FRAMES):
    up = c.resize((big, big), Image.NEAREST)
    sheet.paste(up, (x, pad + lblh))
    d.text((x, pad + lblh + big + 6), name, fill=(150, 200, 170), font=small)
    x += big + gap
# actual goggle size on the right
sheet.paste(cells[0], (x + 20, pad + lblh + 10))
d.text((x + 20, pad + lblh + 10 + cells[0].height + 6), "actual size", fill=(150, 200, 170), font=small)
sheet.save(sys.argv[1])
print("ok", cells[0].size)

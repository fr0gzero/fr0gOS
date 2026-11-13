#!/usr/bin/env python3
"""Paint the two heart glyphs of the first-arm like & subscribe card into the goggle font (slots 0x16 big, 0x17 small).
usage: add_card_glyphs.py <in_dir_with_BTFL_000.bmp+BTFL_FHD_000.bmp> <out_dir>"""
import os, sys
from PIL import Image, ImageDraw
SRC, OUT = sys.argv[1:3]
HEART = ["01100110", "11111111", "11111111", "11111111", "01111110", "00111100", "00011000"]
RED = (255, 59, 59)
TRANS = (127, 127, 127)
SLOTS = {0x16: 3.0, 0x17: 2.0}      # slot -> pixel scale at HD (x1.5 for FHD)
os.makedirs(OUT, exist_ok=True)
for name in ("BTFL_000.bmp", "BTFL_FHD_000.bmp"):
    im = Image.open(os.path.join(SRC, name)).convert("RGB")
    cw, ch = im.width // 16, im.height // 32
    k = ch / 36.0
    for slot, sc in SLOTS.items():
        cell = Image.new("RGB", (cw, ch), TRANS)
        d = ImageDraw.Draw(cell)
        s = sc * k
        w, h = 8 * s, 7 * s
        ox, oy = (cw - w) / 2, 15.5 * k - h / 2
        for j, row in enumerate(HEART):
            for i, c in enumerate(row):
                if c == "1":
                    d.rectangle((round(ox + i * s), round(oy + j * s), round(ox + (i + 1) * s) - 1, round(oy + (j + 1) * s) - 1), fill=RED)
        im.paste(cell, ((slot % 16) * cw, (slot // 16) * ch))
    im.save(os.path.join(OUT, name))
print("ok")

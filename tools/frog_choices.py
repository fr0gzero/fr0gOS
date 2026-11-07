#!/usr/bin/env python3
"""One simple image with the remaining choices: croak A or B, and how to make room in the goggle font."""
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_anim as A  # noqa: E402
from frog_dos import W, H  # noqa: E402

font = Image.open("fonts/hdzero-hacker/BTFL_FHD_000.bmp").convert("RGB")
gw, gh = font.width // 16, font.height // 32


def glyph(c):
    g = font.crop(((c % 16) * gw, (c // 16) * gh, (c % 16 + 1) * gw, (c // 16 + 1) * gh))
    return Image.eval(g, lambda v: v).convert("RGB").point(lambda v: v), g


def text(s):
    out = Image.new("RGB", (gw * len(s), gh), (0, 0, 0))
    for i, ch in enumerate(s):
        g = glyph(ord(ch))[1].load()
        for y in range(gh):
            for x in range(gw):
                if g[x, y] != (127, 127, 127):
                    out.putpixel((i * gw + x, y), g[x, y])
    return out


def logo():
    out = Image.new("RGB", (gw * 24, gh * 2), (0, 0, 0))
    for r in range(2):
        for c in range(24):
            g = glyph(0xA0 + r * 24 + c)[1].load()
            for y in range(gh):
                for x in range(gw):
                    if g[x, y] != (127, 127, 127):
                        out.putpixel((c * gw + x, r * gh + y), g[x, y])
    return out


def strip(frames, s=2):
    out = Image.new("RGB", (len(frames) * (W * s + 6), H * s), (0, 0, 0))
    for i, f in enumerate(frames):
        cell = Image.new("RGB", (W, H), (0, 0, 0))
        cell.paste(f, (0, 0), f)
        out.paste(cell.resize((W * s, H * s), Image.NEAREST), (i * (W * s + 6), 0))
    return out


Wd = 1180
img = Image.new("RGB", (Wd, 1060), (18, 18, 18))
d = ImageDraw.Draw(img)
GREY, WHITE, ACC = (150, 150, 150), (235, 235, 235), (100, 230, 130)


def box(x, y, w, h, label, title, sub):
    d.rectangle([x, y, x + w, y + h], outline=(70, 70, 70), width=2)
    d.rectangle([x, y, x + 46, y + 40], fill=ACC)
    d.text((x + 16, y + 12), label, fill=(0, 0, 0))
    d.text((x + 58, y + 8), title, fill=WHITE)
    d.text((x + 58, y + 24), sub, fill=GREY)


d.text((20, 14), "CHOICE 1 - CROAK", fill=ACC)
box(20, 40, 560, 200, "A", "SWELL + RING", "eyes squeeze, body swells, mouth pops, a light ring bursts")
img.paste(strip([A.croak_a(k) for k in (0, 1, 2, 3, 4, 5)]), (40, 100))
box(600, 40, 560, 200, "B", "THROAT SAC", "a DOS-pixel sac inflates under the chin, then pops")
img.paste(strip([A.croak_b(k) for k in (0, 1, 2, 3, 4)]), (620, 100))

d.text((20, 270), "CHOICE 2 - MAKING ROOM IN THE GOGGLE FONT  (about 30 free characters today; the full frog set needs about 75)", fill=ACC)
box(20, 300, 1140, 210, "1", "KEEP THE BIG BOOT LOGO, TRIM THE FROG to about 30 frames",
    "teleport in 12 -> 5 beam frames, flip spin 7 -> 3, low-battery jump 12 -> 6, peekaboo 8 -> 4, glitch 4 -> 2")
lg = logo()
img.paste(lg.resize((lg.width // 2, lg.height // 2), Image.NEAREST), (60, 380))
d.text((60, 440), "boot logo stays exactly as it is now", fill=GREY)

box(20, 530, 1140, 230, "2", "BOOT LOGO IN NORMAL DOS TEXT, KEEP THE WHOLE FROG SET (about 75 frames)",
    "the logo is typed in the DOS font instead of 48 big custom glyphs, which frees all 48 for the frog")
t = text("> FR0GZERO_")
img.paste(t, (60, 610))
d.text((60, 610 + gh + 8), "same words in normal-size DOS capitals (the font has no lowercase), typed out with the cursor on boot", fill=GREY)

box(20, 780, 1140, 250, "3", "NO BOOT LOGO, KEEP THE WHOLE FROG SET, AND THE FROG DOES THE BOOT",
    "the CRT power-on: a white line opens out and the frog appears where the logo used to be")
crt = [A.IDLE.copy() for _ in range(1)]
from frog_dos2 import frames as f2  # noqa: E402
crt_frames = [im for lab, im in f2()["IDEA 6  CRT POWER-ON  (boot: a white line opens out like an old monitor turning on, the frog appears)"]]
img.paste(strip(crt_frames[1:6] + [A.IDLE]), (60, 860))
img.save("fonts/hdzero-hacker/frog_choices.png")
print("ok", img.size)

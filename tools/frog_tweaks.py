#!/usr/bin/env python3
"""The original DOS frog with minor tweaks: eight variations, each with its rest poses, shown next to real
DOS text at actual size.

usage: frog_tweaks.py <out.png>
"""
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_dos as FD  # noqa: E402
from frog_dos import W, H, dos  # noqa: E402

FD.PAL.update({"D": (30, 128, 62), "L": (150, 255, 170)})


def variant(top, eyes_open, eyes_shut, eyes_l, eyes_r, mid, mouth, smile, bottom):
    """rows: [top..., eye row, mid..., mouth row, bottom...]; returns pose dict"""
    def build(e, m):
        return top + [e] + mid + [m] + bottom
    return {"idle": build(eyes_open, mouth), "blink": build(eyes_shut, mouth), "look L": build(eyes_l, mouth),
            "look R": build(eyes_r, mouth), "smile": build(eyes_open, smile)}


V = [
    ("0  ORIGINAL", variant([".GG..GG."], "GWKGGWKG", "GKKGGKKG", "WKGGWKGG", "GGWKGGWK",
                            ["GGGGGGGG", "GKGGGGKG"], "GGKKKKGG", "GKKKKKKG", [".GGGGGG.", "GG.GG.GG"])),
    ("1  LIGHT BELLY", variant([".GG..GG."], "GWKGGWKG", "GKKGGKKG", "WKGGWKGG", "GGWKGGWK",
                               ["GGGGGGGG", "GKGGGGKG"], "GGKKKKGG", "GKKKKKKG", [".GLLLLG.", "GG.GG.GG"])),
    ("2  DARK FEET", variant([".GG..GG."], "GWKGGWKG", "GKKGGKKG", "WKGGWKGG", "GGWKGGWK",
                             ["GGGGGGGG", "GKGGGGKG"], "GGKKKKGG", "GKKKKKKG", [".GGGGGG.", "DD.GG.DD"])),
    ("3  BIGGER EYES", variant([".WW..WW.", "GWWGGWWG"], "GWKGGWKG", "GKKGGKKG", "GKWGGKWG", "GWKGGWKG",
                               ["GGGGGGGG", "GKGGGGKG"], "GGKKKKGG", "GKKKKKKG", [".GGGGGG.", "GG.GG.GG"])),
    ("4  ROUND BUMPS", variant(["..G..G..", ".GGGGGG."], "GWKGGWKG", "GKKGGKKG", "WKGGWKGG", "GGWKGGWK",
                               ["GGGGGGGG", "GKGGGGKG"], "GGKKKKGG", "GKKKKKKG", [".GGGGGG.", "GG.GG.GG"])),
    ("5  WIDE GRIN", variant([".GG..GG."], "GWKGGWKG", "GKKGGKKG", "WKGGWKGG", "GGWKGGWK",
                             ["GGGGGGGG", "KGGGGGGK"], "GKKKKKKG", "KKKKKKKK", [".GGGGGG.", "GG.GG.GG"])),
    ("6  TALLER (one more row of body)", variant([".GG..GG."], "GWKGGWKG", "GKKGGKKG", "WKGGWKGG", "GGWKGGWK",
                                                 ["GGGGGGGG", "GKGGGGKG"], "GGKKKKGG", "GKKKKKKG", ["GGGGGGGG", ".GGGGGG.", "GG.GG.GG"])),
    ("7  COMBO (belly + dark feet + round bumps)", variant(["..G..G..", ".GGGGGG."], "GWKGGWKG", "GKKGGKKG", "WKGGWKGG", "GGWKGGWK",
                                                          ["GGGGGGGG", "GKGGGGKG"], "GGKKKKGG", "GKKKKKKG", [".GLLLLG.", "DD.GG.DD"])),
]


def text_strip(frog):
    font = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts", "hdzero-hacker", "BTFL_FHD_000.bmp")).convert("RGB")
    gw, gh = font.width // 16, font.height // 32
    strip = Image.new("RGB", (gw * 7, gh), (0, 0, 0))
    for i, ch in enumerate("MK4-2 "):
        c = ord(ch)
        g = font.crop(((c % 16) * gw, (c // 16) * gh, (c % 16 + 1) * gw, (c // 16 + 1) * gh)).load()
        for yy in range(gh):
            for xx in range(gw):
                if g[xx, yy] != (127, 127, 127):
                    strip.putpixel((i * gw + xx, yy), g[xx, yy])
    strip.paste(frog, (gw * 6, 0), frog)
    return strip


if __name__ == "__main__":
    sc = 3
    cw = W * sc + 12
    rowh = H * sc + 40
    sh = Image.new("RGB", (5 * cw + 60 + W * 7, len(V) * rowh + 20), (16, 16, 16))
    d = ImageDraw.Draw(sh)
    y = 8
    for title, poses in V:
        d.text((20, y), title, fill=(230, 230, 230))
        for i, (lab, rows) in enumerate(poses.items()):
            im = dos(rows)
            cell = Image.new("RGB", (W, H), (0, 0, 0))
            cell.paste(im, (0, 0), im)
            sh.paste(cell.resize((W * sc, H * sc), Image.NEAREST), (20 + i * cw, y + 14))
            d.text((20 + i * cw, y + 15 + H * sc), lab, fill=(150, 150, 150))
        sh.paste(text_strip(dos(poses["idle"])), (30 + 5 * cw, y + 14))
        d.text((30 + 5 * cw, y + 18 + H), "actual size, next to the text", fill=(140, 140, 140))
        y += rowh
    sh.save(sys.argv[1])
    print("ok", sh.size)

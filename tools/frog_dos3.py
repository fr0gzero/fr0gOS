#!/usr/bin/env python3
"""DOS frog v3: three taller redesigns that use the whole 8x16 cell, their rest poses
(look around + smile only), and two new croak ideas.

usage: frog_dos3.py <out.png>
"""
import math
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frog_dos import W, H, LIGHT, WHITE, BLACK, CYAN, RED, dos, outline1  # noqa: E402

def _a(eye1, eye2, m1="GKGGGGKG", m2="GGKKKKGG"):
    return [".GG..GG.", eye1, eye2, "GGGGGGGG", m1, m2, "GGGGGGGG", ".GLLLLG.", "GGLLLLGG", "GGLLLLGG",
            "GG.GG.GG", "GG.GG.GG", "GGG..GGG"]


def _b(eye1, eye2, m1="GGGGGGGG", m2="GKKKKKKG"):
    return ["GG....GG", eye1, eye2, "GGGGGGGG", "GGGGGGGG", m1, m2, "GGGGGGGG", ".GLLLLG.", ".GLLLLG.",
            "GGGGGGGG", "G.G..G.G", "GG....GG"]


def _c(eye1, eye2, m="GGKKKKGG", m0="GGGGGGGG"):
    return [".GG..GG.", eye1, eye2, m0, m, "DGGGGGGD", "DDGLLGDD", "DDGLLGDD", "DDDGGDDD", "D.G..G.D", "GG....GG"]


POSES = {
    "A  TALL SITTER  (light belly, long legs, 13 rows)": {
        "idle": _a("GWWGGWWG", "GWKGGKWG"), "blink": _a("GGGGGGGG", "GKKGGKKG"), "look L": _a("GWWGGWWG", "GKWGGKWG"),
        "look R": _a("GWWGGWWG", "GWKGGWKG"), "look up": _a("GWKGGKWG", "GWWGGWWG"),
        "smile": _a("GWWGGWWG", "GWKGGKWG", "KGGGGGGK", "GKKKKKKG")},
    "B  STALK EYES  (eyes out wide on top, big grin, 13 rows)": {
        "idle": _b("WW....WW", "WK....KW"), "blink": _b("GG....GG", "KK....KK"), "look L": _b("WW....WW", "KW....KW"),
        "look R": _b("WW....WW", "WK....WK"), "look up": _b("WK....KW", "WW....WW"),
        "smile": _b("WW....WW", "WK....KW", "KGGGGGGK", "GKKKKKKG")},
    "C  CROUCHER  (dark hind legs folded, ready to spring, 11 rows)": {
        "idle": _c("GWWGGWWG", "GWKGGKWG"), "blink": _c("GGGGGGGG", "GKKGGKKG"), "look L": _c("GWWGGWWG", "GKWGGKWG"),
        "look R": _c("GWWGGWWG", "GWKGGWKG"), "look up": _c("GWKGGKWG", "GWWGGWWG"),
        "smile": _c("GWWGGWWG", "GWKGGKWG", "GKKKKKKG", "KGGGGGGK")},
}
DESIGNS = {k: v["idle"] for k, v in POSES.items()}


def bubble(src, r, pop=False):
    img = src.copy()
    d = ImageDraw.Draw(img)
    cx, cy = 18, 22
    if pop:
        for a in range(0, 360, 45):
            x = cx + int(math.cos(math.radians(a)) * r)
            y = cy + int(math.sin(math.radians(a)) * r)
            d.point((x, y), fill=WHITE)
    else:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=LIGHT)
        d.point((cx - r // 2, cy - r // 2), fill=WHITE)
    return outline1(img)


def pulse(src, k):
    """belly lights up and sound waves ripple out from both sides"""
    img = src.copy()
    px = img.load()
    for y in range(H):
        for x in range(W):
            if px[x, y][:3] == LIGHT and px[x, y][3] and k % 2:
                px[x, y] = WHITE + (255,)
    d = ImageDraw.Draw(img)
    rr = 2 + k * 2                                   # ripples roll up out of the head, into the space above
    d.arc([18 - rr * 2, 8 - rr + 6, 18 + rr * 2, 8 + rr + 6], 200, 340, fill=LIGHT)
    if k > 1:
        rr2 = rr - 3
        d.arc([18 - rr2 * 2, 8 - rr2 + 6, 18 + rr2 * 2, 8 + rr2 + 6], 200, 340, fill=LIGHT)
    return img


def sheet(out):
    sc = 3
    cw = W * sc + 12
    rowh = H * sc + 40
    rows = []
    for title, ps in POSES.items():
        rows.append((title, [(k, dos(v)) for k, v in ps.items()]))
    a = list(DESIGNS.values())[0]
    base = dos(a)
    rows.append(("CROAK option 1  BUBBLE: a vocal bubble grows from its mouth in full res and pops into sparkle",
                 [("rest", base)] + [(f"grow {i + 1}", bubble(base, r)) for i, r in enumerate((3, 6, 9, 12))] + [("pop", bubble(base, 12, True)), ("rest", base)]))
    rows.append(("CROAK option 2  PULSE: belly flashes and sound ripples roll up out of its head",
                 [("rest", base)] + [(f"ripple {k}", pulse(base, k)) for k in range(1, 6)] + [("rest", base)]))
    sh = Image.new("RGB", (7 * cw + 40, len(rows) * rowh + 20), (16, 16, 16))
    d = ImageDraw.Draw(sh)
    y = 8
    for title, fr in rows:
        d.text((20, y), title, fill=(230, 230, 230))
        for i, (lab, im) in enumerate(fr):
            cell = Image.new("RGB", (W, H), (0, 0, 0))
            cell.paste(im, (0, 0), im)
            sh.paste(cell.resize((W * sc, H * sc), Image.NEAREST), (20 + i * cw, y + 14))
            d.text((20 + i * cw, y + 15 + H * sc), lab, fill=(150, 150, 150))
        y += rowh
    sh.save(out)
    print("ok", sh.size)


if __name__ == "__main__":
    sheet(sys.argv[1])

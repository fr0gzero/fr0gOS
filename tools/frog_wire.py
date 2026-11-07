#!/usr/bin/env python3
"""Wireframe frog variants at full goggle resolution (single 36x54, double 72x54).

usage: frog_wire.py <out.png>
"""
import math
import sys
from PIL import Image, ImageDraw

H = 54
G, L, DG = (64, 214, 104), (150, 255, 170), (25, 80, 40)
WH, K, C, R = (240, 255, 240), (0, 0, 0), (120, 255, 255), (255, 44, 44)


def canvas(w):
    img = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def outline(img):
    w = img.width
    out = img.copy()
    src, dst = img.load(), out.load()
    for y in range(H):
        for x in range(w):
            if src[x, y][3]:
                continue
            if any(0 <= x + ex < w and 0 <= y + ey < H and src[x + ex, y + ey][3] and src[x + ex, y + ey][:3] != K
                   for ex in (-1, 0, 1) for ey in (-1, 0, 1)):
                dst[x, y] = K + (255,)
    return out


def body(d, box, col, width=1):
    d.ellipse(box, outline=col, width=width)


def a_thin():
    """A: clean single line, bright eyes"""
    img, d = canvas(36)
    body(d, [5, 29, 31, 46], G)
    for x in (11, 25):
        d.ellipse([x - 5, 25, x + 5, 35], fill=K, outline=G)
        d.rectangle([x - 1, 29, x + 1, 31], fill=WH)
    d.arc([10, 33, 26, 40], 20, 160, fill=G)
    d.line([3, 46, 12, 46], fill=G)
    d.line([24, 46, 33, 46], fill=G)
    return outline(img)


def b_neon():
    """B: neon tube, bright core with a dim glow line either side, 2 px"""
    img, d = canvas(36)
    body(d, [4, 28, 32, 47], DG, 4)
    body(d, [5, 29, 31, 46], L, 2)
    for x in (11, 25):
        d.ellipse([x - 6, 24, x + 6, 36], fill=K, outline=DG, width=3)
        d.ellipse([x - 5, 25, x + 5, 35], outline=L, width=2)
        d.rectangle([x - 1, 29, x + 1, 31], fill=WH)
    d.arc([9, 32, 27, 41], 20, 160, fill=L, width=2)
    d.line([2, 46, 12, 46], fill=L, width=2)
    d.line([24, 46, 34, 46], fill=L, width=2)
    return outline(img)


def c_lowpoly():
    """C: low-poly vector, straight edges, cyan eyes (Tron)"""
    img, d = canvas(36)
    pts = [(4, 40), (8, 31), (14, 29), (22, 29), (28, 31), (32, 40), (28, 46), (8, 46)]
    d.polygon(pts, outline=G)
    for p in ((8, 31), (28, 31)):
        d.line([p, (18, 38)], fill=DG)
    d.line([(4, 40), (32, 40)], fill=DG)
    for x in (11, 25):
        d.polygon([(x - 5, 30), (x, 24), (x + 5, 30), (x, 35)], fill=K, outline=G)
        d.line([x - 2, 30, x + 2, 30], fill=C)
        d.point((x, 29), fill=C)
    d.line([12, 37, 18, 39, 24, 37], fill=G)
    d.line([4, 46, 1, 47], fill=G)
    d.line([32, 46, 35, 47], fill=G)
    return outline(img)


def d_dots():
    """D: dot-matrix, the outline drawn in every other pixel like an old LED sign"""
    img, d = canvas(36)
    tmp = Image.new("L", (36, H), 0)
    td = ImageDraw.Draw(tmp)
    td.ellipse([5, 29, 31, 46], outline=255)
    for x in (11, 25):
        td.ellipse([x - 5, 25, x + 5, 35], outline=255)
    td.arc([10, 33, 26, 40], 20, 160, fill=255)
    td.line([3, 46, 33, 46], fill=255)
    px = img.load()
    for y in range(H):
        for x in range(36):
            if tmp.getpixel((x, y)) and (x + y) % 2 == 0:
                px[x, y] = G + (255,)
    for x in (11, 25):
        d.rectangle([x - 1, 29, x + 1, 31], fill=L)
    return outline(img)


def e_mesh():
    """E: 3D wireframe mesh, contour lines across the body like a scanned model"""
    img, d = canvas(36)
    body(d, [5, 29, 31, 46], G)
    for i, y in enumerate((33, 37, 41)):
        half = int(13 * math.sqrt(max(0, 1 - ((y - 37.5) / 8.5) ** 2)))
        d.arc([18 - half, y - 2, 18 + half, y + 2], 0, 180, fill=DG if i != 1 else G)
    d.line([18, 30, 18, 45], fill=DG)
    d.arc([8, 29, 28, 46], 270, 90, fill=DG)
    for x in (11, 25):
        d.ellipse([x - 5, 25, x + 5, 35], fill=K, outline=G)
        d.arc([x - 5, 27, x + 5, 33], 0, 180, fill=DG)
        d.rectangle([x - 1, 29, x + 1, 31], fill=WH)
    d.line([3, 46, 33, 46], fill=G)
    return outline(img)


def f_side_wire():
    """F (double): side-on sitting frog as a neon wireframe"""
    img, d = canvas(72)
    d.ellipse([10, 24, 50, 47], outline=DG, width=4)
    d.ellipse([10, 24, 50, 47], outline=L, width=2)
    d.ellipse([34, 18, 62, 40], fill=K, outline=L, width=2)
    d.ellipse([40, 12, 54, 26], fill=K, outline=L, width=2)
    d.rectangle([46, 17, 48, 20], fill=WH)
    d.line([46, 33, 61, 30], fill=L, width=1)
    d.arc([6, 32, 30, 48], 120, 300, fill=L, width=2)
    d.line([2, 48, 24, 48], fill=L, width=2)
    d.line([44, 40, 46, 48], fill=L, width=2)
    d.line([42, 48, 52, 48], fill=L, width=2)
    return outline(img)


def g_front_mesh():
    """G (double): big front wireframe mesh with HUD brackets around it"""
    img, d = canvas(72)
    d.ellipse([14, 22, 58, 49], outline=G, width=2)
    for y in (29, 35, 41, 46):
        half = int(21 * math.sqrt(max(0, 1 - ((y - 35.5) / 13.5) ** 2)))
        d.arc([36 - half, y - 3, 36 + half, y + 3], 0, 180, fill=DG)
    d.line([36, 23, 36, 48], fill=DG)
    d.arc([22, 22, 50, 49], 270, 90, fill=DG)
    d.arc([22, 22, 50, 49], 90, 270, fill=DG)
    for x in (25, 47):
        d.ellipse([x - 8, 12, x + 8, 28], fill=K, outline=G, width=2)
        d.rectangle([x - 2, 18, x + 2, 22], fill=WH)
    d.arc([26, 30, 46, 40], 20, 160, fill=L, width=2)
    for (x, y, sx, sy) in ((6, 8, 1, 1), (65, 8, -1, 1), (6, 50, 1, -1), (65, 50, -1, -1)):   # HUD brackets
        d.line([x, y, x + 5 * sx, y], fill=C)
        d.line([x, y, x, y + 5 * sy], fill=C)
    return outline(img)


STYLES = [("A  THIN - single clean line", a_thin()), ("B  NEON - bright 2 px tube with a dim glow", b_neon()),
          ("C  LOW-POLY - straight vector edges, cyan eyes", c_lowpoly()), ("D  DOT-MATRIX - LED-sign dots", d_dots()),
          ("E  MESH - 3D wireframe contour lines", e_mesh()),
          ("F  SIDE-ON NEON  (double)", f_side_wire()), ("G  FRONT MESH + HUD BRACKETS  (double)", g_front_mesh())]

if __name__ == "__main__":
    S = 4
    rowh = H * S + 60
    sheet = Image.new("RGB", (72 * S + 2 * 72 + 120, len(STYLES) * rowh + 20), (16, 16, 16))
    dd = ImageDraw.Draw(sheet)
    y = 10
    for title, img in STYLES:
        dd.text((20, y), title, fill=(230, 230, 230))
        big = Image.new("RGB", (img.width, H), (0, 0, 0))
        big.paste(img, (0, 0), img)
        sheet.paste(big.resize((img.width * S, H * S), Image.NEAREST), (20, y + 16))
        sheet.paste(big, (40 + 72 * S, y + 16))
        dd.text((40 + 72 * S, y + 18 + H), "actual size", fill=(140, 140, 140))
        sheet.paste(big.resize((img.width * 2, H * 2), Image.NEAREST), (40 + 72 * S, y + 36 + H))
        y += rowh
    sheet.save(sys.argv[1])
    print("ok", sheet.size)

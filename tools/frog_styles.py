#!/usr/bin/env python3
"""Six base-frog designs at full goggle resolution: four single-character (36x54), two double (72x54).

usage: frog_styles.py <out.png>
"""
import sys
from PIL import Image, ImageDraw

H = 54
G, D, L, BEL = (64, 214, 104), (30, 128, 62), (150, 255, 170), (120, 236, 150)
WH, K, R, Y, P, C = (240, 255, 240), (0, 0, 0), (255, 44, 44), (255, 220, 60), (255, 120, 170), (190, 255, 255)
GREY, DGREY = (150, 150, 160), (70, 70, 80)


def canvas(w):
    img = Image.new("RGBA", (w, H), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def outline(img, colour=K):
    w = img.width
    out = img.copy()
    src, dst = img.load(), out.load()
    for y in range(H):
        for x in range(w):
            if src[x, y][3]:
                continue
            if any(0 <= x + ex < w and 0 <= y + ey < H and src[x + ex, y + ey][3] and src[x + ex, y + ey][:3] != K
                   for ex in (-1, 0, 1) for ey in (-1, 0, 1)):
                dst[x, y] = colour + (255,)
    return out


def eye(d, x, y, r=5, pupil=1, look=0):
    d.ellipse([x - r, y - r, x + r, y + r], fill=G)
    d.ellipse([x - r + 2, y - r + 2, x + r - 2, y + r - 2], fill=WH)
    d.rectangle([x + look - pupil, y - pupil, x + look + pupil, y + pupil], fill=K)
    d.point((x + look + pupil, y - pupil - 1), fill=WH)


def classic():
    img, d = canvas(36)
    d.ellipse([3, 37, 13, 46], fill=D)
    d.ellipse([23, 37, 33, 46], fill=D)
    d.ellipse([5, 29, 31, 46], fill=G)
    d.ellipse([11, 38, 25, 45], fill=BEL)
    d.rectangle([11, 45, 15, 47], fill=G)
    d.rectangle([21, 45, 25, 47], fill=G)
    eye(d, 11, 30)
    eye(d, 25, 30)
    d.arc([9, 32, 27, 40], 20, 160, fill=K)
    return outline(img)


def kawaii():
    img, d = canvas(36)
    d.ellipse([2, 22, 34, 48], fill=G)                       # big round head-body
    d.ellipse([2, 40, 12, 49], fill=D)
    d.ellipse([24, 40, 34, 49], fill=D)
    for x in (10, 26):                                        # huge eyes
        d.ellipse([x - 8, 15, x + 8, 31], fill=G)
        d.ellipse([x - 6, 17, x + 6, 29], fill=WH)
        d.ellipse([x - 4, 19, x + 4, 28], fill=K)
        d.rectangle([x - 2, 20, x, 22], fill=WH)
        d.point((x + 2, 26), fill=WH)
    d.ellipse([4, 33, 9, 36], fill=P)                          # blush
    d.ellipse([27, 33, 32, 36], fill=P)
    d.arc([14, 31, 22, 37], 20, 160, fill=K)                  # tiny smile
    d.ellipse([12, 39, 24, 46], fill=BEL)
    return outline(img)


def eightbit():
    """chunky 3x3 blocks, two greens, NES-style"""
    art = ["..GG....GG..",
           ".GWWG..GWWG.",
           ".GWKG..GWKG.",
           "GGGGGGGGGGGG",
           "GDGGGGGGGGDG",
           "GGDDDDDDDDGG",
           "GGGLLLLLLGGG",
           ".GGLLLLLLGG.",
           "DD.GG..GG.DD",
           "DDD......DDD"]
    pal = {"G": G, "D": D, "L": BEL, "W": WH, "K": K}
    img, d = canvas(36)
    ox, oy, s = 0, 18, 3
    for y, row in enumerate(art):
        for x, ch in enumerate(row):
            if ch in pal:
                d.rectangle([ox + x * s, oy + y * s, ox + x * s + s - 1, oy + y * s + s - 1], fill=pal[ch])
    return outline(img)


def phosphor():
    """terminal wireframe: outline-only green with a dim inner glow, matches the DOS font"""
    img, d = canvas(36)
    d.ellipse([5, 29, 31, 46], outline=G)
    d.ellipse([6, 30, 30, 45], outline=(20, 70, 35))
    for x in (11, 25):
        d.ellipse([x - 5, 25, x + 5, 35], fill=K, outline=G)
        d.rectangle([x - 1, 29, x + 1, 31], fill=L)
    d.arc([9, 32, 27, 40], 20, 160, fill=G)
    d.line([3, 46, 13, 46], fill=G)
    d.line([23, 46, 33, 46], fill=G)
    d.line([8, 42, 4, 46], fill=G)
    d.line([28, 42, 32, 46], fill=G)
    for y in range(25, 47, 2):                                # faint scanlines
        for x in range(36):
            r, g, b, a = img.getpixel((x, y))
            if a and (r, g, b) == G:
                img.putpixel((x, y), L + (255,))
    return outline(img)


def side_profile():
    """double: a frog sitting side-on, facing right"""
    img, d = canvas(72)
    d.ellipse([10, 24, 50, 47], fill=G)                       # body
    d.ellipse([34, 18, 62, 40], fill=G)                       # head
    d.ellipse([40, 12, 54, 26], fill=G)                       # eye bump
    d.ellipse([43, 15, 51, 23], fill=WH)
    d.rectangle([47, 17, 49, 20], fill=K)
    d.line([46, 33, 61, 30], fill=K)                          # mouth line
    d.ellipse([36, 30, 52, 42], fill=BEL)                     # throat / belly
    d.ellipse([6, 32, 30, 48], fill=D)                        # big back leg
    d.polygon([(4, 46), (22, 46), (26, 49), (2, 49)], fill=G)  # back foot
    d.line([44, 40, 46, 48], fill=G, width=3)                 # front leg
    d.rectangle([43, 47, 51, 49], fill=G)
    for (x, y) in ((22, 30), (28, 37), (16, 36), (32, 27)):  # spots
        d.ellipse([x, y, x + 3, y + 2], fill=D)
    return outline(img)


def fpv_pilot():
    """double: front-facing frog wearing FPV goggles with an antenna, hands on sticks"""
    img, d = canvas(72)
    d.ellipse([12, 38, 26, 50], fill=D)
    d.ellipse([46, 38, 60, 50], fill=D)
    d.ellipse([14, 22, 58, 49], fill=G)                       # body
    d.ellipse([24, 34, 48, 47], fill=BEL)
    d.ellipse([16, 12, 32, 28], fill=G)                       # eye bumps
    d.ellipse([40, 12, 56, 28], fill=G)
    d.rounded_rectangle([14, 15, 58, 27], 4, fill=DGREY)      # goggles
    d.rounded_rectangle([17, 17, 34, 25], 2, fill=K)
    d.rounded_rectangle([38, 17, 55, 25], 2, fill=K)
    d.line([19, 18, 24, 18], fill=C)                          # lens glints
    d.line([40, 18, 45, 18], fill=C)
    d.rectangle([34, 19, 38, 23], fill=GREY)
    d.line([55, 15, 60, 3], fill=GREY, width=2)               # antenna
    d.ellipse([58, 0, 63, 5], fill=R)
    d.arc([28, 29, 44, 37], 20, 160, fill=K)                  # grin
    d.rounded_rectangle([20, 40, 52, 48], 3, fill=DGREY)      # radio in hands
    d.rectangle([25, 42, 28, 45], fill=GREY)
    d.rectangle([44, 42, 47, 45], fill=GREY)
    d.ellipse([16, 39, 23, 46], fill=G)                       # hands
    d.ellipse([49, 39, 56, 46], fill=G)
    return outline(img)


STYLES = [("1  CLASSIC  (single)", classic()), ("2  KAWAII - big eyes, blush  (single)", kawaii()),
          ("3  8-BIT - chunky blocks  (single)", eightbit()), ("4  PHOSPHOR - wireframe, matches the DOS font  (single)", phosphor()),
          ("5  SIDE-ON SITTING FROG  (double)", side_profile()), ("6  FPV PILOT - goggles, antenna, radio  (double)", fpv_pilot())]

if __name__ == "__main__":
    S = 4
    from PIL import ImageFont  # noqa: F401
    rowh = H * S + 60
    sheet = Image.new("RGB", (72 * S + 2 * 72 + 120, len(STYLES) * rowh + 20), (16, 16, 16))
    dd = ImageDraw.Draw(sheet)
    y = 10
    for title, img in STYLES:
        dd.text((20, y), title, fill=(230, 230, 230))
        big = Image.new("RGB", (img.width, H), (0, 0, 0))
        big.paste(img, (0, 0), img)
        sheet.paste(big.resize((img.width * S, H * S), Image.NEAREST), (20, y + 16))
        # actual size, twice: as it really is on the goggles (1:1), and 2x
        sheet.paste(big, (40 + 72 * S, y + 16))
        dd.text((40 + 72 * S, y + 18 + H), "actual size", fill=(140, 140, 140))
        sheet.paste(big.resize((img.width * 2, H * 2), Image.NEAREST), (40 + 72 * S, y + 36 + H))
        y += rowh
    sheet.save(sys.argv[1])
    print("ok", sheet.size)

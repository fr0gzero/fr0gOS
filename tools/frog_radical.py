#!/usr/bin/env python3
"""Twelve radical frog designs. Each: DOS-pixel rest pose, an alternate DOS pose, three frames of its own
full-resolution signature animation, and a squash. All the colours the goggle font can carry.

usage: frog_radical.py <out.png>
"""
import math
import os
import random
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_dos as FD  # noqa: E402
from frog_dos import W, H, dos, outline1, scatter  # noqa: E402
from frog_dos2 import rot, scale  # noqa: E402

COL = {"A": (255, 168, 0), "Y": (255, 220, 60), "B": (70, 130, 255), "C": (120, 255, 255), "P": (255, 120, 170),
       "S": (150, 150, 165), "N": (80, 80, 95), "V": (170, 90, 255), "O": (255, 120, 40)}
FD.PAL.update(COL)
FD.PAL["W"] = (240, 255, 240)
WHITE, BLACK = (240, 255, 240), (0, 0, 0)


def fx(src, fn):
    img = src.copy()
    fn(ImageDraw.Draw(img), img)
    return img


def recolour(src, fn):
    img = src.copy()
    px = img.load()
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if a and (r, g, b) != BLACK:
                px[x, y] = fn(x, y, (r, g, b)) + (255,)
    return img


def trail(src, n):
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for i in range(n, 0, -1):
        g = recolour(src, lambda x, y, c, i=i: tuple(int(v * (0.25 + 0.15 * (n - i))) for v in c))
        out.paste(g, (-3 * i, 0), g)
    out.paste(src, (0, 0), src)
    return out


def designs():
    D = []
    classic = [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"]
    blink = [".GG..GG.", "GKKGGKKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"]
    amber = [r.replace("G", "A") for r in classic]
    a = dos(amber)
    D.append(("1  AMBER TERMINAL  - amber phosphor frog; burns afterimage trails when it moves",
              [("rest", a), ("blink", dos([r.replace("G", "A") for r in blink])), ("trail 1", trail(a, 1)), ("trail 2", trail(a, 2)),
               ("trail 3", trail(a, 3)), ("squash", scale(a, 1.15, 0.8))]))

    face = ["GGG..GGG", "GWWGGWWG", "GWKGGWKG", "GWWGGWWG", "GGGGGGGG", "GGGGGGGG", "KGGGGGGK", "GKPPPPKG", ".GKKKKG.", "..GGGG.."]
    f = dos(face)
    D.append(("2  BIG FACE  - all head, huge eyes, pink tongue; zoom-pulses at full res",
              [("rest", f), ("tongue", dos(face[:-1] + ["..GPPG.."])), ("zoom 1", scale(f, 1.1, 1.1, False)),
               ("zoom 2", scale(f, 1.2, 1.2, False)), ("zoom 3", scale(f, 1.05, 1.05, False)), ("squash", scale(f, 1.15, 0.8))]))

    robot = ["...R....", "...S....", ".SSSSSS.", "SRRSSRRS", "SSSSSSSS", "SKSKSKSS", ".SSSSSS.", "SS.SS.SS"]
    r_ = dos(robot)
    def zap(d, img, k):
        rnd = random.Random(k)
        for _ in range(2):
            x, y = rnd.randint(2, 33), 10
            for _ in range(6):
                nx, ny = x + rnd.randint(-3, 3), y + rnd.randint(2, 5)
                d.line([x, y, nx, ny], fill=COL["C"])
                x, y = nx, ny
    D.append(("3  ROBOT  - steel body, red LED eyes, blinking antenna; zaps with cyan lightning",
              [("rest", r_), ("LEDs off", dos([robot[0].replace("R", "N")] + robot[1:3] + ["SNNSSNNS"] + robot[4:])),
               ("zap 1", fx(r_, lambda d, i: zap(d, i, 1))), ("zap 2", fx(r_, lambda d, i: zap(d, i, 2))), ("zap 3", fx(r_, lambda d, i: zap(d, i, 3))),
               ("squash", scale(r_, 1.15, 0.8))]))

    ninja = ["......RR", ".GG..GGR", "RRRRRRRR", "KWWKKWWK", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"]
    n = dos(ninja)
    def smoke(d, img, k):
        for (x, y, r) in ((8, 40, 4 + k * 2), (28, 38, 3 + k * 2), (18, 44, 5 + k)):
            d.ellipse([x - r, y - r, x + r, y + r], fill=COL["S"] if k < 3 else COL["N"])
    D.append(("4  NINJA  - black mask, red headband tails flutter; vanishes in a smoke bomb",
              [("rest", n), ("flutter", dos([".....RR."] + ninja[1:])), ("smoke 1", fx(n, lambda d, i: smoke(d, i, 1))),
               ("smoke 2", fx(n, lambda d, i: smoke(d, i, 2))), ("smoke 3", fx(Image.new("RGBA", (W, H)), lambda d, i: smoke(d, i, 3))),
               ("squash", scale(n, 1.15, 0.8))]))

    inv = ["..G..G..", ".GGGGGG.", "GGWGGWGG", "GGGGGGGG", "G.GKKG.G", "G.G..G.G", "..GG.GG."]
    iv = dos(inv)
    def laser(d, img, k):
        d.line([18, 20 - k * 6, 18, 6 - k * 6], fill=(255, 44, 44), width=2)
        if k == 3:
            for a_ in range(0, 360, 45):
                d.point((18 + int(4 * math.cos(math.radians(a_))), 4 + int(4 * math.sin(math.radians(a_)))), fill=COL["Y"])
    D.append(("5  SPACE INVADER  - arcade march (legs toggle); fires a red laser that bursts at the top",
              [("rest", iv), ("march", dos(inv[:5] + [".G....G.", "G......G"])), ("fire 1", fx(iv, lambda d, i: laser(d, i, 1))),
               ("fire 2", fx(iv, lambda d, i: laser(d, i, 2))), ("burst", fx(iv, lambda d, i: laser(d, i, 3))), ("squash", scale(iv, 1.15, 0.8))]))

    tad = ["..GGGG..", ".GGGGGG.", "GWKGGWKG", "GGGGGGGG", ".GKKKKG.", "..GGGG..", "...GG...", "....G...", "...G....", "....G..."]
    t_ = dos(tad[:6])
    def tail(d, img, ph):
        pts = [(18 + int(4 * math.sin(ph + y * 0.45)), 34 + y) for y in range(0, 16)]
        d.line(pts, fill=(64, 214, 104), width=3)
    D.append(("6  TADPOLE  - round baby frog; full-res tail swims in a smooth wave",
              [("rest", dos(tad)), ("wiggle", dos(tad[:7] + ["...G....", "....G...", "...G...."])),
               ("swim 1", outline1(fx(t_, lambda d, i: tail(d, i, 0)))), ("swim 2", outline1(fx(t_, lambda d, i: tail(d, i, 2)))),
               ("swim 3", outline1(fx(t_, lambda d, i: tail(d, i, 4)))), ("squash", scale(dos(tad), 1.15, 0.8))]))

    fpv = ["......R.", "......S.", "SSSSSSSS", "SKCSSKCS", "SSSSSSSS", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"]
    fp = dos(fpv)
    def waves(d, img, k):
        for r in range(2, 2 + 3 * k, 3):
            d.arc([27 - r, 6 - r, 27 + r, 6 + r], 200, 340, fill=COL["C"])
    D.append(("7  FPV PILOT  - goggles with cyan glints, antenna light; radio waves pulse out",
              [("rest", fp), ("light off", dos(["......S."] + fpv[1:])), ("tx 1", fx(fp, lambda d, i: waves(d, i, 1))),
               ("tx 2", fx(fp, lambda d, i: waves(d, i, 2))), ("tx 3", fx(fp, lambda d, i: waves(d, i, 3))), ("squash", scale(fp, 1.15, 0.8))]))

    wiz = ["...BB...", "..BBYB..", ".BBBBBB.", "BBBBBBBB"] + classic
    wz = dos(wiz)
    def magic(d, img, k):
        for j in range(8):
            a_ = j * 0.8 + k * 0.9
            r = 6 + j * 1.5
            d.point((18 + int(r * math.cos(a_)), 30 + int(r * 0.6 * math.sin(a_))), fill=COL["Y"] if j % 2 else COL["C"])
    D.append(("8  WIZARD  - blue hat with a twinkling star; casts a yellow/cyan spiral",
              [("rest", wz), ("twinkle", dos(["...BB...", "..BBWB.."] + wiz[2:])), ("spell 1", fx(wz, lambda d, i: magic(d, i, 1))),
               ("spell 2", fx(wz, lambda d, i: magic(d, i, 2))), ("spell 3", fx(wz, lambda d, i: magic(d, i, 3))), ("squash", scale(wz, 1.15, 0.8))]))

    king = ["Y..YY..Y", "YYYRRYYY", "YYYYYYYY"] + classic
    kg = dos(king)
    def glitter(d, img, k):
        rnd = random.Random(k * 7)
        for _ in range(10):
            d.point((rnd.randint(1, 34), rnd.randint(0, 20) + k * 8), fill=COL["Y"])
    D.append(("9  KING  - gold crown, red jewel that glints; gold glitter rains down",
              [("rest", kg), ("glint", dos(["Y..YY..Y", "YYYWRYYY"] + king[2:])), ("gold 1", fx(kg, lambda d, i: glitter(d, i, 1))),
               ("gold 2", fx(kg, lambda d, i: glitter(d, i, 2))), ("gold 3", fx(kg, lambda d, i: glitter(d, i, 3))), ("squash", scale(kg, 1.15, 0.8))]))

    c = dos(classic)
    rainbow = [(64, 214, 104), (255, 220, 60), (255, 168, 0), (255, 44, 44), (255, 120, 170), (170, 90, 255), (70, 130, 255), (120, 255, 255)]
    def hue(k):
        return recolour(c, lambda x, y, col: col if col == WHITE else rainbow[(x // 4 + y // 6 + k) % len(rainbow)])
    D.append(("10  RAINBOW  - colour bands sweep through it every frame (palette cycling)",
              [("rest", c), ("cycle 1", hue(1)), ("cycle 2", hue(3)), ("cycle 3", hue(5)), ("cycle 4", hue(7)), ("squash", scale(hue(2), 1.15, 0.8))]))

    holo = recolour(c, lambda x, y, col: WHITE if col == WHITE else (COL["C"] if y % 2 else (60, 160, 170)))
    def jitter(k):
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for y in range(0, H, 3):
            band = holo.crop((0, y, W, y + 3))
            out.paste(band, ((k * (y // 3)) % 5 - 2, y), band)
        return out
    D.append(("11  HOLOGRAM  - see-through cyan with scanlines; flickers and tears sideways",
              [("rest", holo), ("flicker", recolour(holo, lambda x, y, col: col if y % 4 else (20, 60, 70))), ("tear 1", jitter(1)),
               ("tear 2", jitter(2)), ("tear 3", jitter(3)), ("squash", scale(holo, 1.15, 0.8))]))

    dart = [".YY..YY.", "YWKYYWKY", "YYKYYKYY", "YKYYYYKY", "YYKKKKYY", ".YYKYYY.", "BB.BB.BB"]
    dt = dos(dart)
    def bubbles(d, img, k):
        for (x, y0, r) in ((6, 30, 2), (30, 26, 3), (14, 22, 2), (24, 34, 2)):
            y = y0 - k * 6
            d.ellipse([x - r, y - r, x + r, y + r], outline=COL["V"] if r > 2 else (64, 214, 104))
    D.append(("12  POISON DART  - yellow with black spots and blue legs; toxic bubbles rise off it",
              [("rest", dt), ("shimmer", dos([r.replace("K", "N") if i in (2, 3) else r for i, r in enumerate(dart)])),
               ("toxic 1", fx(dt, lambda d, i: bubbles(d, i, 1))), ("toxic 2", fx(dt, lambda d, i: bubbles(d, i, 2))),
               ("toxic 3", fx(dt, lambda d, i: bubbles(d, i, 3))), ("squash", scale(dt, 1.15, 0.8))]))
    return D


def sheet(out):
    D = designs()
    sc = 3
    cw = W * sc + 12
    rowh = H * sc + 40
    sh = Image.new("RGB", (6 * cw + 40, len(D) * rowh + 20), (16, 16, 16))
    d = ImageDraw.Draw(sh)
    y = 8
    for title, fr in D:
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

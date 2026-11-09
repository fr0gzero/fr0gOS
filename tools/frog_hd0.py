#!/usr/bin/env python3
"""fr0gOS mascot, Dax's take: a cocky DOOM-faced frog in HDZero-branded FPV box goggles, worn a bit wonky
(tilted goggles, one antenna, a cocked brow - not mirror-symmetrical). Fixed 2x2/3x3 block, animates in place.

usage: frog_hd0.py sheet <out.png> [cells=2]
       frog_hd0.py anim  <out.gif> [cells=2]
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_megadrive as M  # noqa: E402

MODE = sys.argv[1] if len(sys.argv) > 1 else "sheet"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/out.png"
CELLS = int(sys.argv[3]) if len(sys.argv) > 3 else 2
M.GW, M.GH = 18 * CELLS, 27 * CELLS
F = M.GW / 36.0


def R(*v):
    return [int(round(c * F)) for c in v]


def W(n):
    return max(1, int(round(n * F)))


def goggles(s):
    """chunky HDZero box goggles, tilted up-right, one gold antenna on the raised side"""
    # strap down the sides (left has a buckle, right is raised -> asymmetry)
    s.shape("D", lambda d: d.polygon(R(0, 15, 6, 13, 7, 21, 1, 23), fill=1))
    s.shape("S", lambda d: d.rectangle(R(2, 17, 5, 19), fill=1))                                   # left buckle
    s.shape("D", lambda d: d.polygon(R(30, 11, 36, 13, 35, 21, 29, 19), fill=1))                   # right strap
    # body (tilted box: higher on the right)
    s.shape("S", lambda d: d.polygon(R(4, 6, 32, 2, 33, 15, 5, 17), fill=1))
    s.shape("K", lambda d: d.polygon(R(6, 8, 30, 4, 31, 13, 7, 15), fill=1))                        # bezel
    s.shape("C", lambda d: d.polygon(R(8, 9, 28, 5, 29, 11, 9, 13), fill=1))                        # lens screen
    s.shape("E", lambda d: (d.line(R(11, 11, 15, 7), fill=1, width=W(1)), d.line(R(17, 11, 21, 7), fill=1, width=W(1))))  # glint stripes
    # HDZERO badge on the lower-left of the body
    s.shape("C", lambda d: d.rectangle(R(7, 15, 14, 17), fill=1))
    s.ink(lambda d: d.text(R(8, 15)[:2], "HD0", fill=1) if F >= 3 else d.rectangle(R(8, 16, 13, 16), fill=1))
    # one antenna, on the raised right
    s.shape("D", lambda d: d.line(R(30, 2, 31, -2), fill=1, width=W(1)))
    s.shape("Y", lambda d: d.ellipse(R(30, -4, 33, -1), fill=1))


def brow(s, box, raise_=0):
    s.ink(lambda d: d.line(R(box[0], box[1] + raise_, box[2], box[3] + raise_), fill=1, width=W(1.5)))


def eyeball(s, box, look, lid):
    x0, y0, x1, y1 = box
    if lid == "x":
        s.shape("E", lambda d: d.ellipse(R(x0, y0, x1, y1), fill=1))
        s.ink(lambda d: (d.line(R(x0 + 1, y0 + 1, x1 - 1, y1 - 1), fill=1, width=W(1)),
                         d.line(R(x0 + 1, y1 - 1, x1 - 1, y0 + 1), fill=1, width=W(1))))
        return
    if lid == "shut":
        s.ink(lambda d: d.arc(R(x0, y0, x1, y1 + 2), 200, 340, fill=1, width=W(1)))
        return
    if lid == "spiral":
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        s.shape("E", lambda d: d.ellipse(R(x0, y0, x1, y1), fill=1))
        s.ink(lambda d: (d.arc(R(cx - 2, cy - 2, cx + 2, cy + 2), 0, 300, fill=1, width=W(1)),
                         d.arc(R(cx - 3.2, cy - 3.2, cx + 3.2, cy + 3.2), 120, 360, fill=1, width=W(1))))
        return
    # open almond eye (slightly narrowed = attitude)
    s.shape("E", lambda d: d.ellipse(R(x0, y0, x1, y1), fill=1))
    if lid == "half":
        s.shape("G", lambda d: d.rectangle(R(x0 - 1, y0 - 1, x1 + 1, (y0 + y1) / 2), fill=1))
        s.ink(lambda d: d.line(R(x0, (y0 + y1) / 2, x1, (y0 + y1) / 2), fill=1, width=W(1)))
    lx, ly = look
    cx = (x0 + x1) / 2 + lx * 2.0
    cy = (y0 + y1) / 2 + 1 + ly * 1.5
    r = (x1 - x0) * 0.30
    s.ink(lambda d: d.ellipse(R(cx - r, cy - r, cx + r, cy + r), fill=1))
    s.shape("E", lambda d: d.rectangle(R(cx - r + 0.4, cy - r + 0.4, cx - r + 1.1, cy - r + 1.1), fill=1))


def mouth(s, kind):
    if kind == "smirk":
        s.ink(lambda d: d.line(R(11, 40, 20, 41), fill=1, width=W(1.3)))
        s.ink(lambda d: d.line(R(20, 41, 25, 38), fill=1, width=W(1.3)))          # one side curls up
    elif kind == "grin":
        s.ink(lambda d: d.chord(R(10, 33, 26, 45), 8, 172, fill=1))
        s.shape("E", lambda d: d.rectangle(R(12, 38, 24, 40), fill=1))
        s.ink(lambda d: [d.line(R(x, 38, x, 41), fill=1, width=W(1)) for x in (15, 18, 21)])
    elif kind == "yell":
        s.ink(lambda d: d.chord(R(11, 32, 25, 48), 0, 180, fill=1))
        s.shape("E", lambda d: d.rectangle(R(13, 37, 23, 39), fill=1))            # top teeth
        s.shape("R", lambda d: d.ellipse(R(15, 42, 21, 47), fill=1))             # tongue
    elif kind == "grit":
        s.shape("E", lambda d: d.rectangle(R(11, 39, 25, 44), fill=1))
        s.ink(lambda d: ([d.line(R(x, 39, x, 44), fill=1, width=W(1)) for x in (14, 18, 22)] + [d.rectangle(R(11, 39, 25, 44), outline=1, width=W(1))]))
    elif kind == "o":
        s.ink(lambda d: d.ellipse(R(15, 39, 21, 46), fill=1, width=W(1)))
        s.shape("R", lambda d: d.ellipse(R(16, 40, 20, 45), fill=1))
    elif kind == "frown":
        s.ink(lambda d: d.arc(R(12, 44, 24, 51), 185, 355, fill=1, width=W(1.3)))
    else:   # plain happy
        s.ink(lambda d: d.arc(R(10, 33, 26, 46), 20, 160, fill=1, width=W(1.3)))


POSES = {
    "idle":    dict(look=(0, 0), lid="open", br=0, mo="smirk"),
    "breath":  dict(look=(0, 0.6), lid="open", br=0, mo="smirk", dy=1),
    "glanceL": dict(look=(-1, 0), lid="open", br=0, mo="smirk"),
    "glanceR": dict(look=(1, 0), lid="open", br=0, mo="smirk"),
    "glanceU": dict(look=(0, -1), lid="open", br=-1, mo="smirk"),
    "glanceD": dict(look=(0, 1), lid="open", br=1, mo="plain"),
    "blink":   dict(look=(0, 0), lid="shut", br=0, mo="smirk"),
    "blinkH":  dict(look=(0, 0), lid="half", br=0, mo="smirk"),
    "grin":    dict(look=(0, 0), lid="open", br=0, mo="grin"),
    "yell":    dict(look=(0, 0), lid="wide", br=-1, mo="yell"),
    "whoa":    dict(look=(0, -1), lid="wide", br=-2, mo="o"),
    "dizzy":   dict(look=(0, 0), lid="spiral", br=0, mo="grin"),
    "pumped":  dict(look=(0, 0), lid="open", br=-1, mo="smirk"),
    "hurt":    dict(look=(0, 0), lid="open", br=2, mo="grit"),
    "ko":      dict(look=(0, 0), lid="x", br=0, mo="frown"),
    "stars":   dict(look=(0, 0), lid="half", br=0, mo="frown", stars=True),
    "flip":    dict(look=(0, -1), lid="wide", br=0, mo="yell", invert=True),
}
ORDER = ["idle", "glanceL", "glanceR", "blink", "grin", "yell", "hurt", "ko",
         "breath", "blinkH", "glanceU", "glanceD", "whoa", "dizzy", "pumped", "stars", "flip"]


def mascot(name):
    p = POSES[name]
    s = M.Sprite()
    dy = p.get("dy", 0)
    s.shape("G", lambda d: d.ellipse(R(2, 12 + dy, 34, 52 + dy), fill=1))
    s.shape("G", lambda d: (d.ellipse(R(0, 26 + dy, 11, 49 + dy), fill=1), d.ellipse(R(25, 26 + dy, 36, 49 + dy), fill=1)))
    goggles(s)
    wide = p["lid"] == "wide"
    lb = [6, 17 + dy, 15, 27 + dy] if not wide else [5, 16 + dy, 16, 28 + dy]
    rb = [21, 17 + dy, 30, 27 + dy] if not wide else [20, 16 + dy, 31, 28 + dy]
    # cocked brows (right sits higher -> asymmetry), angled for attitude
    brow(s, [6, 16 + dy, 15, 15 + dy], p["br"])
    brow(s, [21, 15 + dy, 30, 14 + dy], p["br"] - 1)
    lid = "open" if wide else p["lid"]
    eyeball(s, lb, p["look"], lid)
    eyeball(s, rb, p["look"], "shut" if name == "wink" else lid)
    mouth(s, p["mo"])
    s.shape("P", lambda d: (d.ellipse(R(3, 31 + dy, 8, 36 + dy), fill=1), d.ellipse(R(28, 31 + dy, 33, 36 + dy), fill=1)))
    img = s.render()
    if p.get("stars"):
        d = ImageDraw.Draw(img)
        for sx, sy in ((6, 6), (28, 4), (17, 1)):
            d.text((int(sx * F * M.PX), int(sy * F * M.PX)), "*", fill=(255, 212, 0, 255))
    if p.get("invert"):
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    return img


if MODE == "anim":
    fr = {n: mascot(n) for n in ORDER}
    w, h = fr["idle"].size
    seq = [("idle", 1500), ("blink", 120), ("idle", 1400), ("glanceL", 480), ("idle", 260), ("glanceR", 480),
           ("idle", 900), ("blinkH", 70), ("blink", 110), ("idle", 1200), ("grin", 650), ("idle", 700),
           ("yell", 650), ("idle", 1100), ("whoa", 500), ("idle", 900), ("dizzy", 900), ("idle", 1200),
           ("hurt", 700), ("ko", 1100), ("stars", 900), ("blink", 150), ("idle", 1400)]
    PADX, PADY = 18, 14
    WW, HH = w + PADX * 2, h + PADY + 34
    frames, durs = [], []
    try:
        nf = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 20)
    except Exception:
        nf = None
    for name, ms in seq:
        cv = Image.new("RGB", (WW, HH), (0, 0, 0))
        cv.paste(fr[name], (PADX, PADY), fr[name])
        dd = ImageDraw.Draw(cv)
        dd.rectangle([PADX, PADY + h + 4, PADX + 64, PADY + h + 24], fill=(22, 54, 201))
        dd.text((PADX + 6, PADY + h + 5), "MK42", fill=(255, 212, 0), font=nf)
        frames.append(cv)
        durs.append(ms)
    frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)
    print("anim", OUT, WW, HH)
else:
    cells = [mascot(n) for n in ORDER]
    big = cells[0].width * (3 if CELLS == 2 else 2)
    cols, pad, gap = 6, 18, 20
    cw = big + gap
    chh = big + cells[0].height + 30
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGB", (pad * 2 + cols * cw - gap, pad * 2 + 26 + rows * chh), (18, 20, 24))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 22)
        small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 15)
    except Exception:
        font = small = None
    d.text((pad, pad - 4), "fr0gOS mascot - HD0 goggles, DOOM attitude, animates in place", fill=(200, 230, 210), font=font)
    for i, (c, name) in enumerate(zip(cells, ORDER)):
        cx = pad + (i % cols) * cw
        cy = pad + 26 + (i // cols) * chh
        sheet.paste(c.resize((big, big), Image.NEAREST), (cx, cy))
        sheet.paste(c, (cx, cy + big + 4))
        d.text((cx + c.width + 6, cy + big + 4 + c.height // 2 - 6), name, fill=(150, 200, 170), font=small)
    sheet.save(OUT)
    print("sheet", OUT, cells[0].size)

#!/usr/bin/env python3
"""fr0gOS frog at full goggle resolution (FHD font cell 36x54), built from parts so every frame
matches. Crisp pixel drawing (no anti-aliasing) plus a 1-pixel black outline, like the font.

usage: frog_hd.py sheet <out.png>
"""
import sys
from PIL import Image, ImageDraw

W, H = 36, 54
G = (64, 214, 104)
D = (30, 128, 62)
L = (150, 255, 170)
BEL = (120, 236, 150)
WH = (240, 255, 240)
K = (0, 0, 0)
R = (255, 44, 44)
Y = (255, 220, 60)
P = (255, 120, 170)
C = (190, 255, 255)
TRANS = (127, 127, 127)


def frog(dy=0, dx=0, squash=0.0, eyes="open", look=0, mouth="smile", throat=0.0, arms=None, legs="sit",
         extras=(), flip=False, tint=None, scan=False, flash=None):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = 18 + dx
    base = 47 + dy                                   # feet line
    bh = int(18 * (1 - 0.35 * squash))               # body height
    bw = int(13 + 3 * squash)                        # body half-width
    top = base - bh
    # back legs (haunches) and feet
    if legs == "sit":
        d.ellipse([cx - bw - 1, base - 9, cx - bw + 9, base], fill=D)
        d.ellipse([cx + bw - 9, base - 9, cx + bw + 1, base], fill=D)
        d.rectangle([cx - bw - 2, base - 1, cx - bw + 5, base], fill=G)
        d.rectangle([cx + bw - 5, base - 1, cx + bw + 2, base], fill=G)
    elif legs == "jump":
        d.line([cx - 8, base - 4, cx - 12, base + 4], fill=D, width=3)
        d.line([cx + 8, base - 4, cx + 12, base + 4], fill=D, width=3)
        d.rectangle([cx - 15, base + 3, cx - 10, base + 5], fill=G)
        d.rectangle([cx + 10, base + 3, cx + 15, base + 5], fill=G)
    elif legs == "kick":
        d.line([cx - 8, base - 4, cx - 15, base + 2], fill=D, width=3)
        d.line([cx + 8, base - 4, cx + 11, base + 5], fill=D, width=3)
    elif legs.startswith("dance"):
        s = -1 if legs == "dance1" else 1
        d.ellipse([cx - bw - 1 + 3 * s, base - 9, cx - bw + 9 + 3 * s, base], fill=D)
        d.ellipse([cx + bw - 9 + 3 * s, base - 9, cx + bw + 1 + 3 * s, base], fill=D)
        d.rectangle([cx - bw - 2 + 4 * s, base - 1, cx - bw + 5 + 4 * s, base], fill=G)
        d.rectangle([cx + bw - 5 + 4 * s, base - 1, cx + bw + 2 + 4 * s, base], fill=G)
    # body
    d.ellipse([cx - bw, top, cx + bw, base - 1], fill=G)
    # belly
    d.ellipse([cx - 7, top + bh // 2, cx + 7, base - 2], fill=BEL)
    # front feet
    d.rectangle([cx - 7, base - 2, cx - 3, base], fill=G)
    d.rectangle([cx + 3, base - 2, cx + 7, base], fill=G)
    # eyes (bulging on top of the head)
    ey = top + 1
    for side in (-1, 1):
        ex = cx + side * 7
        d.ellipse([ex - 5, ey - 5, ex + 5, ey + 5], fill=G)
        if eyes == "shades":
            continue
        closed = eyes == "closed" or eyes == "sleepy" or (eyes == "wink" and side == -1)
        if closed:
            d.line([ex - 3, ey + 1, ex + 3, ey + 1], fill=K, width=1)
            if eyes == "sleepy":
                d.line([ex - 3, ey, ex + 3, ey], fill=D, width=1)
        elif eyes == "star":
            d.polygon([(ex, ey - 4), (ex + 1, ey - 1), (ex + 4, ey - 1), (ex + 2, ey + 1), (ex + 3, ey + 4),
                       (ex, ey + 2), (ex - 3, ey + 4), (ex - 2, ey + 1), (ex - 4, ey - 1), (ex - 1, ey - 1)], fill=Y)
        else:
            d.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=WH)
            px = ex + look
            d.rectangle([px - 1, ey - 1, px + 1, ey + 1], fill=K)
            d.point((px + 1, ey - 2), fill=WH)
    if eyes == "shades":
        d.rectangle([cx - 13, ey - 3, cx + 13, ey - 2], fill=K)
        d.rectangle([cx - 12, ey - 2, cx - 3, ey + 3], fill=K)
        d.rectangle([cx + 3, ey - 2, cx + 12, ey + 3], fill=K)
        d.point((cx - 10, ey - 1), fill=WH)
        d.point((cx + 5, ey - 1), fill=WH)
    # throat balloon
    if throat > 0:
        r = int(2 + 7 * throat)
        my = top + bh // 2 + 3
        d.ellipse([cx - r - 1, my - r // 2, cx + r + 1, my + r], fill=L)
        d.ellipse([cx - r + 2, my - r // 2 + 2, cx - r + 4, my - r // 2 + 3], fill=WH)
    # mouth
    my = top + bh // 2
    if mouth == "smile":
        d.arc([cx - 9, my - 6, cx + 9, my + 2], 20, 160, fill=K)
    elif mouth == "big":
        d.chord([cx - 9, my - 4, cx + 9, my + 5], 0, 180, fill=K)
        d.chord([cx - 6, my + 1, cx + 6, my + 5], 0, 180, fill=P)
    elif mouth == "open":
        d.ellipse([cx - 5, my - 1, cx + 5, my + 5], fill=K)
        d.ellipse([cx - 3, my + 2, cx + 3, my + 5], fill=P)
    elif mouth == "line":
        d.line([cx - 7, my, cx + 7, my], fill=K)
    elif mouth == "worried":
        d.arc([cx - 7, my, cx + 7, my + 7], 200, 340, fill=K)
    elif mouth == "tongue":
        d.line([cx - 7, my, cx + 7, my], fill=K)
    # arms
    if arms == "up":
        for side in (-1, 1):
            d.line([cx + side * (bw - 2), top + 8, cx + side * (bw + 3), top - 4], fill=G, width=3)
            d.rectangle([cx + side * (bw + 3) - 2, top - 7, cx + side * (bw + 3) + 2, top - 4], fill=G)
    elif arms in ("wave1", "wave2"):
        d.line([cx - bw + 2, top + 10, cx - bw - 1, top + 16], fill=G, width=3)
        tip = (cx + bw + 4, top - 5) if arms == "wave1" else (cx + bw + 7, top + 1)
        d.line([cx + bw - 2, top + 9, tip[0], tip[1]], fill=G, width=3)
        d.rectangle([tip[0] - 2, tip[1] - 2, tip[0] + 2, tip[1] + 2], fill=G)
    elif arms == "heart":
        hy = top + bh // 2 + 2
        d.line([cx - bw + 2, top + 10, cx - 5, hy + 2], fill=G, width=3)
        d.line([cx + bw - 2, top + 10, cx + 5, hy + 2], fill=G, width=3)
    # extras
    for e in extras:
        if e == "!":
            d.rectangle([cx - 2, top - 20, cx + 1, top - 11], fill=R)
            d.rectangle([cx - 2, top - 8, cx + 1, top - 6], fill=R)
        elif e == "heart":
            hy = top + bh // 2
            d.ellipse([cx - 7, hy - 2, cx, hy + 5], fill=R)
            d.ellipse([cx - 1, hy - 2, cx + 6, hy + 5], fill=R)
            d.polygon([(cx - 7, hy + 3), (cx + 6, hy + 3), (cx - 1, hy + 10)], fill=R)
            d.point((cx - 5, hy), fill=WH)
        elif e in ("zzz1", "zzz2"):
            for i, (zx, zy, s) in enumerate([(cx + 8, top - 10, 3), (cx + 12, top - 17, 4), (cx + 4, top - 24, 5)]):
                if e == "zzz1" and i == 2:
                    continue
                if e == "zzz2" and i == 0:
                    continue
                d.line([zx, zy, zx + s, zy], fill=L)
                d.line([zx + s, zy, zx, zy + s], fill=L)
                d.line([zx, zy + s, zx + s, zy + s], fill=L)
        elif e == "fly":
            d.rectangle([cx + 12, top - 14, cx + 13, top - 13], fill=K)
            d.point((cx + 11, top - 15), fill=WH)
            d.point((cx + 14, top - 15), fill=WH)
        elif e == "tongue":
            my = top + bh // 2
            d.line([cx + 1, my, cx + 12, top - 13], fill=P, width=2)
            d.ellipse([cx + 10, top - 16, cx + 14, top - 12], fill=P)
        elif e == "notes":
            for (nx, ny) in ((cx - 15, top - 6), (cx + 12, top - 12)):
                d.ellipse([nx, ny + 4, nx + 3, ny + 7], fill=Y)
                d.line([nx + 3, ny, nx + 3, ny + 5], fill=Y)
        elif e == "ribbit":
            for s in (-1, 1):
                for r in (3, 6):
                    d.arc([cx + s * (bw + 1) - r, top + 6 - r, cx + s * (bw + 1) + r, top + 6 + r],
                          -50 if s > 0 else 130, 50 if s > 0 else 230, fill=L)
        elif e == "sparkle":
            for (sx, sy, col) in ((cx - 15, top - 6, R), (cx + 14, top - 3, C), (cx - 10, base + 2, C), (cx + 12, base, R)):
                d.line([sx - 2, sy, sx + 2, sy], fill=col)
                d.line([sx, sy - 2, sx, sy + 2], fill=col)
    if flip:
        img = img.rotate(180)
    px = img.load()
    if tint or scan:
        for y in range(H):
            for x in range(W):
                r_, g_, b_, a = px[x, y]
                if not a:
                    continue
                if scan and y % 2:
                    px[x, y] = (0, 0, 0, 0)
                elif tint:
                    lum = (r_ + g_ + b_) / 3
                    px[x, y] = tint if lum > 60 else (0, 0, 0, 0) if tint == C else (40, 90, 90, 255)
    return outline(img, flash)


def outline(img, colour=None):
    """1-pixel outline around everything drawn (black, or a flash colour)"""
    colour = colour or K
    out = img.copy()
    src, dst = img.load(), out.load()
    for y in range(H):
        for x in range(W):
            if src[x, y][3]:
                continue
            if any(0 <= x + ex < W and 0 <= y + ey < H and src[x + ex, y + ey][3] and src[x + ex, y + ey][:3] != K
                   for ex in (-1, 0, 1) for ey in (-1, 0, 1)):
                dst[x, y] = colour + (255,)
    return out


def blank():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def spark():
    img = blank()
    d = ImageDraw.Draw(img)
    for (x, y, c) in ((18, 30, R), (14, 26, C), (23, 34, R), (12, 35, C), (25, 24, R), (18, 40, C)):
        d.line([x - 1, y, x + 1, y], fill=c)
        d.line([x, y - 1, x, y + 1], fill=c)
    d.rectangle([17, 29, 19, 31], fill=WH)
    return outline(img)


def beam(rings=False):
    img = blank()
    d = ImageDraw.Draw(img)
    for y in range(4, 50):
        d.line([16, y, 20, y], fill=R if (y // 2) % 2 else C)
    if rings:
        for ry in (14, 28, 42):
            d.ellipse([7, ry - 2, 29, ry + 2], outline=R)
            d.ellipse([10, ry - 1, 26, ry + 1], outline=C)
    return outline(img)


def frames():
    f = {}
    f["idle"] = frog()
    f["blink"] = frog(eyes="closed")
    f["look left"] = frog(look=-2)
    f["look right"] = frog(look=2)
    # croak
    f["croak 1"] = frog(throat=0.3, mouth="line")
    f["croak 2"] = frog(throat=0.6, mouth="line")
    f["croak 3"] = frog(throat=1.0, mouth="line")
    f["ribbit!"] = frog(mouth="open", extras=("ribbit",))
    # g-force
    f["squash"] = frog(squash=1.0, mouth="worried")
    # flip
    f["flip"] = frog(flip=True)
    f["flip look L"] = frog(flip=True, look=2)
    f["flip look R"] = frog(flip=True, look=-2)
    f["flip kick"] = frog(flip=True, legs="kick", mouth="open")
    # low battery
    f["low crouch"] = frog(arms="up", mouth="worried", extras=("!",), dy=0, squash=0.2)
    f["low jump"] = frog(arms="up", mouth="open", extras=("!",), dy=-6, legs="jump")
    f["low fall"] = frog(arms="up", mouth="open", extras=("!",), dy=-3, legs="jump")
    f["low land"] = frog(arms="up", mouth="worried", squash=0.5)
    # teleport
    f["tp spark"] = spark()
    f["tp beam"] = beam()
    f["tp rings"] = beam(rings=True)
    f["tp scanlines"] = frog(scan=True, tint=L)
    f["tp hologram"] = frog(tint=C)
    f["tp red flash"] = frog(flash=R, extras=("sparkle",))
    # cute extras
    f["heart"] = frog(arms="heart", extras=("heart",), mouth="smile")
    f["wink"] = frog(eyes="wink", mouth="big")
    f["big smile"] = frog(mouth="big")
    f["wave 1"] = frog(arms="wave1", mouth="big")
    f["wave 2"] = frog(arms="wave2", mouth="big")
    f["sleepy 1"] = frog(eyes="sleepy", mouth="line", extras=("zzz1",))
    f["sleepy 2"] = frog(eyes="sleepy", mouth="line", extras=("zzz2",))
    f["shades"] = frog(eyes="shades", mouth="smile")
    f["star eyes"] = frog(eyes="star", mouth="big")
    f["fly spotted"] = frog(look=2, extras=("fly",))
    f["tongue!"] = frog(look=2, mouth="tongue", extras=("tongue",))
    f["gulp"] = frog(eyes="closed", throat=0.4, mouth="line")
    f["dance 1"] = frog(dx=-2, legs="dance1", mouth="big", extras=("notes",))
    f["dance 2"] = frog(dx=2, legs="dance2", mouth="big", extras=("notes",))
    return f


GROUPS = [
    ("BASICS", ["idle", "blink", "look left", "look right", "squash"]),
    ("CROAK  (loops while a warning is up)", ["croak 1", "croak 2", "croak 3", "ribbit!"]),
    ("FLIP  (holds 1 s+, looks around, kicks)", ["flip", "flip look L", "flip look R", "flip kick"]),
    ("LOW BATTERY  (by the voltage, jumping at it)", ["low crouch", "low jump", "low fall", "low land"]),
    ("TELEPORT IN  (red + cyan; leaving plays backwards)", ["tp spark", "tp beam", "tp rings", "tp scanlines", "tp hologram", "tp red flash", "idle"]),
    ("CUTE 1", ["heart", "wink", "big smile", "wave 1", "wave 2", "shades", "star eyes"]),
    ("CUTE 2", ["sleepy 1", "sleepy 2", "fly spotted", "tongue!", "gulp", "dance 1", "dance 2"]),
]

if __name__ == "__main__":
    from PIL import ImageDraw as _D
    out = sys.argv[2]
    fr = frames()
    S = 4
    CW = W * S + 30
    sheet = Image.new("RGB", (7 * CW + 40, len(GROUPS) * (H * S + 50) + 20), (16, 16, 16))
    dd = _D.Draw(sheet)
    y = 10
    for title, names in GROUPS:
        dd.text((20, y), title, fill=(230, 230, 230))
        for i, n in enumerate(names):
            cell = Image.new("RGB", (W, H), (0, 0, 0))
            cell.paste(fr[n], (0, 0), fr[n])
            sheet.paste(cell.resize((W * S, H * S), Image.NEAREST), (20 + i * CW, y + 16))
            dd.text((20 + i * CW, y + 18 + H * S), n, fill=(160, 160, 160))
        y += H * S + 50
    sheet.save(out)
    print("ok", sheet.size, len(fr), "frames")

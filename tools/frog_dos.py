#!/usr/bin/env python3
"""DOS frog: at rest it's drawn in the same chunky pixels as the DOS font (8x16 grid, 3x3 blocks on the
FHD font, black outline), so it reads as part of the text. While it moves it cheats and uses the full
36x54 resolution: pixels scatter and converge, it rotates smoothly, its throat inflates. Then it settles
back into DOS pixels.

usage: frog_dos.py <out.png>
"""
import math
import os
import random
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

W, H = 36, 54
GREEN, LIGHT, DARK = (64, 214, 104), (150, 255, 170), (30, 128, 62)
WHITE, BLACK, RED, CYAN = (236, 255, 236), (0, 0, 0), (255, 44, 44), (190, 255, 255)
PAL = {"G": GREEN, "L": LIGHT, "D": DARK, "W": WHITE, "K": BLACK, "R": RED}
K_FHD = 3                    # the DOS text is VGA 8x16 drawn in 3x3 blocks on the FHD font

# ---- DOS-pixel rest poses (8 wide, same grid as the font letters) ----
REST = {
    "idle":  [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"],
    "blink": [".GG..GG.", "GKKGGKKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"],
    "look L": [".GG..GG.", "WKGGWKGG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"],
    "look R": [".GG..GG.", "GGWKGGWK", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"],
    "flipped": ["GG.GG.GG", ".GGGGGG.", "GGKKKKGG", "GKGGGGKG", "GGGGGGGG", "GWKGGWKG", ".GG..GG."],
    "flip look": ["GG.GG.GG", ".GGGGGG.", "GGKKKKGG", "GKGGGGKG", "GGGGGGGG", "WKGGWKGG", ".GG..GG."],
    "arms up": ["G......G", "G.G..G.G", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKRRKGG", ".GGGGGG.", "GG.GG.GG"],
    "croak": [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKLLLLKG", "GLLLLLLG", ".GLLLLG.", "GG.GG.GG"],
}


def dos(rows, top=None):
    """8x16 grid -> 36x54 cell, 1-cell black outline, 3x3 blocks: exactly how the font draws letters"""
    rows = [r.ljust(8, ".") for r in rows]
    pad = (16 - len(rows)) // 2 if top is None else top
    grid = [[None] * 8 for _ in range(16)]
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if 0 <= y + pad < 16:
                grid[y + pad][x] = PAL.get(ch)
    GWc, GHc = 10, 18
    big = [[None] * GWc for _ in range(GHc)]
    for y in range(16):
        for x in range(8):
            big[y + 1][x + 1] = grid[y][x]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = img.load()
    ox, oy = (W - GWc * K_FHD) // 2, (H - GHc * K_FHD) // 2
    for y in range(GHc):
        for x in range(GWc):
            c = big[y][x]
            if c is None and any(0 <= y + dy < GHc and 0 <= x + dx < GWc and big[y + dy][x + dx] not in (None, BLACK)
                                 for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                c = BLACK
            if c is not None:
                for yy in range(K_FHD):
                    for xx in range(K_FHD):
                        px[ox + x * K_FHD + xx, oy + y * K_FHD + yy] = c + (255,)
    return img


def outline1(img):
    out = img.copy()
    src, dst = img.load(), out.load()
    for y in range(H):
        for x in range(W):
            if src[x, y][3]:
                continue
            if any(0 <= x + ex < W and 0 <= y + ey < H and src[x + ex, y + ey][3] and src[x + ex, y + ey][:3] != BLACK
                   for ex in (-1, 0, 1) for ey in (-1, 0, 1)):
                dst[x, y] = BLACK + (255,)
    return out


# ---- hi-res motion: built from the DOS frog's own pixels ----
def scatter(src, t, seed=1, tint=None):
    """pixels fly out from the centre (t 0..1), with jitter; tint fades them toward a colour"""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    s = src.load()
    d = img.load()
    cx, cy = W / 2, H * 0.62
    for y in range(H):
        for x in range(W):
            r, g, b, a = s[x, y]
            if not a or (r, g, b) == BLACK:
                continue
            ang = math.atan2(y - cy, x - cx) + rnd.uniform(-0.6, 0.6)
            dist = t * rnd.uniform(6, 22)
            nx, ny = int(x + math.cos(ang) * dist), int(y + math.sin(ang) * dist - t * 6)
            if 0 <= nx < W and 0 <= ny < H and rnd.random() > t * 0.55:
                col = (r, g, b)
                if tint:
                    col = tuple(int(c + (tc - c) * t) for c, tc in zip(col, tint))
                d[nx, ny] = col + (255,)
    return img


def rotate(src, deg):
    """rotate the DOS frog around its body centre at full resolution"""
    big = Image.new("RGBA", (W * 2, H * 2), (0, 0, 0, 0))
    big.paste(src, (W // 2, H // 2), src)
    r = big.rotate(deg, resample=Image.NEAREST, center=(W, H))           # pivot = the middle of the cell
    return r.crop((W // 2, H // 2, W // 2 + W, H // 2 + H))


def shift(src, dy):
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(src, (0, dy), src)
    return out


def throat(src, r, ribbit=False):
    img = src.copy()
    d = ImageDraw.Draw(img)
    cx, cy = 18, 39
    d.ellipse([cx - r, cy - r // 2, cx + r, cy + r], fill=LIGHT)
    d.point((cx - r + 2, cy - r // 2 + 2), fill=WHITE)
    if ribbit:
        for s in (-1, 1):
            for rr in (4, 8):
                d.arc([cx + s * 15 - rr, 28 - rr, cx + s * 15 + rr, 28 + rr], -50 if s > 0 else 130, 50 if s > 0 else 230, fill=LIGHT)
    return outline1(img)


def beam(src, t):
    """a thin scan beam sweeps down the frog, drawing it in (arrival)"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    yline = int(10 + t * 40)
    s = src.load()
    d = img.load()
    for y in range(H):
        for x in range(W):
            if s[x, y][3] and y < yline:
                d[x, y] = s[x, y]
    dr = ImageDraw.Draw(img)
    dr.line([0, yline, W - 1, yline], fill=CYAN)
    dr.line([0, yline + 1, W - 1, yline + 1], fill=RED)
    return img


def sheet(out):
    idle = dos(REST["idle"])
    rows = [
        ("AT REST: DOS PIXELS  (same 3x3 blocks as the text)", [("idle", idle), ("blink", dos(REST["blink"])),
                                                                ("look L", dos(REST["look L"])), ("look R", dos(REST["look R"]))]),
        ("TELEPORT OUT: hi-res, its own pixels scatter and fade red", [("rest", idle)] +
         [(f"{int(t * 100)}%", scatter(idle, t, tint=RED)) for t in (0.2, 0.45, 0.7, 0.95)]),
        ("TELEPORT IN: pixels converge, a scan beam draws it in, settles to DOS", [(f"converge {int((1 - t) * 100)}%", scatter(idle, t, seed=3, tint=CYAN)) for t in (0.8, 0.5, 0.25)] +
         [("beam", beam(idle, 0.4)), ("beam", beam(idle, 0.8)), ("rest", idle)]),
        ("FLIP: smooth hi-res rotation, then rests flipped in DOS pixels and looks around", [("0", idle), ("45", rotate(idle, -45)), ("90", rotate(idle, -90)),
                                                                                           ("135", rotate(idle, -135)), ("flipped", dos(REST["flipped"])), ("looks", dos(REST["flip look"]))]),
        ("CROAK: hi-res throat inflates smoothly, ribbit, back to DOS", [("rest", idle), ("swell", throat(idle, 4)), ("bigger", throat(idle, 7)),
                                                                        ("balloon", throat(idle, 10)), ("ribbit!", throat(idle, 6, True)), ("rest", idle)]),
        ("LOW BATTERY: hi-res jump arc, rests in DOS with arms up and a red bar", [("rest", dos(REST["arms up"])),
                                                                                  ("up", shift(dos(REST["arms up"]), -4)), ("top", shift(dos(REST["arms up"]), -9)),
                                                                                  ("down", shift(dos(REST["arms up"]), -4)), ("land", dos(REST["arms up"]))]),
    ]
    S = 4
    CW = W * S + 26
    rowh = H * S + 50
    sh = Image.new("RGB", (6 * CW + 40, len(rows) * rowh + 140), (16, 16, 16))
    d = ImageDraw.Draw(sh)
    # how it sits next to real DOS text, at actual size and 4x
    font = Image.open(os.path.join(os.path.dirname(__file__), "..", "fonts", "hdzero-hacker", "BTFL_FHD_000.bmp")).convert("RGB")
    fgw, fgh = font.width // 16, font.height // 32
    strip = Image.new("RGB", (fgw * 7, fgh), (0, 0, 0))
    for i, ch in enumerate("MK4-2 "):
        c = ord(ch)
        g = font.crop(((c % 16) * fgw, (c // 16) * fgh, (c % 16 + 1) * fgw, (c // 16 + 1) * fgh))
        g = Image.eval(g, lambda v: v)
        gp = g.load()
        for yy in range(fgh):
            for xx in range(fgw):
                if gp[xx, yy] != (127, 127, 127):
                    strip.putpixel((i * fgw + xx, yy), gp[xx, yy])
    strip.paste(idle, (fgw * 6, 0), idle)
    d.text((20, 10), "Next to the real DOS text (actual size, then 2x)", fill=(230, 230, 230))
    sh.paste(strip, (20, 28))
    sh.paste(strip.resize((strip.width * 2, strip.height * 2), Image.NEAREST), (40 + strip.width, 28))
    y = 140
    for title, frames in rows:
        d.text((20, y), title, fill=(230, 230, 230))
        for i, (lab, im) in enumerate(frames):
            cell = Image.new("RGB", (W, H), (0, 0, 0))
            cell.paste(im, (0, 0), im)
            sh.paste(cell.resize((W * S, H * S), Image.NEAREST), (20 + i * CW, y + 16))
            d.text((20 + i * CW, y + 18 + H * S), lab, fill=(160, 160, 160))
        y += rowh
    sh.save(out)
    print("ok", sh.size)


if __name__ == "__main__":
    sheet(sys.argv[1])

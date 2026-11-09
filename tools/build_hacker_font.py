#!/usr/bin/env python3
"""fr0gOS hacker font for HDZero goggles.

Builds BTFL_000.bmp (24x36 glyphs) and BTFL_FHD_000.bmp (36x54 glyphs) plus
the firmware charmap header, from:
  - the stock HDZero Betaflight fonts (symbols fr0gOS keeps, recoloured green)
  - the Oldschool PC "IBM VGA 8x16" bitmaps (CC BY-SA 4.0, VileR, int10h.org),
    as packaged by susam/pcface

HDZero forces a single 256-glyph bank for Betaflight, so colour is done by
giving each colour its own copy of the alphabet inside that bank:
  0x20-0x5F  ASCII, phosphor green
  0xD0-0xF8  amber alphabet
  0xFC-0xFF  cursor, scramble blocks x3
  scattered  red alphabet, in symbol slots fr0gOS never draws
  0x11-0x15  battery bar 0..4
  frog       80 glyphs (old boot logo 0xA0-0xCF and unused GPS / AH / compass symbols), see frog_glyphs.py

usage: build_hacker_font.py <pcface fontmap.js> <stock BTFL_000.bmp> <stock BTFL_FHD_000.bmp> <out dir> <charmap.h> <frog_anim.h>
"""
import os
import re
import sys
from PIL import Image, ImageDraw

FONTMAP, STOCK_HD, STOCK_FHD, OUT_DIR, HEADER, ANIM_HEADER = sys.argv[1:7]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_glyphs  # noqa: E402

TRANS = (127, 127, 127)
BLACK = (0, 0, 0)
# palette: FROG_PALETTE=dos (default, phosphor green) or mega (16-bit: white text, gold, red)
_PAL = os.environ.get("FROG_PALETTE", "dos").lower()
if _PAL == "mega":
    GREEN = (255, 255, 255)     # 16-bit primary: clean white text with a black outline
    DKGREEN = (96, 104, 168)    # scramble noise: dim blue-grey
    AMBER = (255, 212, 0)       # warning: Mega Drive gold (#ffd400)
    RED = (255, 59, 59)         # critical (#ff3b3b)
else:
    GREEN = (64, 214, 104)      # calm phosphor
    DKGREEN = (30, 128, 62)     # scramble noise
    AMBER = (255, 168, 0)
    RED = (255, 44, 44)
EYE = (236, 255, 236)

COLOUR_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-!%:"
AMBER_BASE = 0xD0
RED_SLOTS = (list(range(0x60, 0x70)) + [0x77] + list(range(0x80, 0x8A)) +
             list(range(0x90, 0x97)) + [0x98, 0x99] + list(range(0x9B, 0xA0)))
assert len(COLOUR_SET) == 41 and len(RED_SLOTS) == 41
G_CURSOR, G_SCR1, G_SCR2, G_SCR3 = range(0xFC, 0x100)
G_BATT0 = 0x11
G_RSCR1, G_RSCR2, G_RSCR3 = 0x1D, 0x1E, 0x1F                     # heading/sat slots: red noise (sag, low battery)
assert AMBER_BASE + len(COLOUR_SET) == 0xF9
_used = set(RED_SLOTS) | set(range(AMBER_BASE, AMBER_BASE + len(COLOUR_SET))) | {G_CURSOR, G_SCR1, G_SCR2, G_SCR3, G_RSCR1, G_RSCR2, G_RSCR3} | set(range(G_BATT0, G_BATT0 + 5)) | set(range(0x20, 0x60))
assert not _used & {s for s, _ in frog_glyphs.cells()}, "frog glyph slot clashes with a fr0gOS glyph"

# ---- VGA 8x16 bitmaps (CP437 order) ----
vga = {}
for line in open(FONTMAP, encoding="utf-8"):
    m = re.search(r"\[((?:0x[0-9a-f]{2},?\s*){16})\].*\((\d+)\)\s*$", line)
    if m:
        vga[int(m.group(2))] = [int(b, 16) for b in re.findall(r"0x[0-9a-f]{2}", m.group(1))]
assert len(vga) == 256, len(vga)


def vga_art(code, colour):
    """CP437 glyph -> 8x16 list of colours/None"""
    rows = vga[code]
    return [[colour if (rows[y] >> (7 - x)) & 1 else None for x in range(8)] for y in range(16)]


def art_from_text(rows, palette):
    """8-wide text art, top-padded to 16 rows"""
    rows = [r.ljust(8, ".") for r in rows]
    pad = (16 - len(rows)) // 2
    grid = [[None] * 8 for _ in range(16)]
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            grid[y + pad][x] = palette.get(ch)
    return grid


def render_cell(art, k, gw, gh):
    """art (8x16) -> one gw x gh cell: 1-px pixel-art black outline, scale k, centred"""
    W, H = 10, 18
    big = [[None] * W for _ in range(H)]
    for y in range(16):
        for x in range(8):
            if art[y][x] is not None:
                big[y + 1][x + 1] = art[y][x]
    out = [[None] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if big[y][x] is not None:
                out[y][x] = big[y][x]
            elif any(0 <= y + dy < H and 0 <= x + dx < W and big[y + dy][x + dx] not in (None, BLACK)
                     for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                out[y][x] = BLACK
    cell = Image.new("RGB", (gw, gh), TRANS)
    ox, oy = (gw - W * k) // 2, (gh - H * k) // 2
    px = cell.load()
    for y in range(H):
        for x in range(W):
            if out[y][x] is not None:
                for yy in range(k):
                    for xx in range(k):
                        px[ox + x * k + xx, oy + y * k + yy] = out[y][x]
    return cell


# ---- custom glyph art ----
def batt_art(level):
    """horizontal cell: shell 7 wide + nub, interior x=1..5; level 0..4"""
    fill = {0: RED, 1: AMBER}.get(level, GREEN)
    shell = {0: RED, 1: AMBER}.get(level, GREEN)
    rows = ["GGGGGGG.",
            "G.....GG",
            "G.....GG",
            "G.....GG",
            "GGGGGGG."]
    grid = art_from_text(rows, {"G": shell})
    pad = (16 - len(rows)) // 2
    width = [0, 1, 3, 4, 5][level]
    for y in (1, 2, 3):
        for x in range(1, 1 + width):
            grid[y + pad][x] = fill
    return grid


CURSOR = [[GREEN if y in (13, 14) else None for _ in range(8)] for y in range(16)]


def recolour_green(cell):
    """stock white glyph -> green, keeping black outline and transparency"""
    px = cell.load()
    for y in range(cell.height):
        for x in range(cell.width):
            p = px[x, y]
            if p == TRANS:
                continue
            lum = (p[0] * 299 + p[1] * 587 + p[2] * 114) / 255000.0
            px[x, y] = tuple(int(c * lum) for c in GREEN)
    return cell


# stick code: 8 glyphs, 3 bits each, as three stacked dim-grey bands on solid black, read back from DVR
# footage by tools/stickcode_decode.py. Discreet in the black bars, still easy to read after compression.
STICK_GREY = (72, 72, 72)
STICK_SLOTS = frog_glyphs.free_slots()[:8]
assert len(STICK_SLOTS) == 8, "not enough free slots for the stick code"


def stick_cell(value, gw, gh):
    cell = Image.new("RGB", (gw, gh), (0, 0, 0))
    d = ImageDraw.Draw(cell)
    band = gh // 3
    inset = max(2, gw // 8)
    for b in range(3):
        if value & (4 >> b):                       # bit 2 = top band
            d.rectangle([inset, b * band + inset, gw - 1 - inset, (b + 1) * band - 1 - inset], fill=STICK_GREY)
    return cell


def frog_cell(img, gw, gh):
    """frog glyph (RGBA, FHD 36x54) -> font cell; HD is a 2/3 nearest-neighbour shrink, which maps the 3x3 DOS
    blocks exactly onto the 2x2 blocks the HD letters use"""
    if img.size != (gw, gh):
        img = img.resize((gw, gh), Image.NEAREST)
    cell = Image.new("RGB", (gw, gh), TRANS)
    cell.paste(img.convert("RGB"), (0, 0), img.split()[3].point(lambda a: 255 if a >= 128 else 0))
    return cell


def build(stock_path, k, out_path):
    stock = Image.open(stock_path).convert("RGB")
    gw, gh = stock.width // 16, stock.height // 32
    font = Image.new("RGB", stock.size, TRANS)
    put = lambda code, cell: font.paste(cell, ((code % 16) * gw, (code // 16) * gh))
    get = lambda code: stock.crop(((code % 16) * gw, (code // 16) * gh, (code % 16 + 1) * gw, (code // 16 + 1) * gh))

    # 1. everything from stock, recoloured green (symbols fr0gOS still uses)
    for code in range(256):
        put(code, recolour_green(get(code)))
    # 2. ASCII 0x20-0x5F in VGA green
    for code in range(0x20, 0x60):
        put(code, render_cell(vga_art(code, GREEN), k, gw, gh))
    # 3. amber + red alphabets
    for i, ch in enumerate(COLOUR_SET):
        put(AMBER_BASE + i, render_cell(vga_art(ord(ch), AMBER), k, gw, gh))
        put(RED_SLOTS[i], render_cell(vga_art(ord(ch), RED), k, gw, gh))
    # 4. customs
    put(G_CURSOR, render_cell(CURSOR, k, gw, gh))
    for g, cp in ((G_RSCR1, 176), (G_RSCR2, 177), (G_RSCR3, 178)):
        put(g, render_cell(vga_art(cp, RED), k, gw, gh))
    for g, cp in ((G_SCR1, 176), (G_SCR2, 177), (G_SCR3, 178)):
        put(g, render_cell(vga_art(cp, DKGREEN), k, gw, gh))
    for lvl in range(5):
        put(G_BATT0 + lvl, render_cell(batt_art(lvl), k, gw, gh))
    # 5. the frog (the old boot logo slots and unused symbols)
    for code, img in frog_glyphs.cells():
        put(code, frog_cell(img, gw, gh))
    # 6. stick code glyphs
    for v, code in enumerate(STICK_SLOTS):
        put(code, stick_cell(v, gw, gh))
    font.save(out_path, format="BMP")
    return font, gw, gh


hd, gw, gh = build(STOCK_HD, 2, f"{OUT_DIR}/BTFL_000.bmp")
build(STOCK_FHD, 3, f"{OUT_DIR}/BTFL_FHD_000.bmp")
open(ANIM_HEADER, "w").write(frog_glyphs.header())

# ---- firmware charmap ----
amber = [0] * 64
red = [0] * 64
for i, ch in enumerate(COLOUR_SET):
    amber[ord(ch) - 0x20] = AMBER_BASE + i
    red[ord(ch) - 0x20] = RED_SLOTS[i]
fmt = lambda a: ",\n    ".join(", ".join(f"0x{v:02X}" for v in a[i:i + 16]) for i in range(0, 64, 16))
open(HEADER, "w").write(f"""// Generated by tools/build_hacker_font.py - do not edit by hand.
// fr0gOS HDZero hacker font character map (must match the BTFL_000.bmp on the goggle SD card).
#pragma once

#include <stdint.h>

#define FROG_GLYPH_CURSOR     0x{G_CURSOR:02X}
// stick code (3 bits per glyph): value v is drawn with glyph frogStickGlyph[v]
#define FROG_STICK_GLYPHS {{ {", ".join("0x%02X" % c for c in STICK_SLOTS)} }}
#define FROG_GLYPH_RSCRAMBLE1 0x{G_RSCR1:02X}
#define FROG_GLYPH_SCRAMBLE1  0x{G_SCR1:02X}
#define FROG_GLYPH_SCRAMBLE2  0x{G_SCR2:02X}
#define FROG_GLYPH_SCRAMBLE3  0x{G_SCR3:02X}
#define FROG_GLYPH_BATT0      0x{G_BATT0:02X}   // +0..+4 = empty..full

#ifdef FROG_CHARMAP_TABLES
// index = ASCII - 0x20 (0x20..0x5F); 0 = no coloured copy, keep the green glyph
static const uint8_t frogAmberMap[64] = {{
    {fmt(amber)}
}};
static const uint8_t frogRedMap[64] = {{
    {fmt(red)}
}};
#endif
""")

# ---- preview of the full HD font sheet ----
prev = Image.new("RGB", hd.size, (20, 24, 22))
src, dst = hd.load(), prev.load()
for y in range(hd.height):
    for x in range(hd.width):
        if src[x, y] != TRANS:
            dst[x, y] = src[x, y]
prev.crop((0, 0, hd.width, 16 * gh)).resize((hd.width * 2, 16 * gh * 2), Image.NEAREST).save(f"{OUT_DIR}/font_sheet_preview.png")
print("ok", gw, gh)

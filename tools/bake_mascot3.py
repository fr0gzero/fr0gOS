#!/usr/bin/env python3
"""R55 goggle font post-step: the frog goes 3 wide x 2 tall and moves to font page 1; the page-0 slots it used
(and the retired stick-code slots) take two more letter sets: LABEL (pink) and FLASH (white).

Page 1 = glyphs 256..511 of the BMP (rows 16..31). The firmware writes the frog's rows with the MSP font-page bit
set, so its glyph bytes below are page-1 codes (0x60 upward).

R56 adds the stick gimbals (page 1): a dot glyph at every 4 px offset in a cell, plus the box frame pieces.

usage: bake_mascot3.py <frames_dir> <in_dir> <out_dir> <old_frog_mascot.h> <new_frog_mascot.h> <frog_sets.h> <frog_sticks.h>
"""
import hashlib
import importlib.util
import os
import re
import sys
from PIL import Image

FRAMES_DIR, IN_DIR, OUT_DIR, OLD_H, NEW_H, SETS_H, STICKS_H = sys.argv[1:8]
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mc", os.path.join(HERE, "font_monocaps.py"))
mc = importlib.util.module_from_spec(spec); spec.loader.exec_module(mc)

TRANS = (127, 127, 127)
LABEL = tuple(int(x) for x in os.environ.get("FROG_LABEL_RGB", "255,90,200").split(","))
FLASH = tuple(int(x) for x in os.environ.get("FROG_FLASH_RGB", "255,255,255").split(","))
NAMES = ["idle", "glanceL", "glanceR", "blink", "grin", "exclgrin", "hurt", "ko", "breath",
         "blinkH", "glanceU", "glanceD", "whoa", "dizzy", "pumped", "stars", "upsidedown"]
COLS, ROWS = 3, 2
SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-"
STICK = [0x02, 0x03, 0x05, 0x08, 0x09, 0x0B, 0x0C, 0x0F]
PAGE1 = [c for c in range(0x60, 0x100)] + [c for c in range(0x01, 0x20) if c not in (0x0A, 0x0D)]
os.makedirs(OUT_DIR, exist_ok=True)

old = open(OLD_H).read()
old_slots = sorted({int(x, 16) for x in re.findall(r"0x[0-9A-F]{2}", old.split("frogMascot[")[1])} - {0x20})
free = old_slots + STICK
assert len(free) >= 2 * len(SET), (len(free), 2 * len(SET))

frames = [Image.open(os.path.join(FRAMES_DIR, f"frame_{i + 1:02d}_{n}.png")).convert("RGBA") for i, n in enumerate(NAMES)]
# wink = idle with the right half of the blink frame (the like & subscribe card)
wink = frames[0].copy()
w2 = frames[0].width // 2
wink.paste(frames[3].crop((w2, 0, frames[3].width, frames[3].height)), (w2, 0))
frames.append(wink); NAMES.append("wink")


def block(frame, cw, ch):
    bw, bh = cw * COLS, ch * ROWS
    s = min(bw / frame.width, bh / frame.height)
    r = frame.resize((max(1, round(frame.width * s)), max(1, round(frame.height * s))), Image.LANCZOS)
    canvas = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    canvas.paste(r, ((bw - r.width) // 2, (bh - r.height) // 2), r)
    return canvas


def to_font(cell):
    out = Image.new("RGB", cell.size, TRANS)
    px, op = cell.load(), out.load()
    for y in range(cell.height):
        for x in range(cell.width):
            r, g, b, a = px[x, y]
            if a >= 128:
                op[x, y] = (r, g, b) if (r, g, b) != TRANS else (126, 127, 127)
    return out


fonts = {}
for name in ("BTFL_000.bmp", "BTFL_FHD_000.bmp"):
    im = Image.open(os.path.join(IN_DIR, name)).convert("RGB")
    fonts[name] = (im, im.width // 16, im.height // 32)


def put(name, code, cell):
    im, cw, ch = fonts[name]
    im.paste(cell, ((code % 16) * cw, (code // 16) * ch))


# 1. clear the old page-0 frog and stick slots, paint the two new letter sets there
label_map, flash_map = [0] * 64, [0] * 64
it = iter(free)
for name, (im, cw, ch) in fonts.items():
    for c in free:
        put(name, c, Image.new("RGB", (cw, ch), TRANS))
for colour, table in ((LABEL, label_map), (FLASH, flash_map)):
    for chx in SET:
        slot = next(it)
        table[ord(chx) - 0x20] = slot
        for name, (im, cw, ch) in fonts.items():
            put(name, slot, mc.render(chx, colour, cw, ch, TRANS))

# 2. the frog, 3x2, into page 1
uniq, table, nxt = {}, [], 0
for f in frames:
    b = {name: block(f, cw, ch) for name, (im, cw, ch) in fonts.items()}
    glyphs = []
    for row in range(ROWS):
        for col in range(COLS):
            cells = {}
            for name, (im, cw, ch) in fonts.items():
                cells[name] = b[name].crop((col * cw, row * ch, (col + 1) * cw, (row + 1) * ch))
            if cells["BTFL_FHD_000.bmp"].getbbox() is None:
                glyphs.append(0x20)
                continue
            key = hashlib.md5(cells["BTFL_FHD_000.bmp"].tobytes()).hexdigest()
            if key not in uniq:
                uniq[key] = PAGE1[nxt]; nxt += 1
                for name in fonts:
                    put(name, 256 + uniq[key], to_font(cells[name]))
            glyphs.append(uniq[key])
    table.append(glyphs)
# 3. stick gimbals (page 1). Everything is drawn on a 12x18 unit grid per cell (1 unit = 2 px HD, 3 px FHD).
from PIL import ImageFilter  # noqa: E402
CY, WHITE, PINK, DIM = (80, 230, 255), (255, 255, 255), (255, 90, 200), (50, 140, 170)
pool = PAGE1[nxt:] + list(range(0x21, 0x60))
pit = iter(pool)


def unit_cell(draw_fn, cw, ch):
    """draw_fn(d, s) paints on an RGBA cell; a black edge is added round it, clipped to the cell"""
    s = cw // 12
    art = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    from PIL import ImageDraw
    draw_fn(ImageDraw.Draw(art), s)
    a = art.split()[3]
    k = 3 if s == 2 else 5
    halo = a.filter(ImageFilter.MaxFilter(k))
    out = Image.new("RGB", (cw, ch), TRANS)
    out.paste((0, 0, 0), mask=halo)
    out.paste(art, mask=a)
    return out


def U(d, s, x0, y0, x1, y1, col):          # filled rect in units, inclusive
    d.rectangle((x0 * s, y0 * s, (x1 + 1) * s - 1, (y1 + 1) * s - 1), fill=col + (255,))


def dot_fn(ox, oy):
    def f(d, s):
        for (ax, ay, bx, by, col) in ((1, 0, 2, 3, WHITE), (0, 1, 3, 2, WHITE), (1, 1, 2, 2, PINK)):
            U(d, s, ox + ax, oy + ay, ox + bx, oy + by, col)
    return f


def paint(fn):
    code = next(pit)
    for name, (im, cw, ch) in fonts.items():
        put(name, 256 + code, unit_cell(fn, cw, ch))
    return code


dot = [[paint(dot_fn((ix - 1) * 2, (iy - 1) * 2)) for iy in range(10)] for ix in range(7)]
ring = {
    "TL": lambda d, s: U(d, s, 11, 17, 11, 17, CY),
    "T": lambda d, s: U(d, s, 0, 17, 11, 17, CY),
    "TTICK": lambda d, s: (U(d, s, 0, 17, 11, 17, CY), U(d, s, 5, 14, 6, 16, CY)),
    "TR": lambda d, s: U(d, s, 0, 17, 0, 17, CY),
    "L": lambda d, s: U(d, s, 11, 0, 11, 17, CY),
    "LTICK": lambda d, s: (U(d, s, 11, 0, 11, 17, CY), U(d, s, 8, 8, 10, 9, CY)),
    "R": lambda d, s: U(d, s, 0, 0, 0, 17, CY),
    "RTICK": lambda d, s: (U(d, s, 0, 0, 0, 17, CY), U(d, s, 1, 8, 3, 9, CY)),
    "BL": lambda d, s: U(d, s, 11, 0, 11, 0, CY),
    "B": lambda d, s: U(d, s, 0, 0, 11, 0, CY),
    "BTICK": lambda d, s: (U(d, s, 0, 0, 11, 0, CY), U(d, s, 5, 1, 6, 3, CY)),
    "BR": lambda d, s: U(d, s, 0, 0, 0, 0, CY),
    "CROSS": lambda d, s: (d.rectangle((2 * s, 9 * s - s // 2, 10 * s - 1, 9 * s - s // 2 + s - 1), fill=DIM + (255,)),
                           d.rectangle((6 * s - s // 2, 5 * s, 6 * s - s // 2 + s - 1, 13 * s - 1), fill=DIM + (255,))),
}
ring_codes = {k: paint(fn) for k, fn in ring.items()}
dot_rows = ",\n    ".join("{ " + ", ".join("0x%02X" % c for c in col) + " }" for col in dot)
open(STICKS_H, "w").write(f"""// Generated by tools/bake_mascot3.py - do not edit by hand.
// fr0gOS stick gimbals, goggle font page 1. frogStickDot[ix][iy]: the 8x8 px dot drawn at (ix-1)*4, (iy-1)*4 px
// inside a 24x36 cell (clipped), so a dot anywhere on a 4 px grid is one glyph per cell it touches.
#pragma once
#include <stdint.h>

static const uint8_t frogStickDot[7][10] = {{
    {dot_rows}
}};
""" + "".join(f"#define FROG_STK_{k:<6} 0x{v:02X}\n" for k, v in ring_codes.items()))
print(f"sticks: {7 * 10} dot glyphs + {len(ring)} frame glyphs on page 1")

# page-1 space must be empty (a blank frog cell is written as 0x20 in a page-1 string)
for name, (im, cw, ch) in fonts.items():
    put(name, 256 + 0x20, Image.new("RGB", (cw, ch), TRANS))
    im.save(os.path.join(OUT_DIR, name), format="BMP")
print(f"frog: {len(frames)} frames, {nxt} page-1 glyphs; sets: 2 x {len(SET)} in {len(free)} freed page-0 slots")

rows = ",\n    ".join("{ " + ", ".join("0x%02X" % g for g in gl) + " }" for gl in table)
enum = "".join(f"    FROG_M_{n.upper()},\n" for n in NAMES)
open(NEW_H, "w").write(f"""// Generated by tools/bake_mascot3.py - do not edit by hand.
// fr0gOS goggle-frog mascot: each frame is 3 wide x 2 tall goggle-font glyphs on FONT PAGE 1 (row-major).
// Must match BTFL_000.bmp / BTFL_FHD_000.bmp on the goggle SD card.
#pragma once
#include <stdint.h>

#define FROG_MASCOT_COLS {COLS}
#define FROG_MASCOT_ROWS {ROWS}
#define FROG_MASCOT_FRAMES {len(table)}

typedef enum {{
{enum}    FROG_M_COUNT
}} frogMascotFrame_e;

// [frame][cell], row-major; 0x20 = blank. Page-1 glyph codes.
static const uint8_t frogMascot[FROG_MASCOT_FRAMES][{COLS * ROWS}] = {{
    {rows}
}};
""")


def cmap(t):
    return ",\n    ".join(", ".join("0x%02X" % v for v in t[i:i + 16]) for i in range(0, 64, 16))


open(SETS_H, "w").write(f"""// Generated by tools/bake_mascot3.py - do not edit by hand.
// fr0gOS extra letter sets on font page 0: LABEL (pink) and FLASH (white). index = ASCII - 0x20; 0 = no copy.
#pragma once
#include <stdint.h>

static const uint8_t frogLabelMap[64] = {{
    {cmap(label_map)}
}};
static const uint8_t frogFlashMap[64] = {{
    {cmap(flash_map)}
}};
""")

#!/usr/bin/env python3
"""R55 goggle font post-step: the frog goes 3 wide x 2 tall and moves to font page 1; the page-0 slots it used
(and the retired stick-code slots) take two more letter sets: LABEL (pink) and FLASH (white).

Page 1 = glyphs 256..511 of the BMP (rows 16..31). The firmware writes the frog's rows with the MSP font-page bit
set, so its glyph bytes below are page-1 codes (0x60 upward).

usage: bake_mascot3.py <frames_dir> <in_dir> <out_dir> <old_frog_mascot.h> <new_frog_mascot.h> <frog_sets.h>
"""
import hashlib
import importlib.util
import os
import re
import sys
from PIL import Image

FRAMES_DIR, IN_DIR, OUT_DIR, OLD_H, NEW_H, SETS_H = sys.argv[1:7]
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

#!/usr/bin/env python3
"""fr0gOS font v2: a trimmed, idle-focused mascot + a bespoke high-res stick-overlay glyph set + LCARS caps,
all baked into the frog slot pool. Emits the base font BMPs plus firmware headers.

Stick glyphs: a dot at 4x4 sub-positions inside a cell (bright set for the live dot, dim set for the trace),
plus one faint crosshair cell. The firmware draws a 3x3 box per stick and places the dot sub-cell-accurately,
so the indicator is far higher resolution than Betaflight's sprite overlay.

usage: bake_v2.py <stock_hd.bmp> <stock_fhd.bmp> <frames_dir> <out_dir>
"""
import hashlib, os, sys, math
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_glyphs

STOCK_HD, STOCK_FHD, FRAMES, OUT = sys.argv[1:5]
TRANS = (127, 127, 127)
SLOTS = list(frog_glyphs.SLOTS)
os.makedirs(OUT, exist_ok=True)

# trimmed mascot: a strong idle loop + the few reactions still used (flip->pumped, perch->grin, crash->ko,
# turtle->upsidedown). roll/spin frames (whoa/dizzy) and the extra reactions are dropped.
MASCOT = ["idle", "blink", "glanceL", "glanceR", "glanceU", "glanceD", "breath", "blinkH",
          "pumped", "grin", "ko", "upsidedown"]

hd = Image.open(STOCK_HD).convert("RGB")
fhd = Image.open(STOCK_FHD).convert("RGB")
HCW, HCH = hd.width // 16, hd.height // 32
FCW, FCH = fhd.width // 16, fhd.height // 32
paint = {}            # slot -> (hd_cell_rgb, fhd_cell_rgb)
nextslot = [0]

def claim():
    if nextslot[0] >= len(SLOTS):
        raise SystemExit("out of frog slots")
    s = SLOTS[nextslot[0]]; nextslot[0] += 1; return s

def to_font(cell):
    out = Image.new("RGB", cell.size, TRANS)
    px, op = cell.load(), out.load()
    for y in range(cell.height):
        for x in range(cell.width):
            r, g, b, a = px[x, y]
            if a >= 128:
                op[x, y] = (r, g, b)
    return out

# ---------- mascot ----------
def block(frame, cw, ch):
    bw, bh = cw * 2, ch * 2
    s = min(bw / frame.width, bh / frame.height)
    r = frame.resize((max(1, round(frame.width * s)), max(1, round(frame.height * s))), Image.LANCZOS)
    c = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    c.paste(r, ((bw - r.width) // 2, (bh - r.height) // 2), r)
    return c

uniq = {}
frame_glyphs = []
for n in MASCOT:
    f = Image.open(os.path.join(FRAMES, next(x for x in os.listdir(FRAMES) if x.endswith(n + ".png")))).convert("RGBA")
    bh, bf = block(f, HCW, HCH), block(f, FCW, FCH)
    gl = []
    for (col, row) in ((0, 0), (1, 0), (0, 1), (1, 1)):
        cf = bf.crop((col * FCW, row * FCH, (col + 1) * FCW, (row + 1) * FCH))
        ch = bh.crop((col * HCW, row * HCH, (col + 1) * HCW, (row + 1) * HCH))
        if cf.getbbox() is None:
            gl.append(0x20); continue
        key = hashlib.md5(cf.tobytes()).hexdigest()
        if key not in uniq:
            s = claim(); uniq[key] = s; paint[s] = (to_font(ch), to_font(cf))
        gl.append(uniq[key])
    frame_glyphs.append(gl)
print("mascot:", len(MASCOT), "frames,", nextslot[0], "glyphs")

# ---------- stick dots: 4x4 sub-positions, bright + dim ----------
SUB = 4
BRIGHT = (120, 240, 255)     # cyan dot - high visibility over any scene
DIM = (70, 120, 150)         # trace
def dot_cell(cw, ch, sx, sy, color):
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx = (sx + 0.5) / SUB * cw
    cy = (sy + 0.5) / SUB * ch
    r = cw * 0.26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (255,), outline=(0, 0, 0, 255), width=max(1, int(cw * 0.05)))
    return im
def rgba_to_font(im):
    out = Image.new("RGB", im.size, TRANS); px, op = im.load(), out.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a >= 128: op[x, y] = (r, g, b)
    return out
STICK_BRIGHT = [[0] * SUB for _ in range(SUB)]
STICK_DIM = [[0] * SUB for _ in range(SUB)]
for sy in range(SUB):
    for sx in range(SUB):
        s = claim(); paint[s] = (rgba_to_font(dot_cell(HCW, HCH, sx, sy, BRIGHT)), rgba_to_font(dot_cell(FCW, FCH, sx, sy, BRIGHT))); STICK_BRIGHT[sy][sx] = s
        s = claim(); paint[s] = (rgba_to_font(dot_cell(HCW, HCH, sx, sy, DIM)),   rgba_to_font(dot_cell(FCW, FCH, sx, sy, DIM)));   STICK_DIM[sy][sx] = s

# faint crosshair cell (box interior)
def cross_cell(cw, ch):
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = (60, 70, 90, 255)
    d.line([cw/2, ch*0.2, cw/2, ch*0.8], fill=c, width=max(1, int(cw*0.05)))
    d.line([cw*0.2, ch/2, cw*0.8, ch/2], fill=c, width=max(1, int(cw*0.05)))
    return im
STICK_CROSS = claim(); paint[STICK_CROSS] = (rgba_to_font(cross_cell(HCW, HCH)), rgba_to_font(cross_cell(FCW, FCH)))

# ---------- LCARS caps: solid colour cells ----------
CAPS = {"amber": (255, 178, 74), "lav": (190, 162, 232), "tan": (232, 185, 106), "rust": (194, 123, 74)}
cap_codes = {}
for name, col in CAPS.items():
    s = claim()
    ch = Image.new("RGB", (HCW, HCH), col); cf = Image.new("RGB", (FCW, FCH), col)
    paint[s] = (ch, cf); cap_codes[name] = s

print("total frog-pool glyphs used:", nextslot[0], "of", len(SLOTS))

# ---------- paste + save ----------
for slot, (chd, cfhd) in paint.items():
    hd.paste(chd, ((slot % 16) * HCW, (slot // 16) * HCH))
    fhd.paste(cfhd, ((slot % 16) * FCW, (slot // 16) * FCH))
hd.save(os.path.join(OUT, "BTFL_000.bmp"), "BMP")
fhd.save(os.path.join(OUT, "BTFL_FHD_000.bmp"), "BMP")

# ---------- headers ----------
rows = ",\n    ".join("{ 0x%02X, 0x%02X, 0x%02X, 0x%02X }" % tuple(g) for g in frame_glyphs)
enum = "".join("    FROG_M_%s,\n" % n.upper() for n in MASCOT)
open(os.path.join(OUT, "frog_mascot.h"), "w").write(f"""// Generated by bake_v2.py - trimmed mascot.
#pragma once
#include <stdint.h>
#define FROG_MASCOT_COLS 2
#define FROG_MASCOT_ROWS 2
#define FROG_MASCOT_FRAMES {len(frame_glyphs)}
typedef enum {{
{enum}    FROG_M_COUNT
}} frogMascotFrame_e;
static const uint8_t frogMascot[FROG_MASCOT_FRAMES][4] = {{
    {rows}
}};
""")
br = ",\n    ".join("{ " + ", ".join("0x%02X" % STICK_BRIGHT[sy][sx] for sx in range(SUB)) + " }" for sy in range(SUB))
dm = ",\n    ".join("{ " + ", ".join("0x%02X" % STICK_DIM[sy][sx] for sx in range(SUB)) + " }" for sy in range(SUB))
open(os.path.join(OUT, "frog_sticks.h"), "w").write(f"""// Generated by bake_v2.py - high-res stick overlay glyphs.
#pragma once
#include <stdint.h>
#define STICK_SUB {SUB}
// dot at [subY][subX] inside a cell: bright = live dot, dim = trace
static const uint8_t frogStickDot[STICK_SUB][STICK_SUB] = {{
    {br}
}};
static const uint8_t frogStickDotDim[STICK_SUB][STICK_SUB] = {{
    {dm}
}};
#define FROG_STICK_CROSS 0x{STICK_CROSS:02X}
""")
open(os.path.join(OUT, "frog_caps.h"), "w").write("// Generated by bake_v2.py - LCARS cap block glyphs.\n#pragma once\n"
    + "".join("#define FROG_CAP_%s 0x%02X\n" % (n.upper(), c) for n, c in cap_codes.items()))
print("wrote font + headers to", OUT)

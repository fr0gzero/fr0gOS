#!/usr/bin/env python3
"""Four native 24x36 font directions for the fr0gOS goggle OSD, rendered as OSD previews (50x18 canvas).
Glyphs are 1-bit (the goggle keys on transparent grey), flat colour fill, no outline."""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = sys.argv[1]
BGF = sys.argv[2]
GW, GH, S = 24, 36, 4
MEGA = "/home/claude/frogos/publish/fonts/hdzero-mega/BTFL_000.bmp"
MASC = [0xA0, 0xA1, 0xA2, 0xA3]
WHITE, AMBER, RED, CYAN, GREEN = (245, 245, 245), (255, 200, 40), (235, 70, 60), (90, 220, 255), (120, 235, 120)

DJV = "/usr/share/fonts/truetype/dejavu/"
INTER = "/usr/share/fonts/opentype/inter/"
POP = "/usr/share/fonts/truetype/google-fonts/"
GYRE = "/usr/share/texmf/fonts/opentype/public/tex-gyre/"


def load(path, size):
    return ImageFont.truetype(path, size)


def ink_cell(ch, path, cap_px, squeeze, style, bold_extra=0):
    """Draw ch at S x supersample into a 24x36 frame; returns an 'L' mask of the glyph at S*GW x S*GH."""
    big = Image.new("L", (GW * S, GH * S), 0)
    # pick a size so that a capital H is cap_px tall
    probe = load(path, 200)
    bb = probe.getbbox("H")
    size = 200.0 * cap_px * S / (bb[3] - bb[1])
    f = load(path, int(size))
    d = ImageDraw.Draw(big)
    bb = f.getbbox(ch)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    # glyph layer, squeezed horizontally
    layer = Image.new("L", (w + 8, int(size * 1.4)), 0)
    ImageDraw.Draw(layer).text((4 - bb[0], 0), ch, font=f, fill=255)
    asc = f.getbbox("H")
    top = f.getbbox("H")[1]
    layer = layer.crop((0, 0, w + 8, layer.height))
    nw = max(1, int((w + 8) * squeeze))
    layer = layer.resize((nw, layer.height), Image.LANCZOS)
    # baseline: bottom of H sits on row base
    base = GH * S - 7 * S
    y0 = base - (asc[3] - 0)
    x0 = (GW * S - nw) // 2
    big.paste(layer, (x0, y0), layer)
    if bold_extra:
        big = big.filter(ImageFilter.MaxFilter(bold_extra * 2 + 1))
    return style(big)


def squared(img):
    # close then open with square kernels -> flat, squared corners and ends
    a = img.point(lambda v: 255 if v > 127 else 0)
    a = a.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
    a = a.filter(ImageFilter.MinFilter(7)).filter(ImageFilter.MaxFilter(7))
    return a


def rounded(img):
    a = img.filter(ImageFilter.GaussianBlur(7))
    return a.point(lambda v: 255 if v > 118 else 0)


def sliced(img):
    a = squared(img)
    d = ImageDraw.Draw(a)
    for fr in (0.43, 0.66):
        y = int(GH * S * fr)
        d.rectangle((0, y, GW * S, y + S - 1), fill=0)   # one-pixel LED slits
    return a


def plain(img):
    return img.point(lambda v: 255 if v > 127 else 0)


def finish(mask, colour):
    """supersampled mask -> 24x36 RGBA cell: 1-bit fill + 1px black outline"""
    m = mask.resize((GW, GH), Image.BOX).point(lambda v: 255 if v > 110 else 0)
    cell = Image.new("RGBA", (GW, GH), (0, 0, 0, 0))
    cell.paste(Image.new("RGBA", (GW, GH), colour + (255,)), (0, 0), m)
    return cell


# ---- seven segment digits -------------------------------------------------------------------------------------
SEG = {"0": "abcdef", "1": "bc", "2": "abdeg", "3": "abcdg", "4": "bcfg", "5": "acdfg", "6": "acdefg", "7": "abc",
       "8": "abcdefg", "9": "abcdfg", "-": "g", " ": ""}


def seven(ch):
    big = Image.new("L", (GW * S, GH * S), 0)
    d = ImageDraw.Draw(big)
    W, H = GW * S, GH * S
    x0, x1 = 4 * S, W - 4 * S
    y0, y1, ym = 5 * S, H - 8 * S, 5 * S + (H - 13 * S) // 2
    t = int(3.2 * S)
    c = int(1.6 * S)

    def hbar(y):
        d.polygon([(x0 + c, y), (x1 - c, y), (x1 - c - t // 2, y + t), (x0 + c + t // 2, y + t)] if False else
                  [(x0 + c, y + t // 2), (x0 + c + t // 2, y), (x1 - c - t // 2, y), (x1 - c, y + t // 2),
                   (x1 - c - t // 2, y + t), (x0 + c + t // 2, y + t)], fill=255)

    def vbar(x, ya, yb):
        d.polygon([(x + t // 2, ya + c), (x + t, ya + c + t // 2), (x + t, yb - c - t // 2), (x + t // 2, yb - c),
                   (x, yb - c - t // 2), (x, ya + c + t // 2)], fill=255)
    segs = SEG.get(ch, "")
    if "a" in segs: hbar(y0)
    if "g" in segs: hbar(ym - t // 2)
    if "d" in segs: hbar(y1 - t)
    if "f" in segs: vbar(x0, y0, ym)
    if "b" in segs: vbar(x1 - t, y0, ym)
    if "e" in segs: vbar(x0, ym, y1)
    if "c" in segs: vbar(x1 - t, ym, y1)
    return big


# ---- the four directions ---------------------------------------------------------------------------------------
def dirA(ch, kind):   # clean sci-fi sans: condensed grotesque, squared off
    return ink_cell(ch, DJV + "DejaVuSansCondensed-Bold.ttf", 25, 0.86, squared, 0)


def dirB(ch, kind):   # rounded HUD: chunky, soft corners, tall numerals
    cap = 26 if kind == "digit" else 24
    return ink_cell(ch, POP + "Poppins-Bold.ttf", cap, 0.82, rounded, 1)


def dirC(ch, kind):   # retro digital: true 7-segment digits, LED-slit letters
    if kind == "digit" or ch == "-":
        return seven(ch)
    if ch == ":":
        return ink_cell(ch, DJV + "DejaVuSansMono-Bold.ttf", 25, 1.0, squared, 0)
    return ink_cell(ch, DJV + "DejaVuSansMono-Bold.ttf", 24, 1.0, sliced, 0)


def dirD(ch, kind):   # hybrid: heavy tall numerals, calm medium words
    if kind == "digit":
        return ink_cell(ch, INTER + "Inter-Black.otf", 29, 0.78, plain, 1)
    return ink_cell(ch, INTER + "Inter-SemiBold.otf", 22, 0.80, plain, 0)


DIRS = [("A", "Clean sci-fi sans (squared condensed)", dirA),
        ("B", "Rounded HUD (chunky, soft)", dirB),
        ("C", "Retro-digital (7-seg numbers, LED-slit words)", dirC),
        ("D", "Hybrid (heavy numbers, calm words)", dirD)]


def mk(path, cap, sq, bold=0):
    return lambda ch, kind: ink_cell(ch, path, cap, sq, plain, bold)


DIRS2 = [("E", "Inter ExtraBold (neutral grotesque)", mk(INTER + "Inter-ExtraBold.otf", 25, 0.88)),
         ("F", "TeX Gyre Adventor Bold (geometric, Avant Garde)", mk(GYRE + "texgyreadventor-bold.otf", 25, 0.86)),
         ("G", "Carlito Bold (humanist, Calibri-like)", mk("/usr/share/fonts/truetype/crosextra/Carlito-Bold.ttf", 26, 0.96)),
         ("H", "TeX Gyre Bonum Bold (bookish serif)", mk(GYRE + "texgyrebonum-bold.otf", 25, 0.90)),
         ("I", "DejaVu Sans Mono Bold (terminal)", mk(DJV + "DejaVuSansMono-Bold.ttf", 25, 0.96)),
         ("J", "TeX Gyre Heros Cn Bold (tall condensed Helvetica)", mk(GYRE + "texgyreheroscn-bold.otf", 28, 0.92))]

def sheared(k):
    def f(img):
        a = squared(img)
        w, h = a.size
        return a.transform((w, h), Image.AFFINE, (1, k, -k * h * 0.62, 0, 1, 0), Image.BICUBIC).point(lambda v: 255 if v > 127 else 0)
    return f


DIRS3 = [("K", "Slanted squared techno (Eurostile-ish italic, synthetic)", lambda ch, kind: ink_cell(ch, DJV + "DejaVuSansCondensed-Bold.ttf", 25, 0.9, sheared(0.24), 0)),
         ("L", "Heros Cn Bold Italic (tall slanted grotesque)", mk(GYRE + "texgyreheroscn-bolditalic.otf", 28, 0.92)),
         ("M", "Adventor Bold Italic (wide slanted geometric)", mk(GYRE + "texgyreadventor-bolditalic.otf", 25, 0.86))]

def scan(img):
    a = plain(img)
    d = ImageDraw.Draw(a)
    for y in range(0, GH * S, 3 * S):
        d.rectangle((0, y, GW * S, y + S - 1), fill=0)
    return a


def pix_cell(path, cap, gw, gh, scale, size_px=None, xoff=0, yoff=0):
    """render the glyph on a gw x gh pixel grid (cap px tall), thresholded, then blown up by `scale`"""
    def fn(ch, kind):
        probe = load(path, 100)
        bb = probe.getbbox("H")
        size = size_px or max(4, round(100.0 * cap / (bb[3] - bb[1])))
        f = load(path, size)
        small = Image.new("L", (gw, gh), 0)
        b = f.getbbox(ch)
        hb = f.getbbox("H")
        d = ImageDraw.Draw(small)
        d.text(((gw - (b[2] - b[0])) // 2 - b[0] + xoff, gh - 1 - hb[3] + yoff), ch, font=f, fill=255)
        small = small.point(lambda v: 255 if v > 110 else 0)
        big = small.resize((gw * scale * S, gh * scale * S), Image.NEAREST)
        full = Image.new("L", (GW * S, GH * S), 0)
        full.paste(big, (((GW - gw * scale) // 2) * S, ((GH - gh * scale) // 2) * S))
        return full
    return fn


def chamfer(img):
    a = squared(img)
    a = a.filter(ImageFilter.GaussianBlur(5))
    return a.point(lambda v: 255 if v > 135 else 0)


DIRS4 = [("N", "8-bit arcade (chunky 6x9 pixels)", pix_cell(DJV + "DejaVuSansMono-Bold.ttf", 7, 6, 9, 4)),
         ("O", "Unifont 8x16 pixel (old PC game)", pix_cell("/usr/share/fonts/opentype/unifont/unifont.otf", 0, 8, 16, 2, size_px=16)),
         ("P", "Halo / Mass Effect (wide, flat, chamfered)", lambda ch, kind: ink_cell(ch, DJV + "DejaVuSans-Bold.ttf", 23, 1.05, chamfer, 0)),
         ("Q", "Destiny / Tron (thin, wide, airy)", lambda ch, kind: ink_cell(ch, INTER + "Inter-Light.otf", 25, 1.0, plain, 1)),
         ("R", "Wipeout / Gran Turismo (heavy italic)", lambda ch, kind: ink_cell(ch, INTER + "Inter-BlackItalic.otf", 27, 0.86, plain, 0)),
         ("S", "Fallout terminal (mono with scanlines)", lambda ch, kind: ink_cell(ch, DJV + "DejaVuSansMono-Bold.ttf", 25, 0.98, scan, 0)),
         ("T", "Souls-style classical serif", mk(GYRE + "texgyrepagella-bold.otf", 24, 0.92))]

COLOUR = {"w": WHITE, "g": AMBER, "r": RED, "c": CYAN, "n": GREEN}


class Font:
    def __init__(self, fn):
        self.fn, self.cache = fn, {}

    def cell(self, ch, col):
        key = (ch, col)
        if key not in self.cache:
            if ch == " ":
                self.cache[key] = None
            else:
                kind = "digit" if ch.isdigit() else "other"
                self.cache[key] = finish(self.fn(ch, kind), COLOUR[col])
        return self.cache[key]


mega = Image.open(MEGA).convert("RGB")


def mascot_cell(code):
    return mega.crop(((code % 16) * GW, (code // 16) * GH, (code % 16 + 1) * GW, (code // 16 + 1) * GH))


def render(font, label):
    bg = Image.new("RGB", (1200, 648), (0, 0, 0))
    src = Image.open(BGF).convert("RGB").resize((864, 648)).filter(ImageFilter.GaussianBlur(10))
    bg.paste(src, (168, 0))
    out = bg.convert("RGBA")

    def put(cell, x, y):
        if cell is not None:
            out.alpha_composite(cell, (x * GW, y * GH))

    for i, code in enumerate(MASC):
        c = mascot_cell(code)
        px, k = c.load(), Image.new("L", (GW, GH), 0)
        kp = k.load()
        for yy in range(GH):
            for xx in range(GW):
                if px[xx, yy] != (127, 127, 127):
                    kp[xx, yy] = 255
        out.paste(c, ((i % 2) * GW, (i // 2) * GH), k)

    def text(x, y, t, col="w", right=False, centre=False, digitcol=None):
        if centre:
            x = x - len(t) // 2
        sx = x - len(t) + 1 if right else x
        for k, ch in enumerate(t):
            cc = digitcol if (digitcol and ch.isdigit()) else col
            put(font.cell(ch, cc), sx + k, y)

    text(2, 2, "FLIP X2"); text(2, 3, "COMBO 5")
    for y, t in ((9, "16.4V"), (10, "412MAH"), (11, "7.8A"), (13, "LQ 100"), (14, "RATE 2"), (15, "R:8"), (16, "200MW")):
        text(0, y, t)
    text(49, 0, "MK5-1", "g", right=True); text(49, 1, "02:41", right=True)
    text(49, 2, "LOW BATT", "r", right=True); text(49, 4, "ACRO", right=True)
    text(49, 5, "AIR 1:23", right=True); text(49, 12, "THR 45%", right=True)
    text(49, 14, "RPM 23K", right=True); text(49, 16, "G 3.2", right=True)
    # song layout: cue line (row 1), notes (row 3), caption (bottom)
    text(25, 1, "CLIMB IN 3", "g", centre=True, digitcol="c")
    text(25, 3, "SO FAR FROM LOSING OUT", centre=True)
    text(25, 4, "AROUND HERE", centre=True)
    text(25, 16, "SIX UNDERGROUND  3:18", "w", centre=True)
    out = out.convert("RGB")
    out = out.resize((out.width * 3 // 2, out.height * 3 // 2), Image.NEAREST)
    dr = ImageDraw.Draw(out)
    lf = ImageFont.truetype(DJV + "DejaVuSans-Bold.ttf", 30)
    dr.rectangle((0, out.height - 48, out.width, out.height), fill=(20, 20, 30))
    dr.text((14, out.height - 42), label, fill=(255, 212, 0), font=lf)
    return out


def specimen(font, label):
    """big specimen: alphabet, digits, countdown, symbols at 2x"""
    lines = ["ABCDEFGHIJKLM", "NOPQRSTUVWXYZ", "0123456789 .:-%/", "CLIMB IN 3 2 1", "SAFE AND SOUND <3 & @"]
    img = Image.new("RGBA", (24 * 22 * 2, (36 * len(lines) + 12) * 2), (20, 22, 30, 255))
    for r, t in enumerate(lines):
        for k, ch in enumerate(t):
            c = font.cell(ch, "c" if ch.isdigit() else "w")
            if c is not None:
                img.alpha_composite(c, (k * GW + 6, r * GH + 6))
    img = img.crop((0, 0, 24 * 22, 36 * len(lines) + 12)).resize((24 * 22 * 2 // 2 * 1, (36 * len(lines) + 12)), Image.NEAREST)
    img = img.resize((img.width * 2, img.height * 2), Image.NEAREST)
    dr = ImageDraw.Draw(img)
    lf = ImageFont.truetype(DJV + "DejaVuSans-Bold.ttf", 26)
    dr.text((12, 4), label, fill=(255, 212, 0), font=lf)
    return img.convert("RGB")


os.makedirs(OUT, exist_ok=True)
for key, label, fn in ({"2": DIRS2, "3": DIRS3, "4": DIRS4}.get(sys.argv[3] if len(sys.argv) > 3 else "", DIRS)):
    f = Font(fn)
    render(f, f"{key}  {label}").save(os.path.join(OUT, f"osd_{key}.png"))
    specimen(f, f"{key}  {label}").save(os.path.join(OUT, f"specimen_{key}.png"))
    print("done", key)

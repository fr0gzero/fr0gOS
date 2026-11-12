"""fr0gOS "GT" glyph renderer: heavy, wide, forward-leaning racing-game capitals (Wipeout / Gran Turismo mood),
drawn natively at the goggle cell size (24x36 HD, 36x54 FHD) as crisp 1-bit shapes - no outline, no anti-alias
(the goggle keys on one transparent grey), so every pixel is deliberate.

Pipeline per glyph: vector glyph at SS x supersample -> squared-off, bevelled corners -> forward lean (shear about the
baseline) -> fit the cell (never clipped) -> box-downsample -> 1-bit threshold.

Used by build_hacker_font.py when FROG_RENDERER=<path to this file>. render(ch, colour, gw, gh, trans) -> RGB cell.
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SS = int(os.environ.get("GT_SS", "6"))     # supersample
FACE = os.environ.get("GT_FACE", "/usr/share/fonts/opentype/inter/Inter-Black.otf")
CAP = float(os.environ.get("GT_CAP", "27"))         # cap height in HD px (cell is 36 tall)
SQUEEZE = float(os.environ.get("GT_SQUEEZE", "0.93"))
LEAN = float(os.environ.get("GT_LEAN", "0.21"))     # tan of the lean angle (~12 deg)
BEVEL = float(os.environ.get("GT_BEVEL", "1.0"))    # corner cut strength, 0 = none
BASE = float(os.environ.get("GT_BASE", "7"))        # px between baseline and cell bottom (HD)
THRESH = int(os.environ.get("GT_THRESH", "124"))    # 0-255 coverage needed to light a pixel (lower = bolder)
MAXW = float(os.environ.get("GT_MAXW", "22"))       # widest glyph (HD px) incl. lean

FACE_OPEN = os.environ.get("GT_FACE_OPEN", "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf")
OPEN_CHARS = os.environ.get("GT_OPEN_CHARS", "0123456789&@%#$")   # small counters: a touch lighter so they stay open
_cache = {}


def _path(ch):
    return FACE_OPEN if ch in OPEN_CHARS else FACE


def _face(path, size):
    if (path, size) not in _cache:
        _cache[(path, size)] = ImageFont.truetype(path, size)
    return _cache[(path, size)]


def _size_for_cap(path, cap_px):
    probe = ImageFont.truetype(path, 400)
    b = probe.getbbox("H")
    return max(8, int(round(400.0 * cap_px / (b[3] - b[1]))))


def _bevel(a, r):
    """flat, squared shapes with the corners cut: close with a square, then round off by blur+threshold"""
    if r <= 0:
        return a
    a = a.point(lambda v: 255 if v > 127 else 0)
    k = int(r * 2) * 2 + 1
    a = a.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.MinFilter(k))
    a = a.filter(ImageFilter.GaussianBlur(r * 0.9))
    return a.point(lambda v: 255 if v > 132 else 0)


ZERO = os.environ.get("GT_ZERO", "slash")       # how the zero differs from the O: slash | slit | dot | none
ZT = float(os.environ.get("GT_ZT", "3.0"))          # slash / bar thickness (HD px)
_mcache = {}


def mask(ch, gw, gh):
    key = (ch, gw, gh)
    if key not in _mcache:
        _mcache[key] = _mask(ch, gw, gh)
    return _mcache[key]


def _mask(ch, gw, gh):
    k = gh / 36.0                                        # HD = 1, FHD = 1.5
    ss = SS
    cap = CAP * k * ss
    path = _path(ch)
    f = _face(path, _size_for_cap(path, cap))
    W, H = gw * ss, gh * ss
    base_y = H - int(round(BASE * k * ss))               # baseline row (supersampled)
    hb = f.getbbox("H")
    b = f.getbbox(ch)
    pad = int(6 * k * ss)
    layer = Image.new("L", (b[2] - b[0] + 2 * pad, b[3] - b[1] + 2 * pad), 0)
    ImageDraw.Draw(layer).text((pad - b[0], pad - b[1]), ch, font=f, fill=255)
    # glyph baseline inside the tight layer (rows below the baseline are real ink for , ; Q J)
    gbase = pad + (hb[3] - b[1])
    work = _bevel(layer, BEVEL * k * ss * 0.6)
    # squeeze horizontally
    nw = max(1, int(work.width * SQUEEZE))
    work = work.resize((nw, work.height), Image.LANCZOS)
    # forward lean: x shift grows going up from the baseline
    lean = LEAN
    out_w = nw + int(abs(lean) * work.height)
    sheared = work.transform((out_w, work.height), Image.AFFINE, (1, lean, -lean * gbase, 0, 1, 0), Image.BICUBIC)
    sheared = sheared.point(lambda v: 255 if v > 127 else 0)
    bb = sheared.getbbox()
    if bb is None:
        return Image.new("L", (gw, gh), 0)
    ink = sheared.crop((bb[0], 0, bb[2], sheared.height))
    # fit the cell (leave a 1px margin each side), keep it legible: squeeze only if too wide
    max_w = MAXW * k * ss
    if ink.width > max_w:
        ink = ink.resize((int(max_w), ink.height), Image.LANCZOS)
    x0 = (W - ink.width) // 2
    y0 = base_y - gbase
    final = Image.new("L", (W, H), 0)
    final.paste(ink, (x0, y0))
    if ch == "0" and ZERO != "none":
        zb = final.getbbox()
        cx, cy = (zb[0] + zb[2]) / 2.0, (zb[1] + zb[3]) / 2.0
        zw, zh = zb[2] - zb[0], zb[3] - zb[1]
        d = ImageDraw.Draw(final)
        t = int(ZT * k * ss)
        if ZERO == "slash":      # diagonal through the counter, lean-matched, ends buried in the ring
            d.line([(cx - zw * 0.20, cy + zh * 0.30), (cx + zw * 0.20, cy - zh * 0.30)], fill=255, width=t)
        elif ZERO == "slit":     # upright bar in the counter
            d.rectangle((cx - t // 2 + zw * 0.04, cy - zh * 0.24, cx + t // 2 + zw * 0.04, cy + zh * 0.24), fill=255)
        elif ZERO == "dot":
            r = t * 0.85
            d.ellipse((cx - r + zw * 0.04, cy - r, cx + r + zw * 0.04, cy + r), fill=255)
    small = final.resize((gw, gh), Image.BOX)
    return small.point(lambda v: 255 if v > THRESH else 0)


def render(ch, colour, gw, gh, trans):
    if ch == " ":
        return Image.new("RGB", (gw, gh), trans)
    m = mask(ch, gw, gh)
    cell = Image.new("RGB", (gw, gh), trans)
    cell.paste(Image.new("RGB", (gw, gh), colour), (0, 0), m)
    return cell

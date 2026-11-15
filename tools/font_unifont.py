"""fr0gOS "ARCADE" glyph renderer: GNU Unifont's 8x16 pixel capitals, drawn pixel-perfect (no AA, no outline).
HD cell 24x36 = 8x12 font pixels at exactly 3 px each; FHD cell 36x54 uses 4 px per font pixel, centred.
Unifont's own zero is already slashed, so it never reads as an O.  Used via FROG_RENDERER (render(ch, colour, gw, gh, trans))."""
import os
from PIL import Image, ImageDraw, ImageFont

FACE = os.environ.get("UF_FACE", "/usr/share/fonts/opentype/unifont/unifont.otf")
_f = ImageFont.truetype(FACE, 16)
_cache = {}


def _bits(ch):
    im = Image.new("L", (16, 24), 0)
    ImageDraw.Draw(im).text((0, 0), ch, font=_f, fill=255)
    return im


_HT = None


def _unit(ch):
    """8 wide x 12 tall list of rows (strings of 0/1), caps on rows 1..10"""
    global _HT
    if _HT is None:
        _HT = _bits("H").getbbox()[1]
    im = _bits(ch).point(lambda v: 255 if v > 127 else 0)
    top = _HT - 1
    rows = []
    for y in range(top, top + 12):
        rows.append("".join("1" if im.getpixel((x, y)) else "0" for x in range(8)))
    return rows


def render(ch, colour, gw, gh, trans):
    cell = Image.new("RGB", (gw, gh), trans)
    if ch == " ":
        return cell
    key = ch
    if key not in _cache:
        _cache[key] = _unit(ch)
    rows = _cache[key]
    s = 3 if gh == 36 else 4
    ox = (gw - 8 * s) // 2
    oy = (gh - 12 * s) // 2
    d = ImageDraw.Draw(cell)
    for y, r in enumerate(rows):
        for x, c in enumerate(r):
            if c == "1":
                d.rectangle((ox + x * s, oy + y * s, ox + (x + 1) * s - 1, oy + (y + 1) * s - 1), fill=colour)
    return cell

"""fr0gOS "MONO SMALL CAPS" glyph renderer: DejaVu Sans Mono Bold capitals at small-cap height (about 3/4 of full
cap height), hard-edged (no AA). Digits and punctuation share the same height. Used via FROG_RENDERER."""
import os
from PIL import Image, ImageDraw, ImageFont

FACE = os.environ.get("MC_FACE", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf")
_fonts = {}


def _font(sz):
    if sz not in _fonts:
        _fonts[sz] = ImageFont.truetype(FACE, sz)
    return _fonts[sz]


def render(ch, colour, gw, gh, trans):
    cell = Image.new("RGB", (gw, gh), trans)
    if ch == " ":
        return cell
    cap = 20 if gh == 36 else 30            # small-cap height in px (full caps would be ~26 / ~39)
    sz = round(cap / 0.729)
    f = _font(sz)
    ch = ch.upper() if ch.isalpha() else ch
    m = Image.new("L", (gw * 2, gh * 2), 0)
    d = ImageDraw.Draw(m)
    base = (gh + cap) // 2 + gh // 2 - gh // 2
    adv = f.getlength(ch)
    x = (gw - adv) / 2
    d.text((gw // 2 + x - gw / 2 + gw // 2 - gw // 2, base), ch, font=f, fill=255, anchor="ls")
    m = m.crop((0, 0, gw, gh)).point(lambda v: 255 if v > 118 else 0)
    cell.paste(colour, (0, 0), m)
    return cell

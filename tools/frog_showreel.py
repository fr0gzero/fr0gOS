#!/usr/bin/env python3
"""One labelled GIF that plays the whole frog set back to back, and a count of unique frames."""
import hashlib
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_anim as A  # noqa: E402
from frog_dos import W, H  # noqa: E402

ORDER = [("boot", 1), ("rest", 1), ("teleport_out", 1), ("teleport_in", 1), ("flip", 1), ("low_battery", 3),
         ("squash", 1), ("glitch", 1), ("peekaboo", 1)]
S = 5
LABEL = 34
frames, durs, unique = [], [], set()
for key, loops in ORDER:
    title, fr = A.ANIMS[key]
    name = title.split("  -")[0]
    for _ in range(loops):
        for im, ms in fr:
            cell = Image.new("RGB", (W, H), (0, 0, 0))
            cell.paste(im, (0, 0), im)
            unique.add(hashlib.md5(cell.tobytes()).hexdigest())
            canvas = Image.new("RGB", (W * S, H * S + LABEL), (16, 16, 16))
            canvas.paste(cell.resize((W * S, H * S), Image.NEAREST), (0, LABEL))
            ImageDraw.Draw(canvas).text((8, 10), name, fill=(120, 240, 150))
            frames.append(canvas)
            durs.append(ms)
out = sys.argv[1]
frames[0].save(out, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)
print("showreel", len(frames), "frames,", round(sum(durs) / 1000, 1), "s,", len(unique), "unique glyphs needed")

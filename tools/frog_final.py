#!/usr/bin/env python3
"""The final frog set: one labelled showreel GIF, a trigger list image, and the glyph count."""
import hashlib
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_anim as A  # noqa: E402
import frog_events as E  # noqa: E402
import frog_hop as HP  # noqa: E402
from frog_dos import W, H  # noqa: E402

SAFE = [(A.IDLE, 300), (A.BLINK, 150), (E.SLEEPY, 1800)]           # eyes close and stay closed
HOP = [(HP.CROUCH, 70)] + [(a, 60) for a, b in HP.HOP_L] + [(HP.LAND, 70)]
SET = [
    ("BOOT", "power on: CRT line opens, frog appears", A.ANIMS["boot"][1]),
    ("REST", "idle: blink, look left / right / up, smile", A.ANIMS["rest"][1]),
    ("HOP", "moving: hops cell to cell, wraps off the screen edge", HOP * 2),
    ("ARMED", "on arm: snaps to attention", E.EVENTS["armed"][1]),
    ("MODE HOP", "flight mode / air mode change: hop-dance in place", E.EVENTS["mode"][1]),
    ("PUNCH", "throttle past 90%: speed lines", E.EVENTS["punch"][1]),
    ("FLIP / ROLL", "a 360 flip or roll: rolls over and back", E.EVENTS["trick_flip_roll"][1]),
    ("SPIN", "a 360 yaw spin: front, side, back, side", E.EVENTS["trick_spin"][1]),
    ("SQUASH", "pulling high G: flattens and springs back", A.ANIMS["squash"][1]),
    ("CRASH", "4.5 G+ hit: splat, then dizzy with stars", E.EVENTS["crash"][1]),
    ("NEW HIGH SCORE", "beats your best G: star eyes, gold sparkles", E.EVENTS["record"][1]),
    ("UPSIDE DOWN", "quad inverted or turtle: spins over, holds, looks around, kicks", A.ANIMS["flip"][1]),
    ("LOW BATTERY", "LOW and below: jumps at the voltage, arms up, red !", A.ANIMS["low_battery"][1] * 2),
    ("PEEKABOO", "idle now and then: peeks out from the edge", A.ANIMS["peekaboo"][1]),
    ("SAFE", "on disarm: eyes close and stay closed", SAFE),
]

if __name__ == "__main__":
    out = sys.argv[1]
    S, LABEL = 5, 46
    frames, durs, uniq = [], [], set()
    for name, why, fr in SET:
        for im, ms in fr:
            cell = Image.new("RGB", (W, H), (0, 0, 0))
            cell.paste(im, (0, 0), im)
            uniq.add(hashlib.md5(cell.tobytes()).hexdigest())
            c = Image.new("RGB", (W * S, H * S + LABEL), (16, 16, 16))
            c.paste(cell.resize((W * S, H * S), Image.NEAREST), (0, LABEL))
            d = ImageDraw.Draw(c)
            d.text((8, 8), name, fill=(120, 240, 150))
            d.text((8, 26), why[:34], fill=(150, 150, 150))
            frames.append(c)
            durs.append(ms)
    for a, b in HP.HOP_L + HP.HOP_R:                 # the other half of each hop pair is a glyph too
        for g in (a, b):
            cell = Image.new("RGB", (W, H), (0, 0, 0))
            cell.paste(g, (0, 0), g)
            uniq.add(hashlib.md5(cell.tobytes()).hexdigest())
    frames[0].save(os.path.join(out, "frog_final_showreel.gif"), save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)

    # trigger list with a still of each
    rowh = H * 2 + 12
    sheet = Image.new("RGB", (900, len(SET) * rowh + 60), (16, 16, 16))
    d = ImageDraw.Draw(sheet)
    d.text((20, 14), f"FROGOS FROG - FINAL SET   ({len(uniq)} glyphs in the goggle font, about 104 free once the boot logo goes)", fill=(230, 230, 230))
    y = 44
    for name, why, fr in SET:
        key = fr[len(fr) // 2][0] if name not in ("REST", "SAFE", "ARMED") else fr[-1][0] if name != "REST" else fr[0][0]
        cell = Image.new("RGB", (W, H), (0, 0, 0))
        cell.paste(key, (0, 0), key)
        sheet.paste(cell.resize((W * 2, H * 2), Image.NEAREST), (20, y))
        d.text((110, y + 30), name, fill=(120, 240, 150))
        d.text((300, y + 30), why, fill=(200, 200, 200))
        y += rowh
    sheet.save(os.path.join(out, "frog_final_list.png"))
    print(len(frames), "frames", round(sum(durs) / 1000, 1), "s,", len(uniq), "unique glyphs")

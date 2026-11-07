#!/usr/bin/env python3
"""Full OSD demo (layout C, Four Dash Two): boot, then a mock flight that triggers every frog animation, with the
event log and readouts reacting. Half-size GIF.

usage: frog_osd_demo.py <out.gif>
"""
import os
import random
import re
import sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_anim as A  # noqa: E402
import frog_events as E  # noqa: E402
import frog_hop as HP  # noqa: E402
import frog_boot as B  # noqa: E402
import frog_final as F  # noqa: E402

COLS, ROWS = HP.COLS, HP.ROWS
hdr = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "bf", "src", "main", "osd", "frog_charmap.h")).read()
MAPS = {}
for name in ("Amber", "Red"):
    body = re.search(r"frog%sMap\[64\] = \{([^}]*)\}" % name, hdr).group(1)
    MAPS[name] = [int(v, 16) for v in re.findall(r"0x([0-9A-F]{2})", body)]
GLYPHS = {}
rnd = random.Random(3)


def g(code):
    if code not in GLYPHS:
        GLYPHS[code] = HP.glyph(code)
    return GLYPHS[code]


def colour(c, sev):
    if sev and 0x20 <= c <= 0x5F:
        return MAPS["Amber" if sev == 1 else "Red"][c - 0x20] or c
    return c


def text(img, col, row, s, sev=0, right=False):
    x = COLS - len(s) if right else col
    for i, ch in enumerate(s):
        if ch != " ":
            HP.put(img, x + i, row, g(colour(ord(ch), sev)))


PIC = Image.new("RGB", (COLS * HP.FGW, ROWS * HP.FGH), (0, 0, 0))
_pw = ROWS * HP.FGH * 4 // 3
_x0 = (PIC.width - _pw) // 2
for y in range(PIC.height):
    t = y / PIC.height
    col = (int(70 + 60 * (1 - t)), int(82 + 50 * (1 - t)), int(96 + 40 * (1 - t))) if t < 0.55 else (int(58 + 30 * t), int(48 + 22 * t), int(40 + 10 * t))
    PIC.paste(col, (_x0, y, _x0 + _pw, y + 1))

S = dict(vbat=("3.71V", 0), mah="135\x07", amp="2.10A", lq="LQ100", rate="F1000", ch="R8", pwr="200MW",
         craft="MK4-2", time="00:00", warn=("", 0), arm="SAFE", mode="ACRO", air="AIR", thr=("12.4%", 0), rpm=("14210", 0), gf=("1.0G", 0))
FEED = []      # (text, sev, t_ms)
clock = [0]
frames, durs = [], []
FROG = {"pos": (4, 6), "img": A.IDLE, "extra": []}
CENTRE = [None]


def post(msg, sev=0):
    FEED.insert(0, (msg, sev, clock[0]))
    del FEED[5:]


def render():
    im = PIC.copy()
    t = clock[0]
    for i, (msg, sev, at) in enumerate(FEED):           # event log, newest on top, 4 s then gone
        age = t - at
        if age < 4000:
            s = msg if age > 45 * len(msg) + 60 else msg[:max(0, (age - 60) // 45)]
            text(im, 0, 1 + i, s, sev if age < 2500 else 0)
        elif age < 4300:
            for j in range(len(msg)):
                if age < 4000 + 60 + 45 * j:
                    HP.put(im, j, 1 + i, g(0xFD + rnd.randrange(3)))
    text(im, 0, 7, S["vbat"][0], S["vbat"][1]); text(im, 0, 8, S["mah"]); text(im, 0, 9, S["amp"])
    text(im, 0, 13, S["lq"]); text(im, 0, 14, S["rate"]); text(im, 0, 15, S["ch"]); text(im, 0, 16, S["pwr"])
    text(im, 0, 0, S["craft"], right=True); text(im, 0, 1, S["time"], right=True)
    text(im, 0, 2, S["warn"][0], S["warn"][1], right=True)
    text(im, 0, 3, S["arm"], right=True); text(im, 0, 4, S["mode"], right=True); text(im, 0, 5, S["air"], right=True)
    text(im, 0, 12, "THR", right=True); text(im, 0, 13, S["thr"][0], S["thr"][1], right=True)
    text(im, 0, 14, "RPM", right=True); text(im, 0, 15, S["rpm"][0], S["rpm"][1], right=True)
    text(im, 0, 16, S["gf"][0], S["gf"][1], right=True)
    if CENTRE[0]:
        text(im, COLS // 2 - len(CENTRE[0]) // 2, ROWS // 2, CENTRE[0])
    c, r = FROG["pos"]
    HP.put(im, c, r, FROG["img"])
    for (cc, rr, gg) in FROG["extra"]:
        HP.put(im, cc, rr, gg)
    return im


def show(ms):
    frames.append(render().resize((COLS * HP.FGW // 2, ROWS * HP.FGH // 2), Image.NEAREST))
    durs.append(ms)
    clock[0] += ms


def play(seq, reps=1):
    for _ in range(reps):
        for f, ms in seq:
            FROG["img"] = f
            show(ms)
    FROG["img"] = A.IDLE


def hop(direction):
    c, r = FROG["pos"]
    FROG["img"] = HP.CROUCH; show(60)
    for a, b in (HP.HOP_R if direction > 0 else HP.HOP_L):
        FROG["img"] = a
        FROG["extra"] = [(c + direction, r, b)]
        show(55)
    FROG["extra"] = []
    FROG["pos"] = (c + direction, r)
    FROG["img"] = HP.LAND; show(60)
    FROG["img"] = A.IDLE


def travel(to_side, to_row, ledge_col):
    """hop out to the edge on this row, wrap round, hop in to the ledge on the other side"""
    c, r = FROG["pos"]
    d = -1 if c < COLS // 2 else 1
    while 0 <= FROG["pos"][0] + d < COLS:
        hop(d)
    hop(d)                                              # off the edge
    FROG["pos"] = (COLS if d < 0 else -1, to_row) if to_side == "right" else (-1 if d > 0 else COLS, to_row)
    show(200)
    d2 = -1 if to_side == "right" else 1
    while FROG["pos"][0] != ledge_col:
        hop(d2)


def centre(msg):
    for k in range(4):
        CENTRE[0] = "".join(chr(0xFD + rnd.randrange(3)) if j >= k * 2 else msg[j] for j in range(len(msg)))
        show(90)
    CENTRE[0] = msg; show(700)
    CENTRE[0] = None


# ---- 1. boot ----
for f, d in zip(B.frames, B.durs):
    frames.append(f); durs.append(d); clock[0] += d
# ---- 2. OSD up, frog on the ledge above the voltage, resting ----
FROG["pos"] = (4, 6)
play(A.ANIMS["rest"][1][:6])
# ---- 3. arm ----
S["arm"] = "ARMED"; centre("ARMED"); post("ARMED")
play(E.EVENTS["armed"][1])
# ---- 4. mode change ----
S["mode"] = "ANGLE"; post("ANGLE"); play(E.EVENTS["mode"][1])
S["mode"] = "ACRO"; post("ACRO"); play(E.EVENTS["mode"][1])
# ---- 5. punch ----
S["thr"] = ("96.3%", 2); S["rpm"] = ("41870", 2); S["amp"] = "9.84A"; S["vbat"] = ("3.52V", 0); post("PUNCH", 1)
play(E.EVENTS["punch"][1])
S["thr"] = ("47.1%", 0); S["rpm"] = ("33370", 1); S["amp"] = "6.81A"; S["vbat"] = ("3.71V", 0)
# ---- 6. hop across to the other column ----
travel("right", 11, COLS - 3)
# ---- 7. tricks ----
post("FLIP"); play(E.EVENTS["trick_flip_roll"][1])
post("SPIN"); play(E.EVENTS["trick_spin"][1])
# ---- 8. high G, new record ----
S["gf"] = ("2.8G", 2); play(A.ANIMS["squash"][1][:5])
S["gf"] = ("3.9G", 2); post("RECRD", 2); play(E.EVENTS["record"][1])
S["gf"] = ("1.0G", 0)
# ---- 9. crash, turtle ----
S["gf"] = ("5.1G", 2); post("CRASH", 2); play(E.EVENTS["crash"][1])
S["gf"] = ("1.0G", 0); S["warn"] = ("TURTL", 2); post("TURTL", 2); play(A.ANIMS["flip"][1])
S["warn"] = ("", 0)
# ---- 10. low battery: back over to the voltage, jumping at it ----
S["vbat"] = ("3.48V", 1); S["warn"] = ("LOWV", 1)
travel("left", 6, 4)
play(A.ANIMS["low_battery"][1], reps=3)
# ---- 11. disarm ----
S["arm"] = "SAFE"; S["warn"] = ("", 0); S["thr"] = ("0.0%", 0); S["rpm"] = ("0", 0); post("SAFE")
play(F.SAFE)
FROG["img"] = E.SLEEPY; show(1500)

out = sys.argv[1]
frames[0].save(out, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)
print(len(frames), "frames", round(sum(durs) / 1000, 1), "s")

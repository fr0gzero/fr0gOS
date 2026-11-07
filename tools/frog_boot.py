#!/usr/bin/env python3
"""Boot screen with the frog: CRT power-on at the top-left of the boot text, hops right along the row above it
while the checks type in, then celebrates (spin + star eyes + smile) when everything is OK.

usage: frog_boot.py <out.gif>
"""
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_anim as A  # noqa: E402
import frog_events as E  # noqa: E402
import frog_hop as HP  # noqa: E402

LINES = ["FR0GOS V1.3 R09",
         "CPU   F411 168MHZ    OK",
         "GYRO                 OK",
         "RX    F1000          OK",
         "VIDEO HDZERO         OK",
         "VTX   R8 200MW       OK",
         "ESC   4/4 BIDIR      OK",
         "BATT  4.18V          OK",
         "UP    0H12M   #3       "]
X0 = HP.COLS // 2 - 12
Y0 = (HP.ROWS - len(LINES)) // 2 + 1
FROG_ROW = Y0 - 1


def base(t_ms):
    img = Image.new("RGB", (HP.COLS * HP.FGW, HP.ROWS * HP.FGH), (0, 0, 0))
    per_line = 520
    for i, line in enumerate(LINES):
        start = i * per_line
        if t_ms < start:
            break
        n = min(len(line), int((t_ms - start) / 18) + 1)
        shown = line[:n]
        for j, ch in enumerate(shown):
            if ch != " ":
                col = HP.glyph(ord(ch))
                HP.put(img, X0 + j, Y0 + i, col)
        if n < len(line):
            HP.put(img, X0 + n, Y0 + i, HP.glyph(0xFC))      # cursor rides the typing
    return img


frames, durs = [], []
clock = [0]


def frame(cells, ms):
    im = base(clock[0])
    for c, r, g in cells:
        HP.put(im, c, r, g)
    frames.append(im.resize((im.width // 2, im.height // 2), Image.NEAREST))
    durs.append(ms)
    clock[0] += ms


# 1. CRT power-on at the top-left of the boot block
for f, ms in A.ANIMS["boot"][1][:8]:
    frame([(X0, FROG_ROW, f)], max(60, ms // 2))
# 2. hop right along the top while the checks type in
c = X0
end = X0 + len(LINES[0].rstrip()) - 1          # stop over the last letter of the header, never past the text
while c < end:
    frame([(c, FROG_ROW, HP.CROUCH)], 40)
    for a, b in HP.HOP_R:
        frame([(c, FROG_ROW, a), (c + 1, FROG_ROW, b)], 40)
    frame([(c + 1, FROG_ROW, HP.LAND)], 40)
    c += 1
    if c % 6 == 0:                                           # a little look around now and then
        frame([(c, FROG_ROW, A.LOOK_L)], 160)
# 3. early? fill the wait with random little animations (a different mix every boot)
import random  # noqa: E402
FILLERS = [
    [(A.BLINK, 140), (A.IDLE, 300)],
    [(A.LOOK_L, 500), (A.IDLE, 200)],
    [(A.LOOK_R, 500), (A.IDLE, 200)],
    [(A.LOOK_UP, 500), (A.IDLE, 200)],
    [(A.SMILE, 600), (A.IDLE, 200)],
    E.EVENTS["mode"][1][1:],
]
rng = random.Random()
boot_done = len(LINES) * 520 + 400
while clock[0] < boot_done:
    for f, ms in rng.choice(FILLERS):
        frame([(c, FROG_ROW, f)], ms)
# 4. all OK: celebrate where it stands
for f, ms in E.EVENTS["trick_spin"][1][1:-1]:
    frame([(c, FROG_ROW, f)], ms)
for f, ms in E.EVENTS["record"][1][1:-1]:
    frame([(c, FROG_ROW, f)], ms)
frame([(c, FROG_ROW, A.SMILE)], 900)

if __name__ == "__main__":
    out = sys.argv[1]
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=durs, loop=0, disposal=2)
    print(len(frames), "frames", round(sum(durs) / 1000, 1), "s")

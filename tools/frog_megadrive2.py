#!/usr/bin/env python3
"""Mega Drive style frogs, round two: six more body types, three frames each.

usage: frog_megadrive2.py <out.png>
"""
import os
import sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frog_megadrive as M  # noqa: E402
from frog_megadrive import Sprite, eyes, GW, GH, PX  # noqa: E402

M.TONES.update({
    "N": ((90, 50, 20), (150, 90, 40), (210, 150, 90)),       # leather
    "V": ((80, 30, 140), (150, 80, 230), (210, 170, 255)),    # violet
    "T": ((20, 80, 160), (40, 140, 230), (140, 200, 255)),    # tree-frog blue flank
    "Q": ((170, 120, 0), (240, 190, 40), (255, 240, 160)),    # gold visor
})


def treefrog(pose):
    """red-eyed tree frog, clinging to a branch side-on"""
    s = Sprite()
    dy = {"cling": 0, "peek": 0, "leap": -4}[pose]
    s.shape("N", lambda d: d.rectangle([0, 22, 17, 24], fill=1))                       # branch
    s.shape("G", lambda d: d.ellipse([2, 9 + dy, 14, 20 + dy], fill=1))
    s.shape("T", lambda d: d.ellipse([4, 14 + dy, 12, 19 + dy], fill=1))                # blue flank
    s.shape("Y", lambda d: d.line([5, 17 + dy, 11, 17 + dy], fill=1))                   # yellow stripes
    s.shape("G", lambda d: d.ellipse([9, 5 + dy, 17, 13 + dy], fill=1))                 # head
    s.shape("R", lambda d: d.ellipse([11, 4 + dy, 16, 9 + dy], fill=1))                 # big red eye
    s.ink(lambda d: d.rectangle([13 + (1 if pose == "peek" else 0), 6 + dy, 14 + (1 if pose == "peek" else 0), 7 + dy], fill=1))
    s.ink(lambda d: d.line([11, 11 + dy, 16, 11 + dy], fill=1))
    if pose == "leap":
        s.shape("G", lambda d: (d.line([4, 18 + dy, 0, 26], fill=1, width=2), d.line([12, 18 + dy, 16, 25], fill=1, width=2)))
        s.shape("O", lambda d: (d.ellipse([0, 24, 2, 26], fill=1), d.ellipse([15, 24, 17, 26], fill=1)))
    else:
        s.shape("G", lambda d: (d.line([4, 18, 3, 22], fill=1, width=2), d.line([12, 18, 14, 22], fill=1, width=2)))
        s.shape("O", lambda d: (d.ellipse([1, 21, 4, 23], fill=1), d.ellipse([13, 21, 16, 23], fill=1)))   # orange toe pads
    return s.render()


def aviator(pose):
    """FPV pilot: leather cap, goggles up, flying scarf"""
    s = Sprite()
    s.shape("G", lambda d: d.ellipse([3, 6, 15, 17], fill=1))
    s.shape("N", lambda d: d.chord([3, 2, 15, 14], 180, 360, fill=1))                    # leather cap
    s.shape("N", lambda d: (d.rectangle([2, 8, 4, 13], fill=1), d.rectangle([14, 8, 16, 13], fill=1)))   # ear flaps
    if pose == "goggles":
        s.shape("C", lambda d: (d.ellipse([4, 8, 8, 12], fill=1), d.ellipse([10, 8, 14, 12], fill=1)))
        s.shape("N", lambda d: d.line([8, 10, 10, 10], fill=1))
    else:
        s.shape("C", lambda d: (d.ellipse([5, 4, 8, 7], fill=1), d.ellipse([10, 4, 13, 7], fill=1)))    # goggles up on the cap
        eyes(s, [5, 8, 8, 11], [10, 8, 13, 11], 0)
    s.ink(lambda d: d.arc([6, 11, 12, 16], 20, 160, fill=1))
    s.shape("G", lambda d: d.rounded_rectangle([5, 16, 13, 23], 2, fill=1))
    s.shape("Y", lambda d: d.ellipse([7, 17, 11, 22], fill=1))
    tail = {"idle": [(12, 16), (17, 18), (15, 20)], "goggles": [(12, 16), (17, 15), (16, 18)], "salute": [(12, 16), (17, 17), (16, 19)]}[pose]
    s.shape("R", lambda d: (d.rectangle([5, 15, 13, 16], fill=1), d.polygon(tail, fill=1)))     # scarf
    if pose == "salute":
        s.shape("G", lambda d: d.line([5, 17, 3, 9], fill=1, width=2))
    else:
        s.shape("G", lambda d: d.line([5, 17, 2, 21], fill=1, width=2))
    s.shape("G", lambda d: d.line([13, 17, 16, 21], fill=1, width=2))
    s.shape("N", lambda d: (d.rounded_rectangle([4, 23, 8, 26], 1, fill=1), d.rounded_rectangle([10, 23, 14, 26], 1, fill=1)))   # boots
    return s.render()


def astronaut(pose):
    s = Sprite()
    lift = -4 if pose == "float" else 0
    s.shape("W", lambda d: d.ellipse([2, 1 + lift, 16, 15 + lift], fill=1))              # helmet
    s.shape("Q" if pose != "visor up" else "C", lambda d: d.ellipse([4, 4 + lift, 14, 12 + lift], fill=1))   # gold visor
    if pose == "visor up":
        s.shape("G", lambda d: d.ellipse([5, 6 + lift, 13, 12 + lift], fill=1))
        eyes(s, [6, 6 + lift, 8, 9 + lift], [10, 6 + lift, 12, 9 + lift], 0)
    else:
        s.shape("W", lambda d: d.point((6, 6 + lift), fill=1))
    s.shape("W", lambda d: d.rounded_rectangle([4, 14 + lift, 14, 22 + lift], 2, fill=1))
    s.shape("R", lambda d: d.rectangle([7, 16 + lift, 11, 18 + lift], fill=1))           # chest panel
    s.shape("S", lambda d: d.rectangle([1, 15 + lift, 4, 21 + lift], fill=1))            # backpack
    s.shape("W", lambda d: (d.rectangle([5, 22 + lift, 8, 26 + lift], fill=1), d.rectangle([10, 22 + lift, 13, 26 + lift], fill=1)))
    if pose == "float":
        s.shape("W", lambda d: d.line([14, 16 + lift, 17, 11 + lift], fill=1, width=2))
        s.shape("Y", lambda d: (d.point((1, 2), fill=1), d.point((16, 24), fill=1), d.point((3, 25), fill=1)))
    else:
        s.shape("W", lambda d: d.line([14, 16, 16, 21], fill=1, width=2))
    return s.render()


def rockstar(pose):
    s = Sprite()
    s.shape("G", lambda d: d.ellipse([4, 2, 14, 12], fill=1))
    s.shape("K", lambda d: None)
    s.ink(lambda d: (d.rectangle([4, 5, 14, 6], fill=1), d.rectangle([5, 6, 8, 7], fill=1), d.rectangle([10, 6, 13, 7], fill=1)))   # shades
    s.shape("W", lambda d: d.point((6, 6), fill=1))
    s.ink(lambda d: d.arc([6, 7, 12, 11], 20, 160, fill=1))
    s.shape("V", lambda d: d.rounded_rectangle([4, 12, 14, 20], 2, fill=1))              # violet jacket
    s.shape("G", lambda d: d.rectangle([8, 12, 10, 19], fill=1))
    tilt = {"strum": 0, "jump": -3, "point": 0}[pose]
    s.shape("R", lambda d: d.ellipse([3, 16 + tilt, 10, 22 + tilt], fill=1))           # guitar body
    s.shape("N", lambda d: d.line([9, 17 + tilt, 17, 10 + tilt], fill=1, width=2))      # neck
    s.ink(lambda d: d.ellipse([5, 18 + tilt, 7, 20 + tilt], fill=1))
    if pose == "point":
        s.shape("G", lambda d: d.line([14, 13, 17, 8], fill=1, width=2))
    s.shape("G", lambda d: (d.rectangle([5, 20, 8, 24 + (0 if pose != "jump" else -2)], fill=1), d.rectangle([10, 20, 13, 24], fill=1)))
    s.shape("K", lambda d: None)
    s.shape("W", lambda d: (d.rectangle([4, 24, 8, 26], fill=1), d.rectangle([10, 24, 14, 26], fill=1)))
    if pose == "jump":
        s.shape("Y", lambda d: (d.point((1, 3), fill=1), d.point((16, 2), fill=1), d.point((2, 12), fill=1)))
    return s.render()


def knight(pose):
    s = Sprite()
    s.shape("S", lambda d: d.chord([3, 1, 15, 13], 180, 360, fill=1))                    # helmet
    s.shape("R", lambda d: d.polygon([(9, 1), (12, -2), (14, 2)], fill=1))                # plume
    s.shape("G", lambda d: d.ellipse([4, 5, 14, 13], fill=1))
    eyes(s, [5, 6, 8, 9], [10, 6, 13, 9], 1)
    s.ink(lambda d: d.line([7, 11, 11, 11], fill=1))
    s.shape("S", lambda d: d.rounded_rectangle([4, 13, 14, 21], 2, fill=1))              # armour
    s.shape("Y", lambda d: d.rectangle([8, 14, 10, 20], fill=1))
    s.shape("B", lambda d: d.rounded_rectangle([0, 13, 5, 21], 2, fill=1))               # blue shield
    s.shape("Y", lambda d: d.line([2, 15, 2, 19], fill=1))
    if pose == "slash":
        s.shape("W", lambda d: d.line([13, 15, 17, 3], fill=1, width=2))
        s.shape("C", lambda d: d.arc([8, 0, 18, 12], 270, 360, fill=1))
    elif pose == "raise":
        s.shape("W", lambda d: d.line([14, 13, 15, 1], fill=1, width=2))
        s.shape("Y", lambda d: d.point((15, 0), fill=1))
    else:
        s.shape("W", lambda d: d.line([14, 15, 16, 25], fill=1, width=2))
    s.shape("Y", lambda d: d.line([13, 15, 16, 15], fill=1))
    s.shape("S", lambda d: (d.rectangle([5, 21, 8, 24], fill=1), d.rectangle([10, 21, 13, 24], fill=1)))
    s.shape("N", lambda d: (d.rectangle([4, 24, 8, 26], fill=1), d.rectangle([10, 24, 14, 26], fill=1)))
    return s.render()


def skater(pose):
    s = Sprite()
    lean = {"ride": 0, "ollie": -4, "grind": 0}[pose]
    board = [(1, 23 + lean), (17, 23 + lean)] if pose != "grind" else [(1, 25), (17, 21)]
    s.shape("C", lambda d: d.line(board, fill=1, width=2))                               # hoverboard
    if pose != "ollie":
        s.shape("O", lambda d: (d.point((3, 26), fill=1), d.point((14, 26), fill=1)))      # thrusters
    s.shape("G", lambda d: d.ellipse([5, 4 + lean, 15, 13 + lean], fill=1))
    s.shape("O", lambda d: d.chord([4, 2 + lean, 15, 10 + lean], 180, 360, fill=1))      # backwards cap
    s.shape("O", lambda d: d.rectangle([1, 6 + lean, 5, 7 + lean], fill=1))
    eyes(s, [7, 7 + lean, 9, 10 + lean], [11, 7 + lean, 13, 10 + lean], 1)
    s.ink(lambda d: d.arc([8, 9 + lean, 14, 13 + lean], 20, 160, fill=1))
    s.shape("T", lambda d: d.rounded_rectangle([6, 13 + lean, 14, 19 + lean], 2, fill=1))   # hoodie
    s.shape("G", lambda d: (d.line([6, 14 + lean, 2, 12 + lean], fill=1, width=2), d.line([14, 14 + lean, 17, 16 + lean], fill=1, width=2)))
    s.shape("S", lambda d: (d.line([7, 19 + lean, 5, 22 + lean], fill=1, width=2), d.line([12, 19 + lean, 14, 22 + lean], fill=1, width=2)))
    return s.render()


TYPES = [
    ("7  RED-EYED TREE FROG  - real-frog look: red eyes, blue flanks, orange toe pads, on a branch (cling / peek / leap)", treefrog, ("cling", "peek", "leap")),
    ("8  AVIATOR  - leather cap, goggles, red scarf flying (idle / goggles down / salute)", aviator, ("idle", "goggles", "salute")),
    ("9  ASTRONAUT  - white suit, gold visor, backpack (stand / visor up / float)", astronaut, ("stand", "visor up", "float")),
    ("10  ROCKSTAR  - shades, violet jacket, red guitar (strum / jump / point)", rockstar, ("strum", "jump", "point")),
    ("11  KNIGHT  - steel helmet with plume, blue shield, sword (guard / slash / raise)", knight, ("guard", "slash", "raise")),
    ("12  SKATER  - backwards cap, hoodie, cyan hoverboard (ride / ollie / grind)", skater, ("ride", "ollie", "grind")),
]

if __name__ == "__main__":
    S = 4
    W, H = GW * PX, GH * PX
    cw = W * S + 30
    rowh = H * S + 50
    sheet = Image.new("RGB", (3 * cw + 40 + 2 * W + 60, len(TYPES) * rowh + 20), (16, 16, 16))
    dd = ImageDraw.Draw(sheet)
    y = 10
    for title, fn, poses in TYPES:
        dd.text((20, y), title, fill=(230, 230, 230))
        for i, p in enumerate(poses):
            im = fn(p)
            cell = Image.new("RGB", (W, H), (0, 0, 0))
            cell.paste(im, (0, 0), im)
            sheet.paste(cell.resize((W * S, H * S), Image.NEAREST), (20 + i * cw, y + 16))
            dd.text((20 + i * cw, y + 18 + H * S), p, fill=(150, 150, 150))
            if i == 0:
                sheet.paste(cell, (40 + 3 * cw, y + 16))
                dd.text((40 + 3 * cw, y + 20 + H), "actual size", fill=(140, 140, 140))
        y += rowh
    sheet.save(sys.argv[1])
    print("ok", sheet.size)

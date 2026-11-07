#!/usr/bin/env python3
"""Mega Drive style frogs: 18x27 sprite grid (2x pixels on the 36x54 FHD cell), three-tone shading lit from
the top left, bold black outline, green body with coloured accents. Six body shapes, three frames each.

usage: frog_megadrive.py <out.png>
"""
import sys
from PIL import Image, ImageDraw

GW, GH, PX = 18, 27, 2
TONES = {   # base -> (shadow, base, highlight)
    "G": ((25, 110, 55), (60, 190, 90), (150, 245, 160)),
    "R": ((140, 20, 20), (225, 45, 45), (255, 140, 120)),
    "Y": ((190, 130, 0), (255, 205, 40), (255, 245, 170)),
    "B": ((30, 50, 150), (60, 110, 230), (150, 190, 255)),
    "O": ((180, 70, 0), (255, 140, 30), (255, 210, 130)),
    "C": ((30, 130, 170), (90, 210, 255), (210, 250, 255)),
    "W": ((180, 190, 200), (240, 245, 245), (255, 255, 255)),
    "P": ((200, 70, 120), (255, 130, 175), (255, 210, 225)),
    "D": ((15, 70, 35), (30, 120, 60), (60, 170, 90)),
    "S": ((90, 95, 110), (150, 155, 170), (210, 215, 225)),
    "E": ((245, 250, 245), (245, 250, 245), (255, 255, 255)),     # eye whites: flat, so the pupils read
}
K = (0, 0, 0)


class Sprite:
    def __init__(self):
        self.layers = []      # (key, mask image)

    def shape(self, key, fn):
        m = Image.new("1", (GW, GH), 0)
        fn(ImageDraw.Draw(m))
        self.layers.append((key, m))
        return self

    def ink(self, fn):
        """flat black details (pupils, mouths) drawn last, no shading"""
        m = Image.new("1", (GW, GH), 0)
        fn(ImageDraw.Draw(m))
        self.layers.append(("K", m))
        return self

    def render(self):
        img = Image.new("RGBA", (GW, GH), (0, 0, 0, 0))
        owner = [[None] * GW for _ in range(GH)]
        for key, m in self.layers:
            mp = m.load()
            for y in range(GH):
                for x in range(GW):
                    if mp[x, y]:
                        owner[y][x] = key
        px = img.load()
        for y in range(GH):
            for x in range(GW):
                k = owner[y][x]
                if k is None:
                    continue
                if k == "K":
                    px[x, y] = K + (255,)
                    continue
                sh, base, hi = TONES[k]
                def same(dx, dy):
                    xx, yy = x + dx, y + dy
                    return 0 <= xx < GW and 0 <= yy < GH and owner[yy][xx] == k
                c = base
                if not same(-1, -1) or not same(0, -1):
                    c = hi
                if not same(1, 1) or not same(0, 1):
                    c = sh
                px[x, y] = c + (255,)
        out = img.copy()
        op = out.load()
        for y in range(GH):
            for x in range(GW):
                if px[x, y][3]:
                    continue
                if any(0 <= x + dx < GW and 0 <= y + dy < GH and px[x + dx, y + dy][3] and px[x + dx, y + dy][:3] != K
                       for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                    op[x, y] = K + (255,)
        return out.resize((GW * PX, GH * PX), Image.NEAREST)


def eyes(s, l, r, look=1, wide=False):
    s.shape("E", lambda d: (d.ellipse(l, fill=1), d.ellipse(r, fill=1)))
    for e in (l, r):
        cx, cy = (e[0] + e[2]) // 2 + look, (e[1] + e[3]) // 2
        s.ink(lambda d, cx=cx, cy=cy: d.rectangle([cx - 1 if look <= 0 else cx, cy, cx if look <= 0 else cx + 1, cy + 1], fill=1))


def hero(pose):
    s = Sprite()
    lift = -3 if pose == "jump" else 0
    s.shape("G", lambda d: d.ellipse([3, 3 + lift, 15, 14 + lift], fill=1))
    s.shape("G", lambda d: d.rounded_rectangle([6, 13 + lift, 12, 20 + lift], 2, fill=1))
    s.shape("Y", lambda d: d.ellipse([7, 14 + lift, 11, 19 + lift], fill=1))
    eyes(s, [5, 4 + lift, 8, 9 + lift], [10, 4 + lift, 13, 9 + lift], 1)
    s.ink(lambda d: d.line([7, 12 + lift, 11, 12 + lift], fill=1))
    if pose == "jump":
        s.shape("W", lambda d: (d.ellipse([1, 0, 4, 3], fill=1), d.ellipse([14, 0, 17, 3], fill=1)))
        s.shape("G", lambda d: (d.line([4, 3, 6, 13], fill=1, width=2), d.line([14, 3, 12, 13], fill=1, width=2)))
        s.shape("R", lambda d: (d.rounded_rectangle([4, 18, 8, 21], 1, fill=1), d.rounded_rectangle([10, 18, 14, 21], 1, fill=1)))
    else:
        s.shape("G", lambda d: (d.line([6, 15, 3, 18], fill=1, width=2), d.line([12, 15, 15, 12 if pose == "thumb" else 18], fill=1, width=2)))
        s.shape("W", lambda d: (d.ellipse([1, 17, 4, 20], fill=1), d.ellipse([14, 9 if pose == "thumb" else 17, 17, 12 if pose == "thumb" else 20], fill=1)))
        s.shape("G", lambda d: (d.rectangle([6, 20, 8, 23], fill=1), d.rectangle([10, 20, 12, 23], fill=1)))
        s.shape("R", lambda d: (d.rounded_rectangle([3, 23, 9, 26], 1, fill=1), d.rounded_rectangle([9, 23, 15, 26], 1, fill=1)))
        s.shape("W", lambda d: (d.line([4, 24, 7, 24], fill=1), d.line([10, 24, 13, 24], fill=1)))
    return s.render()


def ball(pose):
    s = Sprite()
    sq = {"idle": (1, 8, 17, 26), "squish": (0, 13, 18, 26), "bounce": (2, 3, 16, 21)}[pose]
    s.shape("G", lambda d: d.ellipse(list(sq), fill=1))
    top = sq[1]
    s.shape("G", lambda d: (d.ellipse([3, top - 4, 8, top + 2], fill=1), d.ellipse([10, top - 4, 15, top + 2], fill=1)))
    eyes(s, [4, top - 3, 7, top + 1], [11, top - 3, 14, top + 1], 0)
    s.shape("B", lambda d: d.rectangle([sq[0] + 1, top + 3, sq[2] - 1, top + 4], fill=1))
    s.shape("B", lambda d: d.polygon([(sq[2] - 1, top + 3), (sq[2] + 1, top + 1), (sq[2] + 1, top + 6)], fill=1))
    s.shape("P", lambda d: (d.ellipse([sq[0] + 2, top + 8, sq[0] + 4, top + 9], fill=1), d.ellipse([sq[2] - 4, top + 8, sq[2] - 2, top + 9], fill=1)))
    s.ink(lambda d: d.arc([7, top + 6, 11, top + 10], 20, 160, fill=1))
    s.shape("O", lambda d: (d.ellipse([3, sq[3] - 2, 7, sq[3] + 0], fill=1), d.ellipse([11, sq[3] - 2, 15, sq[3]], fill=1)))
    return s.render()


def hopper(pose):
    s = Sprite()
    dy = {"sit": 0, "hop": -5, "land": 2}[pose]
    s.shape("D", lambda d: d.ellipse([0, 14 + dy, 8, 23 + dy], fill=1) if pose != "hop" else d.line([5, 18 + dy, 0, 25], fill=1, width=3))
    s.shape("G", lambda d: d.ellipse([1, 10 + dy, 13, 22 + dy], fill=1))
    s.shape("G", lambda d: d.ellipse([8, 6 + dy, 17, 16 + dy], fill=1))
    s.shape("G", lambda d: d.ellipse([11, 3 + dy, 16, 9 + dy], fill=1))
    s.shape("O", lambda d: d.ellipse([5, 14 + dy, 13, 22 + dy], fill=1))
    s.shape("E", lambda d: d.ellipse([12, 4 + dy, 15, 8 + dy], fill=1))
    s.ink(lambda d: (d.rectangle([14, 5 + dy, 14, 6 + dy], fill=1), d.line([11, 13 + dy, 17, 12 + dy], fill=1)))
    s.shape("G", lambda d: d.line([11, 19 + dy, 12, 24 + dy if pose != "hop" else 22 + dy], fill=1, width=2))
    s.shape("Y", lambda d: d.point((13, 9 + dy), fill=1))
    return s.render()


def warrior(pose):
    s = Sprite()
    s.shape("G", lambda d: d.ellipse([4, 2, 14, 11], fill=1))
    s.shape("R", lambda d: d.rectangle([4, 4, 14, 5], fill=1))
    s.shape("R", lambda d: d.polygon([(14, 4), (17, 2), (17, 7)], fill=1))
    s.shape("E", lambda d: (d.rectangle([5, 6, 8, 7], fill=1), d.rectangle([10, 6, 13, 7], fill=1)))
    s.ink(lambda d: (d.point((8, 7), fill=1), d.point((10, 7), fill=1), d.line([7, 10, 11, 10], fill=1)))
    s.shape("G", lambda d: d.rounded_rectangle([2, 11, 16, 19], 3, fill=1))
    s.shape("Y", lambda d: d.rectangle([4, 18, 14, 19], fill=1))
    if pose == "punch":
        s.shape("G", lambda d: d.line([14, 13, 17, 13], fill=1, width=3))
        s.shape("R", lambda d: d.ellipse([15, 11, 18, 15], fill=1))
    else:
        s.shape("R", lambda d: (d.ellipse([0, 15, 3, 18], fill=1), d.ellipse([15, 15, 18, 18], fill=1)))
    s.shape("G", lambda d: (d.rectangle([5, 20, 8, 24], fill=1), d.rectangle([10, 20, 13, 24], fill=1)))
    s.shape("D", lambda d: (d.rectangle([3, 24, 8, 26], fill=1), d.rectangle([10, 24, 15, 26], fill=1)))
    if pose == "flex":
        s.shape("Y", lambda d: (d.point((1, 9), fill=1), d.point((17, 9), fill=1), d.point((9, 0), fill=1)))
    return s.render()


def mecha(pose):
    s = Sprite()
    lift = -3 if pose != "stand" else 0
    s.shape("C", lambda d: d.ellipse([3, 1 + lift, 15, 12 + lift], fill=1))
    s.shape("G", lambda d: d.ellipse([5, 4 + lift, 13, 12 + lift], fill=1))
    eyes(s, [6, 5 + lift, 8, 8 + lift], [10, 5 + lift, 12, 8 + lift], 0)
    s.shape("B", lambda d: d.rounded_rectangle([2, 11 + lift, 16, 19 + lift], 2, fill=1))
    s.shape("Y", lambda d: d.rectangle([7, 13 + lift, 11, 15 + lift], fill=1))
    s.shape("S", lambda d: (d.rectangle([4, 19 + lift, 6, 23 + lift], fill=1), d.rectangle([12, 19 + lift, 14, 23 + lift], fill=1)))
    s.shape("B", lambda d: (d.rectangle([2, 23 + lift, 7, 25 + lift], fill=1), d.rectangle([11, 23 + lift, 16, 25 + lift], fill=1)))
    if pose != "stand":
        s.shape("O", lambda d: (d.polygon([(3, 26 + lift), (6, 26 + lift), (4, 26)], fill=1), d.polygon([(12, 26 + lift), (15, 26 + lift), (14, 26)], fill=1)))
        if pose == "boost":
            s.shape("Y", lambda d: (d.point((4, 25), fill=1), d.point((14, 25), fill=1)))
    s.shape("S", lambda d: d.line([15, 3 + lift, 17, 0], fill=1))
    s.shape("R", lambda d: d.point((17, 0), fill=1))
    return s.render()


def prince(pose):
    s = Sprite()
    s.shape("D", lambda d: d.ellipse([0, 20, 18, 26], fill=1))
    s.shape("P", lambda d: d.ellipse([14, 19, 17, 22], fill=1))
    s.shape("G", lambda d: d.ellipse([3, 10, 15, 22], fill=1))
    s.shape("G", lambda d: (d.ellipse([3, 6, 8, 12], fill=1), d.ellipse([10, 6, 15, 12], fill=1)))
    eyes(s, [4, 7, 7, 11], [11, 7, 14, 11], 0 if pose != "look" else 1)
    s.shape("Y", lambda d: d.polygon([(5, 6), (6, 2), (8, 5), (9, 1), (10, 5), (12, 2), (13, 6)], fill=1))
    s.shape("R", lambda d: d.point((9, 4), fill=1))
    s.shape("W", lambda d: d.ellipse([6, 15, 12, 21], fill=1))
    if pose == "tongue":
        s.shape("P", lambda d: (d.line([9, 14, 17, 9], fill=1, width=2), d.ellipse([15, 7, 18, 10], fill=1)))
    else:
        s.ink(lambda d: d.arc([6, 11, 12, 15], 20, 160, fill=1))
    return s.render()


TYPES = [
    ("1  HERO  - 16-bit mascot: big eyes, white gloves, red sneakers (idle / thumbs up / jump)", hero, ("idle", "thumb", "jump")),
    ("2  BALL  - round and squishy, blue bandana, pink blush (idle / squish / bounce)", ball, ("idle", "squish", "bounce")),
    ("3  HOPPER  - side-on, orange belly, big back leg (sit / hop / land)", hopper, ("sit", "hop", "land")),
    ("4  WARRIOR  - beat-em-up frog, red headband, gold belt (stance / punch / flex)", warrior, ("stance", "punch", "flex")),
    ("5  MECHA  - frog in a glass dome on a blue mech (stand / hover / boost)", mecha, ("stand", "hover", "boost")),
    ("6  POND PRINCE  - crowned, on a lily pad with a flower (idle / look / tongue)", prince, ("idle", "look", "tongue")),
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

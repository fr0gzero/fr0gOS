"""FrogOS frog pixel art (8 wide, up to 16 tall). Shared by the font builder and the previews.

Palette letters: G green, D dark green, L light green, W eye white, K black, C cyan flash,
B blue, P pink, R red, Y yellow, . transparent
"""
GREEN = (64, 214, 104)
PAL = {"G": GREEN, "D": (30, 128, 62), "L": (150, 255, 170), "W": (236, 255, 236), "K": (0, 0, 0),
       "C": (190, 255, 255), "B": (110, 200, 255), "P": (255, 120, 170), "R": (255, 44, 44), "Y": (255, 220, 60)}

IDLE = [".GG..GG.",
        "GWKGGWKG",
        "GGGGGGGG",
        "GKGGGGKG",
        "GGKKKKGG",
        ".GGGGGG.",
        "GG.GG.GG"]

# ---- teleport: six frames, played forwards to arrive, backwards to leave ----
TELEPORT = [
    # T1 spark
    ["........", "........", "........", "...C....", "........", ".C...C..", "...CC...", "...CC...", ".C...C..",
     "........", "....C...", "........"],
    # T2 thin beam
    ["...LC...", "...CL...", "...LC...", "...CL...", "...LC...", "..CLCL..", "..LCCL..", "...LC...", "...CL...",
     "...LC...", "...CL...", "...LC..."],
    # T3 wide beam with scan rings
    ["..LCCL..", "..CLLC..", ".CCCCCC.", "..LCCL..", "..CLLC..", ".CCCCCC.", "..LCCL..", "..CLLC..", ".CCCCCC.",
     "..LCCL..", "..CLLC..", "..LCCL.."],
    # T4 frog on every other scanline
    ["........", "........", ".LL..LL.", "........", "LLLLLLLL", "........", "LGGGGGGL", "........", ".LLLLLL.",
     "........", "........", "........"],
    # T5 hologram frog (light, see-through eyes)
    ["........", "........", ".LL..LL.", "LCKLLCKL", "LLLLLLLL", "LKLLLLKL", "LLKKKKLL", ".LLLLLL.", "LL.LL.LL",
     "........", "........", "........"],
    # T6 solid frog with a cyan flash outline
    ["........", ".CC..CC.", "CGGCCGGC", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG",
     "C......C", "........", "........"],
]

# ---- croak: throat balloons up, ribbit, sound rings ----
CROAK = [
    [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKLLKGG", ".GGLLGG.", "GG.GG.GG"],
    [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGLLGKG", "GGLLLLGG", ".GLLLLG.", "GG.GG.GG"],
    [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKLLLLKG", "GLLLLLLG", "GLLLLLLG", ".GLLLLG.", "GG.GG.GG"],
    ["LGG..GGL", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", "L.GGGG.L", "GG.GG.GG"],
]

# ---- flip: on its back, looking around, legs kicking ----
FLIP = list(reversed(IDLE))
FLIP_LOOK_L = list(reversed([".GG..GG.", "WKGGWKGG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"]))
FLIP_LOOK_R = list(reversed([".GG..GG.", "GGWKGGWK", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"]))
FLIP_KICK = ["G.GG.G.G", ".GGGGGG.", "GGKKKKGG", "GKGGGGKG", "GGGGGGGG", "GWKGGWKG", ".GG..GG."]

# ---- low battery: four options to replace sweat ----
SWEAT_OPTIONS = {
    "A pant": [
        [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGPPGG.", "GG.PP.GG"],
        [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGPPGG.", "GG.PPPGG", "....P..."],
    ],
    "B wilt": [
        ["........", ".GG..GG.", "GKKGGKKG", "GGGGGGGG", "GKGGGGKG", "GGGKKGGG", "GGGGGGGG", "GG.GG.GG"],
        ["........", "........", ".GG..GG.", "GKKGGKKG", "GGGGGGGG", "GGGKKGGG", "GGGGGGGG", "GGGGGGGG"],
    ],
    "C empty battery": [
        ["..DDDD..", "..DRDD..", "..DDDD..", ".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.",
         "GG.GG.GG"],
        ["..DDDD..", "..D..D..", "..DDDD..", ".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.",
         "GG.GG.GG"],
    ],
    "D melt": [
        [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG", ".G...G..", "......G."],
        [".GG..GG.", "GKKGGKKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", "GGGGGGGG", "GGGGGGGG", "GG.G.GG.", ".G..G.G.",
         "GGGGGGGG"],
    ],
}


def _pad16(rows, top):
    """place rows starting at row `top` of a 16-row cell (for vertical motion inside the cell)"""
    out = ["........"] * 16
    for i, r in enumerate(rows):
        if 0 <= top + i < 16:
            out[top + i] = r
    return out


_ARMS_UP = ["G......G", "G.G..G.G", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKRRKGG", ".GGGGGG."]

# ---- low battery: hops over to the voltage readout and jumps at it, arms up, red ! ----
LOWBATT = [
    _pad16(_ARMS_UP + ["GG.GG.GG"], 7),                                        # crouch under the !
    _pad16(["...RR...", "...RR...", "...RR...", "........", "...RR..."] + [""] + _ARMS_UP + [".G.GG.G."], 1),  # jump + !
    _pad16(["...RR...", "...RR...", "........", "...RR..."] + _ARMS_UP + ["G..GG..G"], 3),                  # falling
    _pad16(_ARMS_UP + ["GGGGGGGG"], 8),                                        # squash on landing
]

# ---- teleport with red: red spark and red flash on the way in and out ----
TELEPORT_RED = [
    ["........", "........", "........", "...R....", "........", ".R...C..", "...RR...", "...RR...", ".C...R..",
     "........", "....R...", "........"],
    ["...RC...", "...CR...", "...RC...", "...CR...", "...RC...", "..CRCR..", "..RCCR..", "...RC...", "...CR...",
     "...RC...", "...CR...", "...RC..."],
    ["..RCCR..", "..CRRC..", ".RRRRRR.", "..RCCR..", "..CRRC..", ".CCCCCC.", "..RCCR..", "..CRRC..", ".RRRRRR.",
     "..RCCR..", "..CRRC..", "..RCCR.."],
    ["........", "........", ".RR..RR.", "........", "LLLLLLLL", "........", "LGGGGGGL", "........", ".RRRRRR.",
     "........", "........", "........"],
    ["........", "........", ".LL..LL.", "LCKLLCKL", "LLLLLLLL", "LKLLLLKL", "LLKKKKLL", ".LLLLLL.", "LL.LL.LL",
     "........", "........", "........"],
    ["........", ".RR..RR.", "RGGRRGGR", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG",
     "R......R", "........", "........"],
]

# ---- cute extras (options) ----
CUTE = {
    "heart": [[".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GR.RGGGG", "RRRRRGGG", "GRRRGKGG", "G.R.GGGG", ".GGGGGG.", "GG.GG.GG"]],
    "wink": [[".GG..GG.", "GKKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"],
             [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"]],
    "big smile": [[".GG..GG.", "GWKGGWKG", "GGGGGGGG", "KGGGGGGK", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"]],
    "wave": [["......G.", ".GG..GGG", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"],
             [".....G..", ".GG..GGG", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"]],
    "sleepy zzz": [["....LLL.", ".....L..", "....LLL.", ".GG..GG.", "GKKGGKKG", "GGGGGGGG", "GGGGGGGG", "GGGKKGGG", ".GGGGGG.", "GG.GG.GG"],
                   ["..LL....", "...L....", "..LL....", ".GG..GG.", "GKKGGKKG", "GGGGGGGG", "GGGGGGGG", "GGGKKGGG", ".GGGGGG.", "GG.GG.GG"]],
    "shades": [[".GG..GG.", "KKKKKKKK", "KWKGGWKK", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"]],
    "star eyes": [[".GY..YG.", "GYYYYYYG", "GGYGGYGG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"]],
    "catch a fly": [["......K.", ".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"],
                    ["......P.", ".GG..GP.", "GWKGGPKG", "GGGGPGGG", "GKGPGGKG", "GGKPKKGG", ".GGGGGG.", "GG.GG.GG"],
                    [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG.GG"]],
    "dance": [[".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "G..GG.GG"],
              [".GG..GG.", "GWKGGWKG", "GGGGGGGG", "GKGGGGKG", "GGKKKKGG", ".GGGGGG.", "GG.GG..G"]],
}

# ---- detail test: the same frog at full native resolution (1 pixel = 1 screen pixel) ----
HIRES_IDLE = [
    "...LGGL......LGGL...",
    "..GWWWWG....GWWWWG..",
    "..GWWKKG....GWWKKG..",
    "..GWWKKGGGGGGWWKKG..",
    ".GGGWWGGGGGGGGWWGGG.",
    ".GGGGGGGGGGGGGGGGGG.",
    "GGGGGGGGGGGGGGGGGGGG",
    "GGDGGGGGGGGGGGGGGDGG",
    "GGGDDGGGGGGGGGGDDGGG",
    ".GGGGDDDDDDDDDDGGGG.",
    ".GGGGGGLLLLLLGGGGGG.",
    "..GGGGLLLLLLLLGGGG..",
    ".GGGGGGLLLLLLGGGGGG.",
    "GGG.GGGGGGGGGGGG.GGG",
    "GG..GG........GG..GG",
    "D...D..........D...D",
]

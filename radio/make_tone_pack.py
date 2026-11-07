#!/usr/bin/env python3
"""FrogOS tone pack for EdgeTX: replaces every English voice file with a tone, same filename.

The tones follow one grammar so they read without words:
  rising       = on / active / connected / recovered
  falling      = off / disabled / lost
  3 rising     = ARMED            3 falling = DISARMED
  3 quick mid  = warning (orange)
  siren x2     = critical (red)
  mode chirp   = flight / rate / OSD modes (pitch says which mode, ticks say which number)
  silent       = numbers and units (spoken values just disappear)

usage: make_tone_pack.py <edgetx-sdcard-sounds/SOUNDS/en> <out dir>
Writes <out>/SOUNDS/en/... as 32 kHz 16-bit mono PCM WAV, the format EdgeTX plays.
"""
import os
import re
import struct
import sys
import wave

import numpy as np

SRC, OUT = sys.argv[1:3]
RATE = 32000
AMP = 0.5                       # about -6 dBFS
C5, E5, G5, C6, E6, G6 = 523, 659, 784, 1047, 1319, 1568


def tone(f, ms, f2=None, shape="square"):
    n = int(RATE * ms / 1000)
    freq = np.linspace(f, f2 if f2 else f, n)
    phase = 2 * np.pi * np.cumsum(freq) / RATE
    if shape == "square":
        # soft square: fundamental + 3rd + 5th, cuts through motor noise better than a sine
        w = np.sin(phase) + np.sin(3 * phase) / 3 + np.sin(5 * phase) / 5
        w /= 1.2
    else:
        w = np.sin(phase)
    fade = min(n // 4, int(RATE * 0.006))
    if fade:
        w[:fade] *= np.linspace(0, 1, fade)
        w[-fade:] *= np.linspace(1, 0, fade)
    return w


def gap(ms):
    return np.zeros(int(RATE * ms / 1000))


def seq(*parts):
    return np.concatenate(parts)


# ---- the vocabulary ----
def up():          return seq(tone(E5, 70), gap(25), tone(C6, 110))
def down():        return seq(tone(C6, 70), gap(25), tone(E5, 110))
def armed():       return seq(tone(C5, 60), gap(20), tone(G5, 60), gap(20), tone(C6, 140))
def disarmed():    return seq(tone(C6, 60), gap(20), tone(G5, 60), gap(20), tone(C5, 140))
def warning():     return seq(*(x for _ in range(3) for x in (tone(1200, 60), gap(50))))
def critical():    return seq(tone(1700, 220, 750), gap(40), tone(1700, 220, 750))
def blip():        return tone(880, 60, shape="sine")
def tick(n=1, f=1000):
    return seq(*(x for _ in range(n) for x in (tone(f, 35), gap(55))))
def silent():      return gap(20)
def hello():       return seq(tone(C5, 70), gap(15), tone(E5, 70), gap(15), tone(G5, 70), gap(15), tone(C6, 160))
def timer_done():  return seq(tone(G5, 350, shape="sine"), gap(60), tone(G5, 80, shape="sine"))
def mode(f, n=1):  return seq(*(x for _ in range(n) for x in (tone(f, 50), gap(45))))
def turtle_on():   return seq(tone(400, 90, 900), gap(30), tone(900, 90, 400), gap(30), up())


UNIT_WORDS = {"volt", "amp", "mamp", "knot", "mps", "fps", "kph", "mph", "meter", "foot", "celsius", "fahr", "percent",
              "mamph", "watt", "mwatt", "db", "rpm", "g", "degree", "rad", "ml", "founce", "mlpm", "hertz", "ms", "us",
              "hour", "minute", "second", "dbm", "km"}

CRITICAL = {"rssi_red", "sigcrt", "telemko", "clobat", "fsact", "rxko", "servoko", "sensorko", "swr_red", "danger",
            "eebad", "batcrt", "trainko", "lost", "fson", "mothot", "overht", "htemp", "srvovl", "becovl"}
WARNING = {"rssi_org", "siglow", "lowbatt", "lowbat", "txbatl", "batlow", "thralert", "swalert", "inactiv", "warnng",
           "tohigh", "tolow", "toohgh", "thmwrn", "hvibr", "modelpwr"}
POSITIVE = {"telemok", "telemco", "trainok", "trainco", "good", "ready", "start", "active", "enabl", "on", "bind",
            "open", "unlckd", "homrst"}
NEGATIVE = {"off", "disabl", "deact", "stop", "close", "locked", "bad"}
ARMED = {"armed", "motarm", "engarm", "thract", "thren"}
DISARMED = {"disarm", "engdrm", "thrcut", "thrdis"}


def classify(name):
    """name: filename without .wav, lower case. Returns the sound for it."""
    base = name
    if re.fullmatch(r"\d{4}", base) or re.fullmatch(r"[a-z_]+[01]", base) and base[:-1] in UNIT_WORDS:
        return silent()
    if base in ("hello",):
        return hello()
    if base in ARMED:
        return armed()
    if base in DISARMED:
        return disarmed()
    if base in CRITICAL:
        return critical()
    if base in WARNING:
        return warning()
    if base.startswith("timovr"):
        return timer_done()
    if base.startswith("timrs"):
        return tick(1, 1500)
    if base == "midtrim":
        return tick(1, 1500)
    if base == "maxtrim":
        return tick(2, 2000)
    if base == "mintrim":
        return tick(2, 600)
    if base == "turton":
        return turtle_on()
    # flight modes: pitch says which (angle low, horizon mid, acro high), like the OSD
    if base in ("angmod", "fm-ang", "anglmd", "stabmo", "fm-stb", "stbmod", "lvlmod"):
        return mode(C5, 2)
    if base in ("hznmod", "fm-hor", "hrznmd"):
        return mode(G5, 2)
    if base in ("acrmod", "fm-acr", "acro", "acromd", "ratmod", "actnmd"):
        return mode(C6, 2)
    if base in ("airmon", "airmod"):
        return seq(mode(E6, 1), up())
    if base == "airmof":
        return seq(mode(E6, 1), down())
    m = re.search(r"(\d+)$", base)
    if m and any(base.startswith(p) for p in ("fm-", "rates", "osd", "bank-", "flp", "expo", "idleu", "fm-id")):
        return mode(E6, max(1, min(8, int(m.group(1)) or 1)))
    if base.startswith("vtx"):
        return mode(G6, 1)
    # generic on / off by suffix (crowon / crowof, gpson / gpsoff, ...)
    if base in POSITIVE or base.endswith("on") or base.endswith("act") or base.endswith("en"):
        return up()
    if base in NEGATIVE or base.endswith("of") or base.endswith("off") or base.endswith("dis") or base.endswith("db"):
        return down()
    if base.startswith("fm-") or base.endswith("mod") or base.endswith("md"):
        return mode(E6, 1)
    return blip()


def write(path, samples):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pcm = np.clip(samples * AMP, -1, 1)
    data = (pcm * 32767).astype("<i2").tobytes()
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(data)


count = 0
table = []
for root, _, files in os.walk(SRC):
    for f in sorted(files):
        if not f.lower().endswith(".wav"):
            continue
        rel = os.path.relpath(os.path.join(root, f), SRC)
        name = f[:-4].lower()
        snd = classify(name)
        write(os.path.join(OUT, "SOUNDS", "en", rel), snd)
        table.append((rel, snd))
        count += 1
print("wrote", count, "files")

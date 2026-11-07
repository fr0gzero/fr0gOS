#!/usr/bin/env python3
"""FrogOS tone pack for EdgeTX: replaces every English voice file with a tone, same filename.

The tones follow one grammar so they read without words:
Sound: soft deadmau5-style synth plucks in F minor (detuned saws + sub, filter pluck, dotted-eighth echo).
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
AMP = 0.21                      # half of v2 (about -14 dBFS peak): quiet, sits under the motors


# ---- synth: deadmau5-style pluck ----
# two slightly detuned band-limited saws + a sine sub, through a resonant low-pass whose cutoff
# snaps open and closes (the pluck), soft attack, then a dotted-eighth echo tail. F minor.
BPM = 128
ECHO_S = 60 / BPM * 0.75            # dotted eighth
F4, Ab4, Bb4, C5, Eb5, F5, G5, Ab5, C6, Eb6, F6 = 349.2, 415.3, 466.2, 523.3, 622.3, 698.5, 784.0, 830.6, 1046.5, 1244.5, 1396.9


def saw(f, n):
    t = np.arange(n) / RATE
    out = np.zeros(n)
    k = 1
    while k * f < RATE / 2 * 0.9 and k <= 12:          # fewer harmonics: rounder, less buzzy
        out += np.sin(2 * np.pi * k * f * t) / k
        k += 1
    return out * 0.55


def lowpass_env(x, fc0, fc1, tau, q=0.7, opening=False):       # more damping: no resonant zing
    """state-variable low-pass, cutoff gliding from fc0 to fc1 with time constant tau (s);
    opening=True sweeps linearly from fc1 up to fc0 over the whole sound (a riser)"""
    n = len(x)
    t = np.arange(n) / RATE
    if opening:
        fc = fc1 + (fc0 - fc1) * (t / t[-1]) ** 2
    else:
        fc = fc1 + (fc0 - fc1) * np.exp(-t / tau)
    fcoef = 2 * np.sin(np.pi * np.minimum(fc, RATE / 6) / RATE)
    low = band = 0.0
    y = np.empty(n)
    damp = q
    for i in range(n):
        f = fcoef[i]
        low += f * band
        high = x[i] - low - damp * band
        band += f * high
        y[i] = low
    return y


def pluck(f, ms=150, bright=3.5, decay=0.11, level=1.0):    # darker, shorter
    n = int(RATE * ms / 1000)
    x = saw(f * 1.0035, n) + saw(f / 1.0035, n) + 0.6 * np.sin(2 * np.pi * (f / 2) * np.arange(n) / RATE)
    y = lowpass_env(x, f * bright, f * 1.2, decay * 0.5)
    t = np.arange(n) / RATE
    env = np.minimum(1, t / 0.004) * np.exp(-t / decay)
    rel = min(n // 3, int(RATE * 0.02))
    env[-rel:] *= np.linspace(1, 0, rel)
    return y * env * level


def place(parts, total_ms=None):
    """parts: list of (start_ms, samples)"""
    end = max(int(RATE * st / 1000) + len(sm) for st, sm in parts)
    if total_ms:
        end = max(end, int(RATE * total_ms / 1000))
    out = np.zeros(end)
    for st, sm in parts:
        i = int(RATE * st / 1000)
        out[i:i + len(sm)] += sm
    return out


def echo(x, repeats=1, fb=0.22):                                 # one quiet echo
    d = int(RATE * ECHO_S)
    out = np.zeros(len(x) + d * repeats)
    out[:len(x)] += x
    y = x.copy()
    for r in range(1, repeats + 1):
        y = np.convolve(y, np.ones(6) / 6, mode="same")   # each repeat a bit darker
        out[d * r:d * r + len(y)] += y * (fb ** r)
    return out


def arp(notes, step=95, **kw):
    return echo(place([(i * step, pluck(f, **kw)) for i, f in enumerate(notes)]))


def gap(ms):
    return np.zeros(int(RATE * ms / 1000))


def seq(*parts):
    return np.concatenate(parts)


# ---- the vocabulary (same grammar, softer sound) ----
def up():          return arp([C5, F5])
def down():        return arp([F5, C5])
def armed():       return arp([F4, Ab4, C5, F5], step=80)
def disarmed():    return arp([F5, C5, Ab4, F4], step=80)
def warning():     return echo(place([(i * 110, pluck(Eb5, ms=90, bright=3.5, decay=0.05, level=0.8)) for i in range(3)]), repeats=1)
def critical():
    # dark minor fall, twice, with a slower filter: unmistakable but not harsh
    one = place([(0, pluck(Ab5, ms=200, bright=3.5, decay=0.16)), (150, pluck(F5, ms=220, bright=3, decay=0.18)),
                 (300, pluck(Bb4, ms=280, bright=2.5, decay=0.22))])
    return echo(one, repeats=1, fb=0.2)                          # once, not twice
def blip():        return echo(pluck(C5, ms=120, bright=4, decay=0.08, level=0.6), repeats=1)
def tick(n=1, f=1000):
    return echo(place([(i * 90, pluck(f, ms=50, bright=3, decay=0.025, level=0.5)) for i in range(n)]), repeats=1, fb=0.25)
def silent():      return gap(20)
def hello():
    # F minor add9 rolled up, deadmau5-style stab with a long tail
    return echo(place([(i * 70, pluck(f, ms=320, bright=3.5, decay=0.22, level=0.8)) for i, f in enumerate([F4, Ab4, C5, G5])]), repeats=1, fb=0.25)
def timer_done():
    chord = sum(pluck(f, ms=600, bright=3, decay=0.45, level=0.6) for f in (F4, Ab4, C5))
    return echo(place([(0, chord), (420, pluck(F5, ms=140))]), repeats=1)
def mode(f, n=1):  return echo(place([(i * 85, pluck(f, ms=110, decay=0.07)) for i in range(n)]), repeats=1, fb=0.2)
def turtle_on():
    n = int(RATE * 0.35)
    x = saw(F4, n) + saw(F4 * 1.005, n)
    riser = lowpass_env(x, F4 * 12, F4 * 1.2, 0.0, q=0.2, opening=True)   # filter opens instead of closing
    riser *= np.linspace(0.2, 0.9, n)
    return seq(riser * 0.6, up())


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


import functools
for _fn in ('up','down','armed','disarmed','warning','critical','blip','silent','hello','timer_done','turtle_on'):
    globals()[_fn] = functools.lru_cache(maxsize=None)(globals()[_fn])
mode = functools.lru_cache(maxsize=None)(mode)
tick = functools.lru_cache(maxsize=None)(tick)


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
        return tick(1, F6)
    if base == "midtrim":
        return tick(1, F6)
    if base == "maxtrim":
        return tick(2, F6)
    if base == "mintrim":
        return tick(2, F5)
    if base == "turton":
        return turtle_on()
    # flight modes: pitch says which (angle low, horizon mid, acro high), like the OSD
    if base in ("angmod", "fm-ang", "anglmd", "stabmo", "fm-stb", "stbmod", "lvlmod"):
        return mode(F4, 2)
    if base in ("hznmod", "fm-hor", "hrznmd"):
        return mode(C5, 2)
    if base in ("acrmod", "fm-acr", "acro", "acromd", "ratmod", "actnmd"):
        return mode(F5, 2)
    if base in ("airmon", "airmod"):
        return arp([Ab5, C5, F5], step=85)
    if base == "airmof":
        return arp([Ab5, F5, C5], step=85)
    m = re.search(r"(\d+)$", base)
    if m and any(base.startswith(p) for p in ("fm-", "rates", "osd", "bank-", "flp", "expo", "idleu", "fm-id")):
        return mode(Eb6, max(1, min(8, int(m.group(1)) or 1)))
    if base.startswith("vtx"):
        return mode(G5, 1)
    # generic on / off by suffix (crowon / crowof, gpson / gpsoff, ...)
    if base in POSITIVE or base.endswith("on") or base.endswith("act") or base.endswith("en"):
        return up()
    if base in NEGATIVE or base.endswith("of") or base.endswith("off") or base.endswith("dis") or base.endswith("db"):
        return down()
    if base.startswith("fm-") or base.endswith("mod") or base.endswith("md"):
        return mode(Eb6, 1)
    return blip()


def write(path, samples):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    peak = np.max(np.abs(samples)) or 1.0
    # trim the quiet end of the echo tail (below 3% of peak) so queued alerts don't stack up
    loud = np.nonzero(np.abs(samples) > 0.03 * peak)[0]
    if len(loud):
        end = min(len(samples), loud[-1] + int(RATE * 0.03))
        samples = samples[:end].copy()
        fade = min(len(samples) // 4, int(RATE * 0.03))
        if fade:
            samples[-fade:] *= np.linspace(1, 0, fade)
    pcm = np.clip(samples / peak * AMP, -1, 1)
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

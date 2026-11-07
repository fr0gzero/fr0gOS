#!/usr/bin/env python3
"""fr0gOS radio sound themes for EdgeTX: ten wildly different tone packs with the same vocabulary.

Every theme answers the same events (so any of them can replace the voice pack):
  hello, armed, disarmed, up (on / connected), down (off / lost), warning, critical, timer,
  tick (trim / reset), turtle, mode(level) (angle low / horizon mid / acro high / numbered),
  air(on/off), blip (anything else), silent (numbers and units)

usage:
  make_tone_themes.py audition <out dir>                         one audition WAV per theme
  make_tone_themes.py pack <theme> <edgetx SOUNDS/en> <out dir>  full SD-card pack for one theme
"""
import os
import re
import sys
import wave

import numpy as np

RATE = 32000
AMP = 0.21          # -14 dBFS peak, same as tone pack v3
rng = np.random.default_rng(7)


# ---------------- primitives ----------------
def T(ms):
    return np.arange(int(RATE * ms / 1000)) / RATE


def gap(ms):
    return np.zeros(int(RATE * ms / 1000))


def env(n, a=0.004, d=0.15, r=0.01):
    t = np.arange(n) / RATE
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
    k = min(n // 3, int(RATE * r))
    if k:
        e[-k:] *= np.linspace(1, 0, k)
    return e


def sine(f, ms, f2=None):
    t = T(ms)
    fr = np.linspace(f, f2 or f, len(t))
    return np.sin(2 * np.pi * np.cumsum(fr) / RATE)


def partials(f, ms, amps, ratios=None):
    t = T(ms)
    out = np.zeros(len(t))
    for i, a in enumerate(amps):
        r = ratios[i] if ratios else i + 1
        if f * r < RATE / 2:
            out += a * np.sin(2 * np.pi * f * r * t)
    return out


def square(f, ms, duty=0.5, f2=None):
    t = T(ms)
    fr = np.linspace(f, f2 or f, len(t))
    ph = np.cumsum(fr) / RATE % 1.0
    return np.where(ph < duty, 1.0, -1.0)


def noise(ms):
    return rng.uniform(-1, 1, len(T(ms)))


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / RATE)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def bandpass(x, lo, hi):
    return lowpass(x, hi) - lowpass(x, lo)


def ks_pluck(f, ms, bright=0.5, damp=0.996):
    """Karplus-Strong string: harpsichord-ish"""
    n = len(T(ms))
    p = max(2, int(RATE / f))
    buf = rng.uniform(-1, 1, p) * 1.0
    buf = lowpass(buf, 2000 + 10000 * bright)
    out = np.empty(n)
    for i in range(n):
        j = i % p
        out[i] = buf[j]
        buf[j] = damp * 0.5 * (buf[j] + buf[(j + 1) % p])
    return out


def fm(fc, ms, ratio, index, idecay=0.15, d=0.4):
    t = T(ms)
    ix = index * np.exp(-t / idecay)
    return np.sin(2 * np.pi * fc * t + ix * np.sin(2 * np.pi * fc * ratio * t)) * env(len(t), 0.003, d)


def place(parts, total_ms=None):
    end = max(int(RATE * st / 1000) + len(sm) for st, sm in parts)
    if total_ms:
        end = max(end, int(RATE * total_ms / 1000))
    out = np.zeros(end)
    for st, sm in parts:
        i = int(RATE * st / 1000)
        out[i:i + len(sm)] += sm
    return out


def seq(*xs):
    return np.concatenate(xs)


def echo(x, delay_ms=180, fb=0.25, repeats=1):
    d = int(RATE * delay_ms / 1000)
    out = np.zeros(len(x) + d * repeats)
    out[:len(x)] += x
    for r in range(1, repeats + 1):
        out[d * r:d * r + len(x)] += x * fb ** r
    return out


def hz(note):
    """'A4' / 'C#5' / 'Bb3' -> Hz"""
    m = re.fullmatch(r"([A-G])([#b]?)(-?\d)", note)
    semis = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}[m.group(1)]
    semis += {"#": 1, "b": -1, "": 0}[m.group(2)] + 12 * (int(m.group(3)) - 4)
    return 440.0 * 2 ** (semis / 12)


# ---------------- the themes ----------------
class Theme:
    name = desc = ""
    def silent(self): return gap(20)


class Baroque(Theme):
    name, desc = "baroque", "Classical: harpsichord in D major. Cadences resolve when good, a diminished organ chord when bad, trills for warnings."
    def n(self, note, ms=260): return ks_pluck(hz(note), ms, 0.7) * env(len(T(ms)), 0.001, ms / 1000 * 0.7)
    def run(self, notes, step=70, ms=260): return place([(i * step, self.n(x, ms)) for i, x in enumerate(notes)])
    def organ(self, notes, ms=600):
        x = sum(partials(hz(k), ms, [1, .5, .3, .2, .1]) for k in notes)
        return x * env(len(x), 0.04, 0.5)
    def hello(self): return self.run(["D4", "F#4", "A4", "D5", "F#5", "A5"], 60, 380)
    def armed(self): return self.run(["D4", "E4", "F#4", "G4", "A4", "D5"], 55)
    def disarmed(self): return self.run(["D5", "A4", "F#4", "D4"], 75)
    def up(self): return self.run(["A4", "D5"], 110)
    def down(self): return self.run(["D5", "A4"], 110)
    def warning(self): return self.run(["E5", "F#5", "E5", "F#5", "E5", "F#5"], 55, 150)
    def critical(self): return self.organ(["B3", "D4", "F4", "Ab4"], 700)
    def timer(self): return place([(i * 25, self.n(x, 600)) for i, x in enumerate(["D4", "A4", "D5", "F#5"])])
    def tick(self, kind): return self.n({"mid": "A5", "max": "D6", "min": "D4", "reset": "F#5"}[kind], 120)
    def turtle(self): return self.run(["A5", "G#5", "G5", "F#5", "F5", "E5", "D5", "A5"], 45, 160)
    def mode(self, level, n=1):
        note = ["D4", "A4", "D5", "F#5"][level]
        return self.run([note] * max(1, min(n, 6)), 110, 180)
    def air(self, on): return self.run(["G4", "B4", "D5"] if on else ["D5", "B4", "G4"], 70)
    def blip(self): return self.n("A4", 150) * 0.6


class Starship(Theme):
    name, desc = "starship", "Sci-fi bridge computer: soft sine chirps that glide, ring-modulated sparkle, pulsing alert."
    def chirp(self, f1, f2, ms=90):
        x = sine(f1, ms, f2)
        return x * (0.8 + 0.2 * sine(f1 * 1.5, ms)) * env(len(x), 0.004, ms / 1000 * 0.8)
    def hello(self): return place([(i * 90, self.chirp(600 + 250 * i, 900 + 300 * i, 80)) for i in range(5)])
    def armed(self): return place([(0, self.chirp(500, 900)), (110, self.chirp(800, 1300)), (220, self.chirp(1200, 1900, 160))])
    def disarmed(self): return place([(0, self.chirp(1900, 1200)), (110, self.chirp(1300, 800)), (220, self.chirp(900, 500, 160))])
    def up(self): return seq(self.chirp(800, 1600, 120), gap(30), self.chirp(2000, 2000, 50))
    def down(self): return seq(self.chirp(1600, 800, 120), gap(30), self.chirp(600, 600, 50))
    def warning(self): return seq(*[seq(self.chirp(1100, 1100, 70), self.chirp(880, 880, 70), gap(40)) for _ in range(2)])
    def critical(self):
        t = T(650)
        x = np.sin(2 * np.pi * 330 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t)) + 0.4 * np.sin(2 * np.pi * 495 * t)
        return x * env(len(t), 0.03, 0.6)
    def timer(self): return seq(self.chirp(1200, 1200, 200), gap(60), self.chirp(1200, 1600, 120))
    def tick(self, kind): return self.chirp({"mid": 2600, "max": 3200, "min": 1800, "reset": 2400}[kind], 2600, 25)
    def turtle(self):
        t = T(500)
        f = 500 + 900 * t / t[-1] + 60 * np.sin(2 * np.pi * 14 * t)
        return np.sin(2 * np.pi * np.cumsum(f) / RATE) * env(len(t), 0.01, 0.4)
    def mode(self, level, n=1):
        f = [700, 1000, 1400, 1800][level]
        return seq(*[seq(self.chirp(f, f * 1.25, 60), gap(40)) for _ in range(max(1, min(n, 6)) * (2 if level < 3 else 1))])
    def air(self, on): return self.chirp(900, 1700, 160) if on else self.chirp(1700, 900, 160)
    def blip(self): return self.chirp(1300, 1300, 40) * 0.6


class Dashboard(Theme):
    name, desc = "dashboard", "Cars: indicator relay clicks, door-chime bongs, engine start and rev blips, reverse beeper for turtle."
    def click(self): return bandpass(noise(8), 1500, 6000) * env(len(T(8)), 0.0005, 0.003) * 2.5
    def bong(self, f, ms=500): return partials(f, ms, [1, .35, .15], [1, 2.4, 3.9]) * env(len(T(ms)), 0.002, 0.25)
    def engine(self, f1, f2, ms):
        t = T(ms)
        fr = np.linspace(f1, f2, len(t)) * (1 + 0.03 * np.sin(2 * np.pi * 9 * t))
        ph = np.cumsum(fr) / RATE
        x = sum(np.sin(2 * np.pi * k * ph) / k for k in range(1, 14))
        return lowpass(x, 1800) * env(len(t), 0.03, ms / 1000)
    def hello(self): return seq(self.click(), gap(80), self.click(), gap(120), self.bong(660), )
    def armed(self): return seq(*[seq(self.engine(40, 55, 70), gap(30)) for _ in range(2)], self.engine(70, 190, 650))
    def disarmed(self): return seq(self.engine(160, 50, 600), gap(40), self.click())
    def up(self): return place([(0, self.bong(880, 400)), (160, self.bong(1175, 500))])
    def down(self): return place([(0, self.bong(1175, 400)), (160, self.bong(880, 500))])
    def warning(self): return place([(i * 300, self.bong(700, 350)) for i in range(3)])
    def critical(self): return place([(0, self.click()), (180, self.click()), (360, self.click()), (0, self.bong(440, 700) * 1.2)])
    def timer(self): return place([(0, self.bong(988, 500)), (200, self.bong(988, 600))])
    def tick(self, kind): return self.click()
    def turtle(self): return seq(*[seq(sine(1000, 160) * env(len(T(160)), 0.005, 0.5), gap(140)) for _ in range(3)])
    def mode(self, level, n=1):
        f = [55, 80, 110, 140][level]
        return seq(self.click(), gap(40), *[seq(self.engine(f, f * 1.8, 220), gap(40)) for _ in range(max(1, min(n, 4)))])
    def air(self, on): return seq(self.click(), gap(60), self.bong(1320 if on else 660, 350))
    def blip(self): return self.click()


class GameShow(Theme):
    name, desc = "gameshow", "TV game show: marimba dings for right answers, a soft buzzer for wrong, tick-tock clock, slide whistle."
    def mar(self, note, ms=350):
        f = hz(note)
        x = np.sin(2 * np.pi * f * T(ms)) + 0.35 * np.sin(2 * np.pi * f * 4 * T(ms)) * np.exp(-T(ms) / 0.03)
        return x * env(len(x), 0.001, 0.18)
    def run(self, notes, step=90): return place([(i * step, self.mar(x)) for i, x in enumerate(notes)])
    def wood(self, f=1800): return bandpass(noise(30), f * 0.7, f * 1.3) * env(len(T(30)), 0.0005, 0.01) * 3
    def hello(self): return self.run(["C5", "E5", "G5", "C6", "G5", "C6"], 85)
    def armed(self): return self.run(["G4", "C5", "E5", "G5"], 75)
    def disarmed(self): return self.run(["G5", "E5", "C5", "G4"], 75)
    def up(self): return self.run(["E6", "C6"], 120) if False else self.run(["C6", "E6"], 120)
    def down(self): return self.run(["E5", "C5"], 140)
    def warning(self): return seq(*[seq(self.wood(1800 if i % 2 == 0 else 1300), gap(170)) for i in range(4)])
    def critical(self):
        x = sum(square(f, 450) for f in (147, 156))
        return lowpass(x, 900) * env(len(x), 0.005, 0.5) * 0.6
    def timer(self): return place([(0, partials(1568, 900, [1, .5, .3], [1, 2.76, 5.4]) * env(len(T(900)), 0.001, 0.4))])
    def tick(self, kind): return self.wood({"mid": 1800, "max": 2400, "min": 1200, "reset": 2000}[kind])
    def turtle(self):
        t = T(600)
        f = 450 * 4 ** (t / t[-1]) * (1 + 0.02 * np.sin(2 * np.pi * 6 * t))
        return np.sin(2 * np.pi * np.cumsum(f) / RATE) * env(len(t), 0.02, 0.6)
    def mode(self, level, n=1):
        note = ["C5", "G5", "C6", "E6"][level]
        return self.run([note] * max(1, min(n, 6)) * (2 if level < 3 else 1), 110)
    def air(self, on): return self.run(["G5", "D6"] if on else ["D6", "G5"], 100)
    def blip(self): return self.mar("A5", 200) * 0.6


class Chip8(Theme):
    name, desc = "8bit", "Chiptune: 25% pulse waves and a noise channel, console-style power-ups and power-downs."
    def p(self, note, ms=70, duty=0.25):
        x = square(hz(note), ms, duty)
        return x * env(len(x), 0.001, 1.0, 0.004) * 0.5
    def run(self, notes, ms=60): return seq(*[self.p(x, ms) for x in notes])
    def hat(self): return noise(25) * env(len(T(25)), 0.0005, 0.008) * 0.5
    def hello(self): return self.run(["C5", "E5", "G5", "C6", "rest", "G5", "C6"].__class__([x for x in ["C5", "E5", "G5", "C6", "G5", "C6"]]), 70)
    def armed(self): return seq(*[self.p(n, 35) for n in ["C4", "E4", "G4", "C5", "E5", "G5", "C6"]])
    def disarmed(self): return seq(*[self.p(n, 35) for n in ["C6", "G5", "E5", "C5", "G4", "E4", "C4"]])
    def up(self): return self.run(["G5", "D6"], 70)
    def down(self): return self.run(["D6", "G5"], 70)
    def warning(self): return seq(*[seq(self.p("A5", 60, 0.5), gap(60)) for _ in range(3)])
    def critical(self): return seq(self.run(["E4", "D#4", "D4", "C#4"], 110), noise(120) * env(len(T(120)), 0.001, 0.08) * 0.5)
    def timer(self): return self.run(["C5", "C5", "G5", "C6"], 90)
    def tick(self, kind): return self.hat()
    def turtle(self): return seq(*[self.p(n, 30) for n in ["C4", "C5", "C4", "C5", "G4", "G5", "C5", "C6"]])
    def mode(self, level, n=1):
        note = ["C4", "G4", "C5", "G5"][level]
        return seq(*[seq(self.p(note, 50), gap(40)) for _ in range(max(1, min(n, 6)) * (2 if level < 3 else 1))])
    def air(self, on): return self.run(["E5", "B5"] if on else ["B5", "E5"], 60)
    def blip(self): return self.p("C6", 40)


class Sonar(Theme):
    name, desc = "sonar", "Submarine: sonar pings with long tails, Doppler drops, depth-charge thump, bubbles for turtle. Barely musical."
    def ping(self, f, ms=700, f2=None): return sine(f, ms, f2) * env(len(T(ms)), 0.003, 0.22)
    def hello(self): return echo(self.ping(1500, 600), 300, 0.35, 2)
    def armed(self): return place([(0, self.ping(900, 400)), (180, self.ping(1200, 400)), (360, self.ping(1600, 600))])
    def disarmed(self): return place([(0, self.ping(1600, 400)), (180, self.ping(1200, 400)), (360, self.ping(900, 600))])
    def up(self): return self.ping(1400, 600, 1500)
    def down(self): return self.ping(1400, 600, 1100)
    def warning(self): return place([(0, self.ping(2000, 250)), (140, self.ping(2000, 250)), (420, self.ping(2000, 250))])
    def critical(self):
        thump = lowpass(noise(400), 300) * env(len(T(400)), 0.002, 0.12) * 4
        return place([(0, thump), (60, self.ping(600, 700, 450))])
    def timer(self): return echo(self.ping(1000, 500), 250, 0.4, 2)
    def tick(self, kind): return self.ping({"mid": 2500, "max": 3000, "min": 1800, "reset": 2200}[kind], 60)
    def turtle(self):
        parts = [(int(rng.uniform(0, 450)), sine(f, 40, f * 1.8) * env(len(T(40)), 0.002, 0.02)) for f in rng.uniform(500, 1400, 12)]
        return place(parts, 500)
    def mode(self, level, n=1):
        f = [800, 1200, 1700, 2200][level]
        return place([(i * 160, self.ping(f, 300)) for i in range(max(1, min(n, 6)) * (2 if level < 3 else 1))])
    def air(self, on): return self.ping(1200, 400, 1600 if on else 900)
    def blip(self): return self.ping(1500, 200) * 0.6


class Zen(Theme):
    name, desc = "zen", "Temple: singing bowls and small bells with inharmonic overtones, wood-block knocks. Very calm."
    def bowl(self, f, ms=900, d=0.5):
        return partials(f, ms, [1, .5, .25, .12], [1, 2.71, 5.15, 8.9]) * env(len(T(ms)), 0.006, d) * (1 + 0.15 * np.sin(2 * np.pi * 4 * T(ms)))
    def knock(self, f=900): return bandpass(noise(40), f * 0.7, f * 1.4) * env(len(T(40)), 0.0005, 0.012) * 3
    def hello(self): return place([(0, self.bowl(440, 1100, 0.6)), (250, self.bowl(660, 900, 0.4))])
    def armed(self): return place([(i * 160, self.bowl(f, 600, 0.3)) for i, f in enumerate([523, 659, 880])])
    def disarmed(self): return place([(i * 160, self.bowl(f, 600, 0.3)) for i, f in enumerate([880, 659, 523])])
    def up(self): return self.bowl(988, 600, 0.3)
    def down(self): return self.bowl(523, 700, 0.35)
    def warning(self): return place([(i * 160, self.knock(1000)) for i in range(3)])
    def critical(self): return place([(0, self.bowl(220, 1000, 0.5) * 1.3), (220, self.bowl(233, 900, 0.5) * 1.2)])
    def timer(self): return place([(0, self.bowl(660, 900)), (300, self.bowl(660, 700, 0.3))])
    def tick(self, kind): return self.knock({"mid": 1200, "max": 1600, "min": 800, "reset": 1000}[kind])
    def turtle(self):
        t = T(700)
        x = self.bowl(330, 700, 0.6) * (0.5 + 0.5 * np.sin(2 * np.pi * (2 + 8 * t / t[-1]) * t))
        return x
    def mode(self, level, n=1):
        f = [440, 660, 880, 1175][level]
        return place([(i * 170, self.bowl(f, 450, 0.2)) for i in range(max(1, min(n, 6)) * (2 if level < 3 else 1))])
    def air(self, on): return place([(0, self.bowl(784, 500, 0.25)), (120, self.bowl(1047 if on else 587, 600, 0.3))])
    def blip(self): return self.knock(1100) * 0.7


class DialUp(Theme):
    name, desc = "dialup", "90s computer (fits the fr0gOS hacker look): DTMF keypad tones, PC-speaker beeps, floppy clicks, modem screech for critical."
    DTMF = {"1": (697, 1209), "2": (697, 1336), "3": (697, 1477), "4": (770, 1209), "5": (770, 1336), "6": (770, 1477),
            "7": (852, 1209), "8": (852, 1336), "9": (852, 1477), "*": (941, 1209), "0": (941, 1336), "#": (941, 1477)}
    def key(self, k, ms=80):
        lo, hi = self.DTMF[k]
        x = sine(lo, ms) + sine(hi, ms)
        return x * env(len(x), 0.003, 1.0, 0.006) * 0.5
    def dial(self, s, step=110): return place([(i * step, self.key(k)) for i, k in enumerate(s)])
    def pcspk(self, f, ms=90): return square(f, ms) * env(len(T(ms)), 0.001, 1.0, 0.004) * 0.4
    def floppy(self): return seq(*[bandpass(noise(6), 800, 4000) * 2 * env(len(T(6)), 0.0005, 0.002) for _ in range(1)], gap(25), bandpass(noise(6), 800, 4000) * 1.5)
    def hello(self):
        tone = (sine(350, 300) + sine(440, 300)) * env(len(T(300)), 0.01, 1.0, 0.03) * 0.5
        return seq(tone, gap(60), self.dial("1337", 90))
    def armed(self): return self.dial("159#", 85)
    def disarmed(self): return seq(self.dial("*", 85), gap(40), (sine(480, 250) + sine(620, 250)) * env(len(T(250)), 0.005, 1.0, 0.02) * 0.5)
    def up(self): return self.dial("39", 90)
    def down(self): return self.dial("93", 90)
    def warning(self): return seq(*[seq(self.pcspk(1000, 70), gap(60)) for _ in range(3)])
    def critical(self):
        parts = []
        t = 0
        while t < 600:
            f = rng.choice([1200, 2200, 1650, 980])
            parts.append((t, sine(f, 40) * 0.6))
            t += 40
        x = place(parts) + bandpass(noise(640), 1500, 3500)[:len(place(parts))] * 0.25
        return x * env(len(x), 0.005, 1.0, 0.03)
    def timer(self): return seq(self.pcspk(880, 200), gap(80), self.pcspk(1320, 120))
    def tick(self, kind): return self.floppy()
    def turtle(self):
        t = T(500)
        f = 1650 + 550 * np.sign(np.sin(2 * np.pi * 12 * t))
        return np.sin(2 * np.pi * np.cumsum(f) / RATE) * env(len(t), 0.01, 0.5) * 0.6
    def mode(self, level, n=1):
        k = "123#"[level]
        return self.dial(k * (max(1, min(n, 6)) * (2 if level < 3 else 1)), 120)
    def air(self, on): return self.dial("**" if on else "##", 90)
    def blip(self): return self.pcspk(1200, 40)


class Lounge(Theme):
    name, desc = "lounge", "Lounge jazz: FM electric-piano chords (maj7, 9ths), vibraphone tremolo, brushed snare ticks."
    def ep(self, note, ms=700): return fm(hz(note), ms, 1.0, 2.2, 0.12, 0.45)
    def chord(self, notes, roll=25, ms=800): return place([(i * roll, self.ep(x, ms) * 0.6) for i, x in enumerate(notes)])
    def brush(self): return bandpass(noise(60), 2000, 8000) * env(len(T(60)), 0.005, 0.03)
    def hello(self): return self.chord(["C3", "E4", "G4", "B4", "D5"], 40, 1000)
    def armed(self): return place([(0, self.chord(["D4", "F4", "A4", "C5"], 15, 300)), (220, self.chord(["G3", "F4", "B4", "E5"], 15, 300)), (440, self.chord(["C4", "E4", "B4", "D5"], 20, 600))])
    def disarmed(self): return place([(0, self.chord(["C5", "E5", "B5"], 15, 300)), (220, self.chord(["A4", "C5", "G5"], 15, 300)), (440, self.chord(["F4", "A4", "E5"], 20, 600))])
    def up(self): return place([(0, self.ep("E5", 400)), (130, self.ep("C#6", 600))])
    def down(self): return place([(0, self.ep("C#6", 400)), (130, self.ep("E5", 600))])
    def warning(self): return place([(i * 130, self.ep("F5", 150) * 0.8) for i in range(3)])
    def critical(self): return self.chord(["C3", "F#3", "B3", "F4"], 10, 900)
    def timer(self):
        x = self.chord(["F4", "A4", "C5", "E5"], 0, 900)
        return x * (1 + 0.35 * np.sin(2 * np.pi * 5.5 * np.arange(len(x)) / RATE))
    def tick(self, kind): return self.brush()
    def turtle(self): return place([(i * 35, self.ep(n, 250) * 0.5) for i, n in enumerate(["C4", "E4", "G4", "B4", "D5", "F#5", "A5", "C6"])])
    def mode(self, level, n=1):
        roots = [["C4", "E4", "B4"], ["F4", "A4", "E5"], ["G4", "B4", "F#5"], ["A4", "C#5", "G#5"]][level]
        return place([(i * 180, self.chord(roots, 15, 300)) for i in range(max(1, min(n, 6)))])
    def air(self, on): return self.chord(["D5", "F#5", "A5", "C#6"] if on else ["D4", "F4", "Ab4", "C5"], 30, 500)
    def blip(self): return self.ep("G5", 250) * 0.5


class Pond(Theme):
    LEVELS = {"warning": 0.5}        # crickets are high and dense: half level to match the rest
    name, desc = "pond", "fr0gOS mascot: ribbits and croaks, cricket chirps, water drops and a splash. Not music at all."
    def ribbit(self, f=420, ms=180, pulses=4):
        t = T(ms)
        am = (np.sin(2 * np.pi * pulses / (ms / 1000) * t) > 0).astype(float)
        x = sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 9)) * am
        x = bandpass(x, f * 0.8, f * 5)
        return x * env(len(t), 0.005, ms / 1000 * 0.8) * 2
    def drop(self, f1, f2, ms=90): return sine(f1, ms, f2) * env(len(T(ms)), 0.001, 0.035)
    def cricket(self, n=4):
        return seq(*[seq(sine(4300, 18) * env(len(T(18)), 0.002, 1.0, 0.004), gap(14)) for _ in range(n)])
    def hello(self): return place([(0, self.drop(700, 1800)), (180, self.drop(900, 2100)), (380, self.ribbit(440)), (620, self.ribbit(520, 140, 3))])
    def armed(self): return place([(0, self.ribbit(380, 120, 2)), (160, self.ribbit(470, 120, 2)), (320, self.ribbit(580, 160, 3))])
    def disarmed(self): return self.ribbit(220, 420, 5)
    def up(self): return self.drop(800, 2000, 110)
    def down(self): return self.drop(2000, 700, 130)
    def warning(self): return seq(*[seq(self.cricket(4), gap(120)) for _ in range(3)])
    def critical(self): return seq(self.ribbit(160, 380, 6) * 1.2, gap(80), self.ribbit(150, 380, 6) * 1.2)
    def timer(self): return seq(self.ribbit(500, 140, 3), gap(60), self.ribbit(500, 140, 3))
    def tick(self, kind): return self.drop({"mid": 1500, "max": 2200, "min": 900, "reset": 1300}[kind], 2400, 50)
    def turtle(self):
        splash = bandpass(noise(350), 600, 5000) * env(len(T(350)), 0.002, 0.09)
        return seq(splash, gap(40), self.ribbit(300, 200, 4))
    def mode(self, level, n=1):
        f = [300, 450, 620, 800][level]
        return place([(i * 200, self.ribbit(f, 120, 2)) for i in range(max(1, min(n, 6)) * (2 if level < 3 else 1))])
    def air(self, on): return self.drop(900, 2400, 140) if on else self.drop(2400, 600, 160)
    def blip(self): return self.drop(1200, 1900, 60)


THEMES = [Baroque(), Starship(), Dashboard(), GameShow(), Chip8(), Sonar(), Zen(), DialUp(), Lounge(), Pond()]


# ---------------- EdgeTX filename -> event ----------------
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


def event(name):
    b = name
    if re.fullmatch(r"\d{4}", b) or (re.fullmatch(r"[a-z_]+[01]", b) and b[:-1] in UNIT_WORDS):
        return ("silent",)
    if b == "hello":
        return ("hello",)
    if b in ARMED:
        return ("armed",)
    if b in DISARMED:
        return ("disarmed",)
    if b in CRITICAL:
        return ("critical",)
    if b in WARNING:
        return ("warning",)
    if b.startswith("timovr"):
        return ("timer",)
    if b.startswith("timrs"):
        return ("tick", "reset")
    if b in ("midtrim", "maxtrim", "mintrim"):
        return ("tick", {"midtrim": "mid", "maxtrim": "max", "mintrim": "min"}[b])
    if b == "turton":
        return ("turtle",)
    if b in ("angmod", "fm-ang", "anglmd", "stabmo", "fm-stb", "stbmod", "lvlmod"):
        return ("mode", 0, 1)
    if b in ("hznmod", "fm-hor", "hrznmd"):
        return ("mode", 1, 1)
    if b in ("acrmod", "fm-acr", "acro", "acromd", "ratmod", "actnmd"):
        return ("mode", 2, 1)
    if b in ("airmon", "airmod"):
        return ("air", True)
    if b == "airmof":
        return ("air", False)
    m = re.search(r"(\d+)$", b)
    if m and any(b.startswith(p) for p in ("fm-", "rates", "osd", "bank-", "flp", "expo", "idleu", "fm-id")):
        return ("mode", 3, max(1, min(8, int(m.group(1)) or 1)))
    if b.startswith("vtx"):
        return ("mode", 3, 1)
    if b in POSITIVE or b.endswith("on") or b.endswith("act") or b.endswith("en"):
        return ("up",)
    if b in NEGATIVE or b.endswith("of") or b.endswith("off") or b.endswith("dis") or b.endswith("db"):
        return ("down",)
    if b.startswith("fm-") or b.endswith("mod") or b.endswith("md"):
        return ("mode", 3, 1)
    return ("blip",)


def render(theme, ev):
    kind, *args = ev
    return getattr(theme, kind)(*args)


def level(theme, ev):
    return getattr(theme, "LEVELS", {}).get(ev[0], 1.0)


def finish(samples):
    samples = np.asarray(samples, dtype=float)
    peak = np.max(np.abs(samples)) or 1.0
    loud = np.nonzero(np.abs(samples) > 0.03 * peak)[0]
    if len(loud):
        samples = samples[:min(len(samples), loud[-1] + int(RATE * 0.03))].copy()
        f = min(len(samples) // 4, int(RATE * 0.02))
        if f:
            samples[-f:] *= np.linspace(1, 0, f)
    return np.clip(samples / peak * AMP, -1, 1)


def write(path, samples, gain=1.0):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes((finish(samples) * gain * 32767).astype("<i2").tobytes())


AUDITION = [("hello",), ("armed",), ("disarmed",), ("mode", 0, 1), ("mode", 1, 1), ("mode", 2, 1), ("air", True), ("air", False),
            ("turtle",), ("up",), ("critical",), ("warning",), ("timer",), ("tick", "mid")]

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "audition":
        out = sys.argv[2]
        for i, th in enumerate(THEMES, 1):
            parts = []
            for ev in AUDITION:
                s = finish(render(th, ev))
                parts += [s, np.zeros(int(RATE * 0.7))]
            write(os.path.join(out, f"{i:02d}_{th.name}.wav"), np.concatenate(parts) / AMP * 1.0)
            print(f"{i:02d} {th.name}: {th.desc}")
    elif cmd == "pack":
        name, src, out = sys.argv[2:5]
        th = next(t for t in THEMES if t.name == name)
        cache = {}
        n = 0
        for root, _, files in os.walk(src):
            for f in sorted(files):
                if not f.lower().endswith(".wav"):
                    continue
                ev = event(f[:-4].lower())
                if ev not in cache:
                    cache[ev] = render(th, ev)
                write(os.path.join(out, "SOUNDS", "en", os.path.relpath(os.path.join(root, f), src)), cache[ev], level(th, ev))
                n += 1
        print("wrote", n, "files for", name)

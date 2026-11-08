#!/usr/bin/env python3
"""Read the fr0gOS stick code back off goggle DVR footage -> CSV of stick positions over time.

fr0gOS (v1.3 r27+, HD) writes the four sticks into the bottom OSD row as dim three-band glyphs:
  left  [count][roll hi][roll lo][pitch hi][pitch lo]      right  [yaw hi][yaw lo][thr hi][thr lo][check]
3 bits a cell, 6 bits a stick (0 = 1000 us, 63 = 2000 us), check = (sum of the other nine + 5) & 7.

The OSD grid is found automatically (it hunts for the offset where the checksums come out right), so it
works on HDZero DVR at any resolution.

usage: stickcode_decode.py <dvr video> <out.csv> [--fps 30]
csv columns: t (s, video time), frame, roll, pitch, yaw, throttle  (-1..1, throttle 0..1)
"""
import argparse
import subprocess
import sys
import numpy as np

COLS, ROWS = 50, 18


def frames(path, w, h, fps):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={fps},scale={w}:{h},format=gray", "-f", "rawvideo", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    size = w * h
    try:
        while True:
            buf = p.stdout.read(size)
            if len(buf) < size:
                break
            yield np.frombuffer(buf, np.uint8).reshape(h, w)
    finally:
        p.kill()
        p.wait()


def probe(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                   "stream=width,height", "-of", "csv=p=0", path]).decode().strip().split(",")
    return int(out[0]), int(out[1])


def read_cells(img, x0, y0, cw, ch, cols):
    """3-bit value of each cell in `cols` on the bottom row, or None if a band is ambiguous"""
    vals = []
    top = y0 + (ROWS - 1) * ch
    for c in cols:
        left = x0 + c * cw
        v = 0
        for b in range(3):
            y1 = int(top + b * ch / 3 + ch * 0.1)
            y2 = int(top + (b + 1) * ch / 3 - ch * 0.1)
            x1, x2 = int(left + cw * 0.3), int(left + cw * 0.7)
            if y1 < 0 or y2 > img.shape[0] or x1 < 0 or x2 > img.shape[1]:
                return None
            m = img[y1:y2, x1:x2].mean()
            if 22 < m < 42 or m > 120:           # in between, or bright (picture / text): not a code cell
                return None
            v = (v << 1) | (m >= 42)
        vals.append(v)
    return vals


def decode(img, geo):
    x0, y0, cw, ch = geo
    cells = read_cells(img, x0, y0, cw, ch, list(range(5)) + list(range(COLS - 5, COLS)))
    if cells is None or ((sum(cells[:9]) + 5) & 7) != cells[9]:   # +5 so an all-black row never passes
        return None
    sticks = [(cells[1 + 2 * i] << 3) | cells[2 + 2 * i] for i in range(4)]
    return cells[0], sticks


def calibrate(sample, w, h):
    """find the grid offset where most frames decode with a good checksum"""
    cw, ch = w / COLS * (1200 / 1280) if w == 1280 else w / COLS, h / ROWS * (648 / 720) if h == 720 else h / ROWS
    best, bestGeo = -1, None
    for dy in range(-40, 41, 2):
        for dx in range(-20, 21, 2):
            geo = ((w - COLS * cw) / 2 + dx, (h - ROWS * ch) / 2 + dy, cw, ch)
            # score by how many different frame counts it reads: a real code ticks over, a lucky patch of
            # static OSD or picture doesn't
            ok = len({d[0] for d in (decode(f, geo) for f in sample) if d})
            if ok > best:
                best, bestGeo = ok, geo
    return bestGeo, best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("csv")
    ap.add_argument("--fps", type=float, default=30.0)
    a = ap.parse_args()
    w, h = probe(a.video)
    sample = []
    for i, f in enumerate(frames(a.video, w, h, 10)):
        sample.append(f)
        if len(sample) >= 40:
            break
    geo, ok = calibrate(sample, w, h)
    if ok < 3:
        sys.exit("no stick code found: is this DVR from fr0gOS v1.3 r27+ on HDZero?")
    print(f"grid at x0={geo[0]:.0f} y0={geo[1]:.0f} cell {geo[2]:.1f}x{geo[3]:.1f} ({ok} different frame counts in the sample)")
    rows, last = [], None
    good = bad = 0
    for i, f in enumerate(frames(a.video, w, h, a.fps)):
        d = decode(f, geo)
        if d is None:
            bad += 1
            continue
        good += 1
        count, s = d
        if last is not None and last == (count, tuple(s)):
            continue                              # the same OSD frame again
        last = (count, tuple(s))
        roll, pitch, yaw, thr = [v / 63.0 for v in s]
        rows.append((i / a.fps, count, roll * 2 - 1, pitch * 2 - 1, yaw * 2 - 1, thr))
    with open(a.csv, "w") as fh:
        fh.write("t,frame,roll,pitch,yaw,throttle\n")
        for r in rows:
            fh.write("%.3f,%d,%.3f,%.3f,%.3f,%.3f\n" % r)
    print(f"{len(rows)} stick samples from {good} readable frames ({bad} unreadable) -> {a.csv}")


if __name__ == "__main__":
    main()

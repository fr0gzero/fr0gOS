#!/usr/bin/env python3
"""Slice the fr0gOS goggle-frog sprite sheet (17 frames, 6x3 grid, black background, a label banner under each
frog) into clean, registered, transparent frames ready to bake into the HDZero goggle font.

- keys out the black background by flood-fill from each cell's border (the frog's own black outline survives,
  because it's interior, not connected to the border)
- drops the label banner strip
- registers every frame into one common box so the frog never jumps
- frame 17 ("MIRROR") is flipped 180deg to make the upside-down / turtle-mode frame

usage: sheet_to_mascot.py <sheet.png> <out_dir> [--preview preview.png]
writes <out_dir>/frame_NN_name.png (registered RGBA) and, with --preview, a contact sheet.
"""
import os
import sys
from collections import deque
from PIL import Image

NAMES = ["idle", "glanceL", "glanceR", "blink", "grin", "exclgrin", "hurt", "ko", "breath",
         "blinkH", "glanceU", "glanceD", "whoa", "dizzy", "pumped", "stars", "upsidedown"]
COLS, ROWS, N = 6, 3, 17
LABEL_FRAC = 0.80        # keep the top 80% of each cell; the label banner sits below
BG_MAX = 52              # a pixel darker than this on every channel is "background" black


def key_black(cell):
    """flood-fill near-black inward from the border -> alpha 0; keep interior black (frog outline)"""
    cell = cell.convert("RGBA")
    px = cell.load()
    w, h = cell.size
    seen = [[False] * w for _ in range(h)]
    q = deque()

    def isbg(x, y):
        r, g, b, _ = px[x, y]
        return r <= BG_MAX and g <= BG_MAX and b <= BG_MAX

    for x in range(w):
        for y in (0, h - 1):
            if not seen[y][x] and isbg(x, y):
                q.append((x, y)); seen[y][x] = True
    for y in range(h):
        for x in (0, w - 1):
            if not seen[y][x] and isbg(x, y):
                q.append((x, y)); seen[y][x] = True
    while q:
        x, y = q.popleft()
        px[x, y] = (0, 0, 0, 0)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and isbg(nx, ny):
                seen[ny][nx] = True; q.append((nx, ny))
    return cell


def band_crop(cell, merge=4):
    """keep the frog's vertical band; a label banner (above or below) is a separate band split by a black gap,
    so it drops out. A gap up to `merge` px is bridged (so the goggle on top stays joined to the head)."""
    px = cell.load()
    w, h = cell.size
    rc = [sum(1 for x in range(w) if px[x, y][3] > 20) for y in range(h)]
    bands, y = [], 0
    while y < h:
        if rc[y] == 0:
            y += 1
            continue
        y0 = y
        gap = 0
        while y < h and (rc[y] > 0 or gap < merge):
            gap = gap + 1 if rc[y] == 0 else 0
            y += 1
        y1 = y - gap
        bands.append((sum(rc[y0:y1]), y0, y1))
    if not bands:
        return cell
    _, by0, by1 = max(bands)
    for yy in range(h):
        if yy < by0 or yy >= by1:
            for xx in range(w):
                px[xx, yy] = (0, 0, 0, 0)
    return cell


def main():
    sheet = Image.open(sys.argv[1]).convert("RGB")
    out_dir = sys.argv[2]
    os.makedirs(out_dir, exist_ok=True)
    flip_last = "--flip-last" in sys.argv          # frame 17 drawn upright -> flip it for turtle mode
    frac = float(sys.argv[sys.argv.index("--label-frac") + 1]) if "--label-frac" in sys.argv else LABEL_FRAC
    topm = float(sys.argv[sys.argv.index("--top") + 1]) if "--top" in sys.argv else 0.065
    W, H = sheet.size
    cw, ch = W / COLS, H / ROWS
    frames = []
    for i in range(N):
        r, c = i // COLS, i % COLS
        x0, y0 = int(round(c * cw)), int(round(r * ch + ch * topm))
        x1, y1 = int(round((c + 1) * cw)), int(round(y0 + ch * frac))
        cell = band_crop(key_black(sheet.crop((x0, y0, x1, y1))))
        bbox = cell.getbbox()
        cell = cell.crop(bbox) if bbox else cell
        if NAMES[i] == "upsidedown" and flip_last:
            cell = cell.transpose(Image.FLIP_TOP_BOTTOM)
        frames.append(cell)
    # register: common canvas = max content size + pad, each centred
    mw = max(f.width for f in frames)
    mh = max(f.height for f in frames)
    reg = []
    for f in frames:
        canvas = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))
        canvas.paste(f, ((mw - f.width) // 2, (mh - f.height) // 2), f)
        reg.append(canvas)
    for i, (f, name) in enumerate(zip(reg, NAMES)):
        f.save(os.path.join(out_dir, f"frame_{i + 1:02d}_{name}.png"))
    print(f"ok {N} frames, registered {mw}x{mh} -> {out_dir}")

    if "--preview" in sys.argv:
        pv = sys.argv[sys.argv.index("--preview") + 1]
        from PIL import ImageDraw, ImageFont
        # show each frame downscaled to actual goggle-block sizes: FHD 2x2 = 72x108, HD 2x2 = 48x72
        def fit(f, w, h):
            s = min(w / f.width, h / f.height)
            r = f.resize((max(1, int(f.width * s)), max(1, int(f.height * s))), Image.LANCZOS)
            c = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            c.paste(r, ((w - r.width) // 2, (h - r.height) // 2), r)
            return c
        cols, pad, gap = 6, 16, 18
        big = 180
        cw2 = big + gap
        chh = big + 128
        rows = (N + cols - 1) // cols
        sh = Image.new("RGB", (pad * 2 + cols * cw2 - gap, pad * 2 + 26 + rows * chh), (16, 18, 20))
        d = ImageDraw.Draw(sh)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 20)
            sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
        except Exception:
            font = sm = None
        d.text((pad, pad - 2), "goggle-frog sliced + keyed, at actual goggle sizes (72x108 FHD / 48x72 HD cells)", fill=(200, 230, 210), font=font)
        for i, (f, name) in enumerate(zip(reg, NAMES)):
            cx = pad + (i % cols) * cw2
            cy = pad + 26 + (i // cols) * chh
            sh.paste(fit(f, big, big).convert("RGB"), (cx, cy))                      # scaled up
            fhd = fit(f, 72, 108); hd = fit(f, 48, 72)
            sh.paste(fhd.convert("RGB"), (cx, cy + big + 6))
            sh.paste(hd.convert("RGB"), (cx + 80, cy + big + 6))
            d.text((cx, cy + big + 116), f"{i + 1} {name}", fill=(150, 200, 170), font=sm)
        sh.save(pv)
        print("preview", pv)


if __name__ == "__main__":
    main()

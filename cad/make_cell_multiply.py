"""
"I need 11 of these" - stop-motion multiply animation
=====================================================
Physical AI Agent / Big Reset video, LINE 2.

Takes ONE photo of driver cell #1 and stamps it 11 times, left to right, one
per shutter beat, each staying on screen. Ends holding on all eleven.

    python3 make_cell_multiply.py cell1.jpg

Input handling:
  * PNG with alpha            -> used as-is
  * photo on a plain backdrop -> auto-keyed by flood-filling from the corners
                                 (tune with --tol), then auto-cropped
  * --rect x0 y0 x1 y1        -> skip keying, just crop to that box

Outputs (1080x1920, 30fps, black background so it cuts against the rest):
    cell_x11_horizontal.mp4   single straight row
    cell_x11_diagonal.mp4     same row rotated across the frame, so each board
                              is ~2x larger - see the note in DIAGONAL below

Author: Claude (Opus), Jul 28 2026 session.
"""

import argparse
import math
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
N_CELLS = 11
FRAMES_PER_CELL = 5          # 5 / 30 = 0.167s per stamp -> 1.83s for all 11
HOLD_FRAMES = 30             # 1s on the finished set
# Transition on landing. Daniel's call Jul 29: OFF - each board just IS there
# on its frame, true stop-motion. Set POP_FRAMES=2 / FLASH=0.75 to get the
# stamp overshoot and shutter flash back.
POP_FRAMES = 0               # scale overshoot on landing (0 = hard cut)
FLASH = 0.0                  # 1-frame white hit on the newest board
BG_TOP = (16, 18, 22)
BG_BOT = (7, 8, 10)

# DIAGONAL: a straight horizontal row of 11 across 1080px gives each board only
# ~85px. The frame diagonal is ~2200px, so the same eleven boards laid along it
# are ~190px each - more than double, no change to the "one row, locked off"
# idea. Both are rendered; pick in the edit.
# Steep enough that the frame HEIGHT, not its width, sets the line length -
# at a shallow angle the diagonal buys almost nothing over a straight row.
DIAG_DEG = -52.0


# ---------------------------------------------------------------------------
# INPUT
# ---------------------------------------------------------------------------
def key_out(img, tol=42):
    """Flood-fill the backdrop from the four corners; return RGBA."""
    img = img.convert("RGB")
    a = np.asarray(img).astype(np.int16)
    h, w, _ = a.shape
    seeds = [(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)]
    ref = np.array([a[y, x] for y, x in seeds]).mean(axis=0)
    close = (np.abs(a - ref).sum(axis=2) < tol * 3)

    # 4-connected flood from the corner pixels, iterated dilation on `close`
    mask = np.zeros((h, w), bool)
    for y, x in seeds:
        if close[y, x]:
            mask[y, x] = True
    prev = -1
    while mask.sum() != prev:
        prev = mask.sum()
        g = mask.copy()
        g[1:, :] |= mask[:-1, :]
        g[:-1, :] |= mask[1:, :]
        g[:, 1:] |= mask[:, :-1]
        g[:, :-1] |= mask[:, 1:]
        mask = g & close
    alpha = np.where(mask, 0, 255).astype(np.uint8)
    out = Image.fromarray(np.dstack([np.asarray(img), alpha]), "RGBA")
    return out


def autocrop(img):
    a = np.asarray(img)[:, :, 3]
    ys, xs = np.where(a > 8)
    if len(xs) == 0:
        return img
    return img.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def load_cell(path, tol, rect):
    img = Image.open(path)
    if rect:
        img = img.convert("RGBA").crop(tuple(rect))
    elif img.mode == "RGBA" and np.asarray(img)[:, :, 3].min() < 250:
        img = img.convert("RGBA")
    else:
        img = key_out(img, tol)
    img = autocrop(img)
    # gentle edge feather so the cut-out does not look pasted on
    a = img.split()[3].filter(ImageFilter.GaussianBlur(0.8))
    img.putalpha(a)
    return img


def synthetic_cell():
    """Stand-in board, used only for the preview before the real photo exists."""
    w, h = 520, 360
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 12, fill=(196, 168, 92, 255),
                        outline=(150, 124, 62, 255), width=3)
    for gy in range(18, h - 10, 17):          # perfboard hole grid
        for gx in range(18, w - 10, 17):
            d.ellipse([gx - 2, gy - 2, gx + 2, gy + 2], fill=(120, 96, 48, 255))
    for cx, ch in ((70, 150), (300, 190)):    # the 595 and the ULN
        d.rounded_rectangle([cx, 90, cx + ch, 230], 6, fill=(24, 24, 28, 255))
        for k in range(8):
            yy = 100 + k * 16
            d.rectangle([cx - 8, yy, cx + 2, yy + 6], fill=(190, 190, 196, 255))
            d.rectangle([cx + ch - 2, yy, cx + ch + 8, yy + 6],
                        fill=(190, 190, 196, 255))
    for k in range(8):                        # the jumper fan
        d.line([90 + k * 6, 100 + k * 16, 300 - k * 4, 228 - k * 16],
               fill=(60, 70, 90, 255), width=4)
    return im


# ---------------------------------------------------------------------------
# LAYOUT
# ---------------------------------------------------------------------------
CASCADE_OVERLAP = 0.50   # each board advances by 50% of its width
CASCADE_DROP = 42        # ...and steps down this many px, so nothing is buried


ROWS_443 = (4, 4, 3)     # = 11, and it matches how the real boards populate:
                         # board A = cells 1-4, B = 5-8, C = 9-11


def positions(mode, cell_w, cell_h):
    """Centres + a common scale so 11 cells fit the chosen layout."""
    if mode == "grid443":
        cols = max(ROWS_443)
        mx, gx, gy = 40, 14, 20
        cw = (W - 2 * mx - gx * (cols - 1)) / cols
        scale = cw / cell_w
        ch = cell_h * scale
        block_h = ch * len(ROWS_443) + gy * (len(ROWS_443) - 1)
        y0 = (H - block_h) / 2 + ch / 2
        pts = []
        for r, n in enumerate(ROWS_443):
            # a short row is centred, not left-aligned
            row_w = cw * n + gx * (n - 1)
            x0 = (W - row_w) / 2 + cw / 2
            for c in range(n):
                pts.append((x0 + c * (cw + gx), y0 + r * (ch + gy)))
        return pts, scale, 0.0
    if mode == "cascade":
        # Left-to-right like a fanned deck: overlapping horizontally but
        # stepped vertically, so every board stays readable AND each one is
        # ~2x the width it could be in a straight row.
        margin = 40
        adv = CASCADE_OVERLAP
        span = W - 2 * margin
        cw = span / (1.0 + adv * (N_CELLS - 1))
        scale = cw / cell_w
        ch = cell_h * scale
        total_drop = CASCADE_DROP * (N_CELLS - 1)
        y0 = H / 2 - total_drop / 2
        return [(margin + cw / 2 + i * cw * adv, y0 + i * CASCADE_DROP)
                for i in range(N_CELLS)], scale, 0.0
    if mode == "horizontal":
        margin, gap = 34, 9
        span = W - 2 * margin
        cw = (span - gap * (N_CELLS - 1)) / N_CELLS
        scale = cw / cell_w
        y = H * 0.5
        return [(margin + cw / 2 + i * (cw + gap), y) for i in range(N_CELLS)], \
            scale, 0.0
    ang = math.radians(DIAG_DEG)
    # longest chord of the frame at this angle, minus a margin
    L = min(abs((W - 90) / math.cos(ang)), abs((H - 160) / math.sin(ang)))
    gap = 10
    cw = (L - gap * (N_CELLS - 1)) / N_CELLS
    scale = cw / cell_w
    step = cw + gap
    cx, cy = W / 2, H / 2
    off = (N_CELLS - 1) / 2.0
    pts = [(cx + (i - off) * step * math.cos(ang),
            cy + (i - off) * step * math.sin(ang)) for i in range(N_CELLS)]
    return pts, scale, DIAG_DEG


def background():
    g = np.linspace(0, 1, H)[:, None]
    a = np.zeros((H, W, 3), np.float32)
    for k in range(3):
        a[:, :, k] = BG_TOP[k] + (BG_BOT[k] - BG_TOP[k]) * g
    return Image.fromarray(a.astype(np.uint8))


def build(cell, mode, outdir):
    os.makedirs(outdir, exist_ok=True)
    pts, scale, rot = positions(mode, cell.width, cell.height)
    base_w = max(2, int(round(cell.width * scale)))
    base_h = max(2, int(round(cell.height * scale)))
    bg = background()

    total = N_CELLS * FRAMES_PER_CELL + HOLD_FRAMES
    for fi in range(total):
        frame = bg.copy()
        placed = min(N_CELLS, fi // FRAMES_PER_CELL + 1)
        for i in range(placed):
            age = fi - i * FRAMES_PER_CELL
            if POP_FRAMES > 0:
                # stamp overshoot: lands big, settles over POP_FRAMES
                k = 1.0 + 0.16 * max(0.0, (POP_FRAMES - age) / POP_FRAMES)
            else:
                k = 1.0
            w2, h2 = max(2, int(base_w * k)), max(2, int(base_h * k))
            spr = cell.resize((w2, h2), Image.LANCZOS)
            if rot:
                spr = spr.rotate(-rot, expand=True, resample=Image.BICUBIC)
            if FLASH > 0 and age == 0:         # 1-frame flash = the shutter hit
                wht = Image.new("RGBA", spr.size, (255, 255, 255, 0))
                wht.putalpha(spr.split()[3].point(lambda v: int(v * FLASH)))
                spr = Image.alpha_composite(spr, wht)
            x, y = pts[i]
            px, py = int(x - spr.width / 2), int(y - spr.height / 2)
            # drop shadow, so overlapping boards separate from each other
            sh = Image.new("RGBA", spr.size, (0, 0, 0, 0))
            sh.putalpha(spr.split()[3].point(lambda v: int(v * 0.62)))
            sh = sh.filter(ImageFilter.GaussianBlur(7))
            frame.paste(sh, (px + 6, py + 9), sh)
            frame.paste(spr, (px, py), spr)
        frame.save("%s/m%04d.png" % (outdir, fi))
    return total


def encode(outdir, out):
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i",
                    "%s/m%%04d.png" % outdir, "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-crf", "16",
                    "-movflags", "+faststart", out],
                   check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
    print("wrote", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo", nargs="?", help="photo of cell #1")
    ap.add_argument("--tol", type=int, default=42)
    ap.add_argument("--rect", type=int, nargs=4, default=None)
    ap.add_argument("--suffix", default="")
    a = ap.parse_args()

    if a.photo:
        cell = load_cell(a.photo, a.tol, a.rect)
        cell.save("cell_cutout%s.png" % a.suffix)
        print("cut-out saved: cell_cutout%s.png  (%dx%d) - EYEBALL THIS FIRST"
              % (a.suffix, cell.width, cell.height))
    else:
        cell = synthetic_cell()
        print("no photo given - using the synthetic stand-in board")

    for mode in ("grid443", "cascade", "horizontal"):
        n = build(cell, mode, "mframes_" + mode)
        encode("mframes_" + mode, "cell_x11_%s%s.mp4" % (mode, a.suffix))
        print("  %s: %d frames, %.2fs" % (mode, n, n / FPS))


if __name__ == "__main__":
    main()

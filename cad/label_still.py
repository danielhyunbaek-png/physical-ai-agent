"""Annotated exploded still for the Big Reset video (and thumbnails).

Re-uses render_new_plate's transform so leader lines land on the right parts.
"""
import importlib.util
import math
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

spec = importlib.util.spec_from_file_location("rnp", "render_new_plate.py")
R = importlib.util.module_from_spec(spec)
sys.modules["rnp"] = R
spec.loader.exec_module(R)

FONT = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")


def project(v, az, el, dist, W, H, fov=30.0, ss=1):
    a, e = math.radians(az), math.radians(-el)
    Rz = np.array([[math.cos(a), math.sin(a), 0],
                   [-math.sin(a), math.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, math.cos(e), math.sin(e)],
                   [0, -math.sin(e), math.cos(e)]])
    cam = v @ (Rx @ Rz).T
    depth = cam[:, 1] + dist
    fl = (H * ss / 2.0) / math.tan(math.radians(fov) / 2.0)
    safe = np.maximum(depth, 1.0)
    sx = W * ss / 2.0 + fl * cam[:, 0] / safe
    sy = H * ss / 2.0 - fl * cam[:, 2] / safe
    sx += W * ss / 2.0 - (sx.min() + sx.max()) / 2.0
    sy += H * ss / 2.0 - (sy.min() + sy.max()) / 2.0
    return sx / ss, sy / ss


def anchor(vv, sx, sy, pred):
    idx = np.where(pred)[0]
    return float(sx[idx].mean()), float(sy[idx].mean())


def build_labeled(W, H, az, el, out, fsize, order):
    j = R._init_job()
    v, f, cols = j["v"], j["f"], j["cols"]
    groups = {"deck": j["deck"], "rows": j["rows"]}
    vv = R.make_state(v, groups, 1, 1, j["y_mid"])
    dist = R.fit_exact(vv, az, el, W, H)
    img = R.render(vv, f, cols, W, H, az, el, dist).convert("RGB")
    sx, sy = project(vv, az, el, dist, W, H)

    mask_deck = np.zeros(len(vv), bool)
    mask_deck[j["deck"]] = True
    mask_rows = [np.zeros(len(vv), bool) for _ in j["rows"]]
    for k, vid in enumerate(j["rows"]):
        mask_rows[k][vid] = True
    mask_static = ~mask_deck.copy()
    for mr in mask_rows:
        mask_static &= ~mr

    pts = {
        "deck": anchor(vv, sx, sy, mask_deck),
        "hi": anchor(vv, sx, sy, mask_rows[3]),
        "low": anchor(vv, sx, sy, mask_rows[0]),
        # leftmost static vertex = the exposed plate corner, which is the only
        # unambiguous place to point at once the rows have fanned out
        "plate": (lambda i: (float(sx[i]), float(sy[i])))(
            np.where(mask_static)[0][np.argmin(sx[mask_static])]),
    }

    d = ImageDraw.Draw(img, "RGBA")
    try:
        fb = ImageFont.truetype(FONT[0], fsize)
        fs = ImageFont.truetype(FONT[1], int(fsize * 0.72))
    except OSError:
        fb = fs = ImageFont.load_default()

    for key, title, sub, side in order:
        px, py = pts[key]
        tw = max(d.textlength(title, font=fb), d.textlength(sub, font=fs))
        bw, bh = tw + 34, fsize * 2 + 30
        bx = 40 if side == "L" else W - bw - 40
        by = min(max(py - bh / 2, 30), H - bh - 30)
        d.rounded_rectangle([bx, by, bx + bw, by + bh], 10,
                            fill=(18, 20, 25, 225), outline=(232, 168, 76, 190),
                            width=2)
        d.text((bx + 17, by + 12), title, font=fb, fill=(240, 244, 250))
        d.text((bx + 17, by + 14 + fsize), sub, font=fs, fill=(158, 168, 182))
        ex = bx + bw if side == "L" else bx
        d.line([ex, by + bh / 2, px, py], fill=(232, 168, 76, 210), width=3)
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=(232, 168, 76))

    img.save(out)
    print("wrote", out)


if __name__ == "__main__":
    build_labeled(
        1920, 1080, -34, 26, "new_plate_exploded_wide_labeled.png", 34,
        [("deck", "3 driver PCBs on a top deck", "120 x 66 mm each - 88 channels", "L"),
         ("hi", "6 removable wall modules", "swap any row without touching the others", "R"),
         ("low", "84 solenoids", "leads run straight UP through the deck", "L"),
         ("plate", "plate + side rails", "Nuphy Air75 V3 underneath, 4 deg tilt", "R")])
    build_labeled(
        1080, 1920, -34, 24, "new_plate_exploded_still_labeled.png", 30,
        [("deck", "3 driver PCBs", "on a top deck", "L"),
         ("hi", "removable walls", "one row = one module", "R"),
         ("low", "84 solenoids", "wires straight up", "L")])

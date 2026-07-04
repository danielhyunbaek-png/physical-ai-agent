"""Calibration workflows. Run once per physical setup change, before games.

    python calibrate.py screen                # webcam -> screen corners
    python calibrate.py tft --still shot.png  # check TFT layout points
    python calibrate.py gantry --port ...     # screen px -> gantry mm affine
    python calibrate.py mousekeys             # measure Mouse Keys speeds

Outputs land in agent/calibration/ and are picked up via --calib /
--mouse-calib flags (or automatically where noted). All flows are
keyboard-prompt driven -- no GUI needed, works over SSH.

  screen     Locks the monitor's 4 corners in webcam space so vision.screen()
             can rectify. Auto-detects (show a bright fullscreen page on the
             target) or takes corners typed by hand. Writes
             calibration/screen_quad.json; then pass --calib to entrypoints.
  tft        Draws every tft/layout.json point onto a screenshot ->
             tft_layout_check.png. Eyeball it; nudge layout.json; repeat
             until the dots sit on the shop cards / hexes / buttons.
  gantry     Commands the gantry to 3+ known mm positions; you read the
             resulting cursor position off the target screen (or the check
             image) and type it in. Fits the px->mm affine and writes
             calibration/gantry_affine.json for --mouse-calib.
  mousekeys  Measures held-key speed (est_px_s) and px-per-tap through the
             physical keyboard; writes calibration/mousekeys.json.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CAL_DIR = os.path.join(HERE, "calibration")


def _save(name, data):
    os.makedirs(CAL_DIR, exist_ok=True)
    path = os.path.join(CAL_DIR, name)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print("[calibrate] wrote {}".format(path))
    return path


def _ask_xy(prompt):
    raw = input(prompt + " (x,y): ").strip()
    x, y = [float(v) for v in raw.replace(" ", "").split(",")]
    return x, y


# ---- screen ------------------------------------------------------------------
def cal_screen(args):
    from vision import Vision
    v = Vision(camera_index=args.camera, still=args.still)
    if args.corners:
        pts = [tuple(map(float, c.split(","))) for c in args.corners]
        v.calibrate_screen(pts)
        print("[calibrate] using manual corners")
    else:
        print("[calibrate] auto-detecting -- show a BRIGHT fullscreen page "
              "(white browser window) on the target machine")
        v.calibrate_screen()
    print("[calibrate] quad:", v.screen_quad.tolist())
    v.save_screen_calibration(os.path.join(CAL_DIR, "screen_quad.json"))
    os.makedirs(CAL_DIR, exist_ok=True)
    v.save_frame(os.path.join(CAL_DIR, "screen_check.png"))
    print("[calibrate] inspect calibration/screen_check.png -- it should "
          "look like a flat screenshot, not a photo of a monitor")
    v.close()


# ---- tft layout overlay ---------------------------------------------------------
def cal_tft(args):
    import cv2
    from vision import Vision
    sys.path.insert(0, HERE)
    from tft.tft_agent import TFTLayout
    v = Vision(camera_index=args.camera, still=args.still,
               calib_path=os.path.join(CAL_DIR, "screen_quad.json")
               if not args.still else None)
    img = v.screen()
    L = TFTLayout(w=img.shape[1], h=img.shape[0])

    def dot(px, label):
        cv2.circle(img, px, 6, (0, 0, 255), 2)
        cv2.putText(img, label, (px[0] + 8, px[1] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

    for i in range(1, 6):
        dot(L.shop_px(i), "s{}".format(i))
    for i in range(9):
        dot(L.bench_px(i), "b{}".format(i))
    for r in range(4):
        for c in range(7):
            dot(L.hex_px(r, c), "{}{}".format(r, c))
    for name in ("buy_xp", "reroll", "lock"):
        dot(L.button_px(name), name)
    for i in range(1, 4):
        dot(L.augment_px(i), "aug{}".format(i))
    for name in ("gold", "stage", "level"):
        nx, ny, nw, nh = L.region(name)
        h, w = img.shape[:2]
        cv2.rectangle(img, (int(nx * w), int(ny * h)),
                      (int((nx + nw) * w), int((ny + nh) * h)),
                      (255, 0, 0), 1)
    out = args.out or "tft_layout_check.png"
    cv2.imwrite(out, img)
    print("[calibrate] wrote {} -- dots should sit on shop cards, bench "
          "slots, hexes, buttons. Nudge tft/layout.json and rerun until "
          "they do.".format(out))
    v.close()


# ---- gantry affine -----------------------------------------------------------------
def cal_gantry(args):
    from mouse_driver import GantryMouse, fit_affine
    g = GantryMouse(port=args.port, calib={"pad_mm": [args.pad_w, args.pad_h]})
    probes = [(args.pad_w * 0.1, args.pad_h * 0.1),
              (args.pad_w * 0.9, args.pad_h * 0.1),
              (args.pad_w * 0.5, args.pad_h * 0.9)]
    mm_pts, px_pts = [], []
    print("[calibrate] For each probe: the gantry moves the mouse, then you "
          "read the cursor position off the TARGET screen (e.g. a cursor-"
          "position webpage or a screenshot) and type it here.")
    for mx, my in probes:
        g._send("MOVE {:.2f} {:.2f}".format(mx, my))
        px = _ask_xy("cursor now at (gantry {:.0f},{:.0f}mm)".format(mx, my))
        mm_pts.append((mx, my))
        px_pts.append(px)
    A = fit_affine(px_pts, mm_pts)          # screen px -> pad mm
    _save("gantry_affine.json", {"affine": A,
                                 "pad_mm": [args.pad_w, args.pad_h],
                                 "probes_mm": mm_pts, "probes_px": px_pts})
    print("[calibrate] pass --mouse-calib calibration/gantry_affine.json")
    g.close()


# ---- mousekeys speeds ---------------------------------------------------------------
def cal_mousekeys(args):
    from keyboard_driver import KeyboardDriver
    from mouse_driver import MouseKeysMouse
    kb = KeyboardDriver(args.port)          # None = dry-run (rehearsal)
    m = MouseKeysMouse(kb)
    print("[calibrate] Put the TARGET cursor somewhere with readable "
          "coordinates (cursor-position webpage). Mouse Keys will toggle ON.")
    input("ready? [enter] ")
    m.enable()
    x0, _ = _ask_xy("cursor BEFORE")
    print("[calibrate] holding RIGHT (O) for 2.0s...")
    kb.hold("O")
    import time as _t
    _t.sleep(2.0)
    kb.release("O")
    x1, _ = _ask_xy("cursor AFTER hold")
    est_px_s = abs(x1 - x0) / 2.0
    print("[calibrate] now 20 single taps RIGHT...")
    for _ in range(20):
        kb.key("O")
    x2, _ = _ask_xy("cursor AFTER taps")
    tap_px = max(0.1, abs(x2 - x1) / 20.0)
    m.disable()
    _save("mousekeys.json", {"est_px_s": est_px_s, "tap_px": tap_px,
                             "fine_px": 40, "max_taps": 60})
    print("[calibrate] est_px_s={:.0f} tap_px={:.2f} -- pass "
          "--mouse-calib calibration/mousekeys.json".format(est_px_s, tap_px))


def main():
    ap = argparse.ArgumentParser(description="calibration workflows")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("screen", help="webcam -> screen corner quad")
    s.add_argument("--camera", type=int, default=0)
    s.add_argument("--still", default=None)
    s.add_argument("--corners", nargs=4, default=None,
                   metavar="X,Y", help="manual TL TR BR BL corners")
    s.set_defaults(fn=cal_screen)

    t = sub.add_parser("tft", help="overlay TFT layout points on a frame")
    t.add_argument("--camera", type=int, default=0)
    t.add_argument("--still", default=None)
    t.add_argument("--out", default=None)
    t.set_defaults(fn=cal_tft)

    g = sub.add_parser("gantry", help="fit screen-px -> gantry-mm affine")
    g.add_argument("--port", required=True)
    g.add_argument("--pad-w", type=float, default=300.0)
    g.add_argument("--pad-h", type=float, default=200.0)
    g.set_defaults(fn=cal_gantry)

    k = sub.add_parser("mousekeys", help="measure Mouse Keys speeds")
    k.add_argument("--port", default=None,
                   help="keyboard Arduino port (omit = dry-run rehearsal)")
    k.set_defaults(fn=cal_mousekeys)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()

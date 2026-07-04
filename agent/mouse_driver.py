"""Mouse drivers for the Physical AI Agent (Wave 2 abstraction layer).

All drivers speak SCREEN PIXELS in the rectified 1920x1080 space that
vision.screen() returns -- the agent thinks in one coordinate system and each
backend translates to its own device space. Wave 2 hardware is undecided
(gantry favored for TFT's drag requirement), so the agent codes against
MouseDriver and the backend is a --mouse flag:

    none       no mouse (keyboard-only goals)
    dry        prints actions -- campsite/plumbing tests
    mousekeys  macOS Mouse Keys driven THROUGH THE PHYSICAL KEYBOARD.
               The $0 backend: the robot moves the cursor without touching
               the mouse. Works TODAY with Wave 1 hardware only.
    gantry     XY gantry + click servos over serial (firmware/mouse_gantry_v0)

Dead reckoning is deliberately rough: the agent loop re-observes after every
action and issues corrective moves, so vision closes the loop -- drivers only
need to be directionally right, not exact.

MOUSE KEYS SETUP (one-time, on the TARGET Mac):
  System Settings > Accessibility > Pointer Control > Alternate Control
  Methods > enable "Mouse Keys", and under Options enable "Press the Option
  key five times to toggle Mouse Keys". Set Initial Delay short / Max Speed
  mid. Layout (no numpad): 7 8 9 / U _ O / J K L move (8=up K=down U=left
  O=right, corners diagonal), I=click, M=hold button, .=release.
  CAVEAT: while Mouse Keys is ON those letters don't type -- the driver
  toggles it off around text input (see suspend()/resume()).
"""

from __future__ import annotations

import json
import os
import time

try:
    import serial  # pyserial, only needed for GantryMouse on real hardware
except ImportError:
    serial = None

SCREEN_W, SCREEN_H = 1920, 1080


# ---- calibration math ----------------------------------------------------------
def fit_affine(src_pts, dst_pts):
    """Least-squares affine A mapping src (x,y) -> dst (x,y).

    Needs >= 3 non-collinear point pairs. Returns [[a,b,tx],[c,d,ty]] as
    plain lists (JSON-serializable).
    """
    import numpy as np
    src = np.asarray(src_pts, dtype=float)
    dst = np.asarray(dst_pts, dtype=float)
    n = src.shape[0]
    if n < 3:
        raise ValueError("need >= 3 point pairs for an affine fit")
    m = np.hstack([src, np.ones((n, 1))])          # n x 3
    sol, _, _, _ = np.linalg.lstsq(m, dst, rcond=None)   # 3 x 2
    return sol.T.tolist()                          # 2 x 3


def apply_affine(A, x, y):
    ax = A[0][0] * x + A[0][1] * y + A[0][2]
    ay = A[1][0] * x + A[1][1] * y + A[1][2]
    return ax, ay


def load_calibration(path):
    """Load a calibration JSON written by calibrate.py; None if absent."""
    if path and os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


# ---- interface -----------------------------------------------------------------
class MouseDriver:
    """Base: tracks believed cursor position in screen px; subclasses act."""

    name = "base"

    def __init__(self):
        self.pos = (SCREEN_W // 2, SCREEN_H // 2)   # believed position

    # -- overridables ---------------------------------------------------------
    def _move(self, x, y):
        raise NotImplementedError

    def _button(self, button, down):
        raise NotImplementedError

    def home(self):
        """Return to a known reference (gantry: physical home switch)."""
        pass

    def close(self):
        pass

    # -- shared API (what the agent calls) -------------------------------------
    def move_to(self, x, y):
        x = max(0, min(SCREEN_W - 1, int(x)))
        y = max(0, min(SCREEN_H - 1, int(y)))
        self._move(x, y)
        self.pos = (x, y)

    def press(self, button="L"):
        self._button(button, True)

    def release(self, button="L"):
        self._button(button, False)

    def click(self, button="L", x=None, y=None):
        if x is not None and y is not None:
            self.move_to(x, y)
        self.press(button)
        time.sleep(0.06)
        self.release(button)

    def drag(self, x1, y1, x2, y2, button="L", settle_s=0.15):
        """Press at (x1,y1), move to (x2,y2), release. TFT bench->board."""
        self.move_to(x1, y1)
        time.sleep(settle_s)
        self.press(button)
        time.sleep(settle_s)
        self.move_to(x2, y2)
        time.sleep(settle_s)
        self.release(button)

    # keyboard-coexistence hooks (only MouseKeys needs them)
    def suspend(self):
        """Called before keyboard text input; release grabbed keys/modes."""
        pass

    def resume(self):
        """Called before the next mouse action."""
        pass


# ---- backends ---------------------------------------------------------------
class DryRunMouse(MouseDriver):
    """Prints every action; the campsite backend. Also used by tests."""

    name = "dry"

    def __init__(self):
        MouseDriver.__init__(self)
        self.log = []                      # tests inspect this

    def _emit(self, s):
        self.log.append(s)
        print(f"[mouse] {s}")

    def _move(self, x, y):
        self._emit(f"MOVE -> ({x}, {y})")

    def _button(self, button, down):
        self._emit(f"BTN {button} {'DOWN' if down else 'UP'}")

    def home(self):
        self._emit("HOME")


class MouseKeysMouse(MouseDriver):
    """Cursor control through the PHYSICAL keyboard via macOS Mouse Keys.

    Strategy per move: HOLD the direction key for a coarse leg (macOS
    accelerates while held; est_px_s calibrates the post-ramp speed), then
    single taps for the fine leg (1 tap = ~1 px before acceleration).
    The agent's observe-correct loop absorbs the ramp nonlinearity.

    State machine: Mouse Keys must be ON to move and OFF to type letters.
    enable()/disable() toggle it with 5 quick Option presses; the Actuators
    layer calls suspend() before keyboard actions and resume() before mouse
    actions so the two never fight.
    """

    name = "mousekeys"
    DIR_KEYS = {(0, -1): "8", (0, 1): "K", (-1, 0): "U", (1, 0): "O",
                (-1, -1): "7", (1, -1): "9", (-1, 1): "J", (1, 1): "L"}

    def __init__(self, kb, calib=None):
        MouseDriver.__init__(self)
        self.kb = kb                       # KeyboardDriver (dry-run ok)
        calib = calib or {}
        self.est_px_s = float(calib.get("est_px_s", 350))   # held-key speed
        self.tap_px = float(calib.get("tap_px", 1.0))       # px per tap
        self.fine_px = int(calib.get("fine_px", 40))        # tap below this
        self.max_taps = int(calib.get("max_taps", 60))      # wear guard
        self.enabled = False

    # -- mode toggling -------------------------------------------------------
    def _toggle(self):
        for _ in range(5):                 # 5x Option = macOS toggle
            self.kb.key("LOpt")
            time.sleep(0.12)
        time.sleep(0.4)

    def enable(self):
        if not self.enabled:
            self._toggle()
            self.enabled = True

    def disable(self):
        if self.enabled:
            self._toggle()
            self.enabled = False

    def suspend(self):
        self.disable()

    def resume(self):
        self.enable()

    # -- movement ---------------------------------------------------------------
    def _leg(self, dx, dy):
        """One axis-or-diagonal leg. Returns px actually attempted."""
        sx = 0 if dx == 0 else (1 if dx > 0 else -1)
        sy = 0 if dy == 0 else (1 if dy > 0 else -1)
        key = self.DIR_KEYS[(sx, sy)]
        dist = max(abs(dx), abs(dy))
        if dist > self.fine_px:            # coarse: hold + timed release
            hold_s = dist / self.est_px_s
            self.kb.hold(key)
            time.sleep(min(hold_s, 5.0))
            self.kb.release(key)
        else:                              # fine: discrete taps
            taps = min(int(dist / self.tap_px), self.max_taps)
            for _ in range(taps):
                self.kb.key(key)
        return dist

    def _move(self, x, y):
        self.resume()
        dx, dy = x - self.pos[0], y - self.pos[1]
        d = min(abs(dx), abs(dy))          # diagonal leg first
        if d > 3:
            self._leg((1 if dx > 0 else -1) * d, (1 if dy > 0 else -1) * d)
            dx -= (1 if dx > 0 else -1) * d
            dy -= (1 if dy > 0 else -1) * d
        if abs(dx) > 0:
            self._leg(dx, 0)
        if abs(dy) > 0:
            self._leg(0, dy)

    def _button(self, button, down):
        self.resume()
        if button == "R":                  # ctrl-click = macOS secondary
            if down:
                self.kb.hold("LCtrl")
                self.kb.key("I")
                self.kb.release("LCtrl")
            return
        self.kb.key("M" if down else ".")  # M = press-and-hold, . = release

    def click(self, button="L", x=None, y=None):
        if x is not None and y is not None:
            self.move_to(x, y)
        self.resume()
        if button == "R":
            self._button("R", True)
        else:
            self.kb.key("I")               # I = full click, atomic

    def close(self):
        self.disable()


class GantryMouse(MouseDriver):
    """XY gantry + SG90 click servos, serial line protocol (115200 baud).

    Speaks firmware/mouse_gantry_v0: HOME, MOVE <x_mm> <y_mm>, BTN <L|R>
    <DOWN|UP>, CLICK <L|R> [ms], STATUS, STOP -- every command answered with
    OK/ERR. Screen px -> pad mm via the affine from calibrate.py gantry
    (calibration/gantry_affine.json); an uncalibrated fallback scales the
    full screen onto the pad (rough, but vision corrects).

    Pass transport=<obj with write()/readline()> to test without hardware.
    """

    name = "gantry"

    def __init__(self, port=None, calib=None, transport=None,
                 pad_mm=(300.0, 200.0)):
        MouseDriver.__init__(self)
        calib = calib or {}
        self.pad_mm = tuple(calib.get("pad_mm", pad_mm))
        self.A = calib.get("affine")       # px -> mm, or None
        if transport is not None:
            self.ser = transport
        else:
            if serial is None:
                raise RuntimeError("pyserial missing: pip install pyserial")
            self.ser = serial.Serial(port, 115200, timeout=3.0)
            time.sleep(2.0)                # firmware boot
        self.home()

    def _send(self, line):
        self.ser.write((line + "\n").encode())
        deadline = time.time() + 10.0
        while time.time() < deadline:
            raw = self.ser.readline().decode(errors="replace").strip()
            if raw.startswith("OK"):
                return raw
            if raw.startswith("ERR"):
                raise RuntimeError(f"gantry: {raw} (sent: {line})")
        raise RuntimeError(f"gantry timeout (sent: {line})")

    def _px_to_mm(self, x, y):
        if self.A:
            return apply_affine(self.A, x, y)
        return (x / SCREEN_W * self.pad_mm[0],       # uncalibrated fallback
                y / SCREEN_H * self.pad_mm[1])

    def _move(self, x, y):
        mx, my = self._px_to_mm(x, y)
        mx = max(0.0, min(self.pad_mm[0], mx))
        my = max(0.0, min(self.pad_mm[1], my))
        self._send("MOVE {:.2f} {:.2f}".format(mx, my))

    def _button(self, button, down):
        self._send("BTN {} {}".format(button, "DOWN" if down else "UP"))

    def click(self, button="L", x=None, y=None):
        if x is not None and y is not None:
            self.move_to(x, y)
        self._send("CLICK {}".format(button))       # firmware-timed, atomic

    def home(self):
        self._send("HOME")
        self.pos = (0, 0)

    def close(self):
        try:
            self._send("STOP")
        except Exception:
            pass
        if hasattr(self.ser, "close"):
            self.ser.close()


# ---- factory ------------------------------------------------------------------
def make_mouse(kind, kb=None, port=None, calib_path=None):
    """kind: none | dry | mousekeys | gantry. Returns a MouseDriver or None."""
    calib = load_calibration(calib_path)
    if kind in (None, "none"):
        return None
    if kind == "dry":
        return DryRunMouse()
    if kind == "mousekeys":
        if kb is None:
            raise ValueError("mousekeys backend needs the keyboard driver")
        return MouseKeysMouse(kb, calib)
    if kind == "gantry":
        return GantryMouse(port=port, calib=calib)
    raise ValueError("unknown mouse kind: {}".format(kind))


if __name__ == "__main__":
    # smoke test: dry-run drag (the TFT primitive)
    m = DryRunMouse()
    m.drag(500, 900, 700, 600)
    m.click("L", 960, 1000)
    print("[mouse] smoke test done")

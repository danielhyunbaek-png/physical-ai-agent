"""Serial driver for keyboard_v1 firmware (Arduino Mega, 115200 baud).

Wraps the firmware's line protocol in a Python API. Campsite-testable with no
hardware: pass port=None for a dry-run driver that logs instead of sending.

Usage:
    kb = KeyboardDriver("/dev/tty.usbmodem14101")   # or port=None for dry-run
    kb.type_text("Hello, World!")
    kb.key("Enter")
    kb.chord("LCmd", "Space")
"""

import sys
import time

try:
    import serial  # pyserial
except ImportError:
    serial = None


class KeyboardDriver:
    def __init__(self, port=None, baud=115200, timeout=2.0):
        self.dry_run = port is None
        if self.dry_run:
            self.ser = None
            print("[kb] DRY RUN -- no serial port, commands will be logged")
        else:
            if serial is None:
                sys.exit("pyserial missing: pip install pyserial")
            self.ser = serial.Serial(port, baud, timeout=timeout)
            time.sleep(2.5)          # Mega auto-resets on connect; wait for boot
            self._drain()

    # ---- low-level ------------------------------------------------------------
    def _drain(self):
        if self.ser:
            while self.ser.in_waiting:
                self.ser.readline()

    def send(self, line, wait_ok=True):
        """Send one command line; return firmware reply lines."""
        if self.dry_run:
            print(f"[kb] > {line}")
            return ["OK DRY"]
        self.ser.write((line + "\n").encode())
        replies = []
        if wait_ok:
            deadline = time.time() + 5.0
            while time.time() < deadline:
                raw = self.ser.readline().decode(errors="replace").strip()
                if not raw:
                    continue
                replies.append(raw)
                if raw.startswith(("OK", "ERR", "PULSE", "LEAD", "STATUS")):
                    break
        return replies

    # ---- firmware API ----------------------------------------------------------
    def fire(self, channel, ms=None):
        return self.send(f"FIRE {channel}" + (f" {ms}" if ms else ""))

    def pulse(self, ms=None):
        return self.send("PULSE" + (f" {ms}" if ms else ""))

    def type_text(self, text, lead_ms=0):
        """Type text on the physical keyboard. Firmware handles shift chords.

        keyboard_v1 buffers 127 chars/line -- chunk long text here.
        lead_ms: extra head start to focus the target window (uses LEAD).
        """
        self.send(f"LEAD {lead_ms}")
        out = []
        for chunk in _chunks(text, 100):
            out += self.send(f"TYPE {chunk}", wait_ok=True)
            self.send("LEAD 0")   # only lead once
        return out

    def key(self, name):
        """Press a named key: Enter, Bksp, Tab, Esc, F1..F12, Up/Down/Left/Right,
        Space, nav-Home/End/PgUp/PgDn, LShift/RShift, LCtrl/LOpt/LCmd..."""
        return self.send(f"KEY {name}")

    def chord(self, *names):
        """chord('LCmd', 'Space') -> CHORD LCmd+Space (mods held, last fired)."""
        return self.send("CHORD " + "+".join(names))

    def hold(self, name):
        return self.send(f"HOLD {name}")

    def release(self, name="ALL"):
        return self.send(f"RELEASE {name}")

    def walk(self, start=0, end=87, pulse=None, gap=800):
        """MAP-verification pass; watch the keyboard and log which key clicks."""
        p = pulse or ""
        return self.send(f"WALK {start} {end} {p} {gap}".replace("  ", " "),
                         wait_ok=False)

    def set_map(self, channel, key_name):
        return self.send(f"MAP {channel} {key_name}")

    def save_map(self):
        return self.send("SAVE")

    def status(self):
        return self.send("STATUS")

    def all_off(self):
        return self.send("ALLOFF")

    def close(self):
        if self.ser:
            self.all_off()
            self.ser.close()


def _chunks(s, n):
    return [s[i:i + n] for i in range(0, len(s), n)]


def load_map_from_log(driver, log_path):
    """Push a solder-time MAP log to the firmware and SAVE it.

    Log format (one line per landed wire, written at solder time):
        cell,out,key        e.g.  1,1,Esc
                                  1,2,F1
    channel = (cell-1)*8 + (out-1)   [canonical wiring, FIRE N -> OUT(N+1)]
    """
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            cell, out, key = [x.strip() for x in line.split(",")]
            ch = (int(cell) - 1) * 8 + (int(out) - 1)
            driver.set_map(ch, key)
    driver.save_map()
    print(f"[kb] map loaded from {log_path} and saved to EEPROM")


if __name__ == "__main__":
    # smoke test: dry-run unless a port is given
    port = sys.argv[1] if len(sys.argv) > 1 else None
    kb = KeyboardDriver(port)
    kb.status()
    kb.type_text("hello")
    kb.key("Enter")
    kb.chord("LCmd", "Space")
    kb.close() if not kb.dry_run else None
    print("[kb] smoke test done")

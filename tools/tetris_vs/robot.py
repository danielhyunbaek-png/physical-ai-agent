"""robot -- the ONLY way Claude's Tetris game can touch the physical world.

    import robot
    robot.WINDOW            (width, height) for pygame.display.set_mode
    robot.press(key)        "J" "L" "I" "K" "Space" -> one physical press (queued)
    robot.pending()         presses queued or in flight
    robot.say(text)         speak out loud (macOS `say`), skipped if already talking
    robot.tick()            call once per frame
    robot.report(k, v)      status for the pre-flight test

Modes (env TETRIS_ROBOT):
    real  (default) presses go to the Mega over USB serial: KEY <name>
    sim   no hardware: a press becomes a pygame KEYDOWN after a realistic delay,
          with occasional missed / doubled presses (so Claude's retry logic is
          exercised). Used by the pre-flight test and for laptop rehearsals.

Other env:
    TETRIS_WINDOW       default 1280x720
    TETRIS_SAMEKEY      same-key min period ms, default 130 (50 ms pulse + plate-sag
                        release, Oct 5)
    TETRIS_REPORT       path: pre-flight writes reports here as JSON
    TETRIS_SIM_OPPONENT 1 = sim mode also clicks start, plays Daniel badly, and
                        presses R for one rematch (pre-flight only)
    TETRIS_SIM_MISS     sim missed-press probability, default 0.05
    TETRIS_SILENT       1 = never speak
    KB_PORT, KB_PULSE   as in tools/selfwrite
"""

import atexit
import collections
import glob
import json
import os
import random
import subprocess
import sys
import threading
import time

MODE = os.environ.get("TETRIS_ROBOT", "real")
WINDOW = tuple(int(v) for v in os.environ.get("TETRIS_WINDOW", "1280x720").split("x"))
SAMEKEY_S = int(os.environ.get("TETRIS_SAMEKEY", "130")) / 1000.0
PULSE_MS = int(os.environ.get("KB_PULSE", "50"))
REPORT_PATH = os.environ.get("TETRIS_REPORT")
SIM_OPPONENT = os.environ.get("TETRIS_SIM_OPPONENT") == "1"
SIM_MISS = float(os.environ.get("TETRIS_SIM_MISS", "0.05"))
SILENT = os.environ.get("TETRIS_SILENT") == "1" or bool(REPORT_PATH)
VOICE = os.environ.get("TETRIS_VOICE")          # e.g. "Daniel", "Samantha"

ALLOWED = ("J", "L", "I", "K", "Space")
MAX_QUEUE = 3

_lock = threading.Lock()
_queue = collections.deque()
_inflight = 0
_last_fire = {}
_stats = {"presses": 0, "ticks": 0, "said": [], "errors": 0}
_reports = {}


def _log(msg):
    print("[robot] " + msg, file=sys.stderr, flush=True)


# ---------------------------------------------------------------- reports
_last_dump = 0.0


def _dump(force=False):
    global _last_dump
    if not REPORT_PATH:
        return
    now = time.time()
    if not force and now - _last_dump < 0.25:
        return
    _last_dump = now
    data = dict(_reports)
    data.update(_stats)
    tmp = REPORT_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f)
    os.replace(tmp, REPORT_PATH)


def report(name, value):
    name = str(name)
    changed = _reports.get(name) != value
    _reports[name] = value
    if name == "claude_lines" and isinstance(value, int):
        _reports["best_claude_lines"] = max(_reports.get("best_claude_lines", 0), value)
    if name == "winner":
        w = "wins_" + str(value)
        if _reports.get("_last_state") != "over_counted":
            _reports[w] = _reports.get(w, 0) + 1
            _reports["matches"] = _reports.get("matches", 0) + 1
            _reports["_last_state"] = "over_counted"
    if name == "state" and value != "over":
        _reports["_last_state"] = value
    _dump(force=changed and name in ("state", "winner"))


# ---------------------------------------------------------------- voice
_say_proc = None
_last_say = 0.0


def say(text):
    global _say_proc, _last_say
    text = str(text)[:200]
    now = time.time()
    if _say_proc is not None and _say_proc.poll() is None:
        return False
    if now - _last_say < 1.0:
        return False
    _last_say = now
    _stats["said"].append(text)
    print("[claude says] " + text, flush=True)
    if SILENT or sys.platform != "darwin":
        _say_proc = None
        return True
    cmd = ["say", "-r", "195"] + (["-v", VOICE] if VOICE else []) + [text]
    try:
        _say_proc = subprocess.Popen(cmd)
    except OSError:
        _say_proc = None
    return True


# ---------------------------------------------------------------- presses
def press(key):
    if key not in ALLOWED:
        raise ValueError("robot.press: key must be one of %s, got %r" % (ALLOWED, key))
    with _lock:
        if len(_queue) >= MAX_QUEUE:
            return False
        _queue.append(key)
        _stats["presses"] += 1
    if MODE == "sim":
        _sim_schedule()
    return True


def pending():
    with _lock:
        return len(_queue) + _inflight + len(_sim_due)


_SHOTS = [x.split(":") for x in os.environ.get("TETRIS_SCREENSHOT", "").split(",") if x]


def tick():
    _stats["ticks"] += 1
    for path, n in _SHOTS:              # dev aid: TETRIS_SCREENSHOT=a.png:600,b.png:1800
        if _stats["ticks"] == int(n):
            import pygame as pg
            pg.image.save(pg.display.get_surface(), path)
    if MODE == "sim":
        _sim_tick()
    if REPORT_PATH and _stats["ticks"] % 30 == 0:
        _dump()


# ---------------------------------------------------------------- real mode
_ser = None


def _find_port():
    if os.environ.get("KB_PORT"):
        return os.environ["KB_PORT"]
    ports = sorted(glob.glob("/dev/cu.usbmodem*")) or sorted(glob.glob("/dev/tty.usbmodem*"))
    if not ports:
        sys.exit("[robot] no /dev/cu.usbmodem* -- is the Mega plugged in? (or set KB_PORT)")
    return ports[0]


def _readline(timeout):
    buf = b""
    end = time.time() + timeout
    while time.time() < end:
        b = _ser.read(1)
        if not b:
            continue
        if b == b"\n":
            return buf.decode(errors="replace").strip()
        buf += b
    return None


def _cmd(line, timeout=2.0):
    _ser.write((line + "\n").encode())
    end = time.time() + timeout
    while time.time() < end:
        r = _readline(end - time.time())
        if r is None:
            break
        if r.startswith(("OK", "ERR")):
            return r
    return "ERR timeout"


def _connect():
    global _ser
    import serial  # pyserial
    port = _find_port()
    deadline = time.time() + 15
    while True:
        try:
            _ser = serial.Serial(port, 115200, timeout=0.05)
            break
        except serial.SerialException:
            if time.time() > deadline:
                sys.exit("[robot] %s busy -- close Serial Monitor / other scripts" % port)
            time.sleep(0.3)
    time.sleep(2.5)                     # opening the port resets the Mega
    _ser.reset_input_buffer()
    _cmd("PULSE %d" % PULSE_MS)
    _cmd("LEAD 0")
    _log("robot keyboard ready on %s (pulse %d ms)" % (port, PULSE_MS))


def _worker():
    global _inflight
    while True:
        with _lock:
            key = _queue.popleft() if _queue else None
            if key:
                _inflight = 1
        if key is None:
            time.sleep(0.003)
            continue
        wait = _last_fire.get(key, 0) + SAMEKEY_S - time.time()
        if wait > 0:
            time.sleep(wait)
        _last_fire[key] = time.time()
        r = _cmd("KEY " + key)
        if not r.startswith("OK"):
            _stats["errors"] += 1
            _log("KEY %s -> %s" % (key, r))
        with _lock:
            _inflight = 0


def _shutdown():
    if _ser is not None:
        try:
            with _lock:
                _queue.clear()
            _ser.write(b"ALLOFF\n")
            time.sleep(0.1)
            _ser.close()
        except Exception:
            pass
    _dump(force=True)


atexit.register(_shutdown)

# ---------------------------------------------------------------- sim mode
_sim_due = []            # (time, pygame key)
_sim_t0 = None
_sim_last_menu_click = 0.0
_sim_rematches = 0
_sim_over_since = None
_sim_next_opp = 0.0
_SIM_KEYS = {"J": "j", "L": "l", "I": "i", "K": "k", "Space": "space"}


def _sim_schedule():
    # model the hardware: one press at a time, ~70 ms each, same-key period
    with _lock:
        while _queue:
            key = _queue.popleft()
            start = max([t for t, _, _ in _sim_due] + [time.time()])
            start = max(start, _last_fire.get(key, 0) + SAMEKEY_S)
            _last_fire[key] = start
            _sim_due.append((start + random.uniform(0.055, 0.09), key, True))


def _post_key(pg, k):
    pg.event.post(pg.event.Event(pg.KEYDOWN, key=k, mod=0, unicode="", scancode=0))
    pg.event.post(pg.event.Event(pg.KEYUP, key=k, mod=0, unicode="", scancode=0))


def _sim_tick():
    global _sim_t0, _sim_last_menu_click, _sim_rematches, _sim_over_since, _sim_next_opp
    import pygame as pg
    now = time.time()
    if _sim_t0 is None:
        _sim_t0 = now
    with _lock:
        due = [d for d in _sim_due if d[0] <= now]
        for d in due:
            _sim_due.remove(d)
    for _, key, _ in due:
        r = random.random()
        k = pg.key.key_code(_SIM_KEYS[key])
        if r < SIM_MISS:
            continue                       # missed press
        _post_key(pg, k)
        if r > 1 - SIM_MISS / 3:
            _post_key(pg, k)               # double press

    if not SIM_OPPONENT:
        return
    state = _reports.get("state")
    if state in (None, "menu") and now - _sim_t0 > 0.5 and now - _sim_last_menu_click > 1.0:
        _sim_last_menu_click = now
        pos = (WINDOW[0] // 2, WINDOW[1] // 2)
        pg.event.post(pg.event.Event(pg.MOUSEBUTTONDOWN, pos=pos, button=1))
        pg.event.post(pg.event.Event(pg.MOUSEBUTTONUP, pos=pos, button=1))
    if state == "over":
        if _sim_over_since is None:
            _sim_over_since = now
        if now - _sim_over_since > 1.5 and _sim_rematches < 1:
            _sim_rematches += 1
            _post_key(pg, pg.K_r)
    else:
        _sim_over_since = None
    if state == "playing" and now >= _sim_next_opp:
        # a weak "Daniel": wiggles and soft-drops, never hard-drops
        _sim_next_opp = now + 0.45
        _post_key(pg, random.choice([pg.K_LEFT, pg.K_RIGHT, pg.K_UP, pg.K_DOWN]))


# ---------------------------------------------------------------- start
if MODE == "real":
    _connect()
    threading.Thread(target=_worker, daemon=True).start()
elif MODE != "sim":
    sys.exit("[robot] TETRIS_ROBOT must be real or sim, got %r" % MODE)

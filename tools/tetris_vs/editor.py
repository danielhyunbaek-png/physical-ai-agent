"""Live editor + typo-proof typer: the on-camera "robot types the game" shot.

One process. The editor is a full-screen Terminal app (curses) that receives
whatever the robot's keys actually produce; the typer thread drives the robot
and keeps comparing what ARRIVED with what Claude wrote:

    wrong / doubled char  -> Backspace back to the mistake, retype
    missed char           -> retype
    line perfect          -> Enter (never before)

The editor auto-indents like a Python IDE (keep the previous indentation, +4
after a ':'), so the robot does not spend minutes pressing Space.

Keys only Daniel can press (the robot has no Ctrl mapped):
    Ctrl-P  pause      Ctrl-R  resume      Ctrl-C  abort
While paused Daniel may fix things by hand; the typer re-reads the screen on
resume, so anything already correct is kept.
"""

import os
import random
import re
import threading
import time

BKSP = ("\x7f", "\x08")
ENTER = ("\n", "\r")
SETTLE = float(os.environ.get("TETRIS_SETTLE", "0.15"))  # quiet time after a command before trusting the screen
CHUNK = 40
SEC_PER_CHAR = 0.12     # TYPE: 15 gap + 50 pulse + 60 settle ms, measured Oct 5
MAX_ACTIONS_PER_LINE = 30


class Editor:
    def __init__(self):
        self.lines, self.cur = [], ""
        self.keys = 0
        self.lock = threading.Lock()
        self.last_input = time.time()

    def feed(self, ch):
        with self.lock:
            self.keys += 1
            self.last_input = time.time()
            if ch in BKSP:
                if self.cur:
                    self.cur = self.cur[:-1]
                elif self.lines:
                    self.cur = self.lines.pop()
            elif ch in ENTER:
                line = self.cur.rstrip(" ")
                indent = len(self.cur) - len(self.cur.lstrip(" "))
                if line.endswith(":"):
                    indent += 4
                self.lines.append(line)
                self.cur = " " * indent
            elif " " <= ch <= "~":
                self.cur += ch

    def snapshot(self):
        with self.lock:
            return list(self.lines), self.cur, self.keys, self.last_input

    def text(self):
        with self.lock:
            return "\n".join(self.lines + [self.cur])


def common_prefix(a, b):
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i


def decide(lines, cur, target):
    """Next action from what is on screen. target = full code ending in '\\n'.
    Returns None (done), ('enter',), ('bksp', n) or ('type', text)."""
    r = "\n".join(lines + [cur])
    if r == target:
        return None
    p = common_prefix(r, target)
    if len(r) > p:
        extra = r[p:]
        if p >= len(target):
            return ("bksp", len(r) - p)
        if "\n" not in extra and extra.strip(" ") == "" and target[p] == "\n":
            return ("enter",)              # auto-indent on a blank / shorter line
        return ("bksp", len(r) - p)
    nxt = target[p:]
    if nxt[0] == "\n":
        return ("enter",)
    return ("type", nxt.split("\n", 1)[0])


class Typer(threading.Thread):
    def __init__(self, editor, kb, code):
        super().__init__(daemon=True)
        self.ed, self.kb, self.target = editor, kb, code
        self.total_lines = code.count("\n")
        self.fixes = 0
        self.paused = False
        self.aborted = False
        self.done = False
        self.msg = ""
        self.started = time.time()
        self._actions_on_line = {}
        self.chunk = CHUNK        # shrinks after a messy chunk, grows after clean ones

    def settle(self):
        while not self.aborted:
            _, _, _, last = self.ed.snapshot()
            if time.time() - last >= SETTLE:
                return
            time.sleep(min(0.02, SETTLE / 4))

    def remaining_seconds(self):
        lines, cur, _, _ = self.ed.snapshot()
        p = common_prefix("\n".join(lines + [cur]), self.target)
        rest = self.target[p:].split("\n")
        return sum(len(l.lstrip(" ")) for l in rest) * SEC_PER_CHAR + len(rest) * 0.3

    def run(self):
        expect = None
        while not self.aborted:
            if self.paused:
                time.sleep(0.05)
                continue
            self.settle()
            lines, cur, _, _ = self.ed.snapshot()
            if expect is not None:
                if "\n".join(lines + [cur]) != expect:
                    self.fixes += 1         # the last chunk did not land cleanly
                    self.chunk = max(4, self.chunk // 2)
                else:
                    self.chunk = min(CHUNK, self.chunk + 6)
            act = decide(lines, cur, self.target)
            if act is None:
                self.done = True
                return
            n = len(lines)
            self._actions_on_line[n] = self._actions_on_line.get(n, 0) + 1
            if self._actions_on_line[n] > MAX_ACTIONS_PER_LINE:
                self._actions_on_line[n] = 0
                self.paused = True
                self.msg = ("STUCK on line %d -- check the plate / fix it by hand, "
                            "then Ctrl-R" % (n + 1))
                continue
            try:
                if act[0] == "enter":
                    self.kb.key("Enter")
                    expect = None
                elif act[0] == "bksp":
                    for _ in range(act[1]):
                        self.kb.key("Bksp")
                    expect = None
                else:
                    s = act[1][:self.chunk]
                    self.kb.type_text(s)
                    expect = "\n".join(lines + [cur]) + s
            except Exception as e:          # hardware hiccup: pause, Daniel decides
                self.paused = True
                self.msg = "ROBOT ERROR: %s -- Ctrl-R to retry, Ctrl-C to abort" % e
                expect = None


# ------------------------------------------------------------------ keyboards
class RobotKeyboard:
    """The real solenoids, via tools/selfwrite's Keyboard (TYPE chunks, leading
    spaces as KEY Space, PULSE 50 + LEAD 0 resent on connect)."""

    def __init__(self):
        import sys
        here = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, os.path.join(here, "..", "selfwrite"))
        os.environ.pop("KB_DRY", None)
        import selfwrite
        self.kb = selfwrite.Keyboard()
        self.typeable = self.kb.typeable

    def type_text(self, s):
        self.kb._type_line(s)

    def key(self, name):
        self.kb._key(name)

    def close(self):
        self.kb.close()


class FakeKeyboard:
    """No hardware: 'presses' land straight in the editor with realistic
    mistakes (missed, doubled and wrong keys) so the fix logic is exercised."""

    NEIGHBOR = "qwertyuiopasdfghjklzxcvbnm"

    def __init__(self, editor, speed=1.0, miss=0.02, double=0.01, wrong=0.01, seed=None):
        self.ed, self.speed = editor, speed
        self.miss, self.double, self.wrong = miss, double, wrong
        self.rng = random.Random(seed)
        self.typeable = set(chr(c) for c in range(32, 127)) | {"\n"}
        self.presses = 0

    def _press(self, ch):
        time.sleep(SEC_PER_CHAR * self.speed)
        self.presses += 1
        r = self.rng.random()
        if r < self.miss:
            return
        if r < self.miss + self.wrong and ch.isalpha():
            ch = self.rng.choice(self.NEIGHBOR)
        self.ed.feed(ch)
        if r > 1 - self.double:
            self.ed.feed(ch)

    def type_text(self, s):
        for ch in s:
            self._press(ch)

    def key(self, name):
        self._press({"Enter": "\n", "Bksp": "\x7f", "Space": " "}[name])

    def close(self):
        pass


# ------------------------------------------------------------------ screen
KW = (r"\b(def|class|if|elif|else|for|while|return|import|from|in|not|and|or|"
      r"True|False|None|with|as|try|except|break|continue|pass|lambda|global|is)\b")
TOKEN = re.compile(r"(#.*)|(\"[^\"]*\"?|'[^']*'?)|" + KW + r"|(\b\d+(?:\.\d+)?\b)")


def _draw_code_line(scr, y, x0, text, width, curses):
    pos = 0
    for m in TOKEN.finditer(text):
        if m.start() > pos:
            _put(scr, y, x0 + pos, text[pos:m.start()], 0, width - pos)
        pair = 3 if m.group(1) else 2 if m.group(2) else 1 if m.group(3) else 4
        _put(scr, y, x0 + m.start(), m.group(0), curses.color_pair(pair), width - m.start())
        pos = m.end()
    if pos < len(text):
        _put(scr, y, x0 + pos, text[pos:], 0, width - pos)


def _put(scr, y, x, s, attr, room):
    if room <= 0:
        return
    try:
        scr.addstr(y, x, s[:room], attr)
    except Exception:
        pass


def _render(scr, ed, ty, curses):
    h, w = scr.getmaxyx()
    lines, cur, keys, _ = ed.snapshot()
    allv = lines + [cur]
    scr.erase()
    rem = int(ty.remaining_seconds())
    status = (" CLAUDE'S CODE - every key pressed by the robot   line %d/%d   "
              "keys %d   fixes %d   ~%d:%02d left " % (
                  len(lines) + 1, ty.total_lines, keys, ty.fixes, rem // 60, rem % 60))
    if ty.msg and ty.paused:
        status = " " + ty.msg + " "
    _put(scr, 0, 0, status.ljust(w), curses.color_pair(6) | curses.A_BOLD, w)
    rows = h - 1
    first = max(0, len(allv) - rows)
    for i, text in enumerate(allv[first:]):
        y = 1 + i
        n = first + i + 1
        _put(scr, y, 0, "%4d " % n, curses.color_pair(5), w)
        _draw_code_line(scr, y, 5, text, w - 6, curses)
    cy, cx = len(allv[first:]), 5 + len(cur)
    if cx < w - 1:
        _put(scr, cy, cx, " ", curses.A_REVERSE, 1)
    scr.refresh()


def type_code(code, kb, ui=True, editor=None, poll=None):
    """Type `code` with keyboard `kb` into the live editor. Returns stats dict.
    poll: optional callable run each loop (tests use it)."""
    ed = editor or Editor()
    ty = Typer(ed, kb, code)

    def loop(scr):
        if scr is not None:
            import curses
            curses.curs_set(0)
            curses.raw()
            curses.noecho()
            scr.timeout(15)
            curses.start_color()
            try:
                curses.use_default_colors()
                bg = -1
            except Exception:
                bg = curses.COLOR_BLACK
            for i, c in enumerate((curses.COLOR_MAGENTA, curses.COLOR_YELLOW,
                                   curses.COLOR_GREEN, curses.COLOR_CYAN,
                                   curses.COLOR_BLUE), 1):
                curses.init_pair(i, c, bg)
            curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        ty.start()
        last_draw = 0
        while True:
            if scr is not None:
                c = scr.getch()
                if c != -1:
                    if c == 3:
                        ty.aborted = True
                    elif c == 16:
                        ty.paused, ty.msg = True, "PAUSED -- fix by hand if needed, Ctrl-R to resume"
                    elif c == 18:
                        ty.paused, ty.msg = False, ""
                    elif c in (curses.KEY_BACKSPACE, 127, 8):
                        ed.feed("\x7f")
                    elif c in (10, 13, curses.KEY_ENTER):
                        ed.feed("\n")
                    elif 32 <= c <= 126:
                        ed.feed(chr(c))
                    continue
                if time.time() - last_draw > 0.05:
                    _render(scr, ed, ty, curses)
                    last_draw = time.time()
            else:
                time.sleep(0.01)
            if poll:
                poll(ed, ty)
            if ty.done or ty.aborted:
                if scr is not None:
                    _render(scr, ed, ty, curses)
                    time.sleep(1.0)
                return

    if ui:
        import curses
        curses.wrapper(loop)
    else:
        loop(None)
    got = "\n".join(ed.lines) + "\n" if not ed.cur else ed.text()
    return {"ok": ty.done and got == code, "aborted": ty.aborted, "text": got,
            "keys": ed.keys, "fixes": ty.fixes, "seconds": time.time() - ty.started}

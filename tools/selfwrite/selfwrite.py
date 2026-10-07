"""selfwrite -- the keyboard types (and runs) its own next generation.

Idea (Oct 6 2026, from the 698-like comment "let Claude control it and write
its own software"):

    gen0.py (written by a human) asks Claude to write gen1.py.
    The SOLENOIDS type gen1.py into Terminal, character by character.
    The solenoids then type `python3 gen1.py &` -- gen1 takes over the keyboard,
    asks Claude for gen2.py, types it, launches it ... stops at MAX_GEN.

Each generation file is short on purpose (every character is ~0.1 s of coil
time and one more chance for a missed press). All the plumbing lives here.

Safety rails (Claude cannot edit this file -- only the genN.py files):
    - MAX_GEN hard stop (default 3)
    - generated code may only import selfwrite; no os/subprocess/open/network
    - every typed file is read back from disk and compared before it is run
    - code is compiled (syntax-checked) before it is typed

Run card: see README.md in this folder.

Env vars:
    ANTHROPIC_API_KEY   required (console.anthropic.com)
    CLAUDE_MODEL        default claude-sonnet-5-5
    KB_PORT             default: first /dev/cu.usbmodem*
    KB_PULSE            TYPE pulse ms, default 50 (plate-sag value, Oct 5)
    SELFWRITE_MAX_GEN   default 3
    KB_DRY=1            no hardware: print commands, write files directly
    SELFWRITE_FAKE=1    no API: fake Claude (bumps GEN, for plumbing tests)
"""

from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

MAX_GEN = int(os.environ.get("SELFWRITE_MAX_GEN", "3"))
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
PULSE_MS = int(os.environ.get("KB_PULSE", "50"))
DRY = os.environ.get("KB_DRY") == "1"
FAKE = os.environ.get("SELFWRITE_FAKE") == "1"
MAX_CHARS = 900
MAX_LINES = 30
CHUNK = 40          # chars per TYPE command (firmware line buffer is 200)

# keys a Python file can't live without
PY_NEEDS = ["Enter", "LShift", "9", "0", ";", "=", "'", ".", ",", "-"]

BANNED = [r"(?m)^\s*import\s", r"(?m)^\s*from\s+(?!selfwrite\s+import\b)",
          r"\bos\.", r"\bsys\.", r"subprocess", r"shutil", r"\bopen\(",
          r"\beval\(", r"\bexec\(", r"__import__", r"socket", r"urllib",
          r"\bcompile\(", r"globals\(", r"getattr\("]

SHIFT_PAIRS = dict(zip("!@#$%^&*()_+~{}|:\"<>?", "1234567890-=`[]\\;',./"))


def log(msg):
    print(f"\r[selfwrite] {msg}", flush=True)


# ---- keyboard ---------------------------------------------------------------------
def _find_port():
    if os.environ.get("KB_PORT"):
        return os.environ["KB_PORT"]
    ports = sorted(glob.glob("/dev/cu.usbmodem*")) or sorted(glob.glob("/dev/tty.usbmodem*"))
    if not ports:
        sys.exit("[selfwrite] no /dev/cu.usbmodem* -- is the Mega plugged in? (or set KB_PORT)")
    return ports[0]


class Keyboard:
    """The hands. One per generation; the port is handed over at launch()."""

    def __init__(self):
        self._connect()
        global _TYPEABLE
        _TYPEABLE = self.typeable          # ask_claude tells Claude which keys exist

    def _connect(self):
        self.ser = None
        self.typed_chars = 0
        if DRY:
            log("DRY RUN -- no hardware")
            self.keys = None
            self.typeable = set(chr(c) for c in range(32, 127)) | {"\n"}
            return
        import serial  # pyserial (agent/.venv has it)
        port = _find_port()
        deadline = time.time() + 15          # previous generation may still hold it
        while True:
            try:
                self.ser = serial.Serial(port, 115200, timeout=0.2)
                break
            except serial.SerialException:
                if time.time() > deadline:
                    sys.exit(f"[selfwrite] {port} busy -- close Serial Monitor / Chrome tab")
                time.sleep(0.3)
        time.sleep(2.5)                       # Mega resets on open; wait for boot
        self.ser.reset_input_buffer()
        self._cmd(f"PULSE {PULSE_MS}")        # opening the port reset it to 22
        self._cmd("LEAD 0")
        self.keys = self._read_map()
        self.typeable = typeable_chars(self.keys)
        log(f"keyboard up on {port}: {len(self.keys)} keys mapped, pulse {PULSE_MS} ms")

    # -- serial plumbing --
    def _readline(self, timeout):
        buf = b""
        end = time.time() + timeout
        while time.time() < end:
            b = self.ser.read(1)
            if not b:
                continue
            if b == b"\n":
                return buf.decode(errors="replace").strip()
            buf += b
        return None

    def _cmd(self, line, timeout=5.0):
        """Send one line, return the first OK/ERR reply line (full line, not partial)."""
        if DRY:
            print(f"    > {line}")
            return "OK DRY"
        self.ser.write((line + "\n").encode())
        end = time.time() + timeout
        while time.time() < end:
            r = self._readline(end - time.time())
            if r is None:
                break
            if r.startswith(("OK", "ERR", "PULSE", "LEAD")):
                return r
        raise RuntimeError(f"no reply to: {line}")

    def _read_map(self):
        self.ser.write(b"MAP\n")
        keys = set()
        end = time.time() + 5
        while time.time() < end:
            r = self._readline(end - time.time())
            if r is None or "keys mapped" in r:
                break
            m = re.match(r"\d+\s+c\d+/OUT\d+\s+(\S+)$", r)
            if m:
                keys.add(m.group(1))
        return keys

    # -- typing --
    def _type_line(self, s):
        """Type one line (no Enter). Firmware TYPE strips leading spaces, so runs
        of spaces at a chunk start go out as KEY Space."""
        i = 0
        while i < len(s):
            if s[i] == " ":
                self._key("Space")
                i += 1
                continue
            chunk = s[i:i + CHUNK].rstrip(" ")
            r = self._cmd(f"TYPE {chunk}", timeout=5 + len(chunk) * 0.3)
            if not DRY and (not r.startswith("OK TYPE") or "?" in r[8:] and "?" not in chunk
                            or "!" in r[8:] and "!" not in chunk):
                raise RuntimeError(f"TYPE failed: {r!r}")
            i += len(chunk)
            self.typed_chars += len(chunk)

    def _key(self, name):
        r = self._cmd(f"KEY {name}")
        if not r.startswith("OK"):
            raise RuntimeError(f"KEY {name}: {r}")
        self.typed_chars += 1

    def _enter(self):
        self._key("Enter")

    # -- the API a generation may use --
    def say(self, text):
        """Make text appear in the terminal: types  echo '<text>'  + Enter."""
        text = "".join(c for c in str(text) if c in self.typeable and c not in "'\n")
        self._type_line(f"echo '{text}'")
        self._enter()

    def clear(self):
        self._type_line("clear")
        self._enter()

    def pause(self, seconds):
        time.sleep(max(0, min(float(seconds), 10)))

    def write_file(self, name, code):
        """Type `cat > name <<'EOF'`, the code, `EOF`; then read it back from disk."""
        _check_name(name)
        code = _normalize(code)
        bad = sorted(set(code) - self.typeable)
        if bad:
            raise RuntimeError(f"code uses keys that aren't mapped: {bad}")
        for attempt in (1, 2):
            log(f"typing {name} ({len(code)} chars, attempt {attempt})")
            t0 = time.time()
            if DRY:
                with open(name, "w") as f:
                    f.write(code)
            else:
                self._type_line(f"cat > {name} <<'EOF'")
                self._enter()
                for line in code.rstrip("\n").split("\n"):
                    if line:
                        self._type_line(line)
                    self._enter()
                self._type_line("EOF")
                self._enter()
                time.sleep(0.8)
            got = _normalize(open(name).read()) if os.path.exists(name) else ""
            if got == code:
                log(f"{name} verified on disk, {time.time() - t0:.0f} s of typing")
                return True
            _show_diff(code, got)
        raise RuntimeError(f"{name} didn't come out right twice -- stopping (check the plate)")

    def launch(self, name):
        """Type `python3 name &` + Enter, hand the port over, and exit."""
        _check_name(name)
        n = int(re.match(r"gen(\d+)\.py$", name).group(1))
        if n > MAX_GEN:
            self.say(f"generation {n} would pass the limit of {MAX_GEN}. stopping.")
            self.close()
            return
        cmd = f"python3 {name} &"
        if DRY:
            print(f"    > TYPE {cmd}  + Enter")
            self.close()
            subprocess.run([sys.executable, name])
            return
        self._type_line(cmd)
        self._enter()
        self.close()
        log(f"handed the keyboard to {name}")
        sys.exit(0)

    def close(self):
        if self.ser:
            try:
                self._cmd("ALLOFF")
            except Exception:
                pass
            self.ser.close()
            self.ser = None


def typeable_chars(keys):
    keys = set(keys)
    out = set()
    shift = "LShift" in keys
    for k in keys:
        if len(k) == 1:
            if k.isalpha():
                out.add(k.lower())
                if shift:
                    out.add(k.upper())
            else:
                out.add(k)
    if "Space" in keys:
        out.add(" ")
    if "Enter" in keys:
        out.add("\n")
    if shift:
        for s, base in SHIFT_PAIRS.items():
            if base in out:
                out.add(s)
    return out


# ---- the brain --------------------------------------------------------------------
def my_source(path):
    with open(path) as f:
        return f.read()


API_DOC = """from selfwrite import Keyboard, ask_claude, my_source

kb = Keyboard()                 # connect to the keyboard. call once, first.
kb.say(text)                    # types  echo '<text>'  so text shows in the terminal
kb.clear()                      # types  clear
kb.pause(seconds)               # wait (max 10 s)
code = ask_claude(GEN, my_source(__file__), GOAL)   # Claude writes your child
kb.write_file("genN.py", code)  # the keyboard types the child into the terminal
kb.launch("genN.py")            # types  python3 genN.py &  and hands over. call LAST."""


def _prompt(gen, source, goal, chars):
    child = gen + 1
    final = child >= MAX_GEN
    life = ("You are the FINAL generation. Do NOT call ask_claude, write_file or launch. "
            "Do your new thing, then end with a short kb.say farewell."
            if final else
            f"Keep the life cycle: Keyboard(), your new thing, then "
            f"code = ask_claude(GEN, my_source(__file__), GOAL), "
            f"kb.write_file(\"gen{child + 1}.py\", code), kb.launch(\"gen{child + 1}.py\").")
    return f"""You are writing generation {child} of {MAX_GEN} of a program that is typed by a
physical keyboard: 84 solenoids press real keys on a real keyboard, character by character,
into a macOS terminal. Then the keyboard types `python3 gen{child}.py &` and your code takes
control of the keyboard. You write its software; it types it; it runs it.

Your parent (generation {gen}) is:
<parent>
{source}
</parent>

Your parent's instruction to you (its GOAL): {goal}

API (the only thing you may import):
{API_DOC}

Rules:
- Set GEN = {child}. Set GOAL to a one-line instruction for your own child.
- {life}
- Do ONE new visible thing your parent did not do, following the GOAL. Plain Python logic
  (loops, strings, math) is fine; everything visible goes through kb.say.
- Only these characters exist on the keyboard: {''.join(sorted(c for c in chars if c != chr(10)))}
  (plus newline). Indent with 4 spaces. No tabs. No trailing spaces.
- At most {MAX_LINES} lines and {MAX_CHARS} characters. Each character costs ~0.1 s of solenoid
  time, so be brief. Short comments are welcome; the audience reads them as it types.
- No imports except selfwrite. No file, OS or network access.
- Reply with ONLY the Python code. No markdown fences, no explanation."""


def _call_claude(messages):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("[selfwrite] ANTHROPIC_API_KEY not set (console.anthropic.com -> API keys)")
    body = json.dumps({"model": MODEL, "max_tokens": 2000, "messages": messages}).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body,
        headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"[selfwrite] API error {e.code}: {e.read().decode()[:400]}")
    return "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")


def _fake_claude(gen, source):
    child = gen + 1
    code = re.sub(r"GEN = \d+", f"GEN = {child}", source)
    code = code.replace(f"gen{gen + 1}.py", f"gen{child + 1}.py")
    if child >= MAX_GEN:
        code = code.split("code = ask_claude")[0] + 'kb.say("final generation. goodbye.")\n'
    return code


def ask_claude(gen, source, goal="do something new"):
    """Ask Claude for generation gen+1. Validates and retries up to 3 times."""
    chars = _typeable_for_prompt()
    log(f"generation {gen} is asking Claude ({MODEL}) to write generation {gen + 1}...")
    messages = [{"role": "user", "content": _prompt(gen, source, goal, chars)}]
    for attempt in range(3):
        raw = _fake_claude(gen, source) if FAKE else _call_claude(messages)
        code = _normalize(_strip_fences(raw))
        problem = validate(code, gen + 1, chars)
        if not problem:
            log(f"Claude wrote generation {gen + 1}: {len(code.splitlines())} lines, {len(code)} chars")
            return code
        log(f"rejected ({problem}) -- asking again")
        messages += [{"role": "assistant", "content": raw},
                     {"role": "user", "content": f"That won't work: {problem}. Reply with the fixed code only."}]
    sys.exit("[selfwrite] Claude couldn't produce valid code in 3 tries")


_TYPEABLE = None


def _typeable_for_prompt():
    # set by the running Keyboard (see _register); fallback = everything
    return _TYPEABLE or (set(chr(c) for c in range(32, 127)) | {"\n"})


def validate(code, child, chars):
    if len(code) > MAX_CHARS:
        return f"{len(code)} characters, the limit is {MAX_CHARS}"
    if len(code.splitlines()) > MAX_LINES:
        return f"{len(code.splitlines())} lines, the limit is {MAX_LINES}"
    bad = sorted(set(code) - chars)
    if bad:
        return f"uses characters the keyboard can't type: {bad}"
    for pat in BANNED:
        if re.search(pat, code):
            return f"uses something not allowed ({pat})"
    if not re.search(rf"^GEN = {child}\s*$", code, re.M):
        return f"must contain the line GEN = {child}"
    if re.search(r"^EOF$", code, re.M):
        return "a line that is exactly EOF would end the heredoc early"
    if "from selfwrite import" not in code or "Keyboard()" not in code:
        return "must import from selfwrite and create Keyboard()"
    final = child >= MAX_GEN
    if not final and f'launch("gen{child + 1}.py")' not in code and f"launch('gen{child + 1}.py')" not in code:
        return f'must end with kb.launch("gen{child + 1}.py")'
    if final and ("launch(" in code or "ask_claude(" in code):
        return "the final generation must not ask_claude or launch"
    try:
        compile(code, f"gen{child}.py", "exec")
    except SyntaxError as e:
        return f"syntax error line {e.lineno}: {e.msg}"
    return None


# ---- helpers ------------------------------------------------------------------------
def _strip_fences(s):
    s = s.strip()
    m = re.match(r"^```(?:python)?\n(.*?)\n```$", s, re.S)
    return m.group(1) if m else s


def _normalize(code):
    code = code.replace("\t", "    ").replace("\r", "")
    return "\n".join(l.rstrip() for l in code.strip("\n").split("\n")) + "\n"


def _check_name(name):
    if not re.fullmatch(r"gen\d+\.py", name):
        raise ValueError(f"file name must look like gen1.py, got {name!r}")


def _show_diff(want, got):
    w, g = want.split("\n"), got.split("\n")
    for i in range(max(len(w), len(g))):
        a = w[i] if i < len(w) else "<missing>"
        b = g[i] if i < len(g) else "<missing>"
        if a != b:
            log(f"line {i + 1} differs:\n   want: {a!r}\n   got:  {b!r}")
            return
    log("files differ (whitespace?)")


# ---- python3 selfwrite.py check | preview ------------------------------------------------
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        kb = Keyboard()
        if kb.keys is not None:
            missing = [k for k in PY_NEEDS if k not in kb.keys]
            letters = [c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" if c not in kb.keys]
            print("mapped keys :", " ".join(sorted(kb.keys)))
            print("missing for Python (must map):", " ".join(missing) or "none")
            print("missing letters/digits      :", " ".join(letters) or "none")
            print("typeable    :", "".join(sorted(c for c in kb.typeable if c != "\n")))
        kb.close()
    elif cmd == "preview":
        # no typing: show what Claude would write as gen1 (tests the API key)
        src = my_source(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen0.py"))
        goal = re.search(r'^GOAL = "(.*)"$', src, re.M).group(1)
        print(ask_claude(0, src, goal))
    else:
        sys.exit("usage: python3 selfwrite.py [check|preview]")

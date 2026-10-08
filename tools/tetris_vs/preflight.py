"""Pre-flight: check Claude's game BEFORE the robot types a single key.

    validate(code, typeable)  -> None or a problem string (static checks)
    run_headless(path, secs)  -> (ok, message)  (SDL dummy driver, sim robot,
                                 simulated weak Daniel, must not crash and
                                 Claude's player must clear lines)

CLI:  python3 preflight.py game.py      (run both checks on a file)
"""

import ast
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_TYPED = 9500   # keystrokes excluding leading indentation (the editor auto-indents)
ALLOWED_IMPORTS = {"pygame", "random", "math", "time", "robot"}
BANNED_NAMES = {"open", "eval", "exec", "__import__", "compile", "input",
                "breakpoint", "globals", "locals", "vars", "setattr", "delattr"}
REQUIRED = ["robot.tick(", "robot.press(", "robot.say(", "robot.report(",
            "robot.WINDOW", '"winner"', '"claude_lines"', '"state"']


def normalize(code):
    code = code.replace("\t", "    ").replace("\r", "")
    return "\n".join(l.rstrip() for l in code.strip("\n").split("\n")) + "\n"


def strip_fences(s):
    s = s.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else ""
        if s.rstrip().endswith("```"):
            s = s.rstrip()[:-3]
    return s


def typed_chars(code):
    lines = code.split("\n")
    return sum(len(l.lstrip(" ")) for l in lines) + len(lines) - 1


def validate(code, typeable=None):
    if typed_chars(code) > MAX_TYPED:
        return ("%d typed characters (not counting leading indentation), the hard limit "
                "is %d. Make it shorter." % (typed_chars(code), MAX_TYPED))
    bad = sorted(set(c for c in code if ord(c) > 126 or (ord(c) < 32 and c != "\n")))
    if bad:
        return "non-ASCII or control characters: %r" % bad
    if typeable is not None:
        bad = sorted(set(code) - set(typeable) - {"\n"})
        if bad:
            return "uses characters the robot keyboard cannot type: %r" % bad
    try:
        tree = ast.parse(code, feature_version=(3, 9))
    except SyntaxError as e:
        return "syntax error (Python 3.9) line %s: %s" % (e.lineno, e.msg)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] not in ALLOWED_IMPORTS:
                    return "import not allowed: %s" % a.name
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] not in ALLOWED_IMPORTS:
                return "import not allowed: %s" % node.module
        elif isinstance(node, ast.Name) and node.id in BANNED_NAMES:
            return "not allowed: %s" % node.id
        elif isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            return "dunder attribute access not allowed: %s" % node.attr
    for req in REQUIRED:
        if req not in code and req.replace('"', "'") not in code:
            return "missing required %s (see the robot section of the spec)" % req
    return None


def run_headless(path, secs=40):
    rep = tempfile.NamedTemporaryFile(suffix=".json", delete=False).name
    env = dict(os.environ)
    env.update({
        "SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy",
        "TETRIS_ROBOT": "sim", "TETRIS_SIM_OPPONENT": "1", "TETRIS_REPORT": rep,
        "PYTHONPATH": HERE + os.pathsep + env.get("PYTHONPATH", ""),
        "PYGAME_HIDE_SUPPORT_PROMPT": "1",
    })
    t0 = time.time()
    p = subprocess.Popen([sys.executable, path], env=env, cwd=os.path.dirname(path) or ".",
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        out, err = p.communicate(timeout=secs)
        ended = True
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
        ended = False
    took = time.time() - t0
    try:
        with open(rep) as f:
            r = json.load(f)
    except (OSError, ValueError):
        r = {}
    finally:
        for x in (rep, rep + ".tmp"):
            if os.path.exists(x):
                os.remove(x)
    tail = "\n".join(err.strip().splitlines()[-25:])
    if "Traceback" in err:
        return False, "the game crashed after %.0f s:\n%s" % (took, tail), r
    if ended:
        return False, "the game exited by itself after %.0f s (exit code %s):\n%s" % (
            took, p.returncode, tail), r
    problems = []
    if r.get("ticks", 0) < secs * 20:
        problems.append("robot.tick() called only %d times in %d s (need once per frame)"
                        % (r.get("ticks", 0), secs))
    if r.get("presses", 0) < 20:
        problems.append("Claude's player pressed only %d keys" % r.get("presses", 0))
    lines = max(r.get("claude_lines", 0), r.get("best_claude_lines", 0))
    if r.get("wins_HUMAN") or r.get("wins_DANIEL"):
        problems.append("Claude's player LOST to a simulated opponent that never "
                        "hard-drops (it is far too weak to lose to)")
    if lines < 1:
        problems.append("Claude's player cleared no lines in %d s against a weak "
                        "opponent (claude_lines=%s, state=%s)" % (secs, r.get("claude_lines"), r.get("state")))
    if r.get("state") in (None, "menu"):
        problems.append("the game never left the menu after a mouse click")
    if problems:
        return False, "; ".join(problems), r
    return True, "ran %d s: %d presses, Claude cleared %s lines, %d match(es) finished, said %d lines" % (
        secs, r.get("presses", 0), r.get("claude_lines"), r.get("matches", 0),
        len(r.get("said", []))), r


if __name__ == "__main__":
    path = os.path.abspath(sys.argv[1])
    code = open(path).read()
    print("static :", validate(normalize(code)) or "OK")
    ok, msg, rep = run_headless(path, int(sys.argv[2]) if len(sys.argv) > 2 else 40)
    print("runtime:", "OK" if ok else "FAIL", "-", msg)
    for s in rep.get("said", []):
        print("   said:", s)

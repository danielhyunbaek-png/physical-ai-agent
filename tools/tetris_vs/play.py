"""Me vs Claude: Tetris -- the whole Video 2 run in one command.

    python3 play.py                 the real thing (robot + Claude API)
    python3 play.py --dry           no robot: fake keys land in the editor, the game
                                    runs with a simulated robot (play vs Claude on
                                    the laptop)
    python3 play.py --fake-claude   no API: use reference_game.py as "Claude's" code
    python3 play.py --file X.py     type X.py (rehearsal with a short file)
    python3 play.py --preview       ask Claude + pre-flight only, no typing
    python3 play.py --no-type       skip the typing, launch the game right away
    python3 play.py --game runs/<stamp>/tetris.py    replay an earlier game

Flow: Daniel speaks (Wispr Flow fills the prompt) -> his words + game_spec.md go
to Claude -> static checks + 40 s headless pre-flight (up to 3 fix rounds) ->
the robot types the code into the live editor (typo-proof) -> the robot types
`python3 tetris.py` -> the game starts; Claude's player presses robot keys.

Env: ANTHROPIC_API_KEY, CLAUDE_MODEL (default claude-sonnet-5-5), KB_PORT,
     KB_PULSE (default 50), TETRIS_WINDOW (default 1280x720), TETRIS_VOICE.
"""

import argparse
import json
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import editor      # noqa: E402
import preflight   # noqa: E402

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")


def say(msg):
    print("\033[1;33m>>\033[0m " + msg, flush=True)


class Spinner:
    def __init__(self, text):
        self.text, self.stop = text, False
        self.t = threading.Thread(target=self.run, daemon=True)

    def run(self):
        t0 = time.time()
        while not self.stop:
            sys.stdout.write("\r\033[1;36m%s\033[0m %ds " % (self.text, time.time() - t0))
            sys.stdout.flush()
            time.sleep(0.25)

    def __enter__(self):
        self.t.start()
        return self

    def __exit__(self, *a):
        self.stop = True
        self.t.join()
        sys.stdout.write("\n")


# ------------------------------------------------------------------ Claude
def call_claude(messages):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.exit("ANTHROPIC_API_KEY not set (export it in this Terminal first)")
    body = json.dumps({"model": MODEL, "max_tokens": 16000, "messages": messages}).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body,
        headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit("API error %s: %s" % (e.code, e.read().decode()[:400]))
    u = data.get("usage", {})
    say("Claude replied (%s in / %s out tokens, stop=%s)" % (
        u.get("input_tokens"), u.get("output_tokens"), data.get("stop_reason")))
    return "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")


def get_game(sentence, typeable, run_dir, fake):
    spec = open(os.path.join(HERE, "game_spec.md")).read()
    messages = [{"role": "user", "content":
                 'A human just said to you, out loud: "%s"\n\n%s' % (sentence, spec)}]
    for attempt in range(1, 5):
        if fake:
            raw = open(os.path.join(HERE, "reference_game.py")).read()
        else:
            with Spinner("Claude is writing the game (%s)..." % MODEL):
                raw = call_claude(messages)
        with open(os.path.join(run_dir, "claude_raw_%d.txt" % attempt), "w") as f:
            f.write(raw)
        code = preflight.normalize(preflight.strip_fences(raw))
        problem = preflight.validate(code, typeable)
        if not problem:
            with Spinner("pre-flight: running Claude's game headless vs a simulated player..."):
                ok, msg, _ = preflight.run_headless(_save(run_dir, "candidate.py", code), 40)
            if ok:
                say("pre-flight PASSED: " + msg)
                return code
            problem = "The pre-flight test failed: " + msg
        say("attempt %d rejected: %s" % (attempt, problem.splitlines()[0][:200]))
        if fake:
            sys.exit("reference game failed pre-flight -- fix reference_game.py")
        messages += [{"role": "assistant", "content": raw},
                     {"role": "user", "content": problem +
                      "\nReply with the complete fixed file only, no explanation."}]
    sys.exit("Claude could not produce a game that passes pre-flight in 4 tries")


def _save(run_dir, name, text):
    path = os.path.join(run_dir, name)
    with open(path, "w") as f:
        f.write(text)
    return path


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--fake-claude", action="store_true")
    ap.add_argument("--file")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--no-type", action="store_true")
    ap.add_argument("--game")
    ap.add_argument("--speed", type=float, default=0.25,
                    help="--dry typing speed factor (1 = real robot speed)")
    a = ap.parse_args()
    robot_mode = "sim" if a.dry else "real"

    if a.game:
        if not os.path.isfile(a.game):
            sys.exit("no such game file: %s  (tip: type runs/ then press Tab)" % a.game)
        return launch(os.path.abspath(a.game), robot_mode, None)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    run_dir = os.path.join(HERE, "runs", stamp)
    os.makedirs(run_dir, exist_ok=True)

    kb = None
    ed = editor.Editor()
    if a.dry or a.preview:
        typeable = set(chr(c) for c in range(32, 127)) | {"\n"}
    else:
        say("connecting to the robot keyboard...")
        kb = editor.RobotKeyboard()
        typeable = kb.typeable

    if a.file:
        code = preflight.normalize(open(a.file).read())
        bad = sorted(set(code) - typeable)
        if bad:
            sys.exit("%s uses unmapped characters: %r" % (a.file, bad))
    else:
        print()
        try:
            sentence = input("\033[1;35mTalk to Claude >\033[0m ").strip()
        except (EOFError, KeyboardInterrupt):
            sys.exit("\nbye")
        if not sentence:
            sentence = "Hey Claude, let's play Tetris."
        code = get_game(sentence, typeable, run_dir, a.fake_claude)
    _save(run_dir, "claude_game.py", code)
    if a.preview:
        say("saved %s (%d lines, %d typed chars)" % (os.path.join(run_dir, "claude_game.py"),
                                                       code.count("\n"), preflight.typed_chars(code)))
        return

    game_path = os.path.join(run_dir, "tetris.py")
    if a.no_type:
        _save(run_dir, "tetris.py", code)
    else:
        n = preflight.typed_chars(code)
        say("the robot will now type %d lines, %d keystrokes (~%d min)." % (
            code.count("\n"), n, n * editor.SEC_PER_CHAR / 60 + 1))
        say("click THIS Terminal window. Ctrl-P pause, Ctrl-R resume, Ctrl-C abort.")
        try:
            input("\033[1;35m   press Enter when the camera is rolling and the PSU is ON > \033[0m")
        except (EOFError, KeyboardInterrupt):
            sys.exit("\nbye")
        for i in (5, 4, 3, 2, 1):
            sys.stdout.write("\r   starting in %d " % i)
            sys.stdout.flush()
            time.sleep(1)
        print()
        if a.dry:
            kb = editor.FakeKeyboard(ed, speed=a.speed)
        st = editor.type_code(code, kb, ui=True, editor=ed)
        _save(run_dir, "tetris.py", st["text"])
        if st["aborted"] or not st["ok"]:
            if kb:
                kb.close()
            sys.exit("typing stopped -- partial file in %s" % game_path)
        m = int(st["seconds"])
        say("typed and verified: %d keys pressed, %d fixes, %d:%02d" % (
            st["keys"], st["fixes"], m // 60, m % 60))
    launch(game_path, robot_mode, kb)


def launch(game_path, robot_mode, kb):
    cmd = "python3 tetris.py" if os.path.basename(game_path) == "tetris.py" else \
        "python3 " + os.path.basename(game_path)
    if isinstance(kb, editor.RobotKeyboard):
        # the robot types the launch command itself
        sys.stdout.write("\n$ ")
        sys.stdout.flush()
        t = threading.Thread(target=lambda: (time.sleep(0.8), kb.type_text(cmd),
                                             kb.key("Enter")), daemon=True)
        t.start()
        try:
            got = input().strip()
        except EOFError:
            got = ""
        t.join()
        kb.close()                          # hand the serial port to the game
        if got != cmd:
            say("(typed %r -- launching anyway)" % got)
    else:
        print("\n$ " + cmd)
        if kb:
            kb.close()
    env = dict(os.environ, TETRIS_ROBOT=robot_mode, PYGAME_HIDE_SUPPORT_PROMPT="1",
               PYTHONPATH=HERE + os.pathsep + os.environ.get("PYTHONPATH", ""))
    say("click the game window, then click to start.")
    subprocess.run([sys.executable, os.path.basename(game_path)],
                   cwd=os.path.dirname(game_path), env=env)


if __name__ == "__main__":
    main()

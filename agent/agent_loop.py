"""The agent: observe (webcam) -> decide (Claude) -> act (solenoids).

This is the loop that makes it a *physical AI agent* rather than a keyboard
tester. Each cycle: photograph the target screen, ask Claude what to do next
toward the goal, execute the returned actions on the real keyboard.

Campsite-testable end-to-end with ZERO hardware:
    python agent_loop.py --goal "open spotlight and type hello" --dry-run
uses the built-in camera and a dry-run keyboard driver (actions are printed).

Requires ANTHROPIC_API_KEY in the environment for real decisions;
without it, --scripted replays a fixed action list (pure plumbing test).
"""

import argparse
import base64
import json
import os
import time

import cv2

from keyboard_driver import KeyboardDriver
from vision import Vision

SYSTEM = """You control a PHYSICAL robot keyboard pressing keys on a real \
computer. You see that computer's screen through a webcam photo. Work toward \
the user's goal one small step at a time.

Reply ONLY with JSON: {"done": bool, "reason": "...", "actions": [...]}
Each action is one of:
  {"type": "type", "text": "hello"}          -- type text (shift handled)
  {"type": "key", "name": "Enter"}           -- named key (Enter, Esc, Tab,
                                                Bksp, F1..F12, Up/Down/etc)
  {"type": "chord", "keys": ["LCmd","Space"]} -- modifier combo
  {"type": "wait", "seconds": 2}             -- wait for UI to settle
Use at most 3 actions per turn, then re-observe. Set done=true when the goal
is visibly complete in the screenshot."""


def screenshot_b64(vision, max_px=1568):
    img = vision.screen()
    h, w = img.shape[:2]
    scale = min(1.0, max_px / max(h, w))
    if scale < 1.0:
        img = cv2.resize(img, None, fx=scale, fy=scale)
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 80])
    return base64.b64encode(buf).decode()


def decide(client, goal, img_b64, history):
    msg = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=500,
        system=SYSTEM,
        messages=history + [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64",
                 "media_type": "image/jpeg", "data": img_b64}},
                {"type": "text", "text": f"Goal: {goal}\nWhat next?"},
            ],
        }],
    )
    text = msg.content[0].text
    start, end = text.find("{"), text.rfind("}") + 1
    return json.loads(text[start:end])


def act(kb, actions):
    for a in actions:
        kind = a.get("type")
        if kind == "type":
            kb.type_text(a["text"])
        elif kind == "key":
            kb.key(a["name"])
        elif kind == "chord":
            kb.chord(*a["keys"])
        elif kind == "wait":
            time.sleep(float(a.get("seconds", 1)))
        else:
            print(f"[agent] unknown action skipped: {a}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goal", required=True)
    ap.add_argument("--port", default=None,
                    help="Arduino serial port; omit for dry-run")
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--max-turns", type=int, default=15)
    ap.add_argument("--scripted", action="store_true",
                    help="skip Claude; run a fixed demo action list")
    ap.add_argument("--dry-run", action="store_true",
                    help="force dry-run keyboard even if --port is set")
    args = ap.parse_args()

    kb = KeyboardDriver(None if args.dry_run else args.port)
    vision = Vision(camera_index=args.camera)

    if args.scripted:
        print("[agent] scripted mode -- plumbing test, no Claude")
        act(kb, [{"type": "chord", "keys": ["LCmd", "Space"]},
                 {"type": "wait", "seconds": 1},
                 {"type": "type", "text": "hello"},
                 {"type": "key", "name": "Enter"}])
        vision.save_frame("scripted_after.png")
        return

    import anthropic                      # deferred: not needed for --scripted
    client = anthropic.Anthropic()        # needs ANTHROPIC_API_KEY

    history = []
    for turn in range(args.max_turns):
        img_b64 = screenshot_b64(vision)
        plan = decide(client, args.goal, img_b64, history)
        print(f"[agent] turn {turn}: {plan.get('reason', '')}")
        if plan.get("done"):
            print("[agent] GOAL COMPLETE")
            break
        act(kb, plan.get("actions", []))
        history.append({"role": "user", "content": f"(turn {turn} executed: "
                        f"{json.dumps(plan.get('actions', []))})"})
        history.append({"role": "assistant", "content": json.dumps(plan)})
        history = history[-6:]            # keep context small
        time.sleep(1.0)                   # let the UI settle before re-observe
    else:
        print("[agent] max turns reached without done=true")

    vision.close()
    kb.close() if not kb.dry_run else None


if __name__ == "__main__":
    main()

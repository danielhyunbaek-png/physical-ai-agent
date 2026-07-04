"""The agent: observe (webcam) -> decide (LLM) -> act (solenoids + mouse).

Thin CLI over runtime.Session -- the production loop with logging, budget
guards, stuck detection, and escalation lives there. TFT games have their own
entrypoint (tft/play_tft.py) built on the same runtime.

Campsite-testable end-to-end with ZERO hardware:
    python agent_loop.py --goal "open spotlight and type hello" --dry-run
    python agent_loop.py --goal "..." --still shot.png --dry-run   # no camera

The brain is pluggable (see llm.py):
    --provider ollama     free, local (needs: ollama pull qwen3-vl:8b)
    --provider gemini     cheap cloud (GEMINI_API_KEY)
    --provider deepseek   cheap cloud (DEEPSEEK_API_KEY)
    --provider qwen       cheap cloud (DASHSCOPE_API_KEY)
    --provider anthropic  smartest, priciest (ANTHROPIC_API_KEY) [default]
    --escalate-to X       second brain for hard turns ({"escalate": true})
Without any key, --scripted replays a fixed action list (pure plumbing test).

The mouse is pluggable too (see mouse_driver.py):
    --mouse none          keyboard-only [default]
    --mouse dry           print mouse actions (campsite)
    --mouse mousekeys     macOS Mouse Keys through the PHYSICAL keyboard --
                          real cursor control with Wave 1 hardware only
    --mouse gantry        XY gantry over --mouse-port (Wave 2 hardware)
"""

from __future__ import annotations

import argparse

from keyboard_driver import KeyboardDriver
from llm import LLM, PRESETS
from mouse_driver import make_mouse
from runtime import SYSTEM, Session
from vision import Vision


def build_parser(goal_required=True):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--goal", required=goal_required)
    ap.add_argument("--port", default=None,
                    help="Arduino serial port; omit for dry-run")
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--still", default=None,
                    help="serve this image instead of a camera (no hardware)")
    ap.add_argument("--calib", default=None,
                    help="screen-quad JSON from calibrate.py screen")
    ap.add_argument("--max-turns", type=int, default=15)
    ap.add_argument("--budget-usd", type=float, default=None,
                    help="stop when estimated LLM spend reaches this")
    ap.add_argument("--max-minutes", type=float, default=None)
    ap.add_argument("--provider", default="anthropic", choices=list(PRESETS),
                    help="which brain to use (see llm.py for costs/keys)")
    ap.add_argument("--model", default=None,
                    help="override the provider's default model name")
    ap.add_argument("--escalate-to", default=None, choices=list(PRESETS),
                    help="stronger brain for turns the primary flags")
    ap.add_argument("--mouse", default="none",
                    choices=["none", "dry", "mousekeys", "gantry"])
    ap.add_argument("--mouse-port", default=None,
                    help="gantry serial port (gantry backend only)")
    ap.add_argument("--mouse-calib", default=None,
                    help="mouse calibration JSON from calibrate.py")
    ap.add_argument("--scripted", action="store_true",
                    help="skip the LLM; run a fixed demo action list")
    ap.add_argument("--dry-run", action="store_true",
                    help="force dry-run keyboard even if --port is set")
    ap.add_argument("--no-frames", action="store_true",
                    help="don't save per-turn frames to the session log")
    return ap


def main():
    args = build_parser().parse_args()

    kb = KeyboardDriver(None if args.dry_run else args.port)
    vision = Vision(camera_index=args.camera, still=args.still,
                    calib_path=args.calib)
    mouse = make_mouse(args.mouse, kb=kb, port=args.mouse_port,
                       calib_path=args.mouse_calib)

    if args.scripted:
        from actions import Actuators
        print("[agent] scripted mode -- plumbing test, no LLM")
        acts = [{"type": "chord", "keys": ["LCmd", "Space"]},
                {"type": "wait", "seconds": 1},
                {"type": "type", "text": "hello"},
                {"type": "key", "name": "Enter"}]
        if mouse is not None:
            acts += [{"type": "mouse_move", "x": 960, "y": 540},
                     {"type": "click", "x": 200, "y": 200},
                     {"type": "drag", "x1": 300, "y1": 800,
                      "x2": 600, "y2": 400}]
        Actuators(kb, mouse).run(acts)
        vision.save_frame("scripted_after.png")
        vision.close()
        return

    brain = LLM(args.provider, args.model)
    escalate = LLM(args.escalate_to) if args.escalate_to else None

    session = Session(brain, kb, vision, args.goal, mouse=mouse,
                      system=SYSTEM, max_turns=args.max_turns,
                      budget_usd=args.budget_usd,
                      max_minutes=args.max_minutes,
                      escalate_to=escalate,
                      save_frames=not args.no_frames)
    session.run()
    vision.close()
    if not kb.dry_run:
        kb.close()


if __name__ == "__main__":
    main()

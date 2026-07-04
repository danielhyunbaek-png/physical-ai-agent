"""Play a TFT game with the physical agent. The Wave-2-era entrypoint.

Wires runtime.Session with the TFT system prompt, the semantic-action
translator, and the combat-phase gate. Cost strategy per CLAUDE.md: develop
on ollama (free), play on gemini/deepseek/qwen (~$0.10-0.50/game), escalate
hard turns (augments) to anthropic.

    # zero-hardware rehearsal on a saved screenshot:
    python tft/play_tft.py --still tft_shot.png --dry-run --provider ollama

    # a real cheap game (hardware connected, calibrated):
    python tft/play_tft.py --port /dev/tty.usbmodem14101 \\
        --mouse gantry --mouse-port /dev/tty.usbserial-XXXX \\
        --provider gemini --escalate-to anthropic --budget-usd 1.00

Before real games: fill in tft/set_data.json for the live set, verify
tft/layout.json with `python calibrate.py tft --still <screenshot>`, and
capture tft/templates/combat_marker.png to unlock combat skipping.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_loop import build_parser            # noqa: E402
from keyboard_driver import KeyboardDriver     # noqa: E402
from llm import LLM                            # noqa: E402
from mouse_driver import make_mouse            # noqa: E402
from runtime import Session                    # noqa: E402
from tft.tft_agent import (TFTLayout, TFTTranslator,   # noqa: E402
                           build_system_prompt, make_phase_hook)
from vision import Vision                      # noqa: E402


def main():
    ap = build_parser(goal_required=False)
    ap.set_defaults(goal="win the TFT game (top 4 minimum)",
                    max_turns=800, provider="ollama")
    args = ap.parse_args()

    kb = KeyboardDriver(None if args.dry_run else args.port)
    vision = Vision(camera_index=args.camera, still=args.still,
                    calib_path=args.calib)
    mouse = make_mouse(args.mouse, kb=kb, port=args.mouse_port,
                       calib_path=args.mouse_calib)
    if mouse is None:
        print("[tft] WARNING: no mouse backend -- placements/buys will be "
              "skipped. Use --mouse dry|mousekeys|gantry.")

    layout = TFTLayout()
    session = Session(
        LLM(args.provider, args.model), kb, vision, args.goal,
        mouse=mouse,
        system=build_system_prompt(),
        translate=TFTTranslator(layout),
        phase_hook=make_phase_hook(layout),
        max_turns=args.max_turns,
        budget_usd=args.budget_usd,
        max_minutes=args.max_minutes,
        escalate_to=LLM(args.escalate_to) if args.escalate_to else None,
        save_frames=not args.no_frames,
        turn_delay_s=1.5,
    )
    session.run()
    vision.close()
    if not kb.dry_run:
        kb.close()


if __name__ == "__main__":
    main()

# Agent software — observe → decide → act

The complete software stack for the physical agent, every layer testable
**without any hardware** (campsite rule, July 2026: exercise everything on
the MacBook alone, then point it at the real rig at home).

| File | What | Hardware needed |
|---|---|---|
| `keyboard_driver.py` | Python wrapper for the `keyboard_v1` serial protocol | None (dry-run) → Mega later |
| `mouse_driver.py` | Mouse backends: dry / **mousekeys** / gantry | mousekeys needs only the keyboard! |
| `actions.py` | One action vocabulary: validation + dispatch | None |
| `vision.py` | Capture → rectify → template match + OCR + frame hashing | Mac camera, or `still=` a PNG |
| `llm.py` | Pluggable brain + retries + JSON repair + $ metering | None |
| `runtime.py` | Session engine: logging, budgets, stuck detection, escalation | None |
| `agent_loop.py` | General-goal CLI over the runtime | None (`--dry-run --scripted`) |
| `calibrate.py` | screen / tft / gantry / mousekeys calibration flows | Varies |
| `tft/` | TFT layer: layout, set data, semantic actions, `play_tft.py` | None to rehearse |
| `tests/run_tests.py` | 20-test ladder for all of the above | **None at all** |

## The one command that proves the plumbing

```bash
cd agent && source .venv/bin/activate
python tests/run_tests.py        # 20 tests, no hardware, no network, no keys
```

If that passes, what's left to trust is physics and prompt quality.

## Choosing a brain (`--provider`)

| Provider | Cost per ~700-turn TFT game | Needs |
|---|---|---|
| `ollama` | $0 (local Qwen3-VL) | `brew install ollama && ollama pull qwen3-vl:8b` |
| `gemini` / `deepseek` / `qwen` | ~$0.10–0.50 | API key env var (see `llm.py` header) |
| `anthropic` | ~$4–8 | `ANTHROPIC_API_KEY` |

Strategy: **develop on `ollama`, play on cheap cloud, escalate hard turns.**
`--escalate-to anthropic` lets the cheap brain hand up any turn it flags with
`"escalate": true` (augment choices), and `--budget-usd 1.00` hard-stops the
session at the estimated spend.

## Choosing a mouse (`--mouse`)

| Backend | What moves the cursor | Hardware |
|---|---|---|
| `none` (default) | nothing — keyboard-only goals | Wave 1 |
| `dry` | print statements | none |
| `mousekeys` | **macOS Mouse Keys pressed by the solenoids** | Wave 1 only! |
| `gantry` | XY gantry + click servos (`firmware/mouse_gantry_v0`) | Wave 2 |

`mousekeys` is the sleeper: enable Mouse Keys on the target Mac
(Accessibility → Pointer Control; also enable the 5×-Option toggle) and the
robot gets real clicking and dragging **before any Wave 2 hardware exists**.
The driver toggles Mouse Keys off around text input automatically. Calibrate
speeds with `python calibrate.py mousekeys`.

## Run recipes

```bash
# plumbing, zero everything
python agent_loop.py --goal test --scripted --dry-run --mouse dry

# real brain, no hardware, on a saved screenshot
python agent_loop.py --goal "describe the screen" --dry-run \
    --still shot.png --provider ollama

# real rig, general goal
python agent_loop.py --goal "open spotlight and type hello" \
    --port /dev/tty.usbmodem14101 --calib calibration/screen_quad.json

# TFT rehearsal (no hardware) / TFT for real (cheap + escalation + cap)
python tft/play_tft.py --still tft_shot.png --dry-run --provider ollama
python tft/play_tft.py --port /dev/tty.usbmodemXXXX --mouse gantry \
    --mouse-port /dev/tty.usbserialYYYY --mouse-calib calibration/gantry_affine.json \
    --provider gemini --escalate-to anthropic --budget-usd 1.00
```

Every session writes `logs/session_<ts>/` — `session.jsonl` (plan, actions,
results, cost per turn), the frame each decision saw, and `summary.json`.
That's the replay data for prompt tuning.

## Before real TFT games (checklist)

1. `python calibrate.py screen` — C920 on tripod, bright fullscreen page.
2. `python calibrate.py tft --still <screenshot>` — nudge `tft/layout.json`
   until the dots sit on the shop cards/hexes/buttons.
3. Fill in `tft/set_data.json` for the live set (file explains how).
4. Crop a combat-only UI element into `tft/templates/combat_marker.png` —
   unlocks combat-phase skipping (~70% fewer LLM calls).
5. Mouse: `calibrate.py gantry` or `calibrate.py mousekeys`.

## Setup

```bash
cd agent
python3 -m venv .venv && source .venv/bin/activate   # re-activate EVERY terminal
pip install -r requirements.txt
brew install tesseract        # OCR engine (macOS)
```

### MAP workflow (ties into the solder-time log)

Keep logging `cell,out,key` lines at solder time (MAP discipline: label holes,
not wires). Put them in a CSV, then:

```python
from keyboard_driver import KeyboardDriver, load_map_from_log
kb = KeyboardDriver("/dev/tty.usbmodem14101")
load_map_from_log(kb, "map_log.csv")   # pushes MAP entries + SAVEs to EEPROM
kb.walk()                              # verification pass: watch which key clicks
```

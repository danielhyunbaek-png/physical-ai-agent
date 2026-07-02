# Agent software — observe → decide → act

Three modules, each independently testable **without any hardware** (written
July 2026 camping trip; designed so every layer can be exercised on the
MacBook alone, then pointed at the real rig when home).

| File | What | Hardware needed |
|---|---|---|
| `keyboard_driver.py` | Python wrapper for the `keyboard_v1` serial protocol | None (dry-run mode) → Mega later |
| `vision.py` | C920 capture → screen rectification → template match + OCR | Built-in Mac camera works |
| `agent_loop.py` | The agent: screenshot → Claude decides → solenoids act | None (`--dry-run --scripted`) |

## Setup

```bash
cd agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
brew install tesseract        # OCR engine (macOS)
```

## Campsite test ladder (no hardware)

```bash
# 1. Keyboard driver, dry run — prints the serial commands it would send
python keyboard_driver.py

# 2. Vision on the built-in camera — grabs a frame, OCRs whatever it sees
python vision.py

# 3. Full loop plumbing, no Claude, no Arduino
python agent_loop.py --goal test --scripted --dry-run

# 4. Full loop with real Claude decisions (needs ANTHROPIC_API_KEY),
#    still no Arduino — watch it "type" into the log
export ANTHROPIC_API_KEY=sk-ant-...
python agent_loop.py --goal "open spotlight and search hello" --dry-run
```

## At home (real rig)

```bash
# Flash firmware/keyboard_v1, then:
python agent_loop.py --goal "..." --port /dev/tty.usbmodem14101
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

## Vision calibration (at home, C920 on tripod)

1. Show a bright/white fullscreen page on the target machine.
2. `Vision.calibrate_screen()` auto-finds the monitor's 4 corners.
3. `Vision.screen()` then returns a rectified 1920×1080 screen image; template
   coordinates and OCR regions live in that space, immune to small camera bumps
   (re-calibrate after big ones).
4. Capture templates by cropping `save_frame()` output (menu icons, buttons).

# Brief 09 — Fast-TYPE firmware + Monkeytype page reader (320 WPM)

Written Oct 3, 2026 (Opus) as a handoff to a fresh chat. Hardware wiring is happening IN PARALLEL — the 84 keys are NOT mapped yet (`mapped=0/84`), so anything here must be testable on the single spare solenoid on ch 0 (A.J11 right screw) until wiring finishes.

## Goal (v1 part 2, from the Sep 28 record)
Monkeytype 15-second test, default English (lowercase + space, no punctuation), **> 320 WPM**, typed 100% physically by the solenoids. Demo/video only — never submit to the leaderboard (automation is banned there).

## Measured Oct 3 (spare JF-0530B over a Nuphy Air75 key, wired USB, TextEdit)
| Test | Result |
|---|---|
| Min pulse (10 presses @ 82 ms) | 22/20/18 ms = 10/10 · 16 = 9/10 · 15 = 1/10 · 10 = 0/10 → **use 20 ms** |
| Same-key re-fire (`REPEAT 0 20 <period> 20`) | 80/60/50/45 ms = 20/20 · 40 = 16–18/20 · 30 = 3/20 → **same-key minimum 45 ms** |

## Target math
320 WPM = 26.7 keystrokes/s = **37.5 ms per char average** (~400 chars in 15 s). Clock starts at first keystroke. Only 27 keys needed (a–z + Space).

## Firmware design constraints (`firmware/keyboard_v1/keyboard_v1.ino`, 600+ lines)
- Current TYPE = blocking `firePulse` (22 ms) + `SETTLE_MS` 60 → ~146 WPM ceiling. Needs a **non-blocking, schedule-based** typer: key-down events every ~37.5 ms (tunable, e.g. `SPEED <ms>`), each channel ON for 20 ms, pulses OVERLAP across different keys (the Nuphy only needs key-down order; N-key rollover).
- **Same key twice (double letters): enforce ≥45 ms between its starts** — delay that char, keep the schedule for the rest.
- `MAX_ON = 7` budget guard must stay (at 37.5 ms / 20 ms pulse, ≤1–2 on at once anyway).
- Must accept text as a STREAM over serial (Monkeytype words arrive continuously; the 128-byte line buffer and 64-byte Mega RX buffer are limits). Suggest a queue/ring buffer + a command like `STREAM`/`Q <word>` and an abort.
- Keep existing commands (FIRE/WALK/MAP/SAVE/TYPE/REPEAT…) working; WALK/MAP still needed for the wiring session.
- USB-first-then-12V rule; `PIN_OE = 10`; `CASCADE_REVERSED 0` (proven Sep 25).
- No arduino-cli in the sandbox (downloads.arduino.cc 403) → mock-compile against stub Arduino.h/EEPROM.h with g++ -Wall -Wextra (method used Jul 26).

## Page reader
Browser script reads Monkeytype's upcoming words from the DOM → sends to the Mega over USB serial. Camera/OCR rejected. Options to evaluate: Web Serial API from a userscript/bookmarklet in Chrome (no Python), or a Python bridge (pyserial) fed by the page. The Arduino Serial Monitor must be CLOSED while anything else holds the port. Port on Daniel's Mac: `/dev/cu.usbmodem11401`, 115200 baud, Newline.
- Must keep feeding words ahead of the typing (Monkeytype reveals more words as you type).
- Typing must physically land in the browser: focus the Monkeytype tab; the firmware's `LEAD` delay gives time to click.

## Testable now on 1 coil
`MAP 0 <letter>` (RAM only, never SAVE) then stream that letter → measures scheduler timing with real presses. Full test needs all 27 keys mapped after the wiring session.


## Status — Oct 3 (built)
Firmware stream typer + `tools/monkeytype_reader/` built; see CLAUDE.md Oct 3 (evening) record and `tools/monkeytype_reader/README.md`. Hardware tests pending.

# Fast-TYPE + Monkeytype reader — run card (brief 09)

Built Oct 3, 2026. Two pieces:
- `firmware/keyboard_v1/keyboard_v1.ino` — adds a non-blocking stream typer (`Q GO END FAST STOP WPM FPULSE SAMEKEY`). All old commands unchanged.
- `tools/monkeytype_reader/mt_reader.js` — paste into Chrome DevTools on monkeytype.com; reads the words and streams them to the Mega over Web Serial.

Defaults come from the Oct 3 measurements: **WPM 330** (36.4 ms/char), **FPULSE 20**, **SAMEKEY 45**.

## How the firmware types
- A new key-down every `12000/WPM` ms. Each coil stays on for `FPULSE` ms, so pulses on different keys overlap.
- **Double letters:** the second press waits until 45 ms after the first one started. Only that one character is delayed; the next one goes back on schedule.
- Different keys always start at least 10 ms apart, so the Nuphy sees them in the right order.
- **Unmapped characters keep their time slot but fire nothing.** That's what makes a 1-coil test possible.
- Lowercase and space only. Shifted characters are skipped and counted as `shift=`.
- `MAX_ON 7` guard kept (the simulation peaks at 2 coils on). The run is capped at 120 s. If nothing is queued for 3 s without `END`, it finishes on its own.
- While a stream runs, only `Q END STOP ALLOFF STATUS WPM FPULSE SAMEKEY` are accepted. Anything else gets `ERR busy`.
- At the end it prints: `DONE <why> slots= fired= skipped= shift= same= under= lateMax=us ms= wpm=`
  - `same` = double-letter delays
  - `under` = times the queue ran dry
  - `wpm` = schedule speed actually achieved

## TODAY: 1-coil test (spare on ch 0 = A.J11 right screw)
USB first, then 12V. Serial Monitor at 115200, Newline. Click into TextEdit during the LEAD delay. Never `SAVE`.

```
MAP 0 J
LEAD 3000
FAST jjjjjjjjjjjjjjjjjjjj
```
1. **Expect 20 j's** and `DONE end slots=20 fired=20 same=19 ... wpm≈269`. That's 45 ms each, the same-key limit.
2. `FAST jajajajajajajajajajajajajajajajajajajaja` (20 j, 20 a). **Expect 20 j's** 72.7 ms apart, and `skipped=20 wpm=330.0`. This checks the scheduler's slot timing with real presses.
3. Margin check: `SAMEKEY 40`, then rerun step 1. Oct 3 says you should see misses at 40 ms. Then `SAMEKEY 45` to restore.
4. Optional: `FPULSE 18`, rerun step 2, then `FPULSE 20`.
5. Clean up: `MAP 0 -`

**Full-pipeline dry run on 1 coil** (serial, focus and flow control on real hardware):
- Close Serial Monitor, then follow "Monkeytype run" below.
- Put `MAP 0 J` first in the reader's setup box.
- Only j's will land, so the Monkeytype score is junk. What you're checking is that the panel shows `GO`, then Monkeytype ends, then `STOP` and a `DONE` line with `under=0`.

## Monkeytype run (after all 27 keys are mapped: a–z + Space, then SAVE)
1. **Close the Arduino Serial Monitor.**
2. Chrome → monkeytype.com → **time 15, english**, punctuation and numbers off.
3. Open DevTools (Cmd+Opt+J) and paste all of `mt_reader.js` into the Console. The first time, Chrome makes you type `allow pasting`.
   - Better: DevTools → Sources → Snippets → New, paste it once, and run it with Cmd+Enter from then on.
4. Panel (top right) → **Connect** → `cu.usbmodem11401`.
   - Opening the port resets the Mega. The setup box is sent after every connect, so put RAM-only `MAP` lines there.
5. **Arm & Go.** The panel focuses Monkeytype itself and the Mega starts after `LEAD` (800 ms). Keep hands off. **STOP** aborts.
6. Afterwards the panel shows Monkeytype's WPM/accuracy and the Mega's `DONE` stats.

Note: the panel's "typed" counter only counts real key events.

**Demo/video only. Never submit to the leaderboard** (automated typing is banned there).

### Tuning ladder
- `under>0`: words arrived late. Unlikely, since Monkeytype pre-renders about 100 words (around 530 chars) and the Mega queue holds 1024.
- Errors on specific letters: that coil's pulse or seating. Check it with `REPEAT <ch> 20 80 20`.
- Clean at 330: try `WPM 350` for margin. 320 is the floor that counts.

## UNVERIFIED (as of Oct 3)
- Real avr-gcc compile. The code was only mock-compiled: g++ -Wall -Wextra with Arduino stubs, plus a timing simulation. First Verify in the IDE is the real check.
- 10 ms different-key stagger and overlapping pulses on the Nuphy (needs 2+ coils).
- Each register write costs about 1.3 ms of shiftOut. It's the same on every key, so it shouldn't matter. Faster port writes are possible if `lateMax` gets large.
- Web Serial on Daniel's Chrome with the Mega port.

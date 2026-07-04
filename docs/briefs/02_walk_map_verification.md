# Brief 02 — Flash keyboard_v1, build the MAP, verify with WALK

**Goal:** the soldered board drives real keys with a trusted channel→key map, persisted in EEPROM.

## Context you must hold

- Firmware: `firmware/keyboard_v1/keyboard_v1.ino`. **Read its header before flashing** — power-on rule (USB first, THEN 12V) and `CASCADE_REVERSED` flag (set if WALK shows flipped cell order).
- Protocol: FIRE N → cell(N/8+1)/OUT(N%8+1), sequential by design (canonical Q→IN wiring made this true). TYPE / KEY / CHORD / HOLD / RELEASE; MAP/SAVE/LOAD persist the keymap to EEPROM — **no recompile during solder-time logging.**
- Guards: per-channel 60ms cooldown, MAX_ON=7 (PSU protection — realistic peak ~25A on a 40A supply).
- Host side: `agent/keyboard_driver.py` — `load_map_from_log()` takes a `cell,out,key` CSV and issues MAP+SAVE.

## MAP discipline (canonical — do not improvise)

Position is identity: all leads are identical black. Sharpie the key name beside each landing hole; log `cell · OUT · key` **at solder time**, one line per wire, into the CSV. Cut each wire to length only at the moment it's landed — never pre-cut. WALK mode (fire 0–83, watch which key clicks) is the FINAL verification pass, not the primary bookkeeping.

## Order of operations

1. Flash keyboard_v1 (12V off). Serial sanity: STATUS, then FIRE on a known channel.
2. As each solenoid's low-side wire is landed: log the CSV line immediately.
3. `load_map_from_log()` → MAP+SAVE → LOAD to confirm EEPROM round-trip.
4. WALK pass over all landed channels. Any mismatch → fix the CSV (trust the physical click), re-MAP, re-SAVE.
5. If cell order comes out mirrored → `CASCADE_REVERSED`, reflash, re-WALK.
6. First TYPE of a real sentence — milestone, film it.

## Definition of done

WALK matches MAP 100%; TYPE produces clean text incl. a shifted character (LShift chord); EEPROM survives power cycle; commit + **git push**; CLAUDE.md updated.

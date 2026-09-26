# Session Card — Fri Sep 25, 2026 — Boards B + C gate, chain A→B→C (lab, ~4h)

> **RESULT (Sep 25 evening): ALL PASSED — B 32/32, C 32/32, chain HOLD 0/31/32/63/64/87 PASS = 88/88 proven.** See CLAUDE.md Sep 25 (lab) record. OFF in diode mode may read ~1.8V instead of OL (no 12V) — pass = drop to 0.6–0.9V.

Last soldering-station session of the project. After today everything is screwdriver work.

## Bring
Boards A, B, C · 4× 74HC595 + 4× ULN2803A (B) · 3× 595 + 3× ULN (C) · Mega + USB-C→USB-B cable · F-F ribbons + M-F dupont · 1× 6-pin male header (for A.J72) · Sharpie · laptop w/ Arduino IDE · calipers/ruler · 1 loose spare solenoid · phone for b-roll.

## 0 · First thing (no soldering needed)
- Board A J72 header: confirmed fitted (Sep 25). Nothing to solder — go straight to board B.

## 1 · Board B (~65 min)
1. **Cold gate, chips OUT** — the 7 parts from the Sep 20 record (rails open ×3 · R1 = ~10k at U11.13↔U11.16 · adjacent-pin sweep all 8 sockets · adjacent-screw sweep · 32 output paths · J71 pins 1–6 → U11.16/8/14/11/12/13 · J70 +12V → U12/22/32/42 pin 10, J70 GND → U11.8, CB1 legs).
   **Add for B:** J72 pins 1–6 → U41.16 / U41.8 / **U41.9** / U41.11 / U41.12 / U41.13.
   Probe from the TOP (socket holes, header pins, screw heads) — the underside is all ground plane.
2. **Chips in**, all notches toward the TOP edge (J11/J12 row). Re-check 3 rails open at connectors.
3. **Mega → B.J71** (M-F). End-to-end continuity: D10→U11.13 · D11→U11.14 · D12→U11.11 · D13→U11.12 · 5V→U11.16 · GND→U11.8.
4. USB only. `STATUS`. Then **HOLD 0…31, DIODE mode** (not the beeper), black probe on J70 GND. Probe the screw FIRST, then send HOLD. ON = 0.6–0.9V, OFF = OL.

## 2 · Board C (~55 min)
Same as B, but **only cells 1–3**: leave U41/U42 sockets empty, **Sharpie an X across J41–J44**, HOLD 0…23. Skip the J72 check (chain tail).

## 3 · Chain A→B→C (~30 min)
1. Sharpie a **pin-1 dot** on every header (pin 1 = +5V = top pin, square pad underneath).
2. Plug Mega→A.J71 · A.J72→B.J71 · B.J72→C.J71 (pin 1→1, no crossover). All chips in.
3. **Unpowered end-to-end check through the whole chain:**
   D12→C.U11.11 · D13→C.U11.12 · D10→C.U11.13 · 5V→C.U11.16 · GND→C.U11.8 ·
   A.U41.9→B.U11.14 · B.U41.9→C.U11.14 (data hand-offs).
4. USB. **HOLD 0, 31, 32, 63, 64, 87** in diode mode:
   | ch | board | terminal |
   |---|---|---|
   | 0 | A | J11 right screw (C1-OUT1) |
   | 31 | A | J44 right screw (C4-OUT8) |
   | 32 | B | J11 right screw |
   | 63 | B | J44 right screw |
   | 64 | C | J11 right screw |
   | 87 | C | J34 right screw (C3-OUT8) |
   Right boards but wrong order = `CASCADE_REVERSED` flag in firmware, not a wiring fault.
5. **PASS = all 88 channels proven. The bench gate that matters.** Tape the dupont connectors once it passes.

## 4 · Before leaving (~20 min)
- Ask staff: how to book a Bambu X1C overnight, filament (PLA) source/cost.
- Measure the loose spare solenoid: **factory lead length** + where the leads exit the body.
- B-roll: board-flip reveal, meter reading 0.65V, the three chained boards.

## Tonight (dorm)
- Measure: plate top height above desk at FRONT and BACK edges · plate outer footprint incl. legs · anything protruding (USB cable, keyboard edges).
- Pick the barrier-strip listing (12-position, jumper bars, mounting holes) and send the link — the shelf CAD needs its dimensions.
- Decide: Mega on the shelf too? (yes by default)
- `git push`.

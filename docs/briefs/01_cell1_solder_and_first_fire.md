# Brief 01 — Cell #1: solder, continuity gate, first fire

**Goal:** turn the dry-fit cell #1 (Mega → 74HC595 → ULN2803A → solenoid) into a soldered, verified, firing unit. This is a filmable milestone.

## Context you must hold

- Source docs: `Soldering_Plan.md`, `OneCell_595_ULN_Build_and_Fire_Guide.md`, `TopSide_Wiring_CutList.md`, `Cell_TopSide_Routing.svg`.
- As-built decisions (CANONICAL, do not re-litigate): ULN flipped (notch RIGHT), Q→IN canonical order (Q0→IN1 … Q7→IN8), jumper fan lengths 70/65/60/55/50/50/55/60mm (Q0…Q7), solder longest-first (IN1→IN8), consistent crossing layering. OUT landing holes run right-to-left (OUT1 far right) — chip-internal, independent of jumper scheme.
- 2-2-2-2 middle-rail spacing, 11-row chip gap.
- ULN COM (pin 10) → +12V rail. **Never skip — it's the flyback diodes.**
- Solid wire on board; solid→stranded transition at the landing hole only.

## Order of operations

1. Rails first (per `Soldering_Plan.md`), then sockets, then jumper fan longest-first.
2. **Cold continuity gate BEFORE chips are inserted and BEFORE any power:** beep every rail (5V, GND, 12V — verify NO 5V↔12V or rail↔rail shorts), every Q→IN path, every OUT→landing hole, COM→12V. Chips out of sockets during all of this.
3. Insert chips (595 + ULN, correct orientation — ULN is FLIPPED relative to naive placement; double-check notch direction against `Cell_TopSide_Routing.svg`).
4. **Power-on order: Arduino/USB FIRST, then 12V.** 595s output random data until cleared — 12V-first can fire random solenoids.
5. One solenoid on OUT1 → `FIRE 0` from keyboard_v1 (or keyboard_v0 single-cell test). Expect: FIRE N → OUT(N+1).
6. Walk all 8 channels with one roving solenoid before landing real wires.

## Failure modes to check first

- No fire at all → COM pin, power-on order, cascade wiring (D11/D12/D13), 12V rail actually energized.
- Wrong channel fires → jumper fan crossing error; re-beep Q→IN paths.
- Solenoid stays energized → stuck 595 output (power-on order) or solder bridge on OUT.
- Chip gets hot fast → reversed ULN or 5V/12V short. Kill power immediately.

## Definition of done

All 8 channels fire the roving solenoid correctly; nothing warm at idle; milestone filmed; commit + **git push**; CLAUDE.md session record appended.

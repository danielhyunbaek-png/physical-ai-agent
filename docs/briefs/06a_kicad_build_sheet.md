# Brief 06a — KiCad build sheet (6-cell driver board)

**Companion to brief 06 (the electrical spec — that stays the source of truth). This file = the KiCad-specific recipe: exact symbols, footprints, reference designators, and net names.** Written July 16, 2026 during the design session (tool switched EasyEDA → KiCad so Claude can verify the text-format project files directly in the repo).

Project location: `pcb/solenoid_driver/` in this repo. KiCad 9.x, stock libraries only.

## Reference designator scheme (self-documenting)

Cell *n* (1–6): 595 = **U{n}1**, ULN = **U{n}2**, 595 decoupling cap = **C{n}1**, output terminals = **J{n}1–J{n}4** (4× 2-pos = 8 positions, OUT1..8 left to right).
Board-level: **J70** = 12V input terminal · **J71** = cascade IN header · **J72** = cascade OUT header · **R1** = 10k OE pullup · **CB1** = 4700µF bulk (12V) · **CB2** = 100nF (12V) · **CB3** = 100nF (5V).

## Symbols + footprints (place these)

| Qty | Part | Symbol (library:name) | Footprint |
|---|---|---|---|
| 6 | 74HC595 | `74xx:74HC595` | `Package_DIP:DIP-16_W7.62mm` (DIP socket fits this) |
| 6 | ULN2803A | `Transistor_Array:ULN2803A` | `Package_DIP:DIP-18_W7.62mm` |
| 25 | 2-pos screw terminal (24 out + 1 power) | `Connector:Screw_Terminal_01x02` | `TerminalBlock:TerminalBlock_bornier-2_P5.08mm` |
| 2 | 6-pin cascade header | `Connector_Generic:Conn_01x06` | `Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical` |
| 1 | 10k resistor | `Device:R` | `Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal` |
| 8 | 100nF ceramic (104) | `Device:C` | `Capacitor_THT:C_Disc_D8.0mm_W5.0mm_P5.00mm` (5.00 vs 5.08 pitch — fine for radial leads) |
| 1 | 4700µF 25V electrolytic | `Device:C_Polarized` | `Capacitor_THT:CP_Radial_D18.0mm_P7.50mm` — **MEASURED Jul 16: can Ø17mm × 25mm tall, lead pitch ~8mm (→ standard 7.5). Can height 25mm feeds the brief 07 deck clearance stack.** |
| 4 | M3 mounting hole | `Mechanical:MountingHole_Pad` | `MountingHole:MountingHole_3.2mm_M3` |

## Net names (use net labels, not long wires)

Global power: `+5V`, `+12V`, `GND` (use the power symbols).
Buses: `DATA_IN` · `SCLK` (=CLK, Mega D12) · `RCLK` (=LATCH, Mega D13) · `~OE` · cascade hops `CASC1`…`CASC5` · `DATA_OUT`.
Per cell, Q→IN connections can be drawn as direct short wires (place U{n}1 immediately left of U{n}2) — no labels needed.

## Pin-by-pin — 74HC595 (U{n}1, DIP-16)

| Pin | Name | Connect to |
|---|---|---|
| 16 | VCC | +5V |
| 8 | GND | GND |
| 14 | DS (SER) | cell 1: `DATA_IN` · cell n: `CASC{n-1}` |
| 11 | SHCP (SRCLK) | `SCLK` bus |
| 12 | STCP (RCLK) | `RCLK` bus |
| 10 | ~MR (SRCLR) | +5V |
| 13 | ~OE | `~OE` bus |
| 9 | Q7' (Q7S) | cell 1–5: `CASC{n}` · cell 6: `DATA_OUT` |
| 15 | Q0 | ULN IN1 (pin 1) |
| 1–7 | Q1–Q7 | ULN IN2–IN8 (pins 2–8) — **canonical, in order** |

## Pin-by-pin — ULN2803A (U{n}2, DIP-18)

| Pin | Name | Connect to |
|---|---|---|
| 1–8 | IN1–IN8 | 595 Q0–Q7 (above) |
| 18–11 | OUT1–OUT8 | terminals: J{n}1 pin1=OUT1, pin2=OUT2 · J{n}2 = OUT3/4 · J{n}3 = OUT5/6 · J{n}4 = OUT7/8 |
| 9 | GND | GND |
| 10 | COM | **+12V (flyback — never skip)** |

## Board-level

- **J70 (12V in):** pin 1 → +12V, pin 2 → GND. Attach `PWR_FLAG` to +12V and GND here (ERC needs it).
- **J71 (cascade IN):** 1→+5V · 2→GND · 3→`DATA_IN` · 4→`SCLK` · 5→`RCLK` · 6→`~OE`. Attach `PWR_FLAG` to +5V here (5V enters the board through this header from the Mega).
- **J72 (cascade OUT):** 1→+5V · 2→GND · 3→`DATA_OUT` · 4→`SCLK` · 5→`RCLK` · 6→`~OE`.
- **R1:** `~OE` → +5V (the 10k pullup — outputs disabled until the Mega drives OE).
- **CB1 (4700µF):** +12V to GND. **Polarity: + to +12V.** Place near J70.
- **CB2 (100nF):** +12V to GND, next to CB1. **CB3 (100nF):** +5V to GND, near J71.
- **C{n}1 (100nF):** +5V to GND, one physically adjacent to each 595.

## Workflow checklist

1. Schematic: build **cell 1 completely** → Claude verifies the `.kicad_sch` → copy-paste ×5 → fix per-cell labels (DS/Q7' chain) → board-level parts.
2. **Annotate** (Tools → Annotate Schematic) — keep the U{n}1/U{n}2 scheme (set refs manually as you place; paste-copies annotate with fresh numbers, rename to scheme).
3. **ERC** → expect PWR_FLAG complaints if step "Board-level" missed → fix to zero errors.
4. Assign footprints (table above) → **Update PCB from Schematic** (F8).
5. Layout: Edge.Cuts ≤100×100mm · terminals along 3 edges · chips in 6 rows/columns matching cells · route: OUT traces ≥0.6mm, GND+12V ≥2mm or zone pours (GND pour bottom, +12V pour top around terminals) · silkscreen `S{n}-OUT{m}` + blank Sharpie box per terminal.
6. **DRC** to zero errors. JLCPCB limits (2-layer): ≥0.127mm trace/space — we're nowhere near.
7. 1:1 paper print (File → Print, scale 1.0) — set real parts on it, check terminal spacing.
8. Plot Gerbers (F.Cu, B.Cu, F.SilkS, B.SilkS, F.Mask, B.Mask, Edge.Cuts) + drill files → zip → upload to jlcpcb.com/quote → 2-layer, 1oz, HASL, **qty 5** → cheapest ~1wk shipping.
9. Export board outline + the 4 mounting-hole coordinates → brief 07 Track B (deck CAD datum).
10. **git add pcb/ + commit + push — milestone.**

## Populate plan (unchanged from brief 06)

Board A = cells 1–6 (ch 0–47). Board B = same PCB, populate slots 1–5 only (ch 48–87), slot 6 socket EMPTY — board B goes LAST in the cascade. 3 spare bare boards.

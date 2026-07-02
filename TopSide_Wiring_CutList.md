# Top-Side Wire-Art — Cut List & Method (Driver Cell)

*Goal: clean, camera-ready wiring on the soldered perfboard, in the style of a breadboard "wire-art" build — jumpers routed on the **top (component) side** in crisp right angles. Plan, measure, shape, and cut every wire **before** the chips go in. This is cell #1 of 11; shape one set, then batch-repeat.*

Companion files: `Cell_TopSide_Routing.svg` (the visual target), `Driver_Cell_Perfboard_Layout.svg` (pin map), `Soldering_Plan.md` / `OneCell_595_ULN_Build_and_Fire_Guide.md` (the build itself).

> **Layout — ULN flipped 180° (notch RIGHT).** Inputs (IN) now sit on the ULN's **top** row facing the 595; outputs (OUT) on the **bottom** row facing the solenoids. This shortens the output drops and turns COM and ULN-GND into clean short taps. **AS-BUILT (July 2026): canonical wiring — Q0→IN1, Q1→IN2 … Q7→IN8** — so channel order stays sequential (FIRE N → OUT(N+1), nothing to fix in firmware). The trade: the flipped IN row runs right-to-left, so the 8 jumpers are a symmetric crossing fan of unique lengths (see §4), not a parallel batch. (The 595 is unchanged, notch LEFT.)

> **Spacing — chips moved 1 row apart (11-row gap).** Middle rails use **2 empty rows** between each chip and the nearest rail, and **2 between each rail**: 595 →2→ SH_CP →2→ ST_CP →2→ GND →2→ ULN. You had 10 rows between the chips; nudge to 11 (ULN down one, or 595 up one). The wider gap lengthens the logic bundle slightly (13 holes vs 9) — the trade for clean rail separation.

---

## 1. The one catch with top-side art on pad-per-hole perfboard

On a **breadboard**, every hole in a column is internally bused, so a jumper just plugs into any hole near a pin. On **pad-per-hole perfboard, every hole is isolated** — the electrical joint is made on the **bottom**, at each pad. A socket pin already fills its own hole, so a top-routed jumper cannot drop into the pin's hole.

**The fix (use this at every chip-pin end):** land the wire in the **free hole immediately next to the pin**, then on the bottom bend the stripped tail across and solder it to **both** its own pad **and** the pin's pad (a one-hole solder bridge made by the wire's own tail). Rail ends are easy — they drop straight into any free hole along the rail.

Because the wire body lies on top and only the ends dive through, wires **fly freely over chips, pins, and rails** — nothing mid-path needs a hole. That's exactly what makes the photo look good (wires arcing over the chips).

## 2. Split strategy — hero wires on top, housekeeping on the bottom

Not every wire should be on top. Put the **photogenic** wires up top and hide the **set-and-forget** ties underneath. The result looks intentional and is far easier to build.

**On top (the wire art):**
- The 8 logic jumpers Q→IN (the signature crossing fan)
- Signal taps: SH_CP, ST_CP, DS
- The 8 output drops OUT1–8 → solenoid landing holes
- Power taps: VCC→+5V, MR→+5V, 595 GND→GND, and — thanks to the flip — ULN GND→GND and COM→+12V (both now short, clean taps)

**On the bottom (kept off-camera):**
- OE→GND only — it's a 595 top-row pin needing GND below, the one link that still collides on top
- Both 0.1 µF decoupling caps and the reservoir cap
- The star-ground ties (PSU GND, Mega GND)

## 3. Measure / shape / cut — the method

**Pitch is everything.** Holes are 0.1″ = **2.54 mm** apart. Measure any run by **counting holes**, not with a ruler.

**Length formula (cut long, trim on fit):**

> cut length ≈ (hole span × 2.54 mm) + **15 mm** slack + **5 mm** for each chip it flies over

The 15 mm covers ~7.5 mm at each end for the strip + the 90° down-bend + insertion. Round up to the nearest 5 mm; you'll trim.

**Hole span = Manhattan distance:** horizontal holes + vertical holes between the two endpoints (right-angle path, no diagonals).

**Strip & bend:** strip ~**4 mm** at each end. Bend a crisp **90° down** right at the insulation edge so the bare leg drops into the hole and the insulated body lies flat on the board.

**Use the board as a bending jig.** Poke one end into its hole, lay the wire flat along the surface to the corner, and bend it down into the next hole. Bending *on the grid* guarantees pitch-perfect corners and identical parts — much cleaner than eyeballing.

**Batch identical wires.** Seven of the eight logic jumpers are the same length (see the list) — cut and shape all seven together for a uniform bundle. Uniformity is what reads as "clean" on camera.

**Color discipline (from your wiring map):** red = +5 V · orange = +12 V · black = GND · blue = DS · green = SH_CP · white = ST_CP · grey = signal (Q→IN, OUT→solenoid). One color per net, never reused.

---

## 4. Cut list — one cell

Columns C1–C9 = board columns left→right. The 595 is notch-**LEFT**; the ULN is flipped notch-**RIGHT**, so its IN row is on top. "Holes" = Manhattan span between endpoints. Cut = suggested length to cut, then trim. (Q→IN pairs below are **canonical, as-built**: a symmetric crossing fan — Q0–Q4 cross right, Q5–Q7 cross left. Batch the length-pairs: 2×50, 2×55, 2×60.)

### On-board, top side

| # | Wire | Color | From | To | Holes | Cut | Bend |
|---|------|-------|------|-----|:----:|:---:|------|
| 1 | Q0→IN1 | grey | 595 pin 15 (top row) | ULN pin 1 | 22 | **70 mm** | L (the long one — flies over the 595, over 7 →) |
| 2 | Q1→IN2 | grey | 595 pin 1 | ULN pin 2 | 19 | **65 mm** | L (down, over 7 →) |
| 3 | Q2→IN3 | grey | 595 pin 2 | ULN pin 3 | 17 | **60 mm** | L (down, over 5 →) |
| 4 | Q3→IN4 | grey | 595 pin 3 | ULN pin 4 | 15 | **55 mm** | L (down, over 3 →) |
| 5 | Q4→IN5 | grey | 595 pin 4 | ULN pin 5 | 13 | **50 mm** | L (down, over 1 →) |
| 6 | Q5→IN6 | grey | 595 pin 5 | ULN pin 6 | 13 | **50 mm** | L (down, over 1 ←) |
| 7 | Q6→IN7 | grey | 595 pin 6 | ULN pin 7 | 15 | **55 mm** | L (down, over 3 ←) |
| 8 | Q7→IN8 | grey | 595 pin 7 | ULN pin 8 | 17 | **60 mm** | L (down, over 5 ←) |
| 9 | VCC→+5V | red | 595 pin 16 | +5V rail | 2 | 20 mm | I (straight up) |
| 10 | MR→+5V | red | 595 pin 10 | +5V rail | 2 | 20 mm | I |
| 11 | 595 GND→GND | black | 595 pin 8 | GND spine | 9 | 40 mm | I (crosses SH, ST) |
| 12 | SH_CP tap | green | 595 pin 11 | SH_CP rail | 6 | 30 mm | I (flies over chip) |
| 13 | ST_CP tap | white | 595 pin 12 | ST_CP rail | 9 | 40 mm | I (crosses SH) |
| 14 | **ULN GND→GND** | black | ULN pin 9 (now top-left) | GND spine | 3 | 25 mm | I (short tap ↑) |
| 15 | **COM→+12V** | orange | ULN pin 10 (now bottom-left) | +12V rail | 2 | 20 mm | I (short tap ↓) |
| 16–23 | **OUT1→…OUT8 → landing holes** (8) | grey | ULN pins 18→11 (bottom row) | solenoid landing holes | 2 | 20 mm ×8 | I (straight drop) |

### On-board, bottom side (short link — no need to pre-shape)

| Wire | Color | From | To | Note |
|------|-------|------|-----|------|
| OE→GND | black | 595 pin 13 | GND rail | 595 top-row pin, GND is below it — one short link underneath |

### Flying leads — measure in place, don't pre-cut

| Lead | Color | Length | When |
|------|-------|--------|------|
| DS → Mega D11 | blue | ~150–200 mm | cell #1 only |
| Q7′ → next cell's DS | blue | ~one cell pitch (~45 mm) | cells 1–10 (cascade) |
| SH_CP rail → Mega D12 | green | ~150–200 mm | once per board |
| ST_CP rail → Mega D13 | white | ~150–200 mm | once per board |
| Mega GND → GND rail | black | ~150 mm | once per board (star point) |
| Solenoid runs (OUT landing hole→coil low side; coil high side→+12 V bus) | grey / orange | to the solenoid | 22 AWG **stranded**, off-board |

### Buses (bare wire, laid continuous across all 11 cells)

| Rail | Color | Build |
|------|-------|-------|
| +5V | red | single 22 AWG solid, soldered every hole |
| SH_CP | green | single 22 AWG solid |
| ST_CP | white | single 22 AWG solid |
| **GND spine** | black | **2× 22 AWG solid in parallel + solder bead** (fat) |
| **+12V** | orange | **2× 22 AWG solid in parallel + solder bead** (fat) |

### Components (place, don't cut)

- 0.1 µF ceramic ×2 — across 595 pins 16↔8 and ULN pins 10↔9, legs short, bottom side.
- 470 µF electrolytic (single cell) — + leg → +12 V, stripe → GND, near the ULN.

---

## 5. Work order

1. **Shape & cut** the whole cell from this list (batch the fan's length-pairs: 2×50, 2×55, 2×60). Lay each set out on tape in order — you're pre-building the whole cell before any heat.
2. **Dry-fit** the shaped wires on the board (chips still out) to confirm every length reaches. Trim.
3. **Solder the sockets** — 595 notch **LEFT**, ULN notch **RIGHT** (flipped). Tack 2 corners, check flat, finish.
4. **Lay the 5 rails** (buses). Keep +5 V and +12 V apart; GND and +12 V get the doubled-wire + solder-bead treatment.
5. **Place the top bundle**: logic jumpers first, in **canonical order (Q0→IN1 … Q7→IN8), longest-first** so the fan's crossings layer consistently; then the signal and power taps. Ends into the adjacent free holes, tails soldered across to the pins underneath.
6. **Bottom housekeeping**: OE→GND, both 0.1 µF caps, reservoir cap. (COM and ULN-GND are now top taps.)
7. **Outputs**: OUT1–8 drop straight down to their solenoid landing holes.
8. **Flying leads** last: DS/clock/latch/GND to the Mega, cascade to the next cell.
9. **Cold-test** per `OneCell_595_ULN_Build_and_Fire_Guide.md` §4 → 5 V only → 12 V last.

Then repeat cells 2–11: rails just extend right, and the 8-jumper fan set is identical every time.

---

## 6. For the camera

Uniform wire height, identical bends, tight parallel bundles, and strict color coding are what make it read as "wire art." Shoot the top bundle before you flip the board for the bottom housekeeping. **Milestone:** once the cell fires clean, commit a photo of the finished top-side routing + your final `PULSE` value to GitHub.

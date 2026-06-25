# Full 84-Key Split Plate — Design Brief (Week 4)

Scaling the validated 2×2 up to the full Nuphy Air75 V3, split into two halves for the **Bambu Lab P2S (256 × 256 × 256 mm bed)**. Convention unchanged from the 2×2 master dims: **origin = center of the S-key plunger hole, X = right, Y = toward keyboard back, Z = up. Plate bottom = Z0, plate top = Z4.** All values mm.

> **Layout confirmed from Daniel's top-view diagram (June 2026):** case **318.9 × 128.9 mm** → keycap field is exactly **16u wide** (16 × 19.05 = 304.8 + ~7 mm bezel/side). Six rows on a **uniform 19.05 mm pitch** (no extra function-row gap). The top-right **rotary knob is being replaced with a normal keycap**, so that position is actuated like any other key → the build is a clean **84 keys**. Function row is a full **16 keys** (Esc, F1–F12, PrtSc, + 2 customizable, the last in the ex-knob corner). Bottom row is Mac-style **10 keys** (Ctrl Opt Cmd · Space · Cmd Fn Ctrl · ◄ ▼ ▶).

> **Architecture carried in:** we keep the **screw-in mounting walls** from the 2×2 (solenoids bolt to a perpendicular wall per row, M3×3 flat-heads + flush counterbore). We are **not** using the card-cage / comb-lid / removable-wall scheme. Everything per-key (Ø10 plunger holes, `lower_hole_z=7`, ball ~4 mm below plate, 2.5 mm walls, M3×3 flat-heads, counterbores) is identical to the 2×2 — only the **footprint, the split, and the seam join** are new.

---

## 1. Why split left/right, and into exactly two

| | value |
|---|---|
| Full plate footprint (key centers + 11 mm margin) | **307.8 (X) × 117.2 (Y) mm** |
| P2S usable bed | 256 × 256 mm |
| Binding dimension | **width (X): 307.8 > 256** — depth already fits |

Only the **width** overruns the bed, so the cut removes X: **one vertical seam, a Left half and a Right half.** A front/back cut would leave each piece still 307.8 mm wide — useless. No need for 3+ pieces.

| Half | keys | footprint | fits 256² |
|---|---|---|---|
| Left | 41 | **158.6 × 117.2 mm** | ✅ ~97 mm spare |
| Right | 43 | **163.4 × 117.2 mm** | ✅ ~93 mm spare |

---

## 2. The seam is **stepped**, not straight — and why it must be

A straight vertical seam **cannot** be placed anywhere in the key field without slicing a keycap hole in half. The stagger packs hole-centers ~4.76 mm apart across X, so any straight line lands within ~2.4 mm of a center — inside a Ø10 hole. (Verified: best straight-seam clearance = 2.38 mm.)

The fix is a **staircase seam**: vertical through a column gap on each row, jogging sideways in the hole-free band between rows. Result: **every hole clears the seam by ≥ 9.52 mm.** See `Layout_Map_84Key_Split.svg` (red dashed line).

### Seam centerline — exact path (top-view sketch on the plate)

Single polyline, back edge → front edge. Vertical segments at the per-row X; horizontal jogs at the row-boundary Y's (no holes there).

| segment | X (mm) | from Y | to Y | sits between |
|---|---|---|---|---|
| Function + Number | **90.48** | +68 (back edge) | +28.575 | F7\|F8 and 7\|8 |
| jog | 90.48 → 80.97 | +28.575 | +28.575 | (row gap) |
| QWERTY | **80.97** | +28.575 | +9.525 | Y\|U |
| jog | 80.97 → 85.72 | +9.525 | +9.525 | |
| Home | **85.72** | +9.525 | −9.525 | H\|J |
| jog | 85.72 → 95.25 | −9.525 | −9.525 | |
| ZXCV | **95.25** | −9.525 | −28.575 | N\|M |
| jog | 95.25 → 90.48 | −28.575 | −28.575 | |
| Bottom | **90.48** | −28.575 | −49 (front edge) | inside the spacebar gap |

Total sideways wander ~14 mm. The steps are a feature: **they key the halves together** in X and Y so they can't slide when bolted.

---

## 3. HOW TO SEPARATE — Fusion 360

Model the **whole plate as one body first** (2×2 logic with 84 holes + 6 walls), then split it.

1. **Model the full plate flat** (holes vertical; tilt comes from legs — same as 2×2). Plate rectangle, 84 Ø10 holes at the §5 coordinates, 6 mounting walls (§6).
2. **Sketch the seam** on the plate top face: draw the staircase polyline from the §2 table (one connected sketch).
3. **Make a cutting surface:** select the seam sketch → **Create → Extrude → Surface** → extrude **down** past the plate bottom and **up** past the tallest wall (e.g., Z −5 to Z +35) so it fully spans plate + walls.
4. **Split Body:** **Modify → Split Body** → *Body to split* = plate, *Splitting tool* = that surface → OK.
5. **Rename** `Plate_Left` / `Plate_Right`. Add the join features (§4).
6. **Export each** → Save As Mesh → STL, High refinement.

---

## 4. HOW TO COMBINE — removable screw join (your chosen method)

Two halves bolt together rigidly and coplanar, and come apart for transport / switch swaps. Three elements:

**(a) The steps register X & Y** — done by the staircase; no dowels needed in-plane.

**(b) Four cross-seam bridge screws** hold + flatten them. The plate top, in the **troughs between mounting walls**, is open. Put 4 bridges there, spread along the depth:

| bridge | trough (between walls) | approx Y | seam X there |
|---|---|---|---|
| B1 (back edge) | behind Function wall | +67 | 90.48 |
| B2 | Number ↔ QWERTY | +33 | 90.48 |
| B3 | Home ↔ ZXCV | −1 | ~85.7 |
| B4 (front edge) | in front of Bottom wall | −45 | 90.48 |

At each: **one half has a flat tab** (~14 × 12 × 3 mm) reaching ~12 mm across the seam over the other half; **the other half has a 6 mm boss** with an **M3 heat-set insert** (model Ø5.0 × 6 mm blind hole). An **M3 × 8 screw** through a Ø3.4 clearance hole + counterbore in the tab threads into the insert. Tabs/bosses sit in the wall troughs, clear of every hole and keycap.

**(c) Optional wall tongue-and-groove.** Where the seam crosses each wall (always in a solenoid gap), add a 2 mm tongue on one wall segment and a matching groove on the other to shear-key the tall walls. The bridges already hold the plate flat, so this is insurance.

**Heat-set inserts are correct here** (PLA, unlike the solenoid tab). Press in with a soldering iron at ~240–260 °C.

### Hardware to combine
- 4 × **M3 brass heat-set inserts** (~5–6 mm; Ø5.0 pilot)
- 4 × **M3 × 8 socket-head screws**
- no glue (removable)

### Assembly sequence
1. Print `Plate_Left`, `Plate_Right`, 4 legs.
2. Heat-set the 4 inserts (one half).
3. Mate halves — steps interlock, tabs land on bosses.
4. Drive the 4 M3 × 8 bridge screws. Snug, don't crank.
5. Bolt the 4 legs (§7); shim the 1–2 mm gap.
6. **Mount solenoids row by row, front row first** (flush heads clear the body behind). ~5–7 h for 84.

---

## 5. HOLE SPACINGS — all 84 keys

Standard ANSI 75% geometry, `pitch = 19.05` both axes, on the confirmed 16u field. **Validated against your 2×2:** reproduces S (0,0), D (19.05, 0), W (−4.76, 19.05), E (14.29, 19.05) exactly. Machine-readable list in **`Full_84Key_Hole_Coordinates.csv`** (key, row, x_mm, y_mm, half, seam_x). `half` = which printed piece each hole is on. The rightmost column (X = 233.36) is the nav/utility column, populated on every row.

**Row 0 — Function (Y = +57.15, seam X = 90.48)**

| key | X | key | X | key | X |
|---|--:|---|--:|---|--:|
| Esc | -52.39 | F6 | 61.91 | F12 | 176.21 |
| F1 | -33.34 | F7 | 80.96 | PrtSc | 195.26 |
| F2 | -14.29 | F8 | 100.01 | Cust1 | 214.31 |
| F3 | 4.76 | F9 | 119.06 | Cust2 | 233.36 |
| F4 | 23.81 | F10 | 138.11 |  |  |
| F5 | 42.86 | F11 | 157.16 |  |  |

**Row 1 — Number (Y = +38.10, seam X = 90.48)**

| key | X | key | X | key | X |
|---|--:|---|--:|---|--:|
| ` | -52.39 | 5 | 42.86 | 0 | 138.11 |
| 1 | -33.34 | 6 | 61.91 | - | 157.16 |
| 2 | -14.29 | 7 | 80.96 | = | 176.21 |
| 3 | 4.76 | 8 | 100.01 | Bksp | 204.79 |
| 4 | 23.81 | 9 | 119.06 | nav-Home | 233.36 |

**Row 2 — QWERTY (Y = +19.05, seam X = 80.97)**

| key | X | key | X | key | X |
|---|--:|---|--:|---|--:|
| Tab | -47.62 | T | 52.39 | P | 147.64 |
| Q | -23.81 | Y | 71.44 | [ | 166.69 |
| W | -4.76 | U | 90.49 | ] | 185.74 |
| E | 14.29 | I | 109.54 | \ | 209.55 |
| R | 33.34 | O | 128.59 | nav-PgUp | 233.36 |

**Row 3 — Home (S = origin) (Y = 0.00, seam X = 85.72)**

| key | X | key | X | key | X |
|---|--:|---|--:|---|--:|
| Caps | -45.24 | G | 57.15 | ; | 152.40 |
| A | -19.05 | H | 76.20 | ' | 171.45 |
| S | 0.00 | J | 95.25 | Enter | 202.41 |
| D | 19.05 | K | 114.30 | nav-PgDn | 233.36 |
| F | 38.10 | L | 133.35 |  |  |

**Row 4 — ZXCV (Y = −19.05, seam X = 95.25)**

| key | X | key | X | key | X |
|---|--:|---|--:|---|--:|
| LShift | -40.48 | B | 66.67 | / | 161.93 |
| Z | -9.53 | N | 85.73 | RShift | 188.12 |
| X | 9.53 | M | 104.78 | Up | 214.31 |
| C | 28.58 | , | 123.83 | nav-End | 233.36 |
| V | 47.62 | . | 142.88 |  |  |

**Row 5 — Bottom (Y = −38.10, seam X = 90.48)**

| key | X | key | X | key | X |
|---|--:|---|--:|---|--:|
| LCtrl | -50.01 | RCmd | 138.11 | Down | 214.31 |
| LOpt | -26.19 | Fn | 157.16 | Right | 233.36 |
| LCmd | -2.38 | RCtrl | 176.21 |  |  |
| Space | 69.06 | Left | 195.26 |  |  |

> **Labels vs positions:** the **positions** above are locked by the 16u grid + standard stagger (and match your 2×2). The **labels** for the right nav column (Home/PgUp/PgDn/End), PrtSc, and the 2 customizable keys are indicative — they're whatever you map in NuPhyIO and don't change where the hole goes. The two custom keys (Cust1 at 214.31, Cust2 at 233.36 = the ex-knob corner) get normal solenoids like everything else.

---

## 6. Mounting walls — screw-in, one per row (×6)

Same wall as the 2×2 (`wall_thickness = 2.5`, `wall_offset = 8` toward +Y of the row, top at Z32, screw holes Ø3.3 at Z11 & Z26 with Ø6 × 1 flat counterbore on the head face, M3 × 3 flat-heads). Now **6 continuous walls — one behind each row** (Function, Number, QWERTY, Home, ZXCV, Bottom).

- Each wall spans its row's X extent (±9 mm past the end keys), broken at the seam.
- Per solenoid: two stacked Ø3.3 holes centered on that key's X (§5), at Z11 and Z26.
- The seam cuts each wall in a key-gap, so **no screw hole is ever split.**
- **Interior-row rule (unchanged from 2×2):** each wall sits in the ~3 mm gap between its row's bodies and the next row's bodies. Keep walls ≤ 2.5 mm and **populate front-to-back** so the flush counterbored heads clear the body behind. CLAUDE.md flagged this as "doesn't scale to interior rows" — it **does** scale as long as you assemble strictly front-to-back and keep every head flush, which is exactly the screw-in method you're keeping.

---

## 7. Legs & tilt (separate, shimmable — unchanged)

- Legs a **separate component**, 4 of them (or front/back rails split at the seam). Bolt to the plate's front/back edges, outside the keyboard's 128.9 mm depth.
- **Start from the 2×2:** front ≈ **23.9**, back ≈ **34.5**, leg span ≈ **140 mm** → ~4.3–4.5° tilt. Reuse, then **shim** to the 1–2 mm ball-to-keycap gap.
- **Nail the tilt over the full depth.** Over ~117 mm a 0.5° error ≈ 1 mm of gap variation front-to-back. Build to the measured ~4.5° keycap tilt; keep legs shimmable.

---

## 8. Print plan (P2S, PLA)

| part | size | orientation | notes |
|---|---|---|---|
| `Plate_Left` | 158.6 × 117.2 mm | flat, walls up | 0.2 / 30% / 4 walls; walls self-support |
| `Plate_Right` | 163.4 × 117.2 mm | flat, walls up | same |
| 4 × legs | small | flat | reprint to re-tilt; shim-tunable |

Both halves clear the 256 mm bed by > 90 mm — lots of room. You could print one half + legs together.

---

## 9. Verified vs open

**Verified (computed):** 84 holes; every hole ≥ 9.52 mm from the seam (no hole cut); both halves < 256 mm; layout reproduces the 2×2 S/D/W/E and stagger exactly; 16u field matches your 318.9 mm case; 41 L / 43 R.

**Open / confirm at the bench:**
- Nav-column / PrtSc / custom-key **labels** (positions are fixed; mapping is in software).
- M3 × 3 flat-head still bites the ~1 mm solenoid tab (carried from the 2×2).
- Tilt over the full depth — set legs to measured ~4.5°, shim.
- Dry-fit the two halves before mounting any solenoid: steps interlock, 4 bridge screws pull flat, all holes line up across the seam.

---

### Files
- `Full_84Key_Hole_Coordinates.csv` — all 84 hole centers (+ row, half, seam X) for CAD import.
- `Layout_Map_84Key_Split.svg` — top-view map: halves colored, stepped seam, walls, legs, origin.

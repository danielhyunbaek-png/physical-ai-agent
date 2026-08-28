# Brief 08 — Groove-sandwich removable walls + deck (Fusion execution)

> ## AMENDED July 27, 2026 — DECK HEIGHT WAS WRONG. Read this box before the table below.
>
> **MEASURED (Daniel, calipers, on a mounted solenoid, from the plate's top face):**
> body top **30mm** → `body_top_z = Z34`, so bodies rest on the plate top and `d = 7mm` exactly.
> Plunger top **50mm** → `plunger_top_z = Z54`. Back-solving that against the ball tip at Z−4 gives a **58mm plunger**, matching the figure recorded as "confirmed" months ago — two independent paths agree.
>
> **Was X:** `deck_underside_z = body_top_z + 8` = **Z42**.
> **Now Y:** `deck_underside_z = plunger_top_z + 4` = **Z58**.
>
> **Why:** the plunger is double-ended. Its upper end — shaft, return spring, clevis — stands **20mm above the body top**, so the tallest at-rest point on the populated plate is Z54, not Z34. Brief 08's rule would have put the deck 12mm *inside* 84 plungers. The caliper gate as originally written measured the wrong feature. (The plunger only travels DOWN when fired, so Z54 at rest is the worst case; no dynamic allowance needed.)
>
> **Knock-on changes, all confirmed with Daniel Jul 27:**
> - **Deck stays overhead** (option 1 of three considered) — boards directly above the keyboard, every lead straight up, per brief 07. A low deck with plunger clearance holes was rejected: the PCBs would still have to clear Z54.
> - `wall_top_z` = **Z60**; walls are now **58mm tall**, with 34mm above the upper tab screw.
> - **Wall is STEPPED, not uniform.** 2.50mm only where it lives in the 16.55mm inter-body slot (below the body tops); **flared to 5.05mm above Z36** for stiffness. A plain 2.5mm × 58mm fin is 23:1 and floppy. The datum rule is unaffected — the flare grows BACKWARD only. Flare back face is limited by the NEXT row's return spring: `hole_y + 19.05 − spring_OD/2 − 1.0`. **`spring_OD` is estimated at 10mm from a photo — MEASURE it.**
> - **Two groove widths now.** Plate groove **2.75** (engages the thin section); deck groove **5.30** (engages the flare). Same datum rule for both: front face at `hole_y + 8` exactly.
> - **Wall-top pads are DELETED and replaced by an insert boss.** A 5mm flare can't hold a Ø4 insert, so a local boss thickens to `datum + 10` — but only in a ~7mm x band that slips between two of the next row's springs (9.05mm gap on 19.05 pitch). Put it anywhere else and it fouls a spring.
> - **No pad pockets in the deck.** Boss top stops at the deck underside (Z58), so the M3×8 passes through the full 4mm slab and gets 4mm into a 6mm insert = 2mm of thread margin. *Brief 08's original pocket left 2mm of deck above the screw AND made an M3×8 bottom out in the insert before its head touched the deck — it would have felt tight while clamping nothing.* Claude implemented the working version after Daniel deferred the decision twice; say so and it reverts.
> - **Deck-to-plate connection: metal M3 male-female standoffs, 54mm BODY length** (plate top Z4 → deck underside Z58), 6 positions (4 corners + 2 at the seam). Chosen over brief 08's printed posts because the length is exact and pickable *after* measurement, and a 54mm printed column would be the weakest thing in the assembly. **Gotcha: the stud must clear plate + washer + nut (~9mm for a 6mm plate) — standard M-F studs are 6mm, so either pocket the nut into the plate underside or use F-F standoffs with an M3×10 up from below.**
>
> ## AMENDED August 2, 2026 — STANDOFF GOTCHA RESOLVED, DECK HEIGHT MOVES AGAIN Z58 → Z64
>
> **Deck-to-plate columns are 60mm, built as a STACK: F-F 20mm (bottom) + M-F 20mm + M-F 20mm.** (Revised three times on Aug 2: single-piece M3×60 F-F → unobtainable; M-F-only kit → would have needed a nut pocket; **mixed F-F/M-F assortment kit → final.**) Standoffs screw into one another and the 6mm stud is consumed inside the next bore, so bodies butt and lengths add exactly — provided every joint is fully seated.
>
> **Starting the stack with an F-F piece puts a FEMALE end at both ends of the column, which deletes the Jul 27 gotcha entirely.** Bottom joint: kit M3×12 up from under the plate, 4mm plate → 8mm engagement into the F-F bore. Top joint: M3×8 flat-head countersunk down through the 4mm deck → 4mm engagement, flush (the column tops sit under the PCB footprint, so a proud pan head would stop a board seating). **No nut, no nut pocket, no CAD feature beyond plain holes + a countersink.**
>
> Two checks at assembly: bodies must butt metal-to-metal (a shallow bore makes the column long, and the six end up uneven), and the M3×12 must not bottom out in the F-F bore before its head clamps — if it does, use M3×8 there too.
>
> **Why 60 and not 54:** 54mm is not achievable from stock pieces, and the service gap above the plungers has to house the +12V bus and its 84 solder taps (brief 07 §3) — which brief 08's original 4mm never accounted for. 60mm gives 10mm and absorbs error in the single-reading plunger measurement.
>
> **Was X:** `deck_underside_z` = **Z58**, `wall_top_z` = **Z60**, walls **58mm**.
> **Now Y:** `deck_underside_z` = plate top (Z4) + 60 = **Z64**, `wall_top_z` = **Z66**, walls **64mm tall**.
>
> Consequences, all benign:
> - Clearance above the plungers (Z54) goes 4mm → **10mm**. More service room for landing 84 wires, and the wire loops get 6mm more slack.
> - The wall aspect ratio worsens 23:1 → 25:1 *at the thin section only*; the flared T-section above Z36 is what actually carries load, and the wall is grooved at BOTH ends (plate and deck), so it is a fixed-fixed column, not a cantilever. The coupon still decides this.
> - Insert boss top moves to Z64. M3×8 through the 4mm deck still gets 4mm of insert bite.
> - **Unchanged:** the datum rule, both groove widths, tab holes at Z11/Z26, plate geometry, and the `plate 4→6mm downward` open question (it moves the plate *bottom*, not the top, so the 60mm standoff still lands at Z64 either way).
>
> **Action before printing: update `wall_top_z` and the post/boss heights in `cad/fusion_groove_coupon.py` and re-run `cad/verify_coupon_geometry.py`.** The 60mm standoff is a purchase; the Z64 is a consequence of it, and the coupon must be cut at the height you're actually going to build.
>
> **Executable version of all of the above: `cad/fusion_groove_coupon.py`**, with `cad/verify_coupon_geometry.py` asserting every invariant (0 failures) and cross-checking against `Air75_84Key_Plate_Left.stl`. `cad/README.md` has the Fusion click-path, slicer orientation, and the test sequence.
>
> **Still open:** whether the plate grows from 4mm to 6mm **downward** (bottom face Z0 → Z−2, legs 2mm shorter) to give the groove a 4mm floor instead of 2mm. Daniel's idea, correct instinct, and the keycap clearance he measured (1–2mm above the caps) makes it affordable. Growing *upward* is impossible — the plate would eat the bottom 2mm of every solenoid body.


**Decision (July 15, 2026, Daniel's design):** the rebuild keeps the proven tab-screw solenoid mount but makes each wall a **separate part**, keyed into **grooves in the plate** (bottom) and **matching grooves in the deck underside** (top). The deck carries both PCBs. **This SUPERSEDES brief 03's drop-in-pocket + clamp-bar scheme** (kept on file as fallback #2, after T-studs). Brief 07's tracks/gates still govern; only the fastening scheme and the CAD work change.

**Deck hold-down (confirmed with Daniel, Jul 15): end posts + wall-top screws.** Firing recoil pushes body → wall → deck straight UP; the deck must be pulled DOWN. 4–6 perimeter posts at the plate ends (outside the keyboard footprint, M3 heat-set inserts) take the main clamp; a thickened pad on each wall top (2–3 per wall, insert + M3 through the deck) stops mid-span deck flex on the ~320mm span.

## Why this scheme works (and what it fixes)

- **Row service without teardown:** unscrew that row's wires from the terminals → remove deck screws → lift deck (needs wire service loops, see below) → lift the wall straight up WITH its solenoids. Screw a fresh solenoid to the wall on the bench — full access, no slot-driving.
- **Assembly is bench-side:** each row is screwed to its wall off the plate (open access — the 2×2's counterbore/assembly-order gymnastics were only needed because walls were fixed). Counterbores stay: flush heads slide vertically past adjacent bodies.
- **Self-alignment:** lowering a wall+row assembly, the dangling plungers enter their Ø10 holes (±2mm slop) before the wall reaches its groove — built-in lead-in.
- **Verified base geometry (FULL cross-check vs `Full_84Key_Hole_Coordinates.csv`, Jul 15):** all 84 Ø10 hole XY positions match the CSV (mean err 0.067mm = tessellation noise); wall mounting faces at hole_y+8 with 0.000 deviation (all 12 walls, both halves — both STLs are modeled in the CSV's coordinate frame); wall thickness 2.5 exact; all 168 tab holes present at key-x ±0.003, Z11/Z26, Ø3.30; plate 4mm; walls Z32. **Two as-built deviations from the written record (as-built wins — 84 solenoids mounted and working): (a) tilt = 4.0° exactly (spec value), not the "~4.5° measured" note — 4.0° is now the validated number; (b) counterbore floor sits 1.0mm from the MOUNTING face (1.5mm deep from the back face), not "1mm from the back face" as the 2×2 notes said.** Hole pattern, tilt, stagger carry over UNTOUCHED.

## Parameters (locked unless marked MEASURE)

| Param | Value | Note |
|---|---|---|
| groove_width | 2.75 | wall 2.5 + 0.25 clearance — **coupon-validate; FDM fit is the #1 risk** |
| groove_depth_plate | 2.0 | into 4mm plate → 2mm floor left; don't go deeper |
| groove_depth_deck | 2.0 | into deck underside |
| groove datum | **wall mounting face = hole_y + 8, exactly** | all clearance goes on the BACK face (groove back at hole_y+10.75). The datum face sets solenoid Y — never center the clearance |
| groove length | wall length + 0.3 | groove ends register the wall in X |
| wall bottom edge | 0.5mm chamfer | insertion lead-in |
| tab holes | Z11 / Z26 absolute, Ø3.3 | UNCHANGED — physics-fixed by plunger rest; grooves don't move them |
| body_top_z | **Z34 — MEASURED Jul 27** | 30mm above the plate top; bodies rest on the plate top, d=7 |
| plunger_top_z | **Z54 — MEASURED Jul 27** | 50mm above the plate top; **this, not body_top_z, drives the deck** |
| ~~deck_underside_z~~ | ~~body_top_z + 8~~ → **plunger_top_z + 4 = Z58** | see the AMENDED box at the top — the old rule collided with 84 plungers |
| wall_top_z | deck_underside_z + groove_depth_deck = **Z60** | wall grows from current Z32; 58mm tall overall |
| wall thickness (lower) | 2.50, below Z36 | must fit the 16.55mm inter-body slot |
| wall thickness (flared) | **5.05, above Z36** | grows BACKWARD only; limited by the next row's spring |
| groove_width (deck) | **5.30** | flare 5.05 + 0.25; distinct from the 2.75 plate groove |
| spring_OD | **MEASURE** (est. 10mm from photo) | sets the flare thickness |
| ~~wall-top pads~~ | **DELETED** → insert boss | see the AMENDED box; boss is 7mm wide × `datum+10` deep, in the spring gap, top at Z58, 1/wall |
| ~~end posts~~ | **DELETED** → metal M3 M-F standoffs, 54mm body | 4 corners + 2 at the seam; exact height, pickable after measurement |
| deck thickness | 4 | matches plate; stiffness comes from the box, not the slab |
| deck wire slots | ~10mm wide, per inter-wall bay, chamfered both edges | exact position from lead-exit caliper gate |
| PCB mounts | **from EasyEDA export** | M3 bosses/standoffs on deck top; do NOT guess coords |
| wire service loops | 60–80mm slack per wire | lets the deck lift/prop without unlanding all 84 |

## Fusion instructions — Stage 1 (do now, nothing gates it)

Work in the existing plate design (source of the uploaded STLs). Do L and R halves identically.

1. **Detach the walls.** Find the extrude feature(s) that create the 6 walls (the `Walls` sketch — remember `wall_thickness` is hardcoded there, not linked to the param). Roll the timeline to just before it. You will reuse this sketch for BOTH the grooves and the new wall parts.
2. **Cut plate grooves.** From the Walls sketch profiles, offset each wall footprint: front line stays at hole_y+8 (datum), back line to hole_y+10.75, ends +0.15 each → Extrude → Cut, 2.0mm down from the plate top. Modify > Change Parameters: add `groove_width=2.75`, `groove_depth=2.0` and wire them in.
3. **New wall components.** Create Component per wall (or one component, 6 occurrences won't work — lengths differ; make 6). Each wall: profile 2.5 × (length), extrude from Z2 (groove floor) up to `wall_top_z` (placeholder Z44 until the caliper gate — leave as a user parameter `wall_top_z`). Re-cut the two tab-hole pairs per solenoid position: Ø3.3 at Z11 and Z26, positions projected from the original wall feature (they're in your existing design — project, don't re-derive). **Counterbores: PROJECT the as-built feature too** — measured floor is 1.0mm from the mounting face (1.5mm deep from the back face), which differs from the 2×2 note; the as-built version is the one holding 168 screws.
4. **Wall-top pads.** On each wall: 3 pads (both ends + middle), 8×8mm bulging to +Y (back) side only, starting above Z34 (safe until measured), through the wall top. Hole: Ø4.0 × 6mm deep, vertical, centered — for M3 heat-set inserts.
5. **Chamfer** the wall bottom edges 0.5mm.
6. **End posts.** On the plate: 12×12mm posts at the 4 outer corners + 2 flanking the seam, from plate top to `deck_underside_z + groove_depth` (same placeholder), Ø4.0×8 insert hole on top, ≥3mm base fillet.
7. **Coupon (print FIRST — this is the teardown gate, brief 07):** model a small section — 2 grooves × ~45mm + 2 short walls with 2 tab-hole pairs + 1 pad each + a mini-deck strip with matching grooves + 2 screws. Print → screw 2 solenoids to a wall on the bench → drop in → fit check (groove clearance, datum face contact, plunger drop) → mini-deck on, screws in → fire both solenoids via the breadboard driver → one full swap cycle (deck off, wall out, swap, back in). **Pass = tear down the old plate. Fail on fit = adjust groove_width ±0.1 and reprint the coupon only.**

## Fusion instructions — Stage 2 (gated: caliper gate + EasyEDA export)

Blocked until (a) body_top_z + lead-exit positions measured (10 min, calipers, on the populated plate before teardown — easier than the 2×2 since all rows exist), and (b) PCB outline + mounting holes exported from EasyEDA.

1. Set `body_top_z` from measurement → `deck_underside_z = body_top_z + 8` → update `wall_top_z` + post heights (parametric, should just recompute).
2. **Deck L/R:** 4mm slab matching each plate half's footprint; underside grooves mirroring the plate grooves (same datum rule, interrupted where wall pads rise — pads pass through clearance pockets, not grooves); Ø3.4 through-holes + counterbores over every pad insert and post insert.
3. **Wire slots:** one per inter-wall bay, positioned from the lead-exit measurements, ~10mm wide, chamfered.
4. **PCB mounts:** M3 bosses at the EasyEDA-exported hole coords, boards oriented terminals toward the wire slots. 12V bus routing under the deck: printed wire clips or channels, one 18AWG drop to each board's 12V terminal.
5. Airflow cutouts in the deck between slots (80mm fan path — thermal risk is documented).

## Assembly sequence (write into the record when executed)

Plate down → 12 wall+row assemblies screwed on the bench (label each wall L1–L6/R1–R6) → drop in, plungers first → posts already on plate → deck on, grooves + pads engage → ~20 M3×8 down through deck → land 84 wires up through slots to terminals (MAP discipline: Sharpie silkscreen box, log `cell · OUT · key`, cut at landing, leave 60–80mm loops) → +12V feeds → Mega + cascade dupont.

## Buy-list delta (ask-first — not edited into the spreadsheet)

M3 heat-set inserts ~45 (36 wall pads + ~6 posts + spares) · M3×8 pan heads ~45 · heat-set tip for the soldering iron (~$10, optional but sanity-saving). EVA foam + clamp-bar hardware from brief 03: NO LONGER NEEDED. Existing M3×3 flat-heads: still used (168, tab screws live on).

## UNVERIFIED

- Groove clearance 0.25 is a guess until the coupon (the whole scheme's risk concentrates here). Now applies to **two** groove widths: 2.75 plate / 5.30 deck.
- ~~body_top_z~~ **MEASURED Jul 27 = Z34.** ~~PCB coords~~ **exported Jul 26: 120×66mm, Ø3.20 M3 at (4,4)(4,62)(116,4)(116,62).**
- **`spring_OD` unmeasured** — estimated 10mm from a photo, and it sets the flare thickness. The coupon tests this clearance physically (Wall_A's flare passes within 1.0mm of Wall_B's spring), but measure it first; if the spring is fatter the flare must shrink.
- Lead exit positions: still unmeasured (sets the deck wire-slot X/Y).
- 58mm-tall walls: printability and stiffness are paper until the coupon. Print them **laid flat**, not upright.
- Standoff stud length vs plate + washer + nut: not yet resolved, and standard M-F studs are too short. See the AMENDED box.
- Plate 4mm→6mm downward: open decision.
- Deck lift-with-wires-landed service flow: paper until tried; the 60–80mm loops are the mitigation.

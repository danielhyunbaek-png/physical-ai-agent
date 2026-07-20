# Brief 08 — Groove-sandwich removable walls + deck (Fusion execution)

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
| body_top_z | **MEASURE (caliper gate)** | ≈Z30–34; sets deck height |
| deck_underside_z | body_top_z + 8 | 8mm for lead exits + service; firm up after gate |
| wall_top_z | deck_underside_z + groove_depth_deck | wall grows from current Z32 |
| wall-top pads | 8×8×6mm bulge, +Y side, above body_top_z | M3 heat-set insert Ø4.0×6 deep, vertical; 3/wall (ends + middle) |
| end posts | ~12×12mm, plate top → deck underside | 4 corners + 2 at the L/R seam; insert on top; post base blends into plate ≥3mm fillet |
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

- Groove clearance 0.25 is a guess until the coupon (the whole scheme's risk concentrates here).
- body_top_z, lead exits: unmeasured.
- PCB coords: not yet exported (Track A).
- Deck lift-with-wires-landed service flow: paper until tried; the 60–80mm loops are the mitigation.

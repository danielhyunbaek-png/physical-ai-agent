# Brief 03 — Full 84-key plate CAD

> **STATUS (July 15, 2026, later): SUPERSEDED AGAIN — the fastening scheme for the rebuild is now brief 08's groove-sandwich removable walls (Daniel's design: keep tab screws, walls drop into plate grooves, captured by the deck).** The drop-in pocket + clamp-bar scheme below is FALLBACK #2 (after T-studs). Still current in this brief: the locked parameters, the three real problems (tilt / per-key positions), the caliper-gate concept, and the print/assembly realities. Earlier history: designed Jul 5 → shelved Jul 7 → revived Jul 13 → superseded Jul 15 by brief 08. Amendments marked **[Jul 15]**.

**Goal:** scale the validated 2×2 design to all 84 keys of the Air75 V3. The hardest carry-over is TILT ACCURACY; the unsolved problem is INTERIOR-ROW FASTENING.

## Locked parameters (validated on prototype — do not re-derive)

`pitch_x=pitch_y=19.05` · `stagger=4.76` (back row LEFT of front; NOT uniform — see below) · `plate_thickness=4` · `plunger_hole_dia=10` · `mount_hole_dia=3.3` (M3 clearance) · `mount_hole_spacing=15` · `lower_hole_z=7` above plate top (upper = 22) · lower-hole→ball-tip-at-rest = 15 · `wall_offset=8` · wall thickness **2.5** (slip-fit into the 3.05mm inter-body gap; 3.0 was an FDM coin-flip) · screws **M3×3 flat-head** + 1mm-deep flat-bottomed counterbore ~Ø6 on the head face · solenoid body 30×16×15, holes on ONE side face, axis parallel to plunger.

Existing artifacts: `Full_84Key_Hole_Coordinates.csv` (per-key positions), `Air75_84Key_Plate_Left.stl` / `_Right.stl` (earlier split-plate drafts — audit against current params before trusting), `Layout_Map_84Key_Split.svg`, `2x2_Prototype_Dimensions.md`.

## The three real problems

1. **Tilt over full depth.** 0.5° error ≈ 1mm gap variation over the ~129mm keyboard depth (vs negligible on the 2×2). Build to the MEASURED ~4.5° keycap tilt (not the 4° spec), and/or make legs shimmable. Feet retracted, always. Model the plate FLAT (holes perpendicular) and realize tilt entirely in the legs/rails.
2. **Interior-row fastening — SOLVED (July 5, 2026, Fable): drop-in pockets + top clamp bars.** Full design below ("Fastening scheme"). Three bench measurements on the in-hand 2×2 gate the final dimensions; a coupon print validates before the full plate.
3. **Per-key positions, not per-row formulas.** 75% staggered layout: arrow cluster and right utility column need explicit positions. Use `Full_84Key_Hole_Coordinates.csv` as source of truth; per-row X offsets are parameters, not assumptions.

## Fastening scheme — drop-in pockets + clamp bars (derived July 5, 2026; validate on coupon)

### Why the 2×2 scheme can't scale (root cause, one sentence)

The fastener axis is horizontal (Y): interior screws must be driven inside the 16.55mm inter-wall slot, which on the full plate is ~320mm long and closed at both ends — no driver fits along the axis — AND swapping an interior solenoid would mean tearing down every row behind it (16 spares exist because burnout is expected). One cause, two symptoms (playbook §3): the horizontal axis. **The fix is to rotate all fastening and insertion from Y to Z** — everything inserts and screws vertically, where access is unlimited and rows become order-independent.

### How each DOF is constrained (per solenoid — no tab screws at all)

- **Y — already solved by existing geometry, zero new parts.** Every body sits between its own wall's mounting face (hole_y+8) and the previous row's wall back face (hole_y−19.05+8+2.5 = hole_y−8.55): slot 16.55, body 16, **0.55 float** — the same slip-fit the 2×2 validated. Only the front-most row (space row, y=−38.1) has no wall ahead → add a **front stub rail**, 2.5 thick, back face at y=−46.65, same height as walls.
- **X — printed ribs on each wall's mounting face**, standing in the inter-body gaps: **CSV-verified July 5: min gap 4.04mm across all 84 keys** → rib 3 wide (X) × 4 deep (−Y) × full wall height, ~0.5/side clearance. End ribs capture the outermost body of each row. Budget check: Ø10 hole vs Ø6 plunger = ±2mm radial; ±0.5 X float + 0.55 Y float + max ~2° yaw all land well inside it. Generate rib X-positions from `Full_84Key_Hole_Coordinates.csv`, same as the holes — never per-row formulas.
- **Z down-stop — seat ledges at wall bases** sized so the lower tab hole lands at the validated Z11 (7 above plate top). Gated on ONE measurement: **d = body-bottom → lower-tab-hole distance. Ledge height = 7 − d.** Feasibility is guaranteed: on the in-hand 2×2 the lower hole sits at Z11 and the body cannot intersect the plate (bottom ≥ Z4), so d ≤ 7 always → ledge ≥ 0. If d = 7 the body seats directly on the plate top and no ledges are needed. Ledges = strips ≤3mm deep at the base of each wall face (front-bottom edge rests on the previous wall's back-face strip; 3mm tips clear the Ø10 holes by ~0.5).
- **+Z recoil retention — clamp bar per row-half.** Firing recoil pushes the body straight up (playbook §2) — this puts the fastener ON the load axis, unlike the old M3-in-~1mm-tab (~2 threads) which carried recoil in its weakest joint. Open question #9 (M3×3 bite) becomes **moot for the 84-key build** — tab screws survive only on the 2×2.

### Clamp bar spec

- Raise walls to clear body tops: **wall top = measured body top + ~2mm** (if d=7, body top ≈ Z34 → walls Z36, i.e. 32 above plate top, was 28).
- **Bosses** at wall ends + every ~60mm: M3 **heat-set inserts**, boss bulges +Y only ABOVE body-top height (below that, the 16.55 slot is exactly full of body).
- **Bar** = flat skeleton strip per row-half (~160mm, matches the L/R plate split; bars can deliberately BRIDGE the seam to tie the halves — free rigidity). Underside: **3mm closed-cell EVA foam tape**, compressed ~1mm onto body tops — absorbs ±0.5 body-height batch variance, damps recoil clatter, avoids rigid preload creep in PLA. M3×8 pan heads, driven vertically from open air.
- Bar needs **lead-exit slots** — **[Jul 15] these are now VERTICAL pass-throughs: both leads route straight UP through/past the bar to the deck (brief 07), not sideways over walls.** Check on bench where coil leads leave the body (caliper gate #3) and size the slots so a landed wire doesn't block bar removal. Plus **airflow cutouts** (thermal risk is documented; 80mm fan planned).
- ~~**+12V wall bus vs bars:** route bus wire below boss height or through printed notches~~ **[Jul 15] SUPERSEDED: the +12V bus moves to the deck (brief 07). Walls carry no bus wire; bars only need lead pass-throughs + airflow.**

### Assembly / service (the payoff)

Rows are fully order-independent. Per row: drop 14–16 bodies straight down into pockets → dress leads → land wires (MAP discipline unchanged: label holes, cut at landing) → foam + bar + 3–5 vertical screws. **Swap any solenoid anywhere: remove that row's bar, lift the body straight up, drop the spare in.** Also deletes all 168 fiddly horizontal M3×3 operations.

### Rejected alternatives (don't re-derive)

- **Scaled 2×2 scheme** (horizontal screws, sequential row order): no driver access inside the slot; no serviceability.
- **T-stud keyhole hang** (M3s pre-set in tabs to a 1.3mm standoff, heads riding open-top T-slots in the walls, slot bottom = Z11 datum): geometrically exact — **keep as FALLBACK if the coupon shows unacceptable slop** — but costs 168 depth-set screws (jig) and ~1.2mm slot webs at the FDM tolerance floor.
- **Bolt-on per-row wall modules:** joints kill pitch accuracy and rigidity.
- **Per-solenoid printed snap clips:** 168 FDM springs → fatigue.
- **Magnets on the steel frame:** coil fields + heat + cost.

### Bench measurements gating CAD (do on the 2×2 BEFORE drawing — calipers, 10 min)

1. **d** = body-bottom → lower-tab-hole → ledge height 7−d.
2. **Body top height** above plate top → wall raise + boss Z + foam crush.
3. **Lead exit points** on the body → bar slot placement.

### Coupon (playbook §6 — must contain the failure mode)

Print a 3-wall × 2-column interior section: exercises sandwich fit, ribs, seat ledges, insert boss, bar preload, AND the vertical swap motion. Fire it with the breadboard driver (**[Jul 15]** cell #1 is parked — use the dry-fit chips on the breadboard, same rig as the Jul 13 fire test). Only then draw the full plate. **[Jul 15] The coupon is also the TEARDOWN GATE: the old tab-screw plate stays fully assembled until the coupon passes swap + fire (brief 07).**

### Spreadsheet impact (NOTE ONLY — ask-first before editing)

Row 39 M3×3 flat-heads: needed for the 2×2 only, qty drops. New: M3 heat-set inserts (~30), M3×8 pan heads (~30), 3mm EVA foam tape roll.

## Print/assembly realities

- Plate footprint ~320×130mm — exceeds most FDM beds; the split-plate (Left/Right) approach exists for this reason. Verify the joint design preserves pitch across the seam.
- Assembly order mattered on the 2×2 (bottom row first) because fastening was horizontal; the drop-in scheme makes rows order-independent. Still write the full assembly sequence BEFORE finalizing geometry — if anything can't be reached vertically, the geometry is wrong.
- Propagate the +4mm hole-height correction everywhere; check Fusion params are actually WIRED to geometry (the 2×2's `wall_thickness` wasn't).
- Print a one-row (or 2×2 interior-scheme) test coupon of the new fastening scheme before committing to the full plate.

## Definition of done

Three bench measurements taken; STL(s) sliceable; dimension doc updated (like `2x2_Prototype_Dimensions.md`); drop-in fastening validated on the coupon (incl. one swap cycle + a fire); assembly sequence written; commit + **git push**.

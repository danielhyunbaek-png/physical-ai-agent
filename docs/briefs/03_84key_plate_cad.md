# Brief 03 — Full 84-key plate CAD

**Goal:** scale the validated 2×2 design to all 84 keys of the Air75 V3. The hardest carry-over is TILT ACCURACY; the unsolved problem is INTERIOR-ROW FASTENING.

## Locked parameters (validated on prototype — do not re-derive)

`pitch_x=pitch_y=19.05` · `stagger=4.76` (back row LEFT of front; NOT uniform — see below) · `plate_thickness=4` · `plunger_hole_dia=10` · `mount_hole_dia=3.3` (M3 clearance) · `mount_hole_spacing=15` · `lower_hole_z=7` above plate top (upper = 22) · lower-hole→ball-tip-at-rest = 15 · `wall_offset=8` · wall thickness **2.5** (slip-fit into the 3.05mm inter-body gap; 3.0 was an FDM coin-flip) · screws **M3×3 flat-head** + 1mm-deep flat-bottomed counterbore ~Ø6 on the head face · solenoid body 30×16×15, holes on ONE side face, axis parallel to plunger.

Existing artifacts: `Full_84Key_Hole_Coordinates.csv` (per-key positions), `Air75_84Key_Plate_Left.stl` / `_Right.stl` (earlier split-plate drafts — audit against current params before trusting), `Layout_Map_84Key_Split.svg`, `2x2_Prototype_Dimensions.md`.

## The three real problems

1. **Tilt over full depth.** 0.5° error ≈ 1mm gap variation over the ~129mm keyboard depth (vs negligible on the 2×2). Build to the MEASURED ~4.5° keycap tilt (not the 4° spec), and/or make legs shimmable. Feet retracted, always. Model the plate FLAT (holes perpendicular) and realize tilt entirely in the legs/rails.
2. **Interior-row fastening.** Wall-per-row does NOT scale inward: screw heads can't fit between rows (the 2×2's flush-counterbore trick works only when the facing row can be dropped in after — with 6 rows you run out of assembly order). Design a top-clamp or pocket scheme for interior rows before drawing anything. This is the open design problem — brainstorm before CAD.
3. **Per-key positions, not per-row formulas.** 75% staggered layout: arrow cluster and right utility column need explicit positions. Use `Full_84Key_Hole_Coordinates.csv` as source of truth; per-row X offsets are parameters, not assumptions.

## Print/assembly realities

- Plate footprint ~320×130mm — exceeds most FDM beds; the split-plate (Left/Right) approach exists for this reason. Verify the joint design preserves pitch across the seam.
- Assembly order matters (learned on the 2×2: bottom row first). Write the full 6-row assembly sequence BEFORE finalizing geometry; if a row can't be reached, the geometry is wrong.
- Propagate the +4mm hole-height correction everywhere; check Fusion params are actually WIRED to geometry (the 2×2's `wall_thickness` wasn't).
- Print a one-row (or 2×2 interior-scheme) test coupon of the new fastening scheme before committing to the full plate.

## Definition of done

STL(s) sliceable; dimension doc updated (like `2x2_Prototype_Dimensions.md`); interior fastening validated on a coupon; assembly sequence written; commit + **git push**.

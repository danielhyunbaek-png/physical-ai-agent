# 2×2 Prototype — Master Dimensions

Quick-reference for the finished one-piece 2×2 prototype (`Prototype_2x2.stl`). All values in mm unless noted. Origin = center of the **S key** plunger hole. X = right, Y = toward keyboard back, Z = up. Plate bottom = Z 0, plate top = Z 4.

## Quick table (simplified names)

| Name | Value | What it is |
|---|---|---|
| `key_pitch` | 19.05 | key-to-key spacing, both axes |
| `stagger` | 4.76 | back row shifted left of front row |
| `tilt` | ~4.28° | plate tilt (back up); was 4°, moving the legs in shrank the leg span |
| `plate_thickness` | 4 | flat plate thickness |
| `plate_size` | 148 × 48 | plate length (Y) × width (X) — trimmed 5mm/end (was 158) |
| `plunger_hole` | Ø10 | plunger clearance hole (4 of them) |
| `screw_hole` | Ø3.3 | M3 clearance in walls (8 total), + Ø6×1 flat counterbore on the head/back face |
| `screw_spacing` | 15 | vertical gap between the 2 screw holes |
| `wall_offset` | 8 | hole center → wall mounting face |
| `wall_thickness` | 2.5 | mounting wall thickness — was 4, thinned off the BACK face for body slip-fit |
| `wall_height` | 28 | wall height above plate top (top at Z 32) |
| `lower_screw_z` | 7 above top (11 above bottom) | lower screw hole height |
| `upper_screw_z` | 22 above top (26 above bottom) | upper screw hole height |
| `front_leg` | 23.9 | front leg height |
| `back_leg` | 34.5 | back leg height (unchanged; tilt now ~4.28° after legs moved in) |
| `leg_gap` | 136 | inner gap between legs — was 146; legs moved in 5mm/side; still clears the 128.9 board |
| `overall_height` | 66.5 | bottom of back leg (Z −34.5) to wall top (Z 32) |

## Plunger holes (Ø10) — center positions (X, Y)

| Key | X | Y |
|---|---|---|
| S | 0 | 0 |
| D | 19.05 | 0 |
| W | −4.76 | 19.05 |
| E | 14.29 | 19.05 |

## Mounting walls

- **Front wall** (holds S, D): mounting face at Y 8, **2.5 thick → back face at Y 10.5** (~0.55 clear of the back body at Y 11.05), spans X −8…27, Z 4…32.
- **Back wall** (holds W, E): mounting face at Y 27.05, **2.5 thick → back face at Y 29.55**, spans X −13…23, Z 4…32.
- Screw holes (Ø3.3) per solenoid: centered on each plunger hole's X, at Z 11 and Z 26 (i.e. 7 and 22 above the plate top), 15 apart. **Each gets a Ø6 × 1 flat counterbore on the back/head face so the M3×3 flat head sits flush** (front-wall holes essential; back-wall optional).

## Legs (fused to plate, one piece)

- **Front leg:** Y −63.5…−57.5, height 23.9 (Z 0 → −23.9). (Moved in 5; was −68.5…−62.5.)
- **Back leg:** Y 78.5…84.5, height 34.5 (Z 0 → −34.5). (Moved in 5; was 83.5…89.5.)
- Inner gap (desk straddle) = 136. Leg spacing (center-to-center) = 142.
- Height difference 10.6 over 142 = ~4.28° tilt (heights unchanged; moving the legs in shrank the span).

## Solenoid (JF-0530B)

- Body 30 × 16 × 15. Plunger Ø6 × 58, 10 stroke.
- Mounting tab ~1 thick (re-measured; was ~1.5), **tapped M3**, 2 holes 15 apart, axis parallel to plunger.
- Lower mount hole → ball tip at rest = 15.
- Ball tip sits ~4 below the plate bottom at rest.
- **Screws: M3×3 FLAT-head** (flat-bottom, M3 thread; was M3×6 cap), seated in the Ø6×1 flat counterbore so the head is flush.

## Keyboard / assembly (Nuphy Air75 V3, feet retracted)

- Keyboard depth straddled = 128.9.
- S key = 54 from the keyboard front edge.
- Keycap height above desk: **S = 23**, **W = 24.5** (→ ~4.5° measured key tilt).
- Resulting ball-to-keycap gap at rest: **~1.5 over S, ~1.3 over W.**
- Leg clearance: ~8.5 in front of and behind the keyboard.

## Notes

- These are the validated values from the printed test-fit cell + the measured solenoid and keyboard. `lower_hole_z` was corrected 3 → 7 (the +4mm fix). `plunger_hole` widened 7 → 10. Screws confirmed M3, not M2.5.
- **June 2026 redesign (from the in-hand 2×2):** wall 4 → 2.5 (body slip-fit), M3×6 cap → M3×3 flat-head + Ø6×1 flat counterbore on the head face, plate 158 → 148 (5/end), legs moved in 5 (straddle 146 → 136, tilt ~4.0 → 4.28°). Assemble bottom row first, then top. No gussets (firing recoil is in-plane). Rationale in CLAUDE.md → "2×2 redesign."
- Open: confirm the M3×3 flat-head bites the ~1mm tab and holds (tip ~0.5 past the tab); FIRE test pending. Leg heights assume ball-4mm-below-plate and 23/24.5 keycap heights — shim-tunable if reality differs.

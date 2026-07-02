# CAD Design Brief — 2×2 Solenoid Mounting Prototype (Fusion 360)

> **Self-contained handoff.** This file has everything needed to model the part in Fusion 360. If you are a fresh assistant with only this file, you have full context — no other files required. All numbers below are measured/confirmed unless marked "placeholder" or "verify."

---

## 1. What we're building and why

This is a small 3D-printed fixture for a hobby project: a "physical AI agent" that presses real keyboard keys using electric solenoids (one solenoid pushes down on one key). The full build has 84 solenoids over a Nuphy Air75 V3 keyboard. **Before** committing to the full 84-key part, we print a small **2×2 prototype** that mounts **4 solenoids over 4 keys** to validate the mounting approach — specifically that it correctly handles the keyboard's **tilt** and **row stagger**.

The owner has a basic Fusion 360 skill level and an FDM (PLA) printer. Keep modeling steps explicit.

**This part's job:** hold 4 solenoids so their plungers rest 1–2 mm above 4 keycaps (keys S, D, W, E) and strike them perpendicular when fired.

---

## 2. The solenoid — JF-0530B (measured & confirmed)

| Property | Value |
|---|---|
| Type | Open-frame linear pull solenoid, 12 VDC, 5 N, 300 mA |
| Body | **30 × 16 × 15 mm** (length × width × height) |
| Plunger | **Ø6 mm**, 58 mm long, **10 mm stroke** |
| Mounting holes | **Tapped M3** (bore measures ~Ø2.5 mm = the M3 tap-drill size; an M2.5 screw spins loose and falls out). **2 holes on ONE side face only**, **15 mm apart (center-to-center)**, hole axis **parallel to the plunger axis**. Tab is only ~1 mm thick (re-measured June; was ~1.5). |
| Lower mounting hole → ball tip, at rest | **15 mm** |
| Actuation | Energize → the **ball-tip end extends** (pushes out). Spring **retracts** the ball end at rest. So: rest = ball retracted (clear of key); fired = ball pushes down onto key. |
| Body depth from mounting face to far side | ~15–16 mm (verify on the part; used for `wall_offset`) |

**Critical mounting consequence:** because the 2 holes are on a side face whose axis is *parallel* to the plunger, the solenoid **cannot bolt flat to a horizontal plate** (that would point the plunger sideways). It must bolt by that side face to a **wall that stands perpendicular to the mounting plate**, with the plunger hanging down through a clearance hole. Mount **ball-tip end downward** toward the key.

Screws (UPDATED June redesign): **M3×3 FLAT-head** (flat-bottom, NOT countersunk; M3 thread — was M3×6 cap), seated in a **Ø6 × 1 mm flat counterbore** on the back/head face of each wall so the head sits flush and clears the back-row body. Wall clearance holes = **Ø3.3 mm**. 2 screws per solenoid. Reach: under-head shank = remaining wall (~1.5 mm after the counterbore; wall now 2.5 mm) + ~1 mm tab ≈ 2.5 mm → M3×3 (tip ~0.5 mm past the tab). Engagement ~1 mm (~2 threads) — snug, don't over-torque; threadlocker helps. **Confirm the M3×3 bites and holds at assembly.**

---

## 3. The keyboard — Nuphy Air75 V3 (spec + measured)

| Property | Value |
|---|---|
| Layout | ANSI 75%, 84 keys, low-profile |
| Key pitch (both axes) | **19.05 mm** |
| Tilt (typing angle, feet RETRACTED) | **4°** (build is always run with feet retracted) |
| Row stagger | Back row sits **4.76 mm LEFT** of the front row (standard 0.25u; measured ~5 mm) |
| Front-row keycap top above desk | **~18 mm placeholder** — only sets starting leg height; final gap is tuned with shims |

The 4 target keys form a 2×2 block: front row **S, D**; back row **W, E** (the two keys behind S, D). Because of stagger, W/E are shifted 4.76 mm left of S/D. Because of tilt, the back row keycaps sit higher.

---

## 4. Design architecture (decided — build this)

A single **flat plate, tilted 4°** so it sits parallel to the keycap plane. Tilting the whole plate means every key has the same gap — the tilt is handled **once**, not per row. This is the chosen approach over per-row height steps.

- **Plunger holes:** four Ø7 mm through-holes in a 2×2 grid; back pair shifted 4.76 mm left (stagger). Holes are perpendicular to the plate → perpendicular to the keycaps → plungers strike straight in.
- **Mounting walls:** two short walls stand up **perpendicular to the plate** (one behind the front-row holes, one behind the back-row holes). Each solenoid bolts to its wall by the side face; body stands up, plunger hangs down through its hole. (A per-solenoid "ear" is equivalent — a continuous wall per row is simpler.)
- **Legs:** two side legs hold the plate at the 4° tilt and at the right height, resting on the desk straddling the keyboard. Legs are a **separate body/component** so they can be reprinted or shimmed to dial in the 1–2 mm gap.

**Modeling tip:** model the plate, holes, and walls **flat** (in the plate's own plane). The 4° tilt is realized by the legs (back taller than front). This keeps the plunger holes automatically perpendicular to the plate, hence to the keycaps.

---

## 5. Layout / coordinates

Origin at the front-left plunger hole (key S). X = right, Y = toward the back of the keyboard.

| Hole | Key | X (mm) | Y (mm) |
|---|---|---|---|
| 1 | S | 0 | 0 |
| 2 | D | 19.05 | 0 |
| 3 | W | −4.76 | 19.05 |
| 4 | E | 14.29 | 19.05 |

(W = −stagger; E = pitch_x − stagger.)

---

## 6. Fusion 360 parameters (Modify → Change Parameters → User Parameters)

```
pitch_x              mm     19.05
pitch_y              mm     19.05
stagger              mm     4.76      // back row shifts -X (left)
tilt_angle           deg    4
plate_thickness      mm     4
plunger_hole_dia     mm     10        // UPDATED (was 7): Ø7 cleared the ball but not the screw/nut above it; Ø10 clears that. Ø6 plunger now has slop.
mount_hole_dia       mm     3.3       // UPDATED (was 2.7): clearance for M3. Holes are tapped M3, not M2.5.
mount_hole_spacing   mm     15        // measured; vertical spacing on the wall
wall_offset          mm     8         // hole center -> mounting-wall face. VALIDATED at test-fit (solenoid seats, ball drops centered).
wall_thickness       mm     4
lower_hole_z         mm     7         // UPDATED (was 3): lower screw-hole height above plate top. +4mm test-fit correction (solenoid sits flush with plate BOTTOM, plate is 4mm).
wall_height          mm     24        // note: in the test-fit model the wall extrude nets ~28mm tall above the plate top so the upper hole (lower_hole_z+15=22) has ~6mm margin
leg_height_front     mm     28        // placeholder; shim to set the 1-2mm gap
```

> **June 2026 redesign update (supersedes values above):** `wall_thickness` is now **2.5** (was 4) — thinned off the BACK face for the body slip-fit; it's a hardcoded dimension in the `Walls` sketch (the parameter wasn't wired to the geometry). Screw holes get a **Ø6 × 1 mm flat counterbore** on the head face for M3×3 flat-heads. Plate trimmed to **148 mm**; legs moved in 5 mm (straddle 136, tilt ~4.28°). Full rationale in CLAUDE.md → "2×2 redesign."

> **Test-fit correction (June 2026):** The first print's screw holes were 4mm too low and didn't line up with the solenoid. The solenoid's rest position is fixed by physics (plunger dropped through the hole); the wall holes must be placed to match it. The holes line up when the solenoid body is flush with the plate BOTTOM — and since the plate is 4mm thick, both holes (the rigid 15mm pair) shift UP 4mm: `lower_hole_z` 3 → 7. Moving the holes does NOT move the ball. Validated with a real solenoid: frame seats flat on the wall, ball-tip-down drops cleanly through the Ø10 hole and protrudes below the plate.

### Vertical-stack relationship (perpendicular to the plate)
With `lower_hole_z = 3`, a 4 mm plate, and the measured 15 mm (lower-hole→tip at rest), the ball hangs **~8 mm below the plate bottom at rest** (15 − 3 − 4). The keycap stops the plunger well before it bottoms out (only ~3 mm of travel is used: 1–2 mm gap + 1.4 mm switch actuation). Plate bottom should clear the keys by `desired_gap + 8 mm` ≈ 9.5 mm. Raise `lower_hole_z` if you want the ball to hang less.

---

## 7. Modeling steps

**A. Plate** — Sketch the plate rectangle on XY and extrude `plate_thickness`. Final size **148 × 48 mm** (length Y × width X; trimmed 5 mm/end from the original 158). Holes are origin-anchored, so trimming the ends doesn't move them.

**B. Plunger holes** — New sketch on top face; four circles Ø `plunger_hole_dia` at the coordinates in §5; extrude-**cut** "All" through the plate.

**C. Mounting walls** — Sketch a rectangle `wall_thickness` deep, offset +Y by `wall_offset` from the S–D line (front wall) and another offset `wall_offset` from the W–E line (back wall), each spanning past both keys in X; extrude up by `wall_height`. On each wall face, sketch screw holes Ø `mount_hole_dia`: two stacked per solenoid at heights `lower_hole_z` and `lower_hole_z + mount_hole_spacing`, centered in X on that solenoid's plunger hole (front wall = S, D; back wall = W, E). Extrude-cut through the wall. **Then add a flat counterbore on the BACK/head face of each screw hole — Ø6 × 1 mm deep — so the M3×3 flat heads sit flush and clear the back-row body** (wall is now 2.5 mm, not 4).

**D. Legs** — Two legs under the left/right plate edges, back edge taller than front so the plate tilts `tilt_angle`. Height difference = `tan(tilt_angle) × front-to-back span` (~3.5 mm over a 50 mm span). Make legs a **separate component**. **June redesign: legs sit flush with the trimmed 148 mm plate ends (moved in 5 mm each → straddle 136 mm, leg spacing 142 mm, tilt ~4.28°); leg heights unchanged (23.9 / 34.5).**

**E. Test-fit cell FIRST** — Before printing the full part, isolate **one** plunger hole + its piece of wall (with 2 screw holes) and print just that. Mount one real solenoid: confirm the side face sits flush, M2.5 screws bite, and the plunger drops through the Ø7 hole **centered**. This validates `wall_offset` (my best estimate is half the body depth ≈ 8 mm). Adjust parameters, then export the full 2×2.

**F. Export** — Body → Save As Mesh → STL, High refinement.

---

## 8. Print settings (PLA)

0.2 mm layer, 30 % infill, 4 walls (perimeters). Plate flat on the bed, mounting walls pointing up (self-supporting, no supports). Legs printed separately, flat.

---

## 9. Constraints, gotchas, success criteria

- **Plunger must strike perpendicular to the keycaps** — guaranteed if holes are normal to the (tilted) plate. Don't make the plate flat-on-the-desk; it must tilt with the keyboard.
- **Mount ball-tip end down.** Spring holds it retracted at rest (the gap); energizing pushes it onto the key.
- **PLA strips easily** — snug the M3×3 flat-head screws, don't crank; threadlocker helps. (The thread is in the solenoid's metal tab, not PLA, so heat-set inserts don't apply here.)
- **The front wall sits in a ~3 mm gap between rows** — between the two solenoid bodies (3.05 mm). It must be ≤2.5 mm (gives ~0.55 mm slip-fit; 4 mm interferes), and the screw heads on the gap-facing face MUST be counterbored flush or they foul the back body. Screw the bottom row first, then the top. **No gussets** — firing recoil is straight up (the wall's stiff in-plane direction).
- **wall_offset is the one estimated dimension** — confirm via the §7-E test-fit before printing the full plate.
- **Bodies at 19.05 mm pitch:** body is ~15–16 mm across, leaving ~3–4 mm between neighbors. Tight but fits; check clearance in the model.

**CAD is successful when:** the printed part accepts all 4 solenoids flush on the walls, all 4 plungers drop centered through their holes, and (with the legs shimmed) all four ball tips rest an even 1–2 mm above S, D, W, E. The downstream electrical/typing test (FIRE the solenoids to type "sdwe") is covered in the separate Week-3 plan and is not part of the CAD work.

---

## 10. Open / to-verify (non-blocking)

- `wall_offset` (8 mm) — **VALIDATED at test-fit:** solenoid seats flat, ball drops centered through the Ø10 hole.
- **M3 thread engagement in the ~1 mm tab:** committed screw is now **M3×3 flat-head** (June redesign); ~1 mm / ~2-thread engagement, tip ~0.5 mm past the tab. Confirm it bites and holds at assembly.
- Body depth from mounting face (15 vs 16 mm) — confirm which cross-dimension is perpendicular to the hole face; feeds `wall_offset`.
- Front-row keycap height (~18 mm placeholder) — tuned physically with leg shims, so exactness isn't required for the model.
- Full-matrix (Week 4) note: 84-key version will need this same tilted-plate idea scaled up, with multiple mounting walls (one per keyboard row); the prototype is the de-risk for that.

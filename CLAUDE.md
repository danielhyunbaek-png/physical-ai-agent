# Physical AI Agent — Project Context

## Project overview

12-week summer build of a physical AI agent that types on a real keyboard and moves a real mouse, observed by a webcam. The agent runs on a MacBook Pro M4 and controls a Nuphy Air75 V3 keyboard (84 keys, Blush Nano linear switches) via an 84-solenoid matrix mounted above the keyboard. A second subsystem (Wave 2) is a Cartesian XY gantry that moves a Logitech B100 mouse, with SG90 servos for L/R click. Vision via a Logitech C920 webcam with template matching + OCR.

Budget ceiling: $1,500. Current estimate: ~$1,366.

## Key files in this folder

- `PRD_v2_Physical_AI_Agent.docx` — Product Requirements Document. Source of truth for *what* and *why*.
- `Build_Walkthrough_Physical_AI_Agent.docx` — Week-by-week operational guide. Source of truth for *how* and *when*.
- `Wave_1_Order_Checklist.xlsx` — Parts spreadsheet with audit trail. Wave 1 (essentials, order now), Wave 2 (deferred to Week 6), Tools, Optional. Audit Trail tab maps every line back to PRD/walkthrough.
- `CLAUDE.md` (this file) — Conversational context and design decisions accumulated across sessions.
- `Week3_2x2_Prototype_Plan.md` — Step-by-step Week 3 prototype plan (2×2 tilted plate). Supersedes the earlier single-row/4×4 plan, which was deleted.
- `CAD_Design_Brief_2x2_Prototype.md` — Self-contained CAD spec for the 2×2 mounting plate: every dimension, parameter, and modeling step needed to do the Fusion 360 work in a fresh session with no other context.
- `2x2_Prototype_Dimensions.md` — Master dimension reference for the finished one-piece 2×2 prototype (`Prototype_2x2.stl`): simplified names + exact values for keys, plate, walls, screw holes, legs, solenoid, and keyboard fit. Use this when asked for any 2×2 dimension.

## Owner

Daniel. Comfortable with basic Python and basic Arduino, beginner CAD, owns an FDM 3D printer.

---

## Design decisions made (with rationale)

### Solenoid choice: JF-0530B, 5N / 10mm (big-solenoid plan) — PART RECEIVED & MEASURED

- DC 12V, 5N peak force, 10mm stroke, 300mA holding current.
- Body: 30×16×15mm (confirmed). Plunger: Ø6×58mm steel, 10mm stroke (confirmed).
- **Actuation (bench-confirmed): it's a PULL solenoid with a double-ended plunger. Energizing makes the BALL-TIP end extend (a push); the return spring retracts that end at rest. → Mount ball-tip-DOWN: rest = plunger clear of key, fired = plunger presses key. The ball tip is also the key-contact point (gets the silicone tip).**
- Qty 100 ordered (84 in matrix + 16 spares for DOA/burnout/test rig).
- Source: AliExpress/Alibaba bulk at ~$3.50/unit.
- Risks documented in spreadsheet's "Build Notes" tab: heavier plunger adds ~3–4ms latency, switch wear from higher kinetic energy, ±20–25% force variance across bulk batch, thermal under PRD §7 endurance test, build tolerance on 19mm key pitch.
- Mitigations in place: silicone tubing on plungers, 30 spare Blush Nano switches (up from 8), 80mm USB fan, 4-unit fast-ship prototype kit for early validation.

### Solenoid mounting holes: tapped **M3** (NOT M2.5, NOT M2) — corrected at test-fit

- **CORRECTED (test-fit print, June 2026): the mounting holes are tapped M3, not M2.5.** Earlier the holes were measured as "2.5mm dia" and assumed M2.5 — but 2.5mm is exactly the M3 tap-drill (minor) diameter. Bench test: an M2.5 screw "looks like it threads" but spins loose and falls out, because its 2.5mm major diameter only kisses the M3 thread crests and never engages. **Use M3 screws.**
- **Screw length: M3 × 6mm.** The wall is 4mm PLA + the solenoid's mounting tab is only ~1.5mm thick → screw spans ~5.5mm. Do NOT use 8mm (would jut ~2.5mm past the tab into the solenoid frame and foul it). 5mm only catches ~1mm of the tab (too little). 6mm is the sweet spot. **→ SUPERSEDED in the June redesign: now M3×3 flat-head + flush counterbore + 2.5mm wall — see "2×2 redesign — fit + fastening fixes" below.**
- **Thin tab caveat:** thread engagement is limited by the ~1.5mm tab thickness (~3 threads of M3) — marginal but fine for a ~30g solenoid with light side loads. Don't over-torque; threadlocker optional. (Heat-set inserts do NOT help here — the thread is in the metal tab, not the PLA.)
- Wall clearance holes for the screw shaft: **Ø3.3mm** (`mount_hole_dia`), so the M3 passes through the wall and threads into the tab. No nut needed when the tab is tapped.
- **CONFIRMED on the part: 2 holes on ONE side face only (not both), 15mm apart center-to-center. So 2 screws per solenoid × 84 = 168 total.**
- **CRITICAL — mounting orientation discovery:** the 2 holes' axis is PARALLEL to the plunger. So the solenoid CANNOT bolt flat to a horizontal plate (that would point the plunger sideways). It must bolt by its side face to a wall standing PERPENDICULAR to the plate, with the plunger hanging through a clearance hole. This drove the tilted-plate + mounting-wall design (see next subsection). Also measured: lower mounting hole → ball tip at rest = 15mm.
- **M3 bite CONFIRMED (June 11, 2026)** — screws thread firmly into the tab and hold. **TODO when ordering:** update spreadsheet row 39 hardware to **M3×3 flat-head** (was M2 → M2.5 → M3×6 cap → now M3×3 flat-head + counterbore; see June redesign) and refresh the search link. (Spreadsheet NOT yet edited — per "ask first" rule.)

### Test-fit cell — printed & validated (June 2026)

Single-cell test print (one Ø10 plunger hole + one perpendicular mounting wall + two M3 screw holes) done to de-risk the mount before the full 2×2. Modeled in Fusion via the live connector; STL at `TestFitCell.stl`. **Results:**

- **Plunger hole widened Ø7 → Ø10mm** (`plunger_hole_dia=10`). The Ø7 cleared the ball tip but NOT the screw/nut feature just above the ball that also travels through the hole. Ø10 clears it. (Trade-off: the Ø6 plunger now has ~2mm slop, so the hole no longer guides it; acceptable for the fit test, silicone tubing helps. A stepped hole — wide bottom, Ø7 top — could restore guidance later.)
- **Screw holes → M3 clearance Ø3.3mm** (see above).
- **Hole height corrected UP by 4mm → `lower_hole_z` 3 → 7mm** (above the plate top; upper hole = `lower_hole_z + mount_hole_spacing` = 22mm). First print's holes were 4mm too low and didn't line up with the solenoid's holes. Cause: the solenoid sits 4mm higher than the original model assumed — its mounting holes line up when the solenoid body sits flush with the plate BOTTOM, and the plate is 4mm thick. **Key insight: the ball/solenoid rest position is fixed by physics (plunger dropped through the hole); the wall holes must be placed to match it — moving the holes does NOT move the ball.** Fix = shift BOTH holes (the rigid 15mm pair) up 4mm and lengthen the wall to contain the upper hole.
- **Wall lengthened** so the upper hole (22mm above plate top) has material around it; ~6mm margin above it.
- **Validated with a real solenoid (photos on file):** frame seats flat against the wall, ball-tip-down, ball drops cleanly through the Ø10 hole and protrudes below the plate at rest, and the two M3 holes line up. → **`wall_offset≈8mm` is good** (open question #8 resolved). Still to physically confirm: that an M3 screw actually threads into the 1.5mm tab and holds (alignment is confirmed; fastening not yet).
- **For the full 84-key plate:** reuse `lower_hole_z=7` and `plunger_hole_dia=10`; the +4mm correction must propagate to all 84 positions.

### Structural mounting: SIDE RAILS (not standoffs, not full encasement)

**Decision: two parallel 3D-printed PLA walls running along the long axis of the keyboard, with the matrix plate spanning between them as a removable lid.**

Rejected alternatives:
- **4 M5 standoffs (original PRD spec):** low rigidity, awkward differential heights to match keyboard tilt, lots of swap-test iteration.
- **Full 4-walled encasement:** most rigid but print size is brutal (320×130mm footprint × tall walls = 6–8 sub-parts joined with dowels, 30–40hr print time, heat trap, keyboard inaccessible for switch swaps).

Why side rails win:
- Tilt baked into wall geometry (front edge of walls shorter than back edge) — no differential standoffs needed.
- Much better rigidity than 4 standoffs.
- Only 2 wall pieces to print (vs 4 for full encasement).
- Sides of keyboard remain open → switch-swap access, airflow, debug visibility.
- Matrix plate stays removable for full keyboard access from above.

**Implication for Wave 1 order:**
- **Row 40 (M5 standoffs): SKIP.** Side rails replace this entirely.
- M5 SCREWS still needed (different part) — to attach matrix plate to side rails (top), side rails to base board (bottom), and for all Wave 2 V-slot gantry hardware. Buying the 260pc M5 screw assortment kit covers all of this.

### Mounting refinement: TILTED FLAT PLATE + perpendicular mounting walls

Because the JF-0530B's holes are on a side face (parallel to the plunger), solenoids bolt to walls that stand perpendicular to the plate, not to the plate's flat surface. The architecture:

- **One flat plate, tilted to match the keycap plane (4°).** Tilting the whole plate means every row has the same plunger gap — tilt is solved ONCE, not per row. (This is the right way to scale the side-rail idea to all 5 rows.)
- Plunger holes are perpendicular to the plate → perpendicular to the keycaps → plungers strike straight in. Model the plate FLAT (holes vertical) and let the legs/rails create the tilt, so perpendicularity is automatic.
- **Mounting walls** stand up perpendicular to the plate (one per keyboard row) — solenoids bolt to them by the side face, bodies up, plungers down through the holes.
- **Stagger is separate from tilt:** tilting fixes the front/back height difference but NOT the left/right row offset. Per-row X offset (stagger) must still be modeled.
- Plate height set by legs/rails, then shimmed for the 1–2mm gap.

### Keyboard tilt: must be modeled in CAD

- Nuphy Air75 V3 has ~4° case angle even with feet retracted (more if feet extended).
- Across 130mm keyboard depth → ~9mm vertical difference between front and back rows.
- A flat plate over a tilted keyboard would make front row gap ~10mm (too far) and back row gap ~0mm (false-triggers).
- **Fix:** side rails have built-in 4° tilt — back edge taller than front edge — so the matrix plate sits parallel to the keycap plane.
- **Always run the build with the keyboard's flip-out feet RETRACTED** to minimize tilt to just the case angle.
- **CONFIRMED from Air75 V3 spec: tilt = 4° ("Type Angle" base, feet retracted). Key pitch = 19.05mm both axes. Row stagger = 4.76mm (standard 0.25u), back row LEFT of front. `tilt_angle=4` locked.**

### Solenoid stroke trimming

- Big solenoid has 10mm stroke; only ~3mm is the minimum useful travel (1–2mm air gap + 1.4mm Blush Nano actuation distance + margin). **MEASURED on the prototype: the key bottoms out at ~5mm of ball-tip travel, leaving ~5mm buffer — fine by design (see "2×2 redesign" below).**
- Plate is positioned so the keycap mechanically limits plunger extension — effectively "trimming" the stroke to the useful range.
- Remaining ~7mm is overtravel buffer; never let plunger fully extend at rest.

### PSU choice: BOSYTRO 480W 40A 12V ($33)

- Picked over Meishile S-600-12 600W 50A ($28) because BOSYTRO bundles the IEC C13 mains cord; Meishile doesn't.
- Tradeoff: less headroom (40A vs 50A) and only 20 reviews (vs 446). Acceptable because realistic peak load is ~25A (7 keys simultaneous × 300mA + transients).
- **TODO when marking ordered:** mark spreadsheet row 33 "Ordered" AND row 34 (IEC cord) "Skip" (bundled with PSU).

### 2×2 redesign — fit + fastening fixes (June 2026, from the in-hand prototype)

Printed the 2×2, test-fit the solenoids, found two coupled problems, and redesigned. Values here supersede earlier ones; `2x2_Prototype_Dimensions.md` and the CAD brief are updated to match.

- **The problem (read off the model):** the front (bottom-row) wall sits in the 3.05mm gap between the two solenoid bodies (front body ends Y8, back body starts Y11.05). At `wall_thickness=4` the wall overran that gap by ~1mm, AND the bottom-row screws drive from the back face so their heads pointed into the back body → the bottom row couldn't be fastened (the top row, screwing into open space, was fine). One cause, both symptoms.
- **Wall 4 → 2.5mm.** Material comes off the BACK face only (the wall is anchored at its mounting face via `wall_offset=8`, so the mounting face — and the 19.05 pitch — don't move). 2.5mm gives ~0.55mm slip-fit to the back body; 3mm was too tight (0.05mm — an FDM coin-flip). Inter-wall clear gap = 16.55mm. **Gotcha: `wall_thickness` was never wired to the geometry — the thickness is a hardcoded dimension in the `Walls` sketch, so it must be changed there (and re-linked to the param).**
- **Screws: M3×6 cap → M3×3 FLAT-head** (flat-bottom, NOT countersunk) + a **flat-bottomed counterbore** at each hole on the BACK/head face (1mm deep, ~Ø6 = head dia + 0.4, leaving ~1.5mm wall) so the head sits flush and clears the back body. Reach: under-head shank = remaining wall (1.5) + tab (re-measured ~1mm, was 1.5) ≈ 2.5 → M3×3 (tip sits ~0.5mm past the tab; verify nothing's behind it). Flat-head length is measured under-head, so the 1mm head adds no reach. Counterbore must be a FLAT pocket, not a cone. **Still M3 thread (not M2.5).**
- **Bottom-row assembly order:** screw the bottom (front) row FIRST, then drop in the top (back) row — the flush heads then clear and the back body seats. (Chosen over flipping the row or a top hold-down bar.)
- **Gussets: NOT needed.** The firing recoil pushes the body straight UP (+Z), the wall's stiff in-plane direction, so a 2.5mm wall is fine. (Reversed an earlier "add gussets" call once the load direction was clear.)
- **Plate trimmed 5mm per end: 158 → 148mm** (ends now Y84.5 / Y-63.5). Holes are origin-anchored so they don't move. **Legs moved in 5mm each** to stay flush with the new ends; leg HEIGHTS unchanged (front 23.9, back 34.5). Straddle inner gap 146 → 136mm (still clears the 128.9mm keyboard, ~3.5mm/side); leg spacing 152 → 142mm, so tilt drifts 4.0° → ~4.28° — negligible over 2 rows (~0.09mm) and actually nearer the measured ~4.5° keycap tilt.
- **Stroke check (supersedes "~3mm useful"):** the key bottoms out at ~5mm of ball-tip travel, leaving ~5mm buffer. Fine by design — the keycap limits the plunger, the buffer prevents missed presses, and for this pull solenoid force is weakest at the start of extension / strongest near seat, so bottoming at 5mm is well up the force curve. FIRE test still pending to confirm reliable presses.
- **For the final 84-key plate:** the per-key mounting height (`lower_hole_z=7`, ball ~4mm below plate) carries over directly. Legs scale up. The TILT is the thing to NAIL over the full ~129mm depth — a 0.5° error there is ~1mm of gap variation (vs negligible over 2 rows), so build the final plate to the measured ~4.5° (or make legs shimmable). Wall-per-row still doesn't scale to interior rows (heads can't fit between rows) — those need a top-clamp/pocket scheme.

---

## Pipeline of upcoming CAD work (Week 3)

**Authoritative, self-contained CAD spec: `CAD_Design_Brief_2x2_Prototype.md`.** That file has the full parameter table, coordinates, and modeling steps. Summary below.

**Prototype scope: 2×2 (not the walkthrough's flat 4×4).** Decided to test 4 solenoids over a 2×2 key block (front S, D / back W, E) so the prototype also exercises tilt AND stagger — the two hardest parts of the full build — not just "does a solenoid press a key." Tilt within a single row is zero, so a single-row test would have skipped it; the 2×2 forces a two-row, tilted, staggered mount.

**Key confirmed parameters** (full list in the brief): `pitch_x=pitch_y=19.05`, `stagger=4.76` (back row left), `tilt_angle=4`, `plate_thickness=4`, `plunger_hole_dia=10` (was 7 — widened to clear the screw/nut under the ball), `mount_hole_dia=3.3` (M3 clearance — was 2.7/M2.5), `mount_hole_spacing=15`, `lower_hole_z=7` (above plate top — was 3; +4mm test-fit correction), lower-hole→ball-tip-at-rest `=15`. `wall_offset=8` (VALIDATED at test-fit). Solenoid body 30×16×15 confirmed.

**Approach:** flat plate modeled in its own plane (holes perpendicular → strike keys straight in), tilt realized by legs (back taller than front); two perpendicular mounting walls (one per row) for the side-hole solenoids; legs separate/shimmable for the 1–2mm gap. **Print a single test-fit cell FIRST** (one hole + wall) to validate `wall_offset` before the full 2×2.

**Per-row offsets:** Air75 V3 is a staggered 75% layout — back-row X shifts 4.76mm left of front. For the full 84-key plate (Week 4): arrow cluster and right utility column need explicit per-key positions; per-row X offsets are CAD parameters, not assumed uniform.

---

## Open questions — status

1. Solenoid body dimensions — **RESOLVED: 30×16×15mm confirmed.**
2. Mounting tabs — **RESOLVED: 2 holes on ONE side face only.**
3. Mounting hole spacing — **RESOLVED: 15mm center-to-center.**
4. Plunger extension at rest — **RESOLVED: lower hole → ball tip at rest = 15mm; ball extends on energize (push).**
5. Plunger spring rate / resting force — still open (assess during prototype assembly; informs whether silicone tubing is enough damping).
6. Keyboard tilt angle — **RESOLVED: 4° (spec, feet retracted).**
7. Keycap height above desk (with VHB) — rough placeholder ~18mm; not blocking (gap is shimmed). Still worth a clean measurement at assembly.
8. `wall_offset` (8mm, half body depth) — **RESOLVED: validated at the test-fit print — solenoid seats flat and the ball drops centered through the Ø10 hole.**
9. Screw thread engagement in the tapped tab — **RESOLVED June 11, 2026 (M3 bites & holds). UPDATED in the June redesign: committed screw is now M3×3 flat-head (not M3×6 cap); tab re-measured ~1mm → ~1mm / ~2-thread engagement. Confirm the M3×3 holds at assembly.**
10. Mounting hole size/thread — **RESOLVED: tapped M3 (not M2.5). Wall clearance Ø3.3.**

---

## Workflow notes

- User says "ask first" before making sweeping spreadsheet changes — single-cell edits get confirmed before being applied.
- User prefers concise answers. Skip token-burning preambles.
- When user makes a sharp observation that contradicts something I said, acknowledge it and re-explain honestly rather than glossing over.
- Always cite spreadsheet row numbers and document sections when discussing the build.

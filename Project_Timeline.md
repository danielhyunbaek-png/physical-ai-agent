# Physical AI Agent — Project Timeline

*The history of this build: every phase, mistake, dead end, and fix. Current-state truth lives in `CLAUDE.md` and the live docs; this file is the story of how it got there. Files retired during the July 1, 2026 folder cleanup are summarized here — their full contents are recoverable from git commit `84a796c` ("Pre-cleanup snapshot").*

---

## Phase 0 — Planning (May 2026)

- **PRD v2 + Build Walkthrough written.** 12-week summer build: a physical AI agent that types on a real Nuphy Air75 V3 (84 solenoids) and moves a real Logitech B100 mouse (Wave 2 XY gantry), watched by a C920 webcam. Budget ceiling $1,500; estimate settled around ~$1,366.
- Original spec that later died: **4× M5 standoffs** for plate mounting, and a **flat single-row/4×4 prototype**. Both superseded (see Phases 2–3).

## Phase 1 — Parts selection (May–June 2026)

- **Solenoid: JF-0530B, 12V 5N/10mm, ×100** (~$3.50/u bulk) — 84 + 16 spares. Risks logged upfront: plunger mass latency (~3–4ms), switch wear, ±20–25% force variance across the batch, thermal under endurance. Mitigations: silicone tips, 30 spare switches, USB fan, 4-unit fast-ship kit for early validation.
- **PSU: BOSYTRO 480W 40A 12V ($33)** over the cheaper Meishile 600W — BOSYTRO bundles the IEC cord. Realistic peak ~25A, so 40A is enough headroom.
- **M5 standoffs (spreadsheet row 40): skipped** — replaced by the side-rail architecture before ever being ordered.

## Phase 2 — Solenoid reality check (June 2026)

The part in hand rewrote the mounting design:

- **It's a PULL solenoid with a double-ended plunger.** Energize → ball-tip end extends. So: mount ball-tip-DOWN; rest = clear of key, fired = presses key.
- **Mounting holes are on ONE side face, axis parallel to the plunger** → the solenoid physically cannot bolt flat to a horizontal plate. This single discovery drove the whole architecture: **tilted flat plate + perpendicular mounting walls** (one per row), solenoids bolted by their side faces, plungers hanging through Ø holes.
- **Mistake: assumed the tapped holes were M2.5** because they measured 2.5mm — but 2.5mm is exactly the M3 tap-drill diameter. An M2.5 screw "threads" but spins loose (its crests only kiss the M3 valleys). **Fix: M3.** Confirmed biting June 11.
- **Test-fit cell print — three corrections in one coupon:**
  - Plunger hole **Ø7 → Ø10**: the Ø7 cleared the ball but not the screw/nut feature above it that also travels through the hole.
  - **Holes 4mm too low** (`lower_hole_z` 3 → 7): the solenoid seats flush with the plate *bottom*, 4mm higher than modeled. Lesson: **the ball's rest position is fixed by physics; the wall holes must chase it — moving holes doesn't move the ball.**
  - Wall lengthened to contain the raised upper hole.
- `wall_offset=8` validated: frame seats flat, ball drops centered.
- Structural decision: **side rails** beat 4 standoffs (rigidity, tilt baked into geometry) and full encasement (30–40h of printing, heat trap, no switch access). Tilt = 4° (spec, feet retracted); solved ONCE by tilting the whole plate; stagger (4.76mm) handled separately.

## Phase 3 — 2×2 prototype (Week 3, June 2026)

- **Scope upgraded from the walkthrough's single-row/4×4 to a 2×2** (S, D / W, E) — deliberately forcing tilt AND stagger into the prototype, the two hardest parts of the full build. A single row would have tested neither.
- Several STL iterations (V2 → v3 → V3/VFINAL → one-piece `Prototype_2x2.stl`). Printed and test-fit.
- **June redesign — two coupled problems found on the printed part, one cause:** the front wall sits in the 3.05mm gap between solenoid-body rows; at 4mm thick it overran the gap, AND the bottom-row screw heads pointed into the back body — the bottom row couldn't be fastened.
  - **Wall 4 → 2.5mm** (material off the back face only, mounting face and pitch unmoved). 3mm was tried on paper first — 0.05mm clearance, an FDM coin-flip.
  - **Screws M3×6 cap → M3×3 flat-head + 1mm flat-bottomed Ø6 counterbore** so heads sit flush and clear the back body. Tab re-measured ~1mm (was thought 1.5).
  - **Assembly order rule born: front row first**, then back row drops in past the flush heads.
  - **Gussets considered, then rejected** — firing recoil loads the wall in-plane (+Z), its stiff direction. Reversed an earlier "add gussets" call once the load path was understood.
  - Plate trimmed 158 → 148mm; legs moved in; tilt drifted 4.0° → ~4.28° — accepted (measured keycap tilt is ~4.5° anyway).
  - **Gotcha for posterity:** the `wall_thickness` parameter was never wired to the wall sketch — the value was hardcoded. Bit us once; documented forever.
- **Stroke reality:** key bottoms out at ~5mm of ball travel with ~5mm buffer left — fine by design (keycap limits the plunger; pull solenoids are strongest near seat).
- Breadboard fire tests: **PULSE ~22ms** worked well on the 2×2.

## Phase 4 — Dead end: the card-cage architecture (June 2026) ✝

- **The idea:** replace glued-in walls with *removable* ones — wall feet slip into grooves in the base plate, a screwed-down "comb lid" clamps the wall tops. Payoff: populate each wall with solenoids on the open bench, then drop the finished module in; lift any wall out for service.
- A full single-row 3-key test-coupon plan was written (groove 2.9mm slip-fit, 2.3mm foot, 0.2mm lid preload, lead-in chamfers everywhere) with a one-day CAD→print→test schedule.
- **Abandoned before scale-up.** The Week 4 split-plate brief explicitly carried the validated screw-in walls forward instead; the interior-row access problem the cage was meant to solve got a cheaper answer — **strict front-to-back assembly order + flush counterbored heads**. Lesson: the simpler, already-validated scheme beat the cleverer one; serviceability was traded for build simplicity.

## Phase 5 — Full 84-key split plate (Week 4, June 2026)

- **Knob replaced with a normal keycap** → a clean 84-key build, every position actuated identically. 16u-wide field confirmed against the 318.9mm case.
- **The seam had to be a staircase.** A straight vertical seam is geometrically impossible — stagger packs hole centers so any straight line passes within ~2.4mm of a hole center (inside the Ø10). The stepped seam jogs between rows; every hole clears by ≥9.52mm, and the steps key the halves together in X/Y.
- Halves join with **4 cross-seam bridge screws** (tab + boss, M3 heat-set inserts — correct here in PLA, unlike the solenoid tabs where the thread is in metal). 41 keys left / 43 right; both halves fit the 256mm bed with ~90mm to spare.
- **First STL pair (`Plate_Left/Right`) superseded by `Air75_84Key_Plate_Left/Right`** — the pair actually printed.
- Printed, assembled, and populated through late June; ~half the solenoids mounted by July 1 — producing the infamous wire-mess photo that kicked off the harness redesign (Phase 7).
- Per-key data preserved in `Full_84Key_Hole_Coordinates.csv` + `Layout_Map_84Key_Split.svg` (feeds the firmware key MAP).

## Phase 6 — Driver electronics (late June – July 2026)

- **Chain: Arduino Mega → 11× 74HC595 (cascaded) → 11× ULN2803A → 84 solenoids** (88 channels, 4 spare). ULN2803A = 8 Darlington channels @ 500mA with built-in flyback diodes (COM → +12V, the never-skip pin).
- Breadboard proofs first: `sr_led_walk.ino` (shift register + LEDs), then `keyboard_v0.ino` firing the 2×2.
- **Board split: 3 perfboards** (2-board layout drafted and rejected).
- Comprehensive first-time-solderer docs written (`Soldering_Plan.md`, `OneCell_595_ULN_Build_and_Fire_Guide.md`).
- **Top-side "wire-art" routing adopted for camera appeal:** ULN flipped 180° (notch RIGHT) so IN faces the 595 and OUT faces the solenoid landing holes; rails spaced 2-2-2-2; 11-row chip gap.
- **The flip scrambles channel order.** Cut list recommended *nearest-IN* wiring (7 identical parallel jumpers, scramble absorbed in firmware `MAP`). **Daniel chose canonical order instead (Q0→IN1, Q1→IN2…)** — electrically identical, wired as a crossing fan of unique-length jumpers; MAP becomes sequential. As-built decision, applies to all 11 cells.
- Cell #1 dry-fit July 1 (photo on file); rails and soldering next, then the cold-continuity gate before the wire set is copied ×10.

## Phase 7 — Harness architecture (July 1, 2026)

- Problem: as originally drawn, every solenoid sent BOTH leads to the driver board = 168-wire harness (see: wire-mess photo).
- **Decision: plate-side +12V distribution.** Bare doubled-22AWG bus along each mounting wall, walls tied by a trunk, fed by ONE 18AWG wire from the board's +12V rail (which stays — COMs + reservoir live there). No ground to the plate; return is via the low-side wires.
- Result: **85-wire harness (84 grey low-side + 1 orange feed) instead of 168.**
- Disciplines adopted: **label landing holes, not wires** (84 identical black leads — position is identity; log `cell · OUT · key` at solder time); **cut each wire to length only at the moment it's landed.**

## Content thread (ongoing)

- Social strategy, content calendar, and per-video scripts (video 3 w/ EE guest, video 4 2×2 B-roll, solenoid-plate short) tracked alongside the build. The $0 gag in the bank: macOS Mouse Keys — "the robot refuses to touch the mouse."

## Still open (as of July 1, 2026)

- Wave 2 mouse approach: shortlist stands (animatronic hand on gantry / trackball spinner / 5-bar arm / holonomic rover) — no decision.
- FIRE reliability test on the mounted plate (pulse tuning at scale).
- Plunger spring rate / resting force (open question #5); keycap height clean measurement (#7).
- Cell #1: rails, solder, continuity gate, first fire from a soldered board (milestone).

---

## Folder cleanup record — July 1, 2026

Deleted after review (all recoverable from git commit `84a796c`): `Plate_Left/Right.stl` (superseded plate pair), card-cage plan + assembly SVG (abandoned architecture, summarized above), `Driver_Board_2Board_Layout.svg` (3-board chosen), 84-key CAD-phase docs (`Fusion_CAD_Build_Guide_84Key.md`, `Full_84Key_Split_Plate_Design_Brief.md`, `Join_Clarify.svg`, `Plate_Holes_Air75.dxf`, `Seam_Air75.dxf`), 2×2-phase docs (`Week3_2x2_Prototype_Plan.md`, `CAD_Design_Brief_2x2_Prototype.md`, `TestFitCell_v2.stl`), and junk (`.DS_Store`s, stale `.~lock` files). Kept by choice: all 2×2 STLs + DXF, all video/content docs, `Driver_Board_Wiring_Map.svg`, empty `docs/` stubs.

# Physical AI Agent — Project Brain

> **Handoff note (July 4, 2026).** Restructured by Claude Fable 5 before its access window closed, as a deliberate knowledge transfer to future models (Opus and beyond). Read order for any session: **§Operating rules → §Current state**, then whatever §Design decisions sections the task touches. The companion files are part of this brain: `docs/PLAYBOOK.md` (the reasoning patterns behind every decision here — read it before designing, debugging, or deciding anything), `docs/briefs/` (ready-to-run prompts for each upcoming milestone), and `.claude/commands/` (`/session-start`, `/session-end`, `/verify`, `/brief` — the session protocol, automated for Claude Code). Nothing in this file is decorative; every bolded correction cost a print, a part, or an afternoon.

## Operating rules (read every session)

- **Ask first.** Clarify with questions until ~90% sure of intent (project rule). Sweeping spreadsheet changes get confirmed before applying; single-cell edits get confirmed too.
- **Concise.** No preambles, no padded summaries. Daniel reads fast.
- **When Daniel catches an error, own it and re-derive honestly** — his sharp observations have corrected the record repeatedly. Never gloss.
- **Cite sources:** spreadsheet row numbers, doc sections, file names, commit hashes.
- **git push at every milestone.** Check `git status -sb` at session start; the repo drifts ahead of origin. Remind him.
- **Physical measurement beats any assumption, datasheet, or earlier note.** Corrections are written as "was X, now Y" — never silently overwritten.
- **End every session** by appending a dated session record here (decisions + rationale, changes, corrections, UNVERIFIED items, next steps).

## Project overview

**★ NORTH STAR CHANGED Sep 20, 2026 (was X, now Y) — see the Sep 20 session record.**

**Was:** a physical AI agent that types on a real keyboard AND moves a real mouse, observed by a webcam, whose ultimate goal was playing TFT (Teamfight Tactics).

**Now: a keyboard that plays itself.** An 84-solenoid matrix mounted above a Nuphy Air75 V3 (84 keys, Blush Nano linear switches), driven from a MacBook Pro M4 via Arduino Mega → 11× 74HC595 → 11× ULN2803A, that physically types whatever it is told to type. Self-playing-piano energy, not AI-agent energy.

**v1 is DONE when all 84 keys type any sentence on command.** Nothing beyond WALK → MAP → TYPE is required.

**DROPPED Sep 20:** TFT (brief 05), and Wave 2 / the mouse gantry entirely (brief 04) — TFT's drag-and-drop was the only hard requirement for 2D mouse precision, so with TFT gone the project needs no mouse at all.

**SHELVED, not deleted** (on disk, off the critical path, costs nothing to keep): the whole `agent/` stack — vision (C920 + template matching/OCR), `llm.py`, `runtime.py`, `agent_loop.py`, `agent/tft/`, `mouse_driver.py` — plus `firmware/mouse_gantry_v0`. All of it is built and its 20-test ladder passes. If an AI layer ever comes back it starts from there, but no session should treat any of it as work owed.

Project folder and repo keep the name "Physical AI Agent" (decided Sep 20 — least disruption); the name is now a historical artifact, not a description.

Budget ceiling: $1,500. Current estimate: ~$1,366.

## Owner

Daniel. Comfortable with basic Python and basic Arduino, beginner CAD (Fusion), owns an FDM 3D printer. Give exact click-paths and commands; don't explain fundamentals.

## Key files in this folder

- `docs/PLAYBOOK.md` — **Reasoning patterns + working style.** The "how to think" half of this brain.
- `docs/briefs/` — Milestone briefs: 01 cell-#1 solder/fire (amended by 06) · 02 WALK/MAP · 03 84-key plate CAD (revived Jul 15, amended for the rebuild) · ~~04 Wave 2 mouse decision~~ (**OBSOLETE — Wave 2 dropped Sep 20**) · ~~05 TFT bring-up~~ (**OBSOLETE — TFT dropped Sep 20**) · 06 driver PCB (replaces perfboard) · **07 plate rebuild + top deck (MASTER PLAN — read this first for anything hardware)**.
- `.claude/commands/` — Claude Code slash commands: session-start, session-end, verify, brief.
- `PRD_v2_Physical_AI_Agent.docx` — Product Requirements Document. Source of truth for *what* and *why*.
- `Build_Walkthrough_Physical_AI_Agent.docx` — Week-by-week operational guide. Source of truth for *how* and *when*.
- `Wave_1_Order_Checklist.xlsx` — Parts spreadsheet with audit trail. Wave 1 (essentials), Wave 2 (deferred), Tools, Optional. Audit Trail tab maps every line to PRD/walkthrough.
- `Project_Timeline.md` — **The project's history**: every phase, mistake, dead end (incl. the abandoned card-cage architecture), and fix, plus the July 2026 folder-cleanup record. Old planning docs were deleted (recoverable from commit `84a796c`).
- `2x2_Prototype_Dimensions.md` — Master dimension reference for the finished 2×2 prototype (`Prototype_2x2.stl`). Use for any 2×2 dimension question.
- `firmware/` — `keyboard_v1` (production, 88ch), `mouse_gantry_v0` (**shelved — Wave 2 dropped Sep 20**), `keyboard_v0`, `sr_led_walk` (bring-up aids).
- `agent/` — the complete software stack (see `agent/README.md`; `tests/run_tests.py` = 20-test hardware-free ladder).
- Driver-board docs: `Soldering_Plan.md`, `OneCell_595_ULN_Build_and_Fire_Guide.md`, `TopSide_Wiring_CutList.md`, `Cell_TopSide_Routing.svg`, `Driver_Board_3Board_Layout.svg`, `Driver_Cell_Perfboard_Layout.svg`, `Driver_Board_Wiring_Map.svg`.
- Content/social files: `Content_Calendar.xlsx`, `Social_Media_Strategy.md`, `Video_Scripts.md` + Video3/Video4 files.

---

## CURRENT STATE — as of July 13, 2026

> **STALE HEADER — read the Sep 10 and Sep 20 session records first.** Since this section was written: the plate rebuild was PARKED (old 84-key plate is the vehicle), the harness reverted to the desk form, the project's north star changed to a self-playing keyboard with TFT and Wave 2 dropped, and **BOARD A IS BUILT AND PASSED ITS FULL CONTINUITY GATE (Sep 20)** — chips not yet inserted, never powered.

**Software: COMPLETE production stack, all 20 ladder tests pass** (verified on Daniel's Mac Jul 4). Firmware `keyboard_v1` + `mouse_gantry_v0` mock-compile clean. Full detail in the July 2/July 4 session records below.

**Hardware (Jul 7): FULL 84-KEY PLATE PRINTED AND FULLY POPULATED — all 84 solenoids screwed on.** As-built = the 2×2 scheme scaled up: **6 walls + M3×3 flat-head tab screws + counterbores, assembled bottom row → top row** (was: brief 03 drop-in pockets + clamp bars — NOT used; brief 03's scheme is shelved). Counterbores confirmed to clear adjacent bodies. Consequence: interior-row swap = unscrew the rows behind it. Solenoid leads untouched/tangled — tidy plan in the Jul 7 session record. BOSYTRO 12V PSU in hand.

**Driver build (Jul 10): PERFBOARD CANCELLED → CUSTOM PCB — see `docs/briefs/06_driver_pcb.md`.** Daniel found perfboard interconnect soldering untenable (components fine, point-to-point routing not). Decision: one 6-cell PCB design (595+ULN+screw terminals, DIP sockets for his existing chips), ordered ×5 bare from JLCPCB, 2 populated (6+5 cells = 11), ~$35–60, ~2wk lead. Interconnects become copper; remaining solder is all easy through-hole. Interim: **breadboard fire test with the dry-fit cell #1 chips + clipped spare solenoid — the new immediate milestone.** Firmware unchanged (canonical Q→IN preserved; FIRE N → cell/OUT mapping intact).

**Jul 13 updates: (a) BREADBOARD FIRE TEST DONE — full 595+ULN chain (dry-fit cell #1 chips), repeated reliable key presses at real mounting geometry, characters on screen. UNVERIFIED #3 CLOSED. (b) Soldering unblocked** (root cause was technique — see Jul 13 record); **cell #1 fully soldered on perfboard (~4h) except final rail taps** (595 pins 16/10→+5V, 13→GND, 14→Mega DATA; ULN COM→+12V) — in progress. **(c) PCB route RE-CONFIRMED with data:** 4h/cell measured → ~25h+ for 10 more cells + 84 solder landings, declined. Cell #1's role: interim driver (8 keys during the ~2wk PCB lead), then reference/spare. Cell #1 still needs its own continuity gate + fire verify (workmanship check, not design risk).

**UNVERIFIED — ask Daniel / check first:**
1. ~~Did `python tests/run_tests.py` (20 tests) run clean on HIS Mac?~~ **RESOLVED Jul 4 (Opus): 20/20 OK in the 3.9 venv on Daniel's Mac.** Still open: the 3 earlier campsite tests + camera permission.
2. ~~Is the repo fully pushed?~~ **RESOLVED Jul 4 (Opus): pushed to origin/main; handoff package committed too (`353494b`). Repo in sync.**
3. ~~FIRE test (reliable presses at ~5mm bottom-out)~~ **RESOLVED Jul 13 (reported; test run during the Jul 10–13 wait window): breadboard, dry-fit cell #1 chips (595+ULN chain, Mega FIRE commands), solenoid at real 2×2 mounting geometry — repeated reliable presses, characters on screen.**
4. ~~M3×3 flat-head actually holds in the re-measured ~1mm tab (~2 threads)~~ **RESOLVED Jul 7: all 168 driven on the 84-key plate, bite firm, counterbores clear.**

**Pending TODOs gated on ask-first (spreadsheet NOT yet edited):**
- Row 39: hardware → **M3×3 flat-head** (history: M2 → M2.5 → M3×6 cap → M3×3 flat-head + counterbore) + refresh search link.
- Row 33: PSU → "Ordered"; row 34 (IEC cord) → "Skip" (bundled with BOSYTRO).
- Row 40 (M5 standoffs): SKIP — replaced by side rails. M5 *screws* still needed (260pc assortment covers plate→rails, rails→base; the Wave 2 V-slot use is void — Wave 2 dropped Sep 20).
- NEW (Jul 10, brief 06 buy list): PCB order ~$20–40 + 5.08mm screw terminals ~$12 + DIP sockets ~$6 (reuse perfboard sockets if on hand) + 6-pin cascade cable. Perfboard line items for cells 2–11 become spares/unneeded.

**Next milestones — RESEQUENCED Jul 15 around the rebuild; brief 07 is the master plan:**
1. **Track A (critical path, start now):** EasyEDA design session (Claude drives via Chrome; Daniel needs a JLCPCB account) → netlist check vs brief 06 → DRC → 1:1 paper print → **order 5 boards ASAP** (NOT gated on cell #1 — superseded Jul 13). Same day: export board outline + mounting-hole coords for the deck.
2. **Track B (inside the ~2wk lead):** wire-tidy Phase 0 (snip frayed tips) → brief 03 caliper gates (d, body-top height, lead exits) → coupon print + **swap cycle + fire (breadboard driver)** → **GATE: coupon passes = old-plate teardown authorized** → full CAD (plate L/R + walls + clamp bars + deck L/R) → print.
3. **Track C (boards arrive):** populate boards → continuity gate → WALK 0–87 (brief 06 DoD) → one rebuild session (teardown → drop-in populate → bars → deck → land 84 wires up through slots, label + log) → flash, MAP, WALK all 88 (brief 02). **Push — milestone of milestones.**
4. **That's it — v1 is done when 84 keys type a sentence on command.** *(Items 4–6 here were C920 vision calibration, the Wave 2 mouse decision, and TFT bring-up. ALL DROPPED Sep 20 — do not revive them as work owed.)*
5. Optional, after v1: a score player (timestamped key events over serial) so the keyboard can perform a pattern rather than just type. Not started, not required.

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
- **Screw length: M3 × 6mm.** The wall is 4mm PLA + the solenoid's mounting tab is only ~1.5mm thick → screw spans ~5.5mm. Do NOT use 8mm (would jut ~2.5mm past the tab into the solenoid frame and foul it). 5mm only catches ~1mm of the tab (too little). 6mm is the sweet spot. **→ SUPERSEDED in the June redesign: now M3×3 flat-head + flush counterbore + 2.5mm wall — see "2×2 redesign" below.**
- **Thin tab caveat:** thread engagement is limited by the tab thickness — marginal but fine for a ~30g solenoid with light side loads. Don't over-torque; threadlocker optional. (Heat-set inserts do NOT help here — the thread is in the metal tab, not the PLA.)
- Wall clearance holes for the screw shaft: **Ø3.3mm** (`mount_hole_dia`), so the M3 passes through the wall and threads into the tab. No nut needed when the tab is tapped.
- **CONFIRMED on the part: 2 holes on ONE side face only (not both), 15mm apart center-to-center. So 2 screws per solenoid × 84 = 168 total.**
- **CRITICAL — mounting orientation discovery:** the 2 holes' axis is PARALLEL to the plunger. So the solenoid CANNOT bolt flat to a horizontal plate (that would point the plunger sideways). It must bolt by its side face to a wall standing PERPENDICULAR to the plate, with the plunger hanging through a clearance hole. This drove the tilted-plate + mounting-wall design (see below). Also measured: lower mounting hole → ball tip at rest = 15mm.
- **M3 bite CONFIRMED (June 11, 2026)** — screws thread firmly into the tab and hold. **TODO when ordering:** update spreadsheet row 39 hardware to **M3×3 flat-head** (was M2 → M2.5 → M3×6 cap → now M3×3 flat-head + counterbore) and refresh the search link. (Spreadsheet NOT yet edited — per ask-first rule.)

### Test-fit cell — printed & validated (June 2026)

Single-cell test print (one Ø10 plunger hole + one perpendicular mounting wall + two M3 screw holes) done to de-risk the mount before the full 2×2. Modeled in Fusion via the live connector; STL at `TestFitCell.stl`. **Results:**

- **Plunger hole widened Ø7 → Ø10mm** (`plunger_hole_dia=10`). The Ø7 cleared the ball tip but NOT the screw/nut feature just above the ball that also travels through the hole. Ø10 clears it. (Trade-off: the Ø6 plunger now has ~2mm slop, so the hole no longer guides it; acceptable, silicone tubing helps. A stepped hole — wide bottom, Ø7 top — could restore guidance later.)
- **Screw holes → M3 clearance Ø3.3mm** (see above).
- **Hole height corrected UP by 4mm → `lower_hole_z` 3 → 7mm** (above the plate top; upper hole = `lower_hole_z + mount_hole_spacing` = 22mm). First print's holes were 4mm too low. Cause: the solenoid sits 4mm higher than the original model assumed — its mounting holes line up when the solenoid body sits flush with the plate BOTTOM, and the plate is 4mm thick. **Key insight: the ball/solenoid rest position is fixed by physics (plunger dropped through the hole); the wall holes must be placed to match it — moving the holes does NOT move the ball.** Fix = shift BOTH holes (the rigid 15mm pair) up 4mm and lengthen the wall to contain the upper hole.
- **Wall lengthened** so the upper hole (22mm above plate top) has material around it; ~6mm margin above it.
- **Validated with a real solenoid (photos on file):** frame seats flat against the wall, ball-tip-down, ball drops cleanly through the Ø10 hole and protrudes below the plate at rest, and the two M3 holes line up. → **`wall_offset≈8mm` is good.**
- **For the full 84-key plate:** reuse `lower_hole_z=7` and `plunger_hole_dia=10`; the +4mm correction must propagate to all 84 positions.

### Structural mounting: SIDE RAILS (not standoffs, not full encasement)

**Decision: two parallel 3D-printed PLA walls running along the long axis of the keyboard, with the matrix plate spanning between them as a removable lid.**

Rejected alternatives:
- **4 M5 standoffs (original PRD spec):** low rigidity, awkward differential heights to match keyboard tilt, lots of swap-test iteration.
- **Full 4-walled encasement:** most rigid but print size is brutal (320×130mm footprint × tall walls = 6–8 sub-parts joined with dowels, 30–40hr print time, heat trap, keyboard inaccessible for switch swaps).

Why side rails win: tilt baked into wall geometry (front edge shorter than back) — no differential standoffs; much better rigidity than 4 standoffs; only 2 wall pieces to print; sides of keyboard stay open (switch-swap access, airflow, debug visibility); matrix plate stays removable.

**Implication for Wave 1 order:** Row 40 (M5 standoffs): SKIP. M5 SCREWS still needed (different part) — plate→rails, rails→base board, and all Wave 2 V-slot hardware. The 260pc M5 assortment covers all of it.

### Mounting refinement: TILTED FLAT PLATE + perpendicular mounting walls

Because the JF-0530B's holes are on a side face (parallel to the plunger), solenoids bolt to walls that stand perpendicular to the plate:

- **One flat plate, tilted to match the keycap plane (4°).** Tilting the whole plate means every row has the same plunger gap — tilt is solved ONCE, not per row.
- Plunger holes perpendicular to the plate → perpendicular to the keycaps → plungers strike straight in. Model the plate FLAT (holes vertical) and let the legs/rails create the tilt, so perpendicularity is automatic.
- **Mounting walls** stand perpendicular to the plate (one per keyboard row) — solenoids bolt by the side face, bodies up, plungers down through the holes.
- **Stagger is separate from tilt:** tilting fixes front/back height but NOT the left/right row offset. Per-row X offset must still be modeled.
- Plate height set by legs/rails, then shimmed for the 1–2mm gap.

### Keyboard tilt: must be modeled in CAD

- Air75 V3 has ~4° case angle even with feet retracted. Across 130mm depth → ~9mm front/back difference; a flat non-tilted plate would give front gap ~10mm (too far) / back ~0mm (false-triggers).
- **Fix:** rails have built-in 4° tilt so the plate sits parallel to the keycap plane. **Feet always RETRACTED.**
- **CONFIRMED from spec: tilt = 4° ("Type Angle" base, feet retracted). Key pitch = 19.05mm both axes. Row stagger = 4.76mm (standard 0.25u), back row LEFT of front. `tilt_angle=4` locked** (but see 2×2 redesign: measured keycap tilt ~4.5° — build the 84-key plate to the measurement).

### Solenoid stroke trimming

- 10mm stroke; only ~3mm is minimum useful travel (1–2mm air gap + 1.4mm Blush Nano actuation + margin). **MEASURED on the prototype: key bottoms out at ~5mm of ball-tip travel, leaving ~5mm buffer — fine by design (see 2×2 redesign).**
- Plate positioned so the keycap mechanically limits plunger extension. Never let plunger fully extend at rest.

### PSU choice: BOSYTRO 480W 40A 12V ($33)

- Over Meishile S-600-12 600W 50A ($28) because BOSYTRO bundles the IEC C13 cord. Tradeoff: less headroom (40A vs 50A), fewer reviews. Fine: realistic peak ~25A (7 keys × 300mA + transients). **TODO on ordering:** row 33 "Ordered", row 34 (IEC cord) "Skip".

### 2×2 redesign — fit + fastening fixes (June 2026, from the in-hand prototype)

Printed the 2×2, test-fit the solenoids, found two coupled problems, redesigned. Values here supersede earlier ones; `2x2_Prototype_Dimensions.md` is updated to match.

- **The problem (read off the model):** the front (bottom-row) wall sits in the 3.05mm gap between the two solenoid bodies (front body ends Y8, back body starts Y11.05). At `wall_thickness=4` the wall overran that gap by ~1mm, AND the bottom-row screws drive from the back face so their heads pointed into the back body → the bottom row couldn't be fastened (the top row, screwing into open space, was fine). One cause, both symptoms.
- **Wall 4 → 2.5mm.** Material comes off the BACK face only (the wall is anchored at its mounting face via `wall_offset=8`, so the mounting face — and the 19.05 pitch — don't move). 2.5mm gives ~0.55mm slip-fit to the back body; 3mm was too tight (0.05mm — an FDM coin-flip). Inter-wall clear gap = 16.55mm. **Gotcha: `wall_thickness` was never wired to the geometry — it's a hardcoded dimension in the `Walls` sketch; change it there (and re-link to the param).**
- **Screws: M3×6 cap → M3×3 FLAT-head** (flat-bottom, NOT countersunk) + a **flat-bottomed counterbore** on the BACK/head face (1mm deep, ~Ø6 = head dia + 0.4, leaving ~1.5mm wall) so the head sits flush and clears the back body. Reach: under-head shank = remaining wall (1.5) + tab (re-measured ~1mm, was 1.5) ≈ 2.5 → M3×3 (tip ~0.5mm past the tab; verify nothing's behind it). Flat-head length is measured under-head, so the 1mm head adds no reach. Counterbore must be a FLAT pocket, not a cone. **Still M3 thread.**
- **Bottom-row assembly order:** screw the bottom (front) row FIRST, then drop in the top (back) row — flush heads clear and the back body seats. (Chosen over flipping the row or a top hold-down bar.)
- **Gussets: NOT needed.** Firing recoil pushes the body straight UP (+Z), the wall's stiff in-plane direction. (Reversed an earlier "add gussets" call once the load direction was clear.)
- **Plate trimmed 5mm per end: 158 → 148mm** (ends Y84.5 / Y-63.5). Holes are origin-anchored, unmoved. **Legs moved in 5mm each**; heights unchanged (front 23.9, back 34.5). Straddle inner gap 146 → 136mm (clears the 128.9mm keyboard, ~3.5mm/side); leg spacing 152 → 142mm → tilt drifts 4.0° → ~4.28° — negligible over 2 rows (~0.09mm), and nearer the measured ~4.5° keycap tilt.
- **Stroke check (supersedes "~3mm useful"):** key bottoms out at ~5mm of ball-tip travel, ~5mm buffer. Fine: keycap limits the plunger, buffer prevents missed presses, and this pull solenoid is weakest at start of extension / strongest near seat, so bottoming at 5mm is well up the force curve. **FIRE test PASSED Jul 13 (breadboard, real geometry, characters on screen — see UNVERIFIED #3).**
- **For the final 84-key plate:** `lower_hole_z=7` (ball ~4mm below plate) carries over. Legs scale up. **TILT is the thing to NAIL over the full ~129mm depth** — 0.5° ≈ 1mm gap variation — build to the measured ~4.5° or make legs shimmable. **Wall-per-row does NOT scale to interior rows** (heads can't fit between rows) — needs a top-clamp/pocket scheme. See brief 03.

### Locked CAD parameters (carry into the 84-key build)

`pitch_x=pitch_y=19.05` · `stagger=4.76` (back row left; NOT uniform — arrow cluster + right utility column need explicit per-key positions from `Full_84Key_Hole_Coordinates.csv`) · `tilt_angle=4` (spec; measured ~4.5 — build to measurement) · `plate_thickness=4` · `plunger_hole_dia=10` · `mount_hole_dia=3.3` · `mount_hole_spacing=15` · `lower_hole_z=7` · lower-hole→ball-tip-at-rest=15 · `wall_offset=8` · wall thickness 2.5 · solenoid body 30×16×15.

*(Historical note: the 2×2 prototype scope was deliberately chosen over the walkthrough's flat 4×4 / single-row because tilt within one row is zero — the 2×2 (front S,D / back W,E) forced tilt AND stagger to be exercised. Its CAD brief and Week 3 plan were retired in the July 2026 cleanup; see `Project_Timeline.md`.)*

## Open questions — status

1. Solenoid body dimensions — **RESOLVED: 30×16×15mm.**
2. Mounting tabs — **RESOLVED: 2 holes on ONE side face only.**
3. Mounting hole spacing — **RESOLVED: 15mm c-t-c.**
4. Plunger extension at rest — **RESOLVED: lower hole → ball tip at rest = 15mm; ball extends on energize.**
5. Plunger spring rate / resting force — **still open** (assess at prototype assembly; informs whether silicone tubing is enough damping).
6. Keyboard tilt angle — **RESOLVED: 4° spec / ~4.5° measured.**
7. Keycap height above desk (with VHB) — placeholder ~18mm; not blocking (gap is shimmed); measure cleanly at assembly.
8. `wall_offset` (8mm) — **RESOLVED: validated at test-fit.**
9. Screw thread engagement in tab — **RESOLVED (M3 bites). Committed screw now M3×3 flat-head; tab re-measured ~1mm → ~2-thread engagement. Confirm the M3×3 holds at assembly. Jul 5: MOOT for the 84-key build — the drop-in scheme (brief 03) uses no tab screws; only the 2×2 still relies on them.**
10. Mounting hole size/thread — **RESOLVED: tapped M3. Wall clearance Ø3.3.**

## Driver board + solenoid wiring architecture (July 2026)

### Driver design

- Chain: **Arduino Mega → 11× 74HC595 (cascaded off D11/D12/D13) → 11× ULN2803A → 84 solenoids** (88 channels, 4 spare). ULN2803A = "the driver": 8 Darlington channels, 500mA each, built-in flyback diodes enabled by COM (pin 10) → +12V — **never skip**.
- **CAPACITORS ON HAND (Daniel, Jul 13 — design to THESE, stop speccing others): 0.1µF (104) multilayer ceramic 5.08mm pitch, and 4700µF 25V electrolytic. Nothing else.** Usage: 100nF per chip (595 VCC/GND) + per-board decoupling; 4700µF on each board's 12V rail (+ to +12V, stripe to GND) — it exceeds the 470–1000µF minimum, correct per Soldering_Plan §B. The brief-06 "100µF on 5V" line: SKIP, 100nF alone is fine there.
- **BUILD METHOD CHANGED Jul 10: custom PCB (brief 06), perfboard cancelled.** The chain/architecture above is unchanged — only its physical realization moved to copper. Two 6-cell boards (A = cells 1–6, B = 7–11 + empty last slot), DIP sockets, 5.08mm screw terminals for the 84 grey low-side wires, OE pullup improvement. Perfboard docs below are HISTORICAL: `TopSide_Wiring_CutList.md`, `Cell_TopSide_Routing.svg`, `Soldering_Plan.md` (the flipped-ULN + jumper-fan scheme was a perfboard artifact). `OneCell_595_ULN_Build_and_Fire_Guide.md`'s fire protocol still applies.

### Q→IN wiring with the flipped ULN — CANONICAL (as-built)

- **AS-BUILT (cell #1 dry-fit, July 1, 2026): canonical order — Q0→IN1, Q1→IN2 … Q7→IN8. Applies to all 11 cells.** (Nearest-IN was the cut list's recommendation; Daniel chose canonical.)
- Physical result: with the flipped IN row running right-to-left, the 8 jumpers form a **symmetric crossing fan** — **70/65/60/55/50/50/55/60 mm** (Q0…Q7; verified against `Cell_TopSide_Routing.svg`, chips left-aligned). Solder longest-first (IN1→IN8), layer crossings consistently.
- Payoff: **FIRE N → OUT(N+1)**, sequential — no scramble table; firmware `keymap[]` only maps channels→keys for TYPE.
- OUT landing holes run **right-to-left (OUT1 far right)** regardless of jumper scheme — chip-internal.

### MAP discipline — label holes, not wires

All 84 solenoid leads are identical black → **position is identity**. Sharpie the key name beside each landing hole; log `cell · OUT · key` **at solder time**, one line per wire; type the table into firmware MAP when done. WALK mode is the final verification pass, not the primary method.

### Harness: plate-side +12V distribution (DECIDED — **PARTIALLY SUPERSEDED Jul 15 by brief 07:** boards move onto a top deck above the plate → the 85-wire desk harness is gone, buses relocate wall-tops → deck, both leads route straight UP. Bus sizing, one-feed topology, no-ground-to-plate, MAP + cut-at-landing rules all carry over unchanged.)

- Board's +12V rail **stays** (ULN COMs + reservoir cap). Added: **+12V distribution on the plate** — bare ~16 AWG bus wire along each mounting wall, walls tied by a trunk at one end. **No ground wire to the plate** — return current comes back through the 84 low-side wires.
- **BUS FEED — CORRECTED Jul 26 (was X, now Y). Was:** bus "fed by ONE 18 AWG +12V wire **from the board rail**." **Now:** bus is fed **ONE 18 AWG wire straight from PSU V+**, and each board's **J70 pin 1 taps a short stub off the bus** (not off the PSU). Rationale: what matters is whether coil current *passes through* board copper. Feeding the bus from a board rail makes that board a pass-through (2.1A in J70 → across board traces → out to bus), which the widened +12V traces (0.8mm, two 0.3mm necks ≈1.3A) are NOT sized for. Tapping J70 off the bus makes each board a **dead-end leaf** — the 2.1A never enters the board. Same net, opposite current path. Also solves the PSU terminal count (**BOSYTRO has 3× V+ / 3× V−**): **1 wire on V+** (to bus trunk) + **3 wires on V−** (one per board's J70 pin 2), 2 V+ terminals spare.
- **CB1 (4700µF) stays useful under this topology** — with a short fat bus→J70 stub (~10cm ≈ 100nH, nothing on ms solenoid timescales) the cap still sits electrically on the bus and buffers switch-on surge. Keep the stubs short; don't move the cap.
- **Return current still goes through the board either way and this is by design:** solenoid low → terminal → ULN → B.Cu ground plane → J70 pin 2 → PSU V−. No alternative path exists. The plane was measured for it (narrowest neck 1.13mm ≈ 2.4–2.6A vs 2.1A worst case); the +12V traces were not and now don't need to be.
- Per solenoid: high side → ~5cm hop to its wall bus; low side → 22 AWG stranded grey, cut to length, → its ULN OUT landing hole. Plate↔board harness = 84 grey + 1 orange = **85 wires (vs 168)**.
- Peak bus load ≈ 7 × 300mA ≈ 2A — 16 AWG has big margin. If ringing/resets under heavy typing: optional 470µF across the plate bus.
- Solid→stranded transition **at the landing hole** (solid on board, stranded off-board), never mid-run.

### Bench triage for the wire mess (photo on file: plate ~half-populated, leads frayed + tangled)

1. Snip/tape every frayed bare tip immediately — shed strands are a 12V short waiting to happen.
2. Velcro leads into per-row bundles; work one wall at a time.
3. **Golden rule: cut each wire to length only at the moment it's landed. Never pre-cut.** Length = label.
4. Optional: snap-on printed combs over the wall tops (plate already printed, so integrated troughs are out).

### Wave 2 mouse — **DROPPED Sep 20, 2026.** Historical; brief 04 is obsolete

**Was:** undecided, explicitly gated on the TFT drag requirement. **Now:** dropped outright. TFT was the only hard requirement for real 2D mouse precision; with TFT gone the project needs no mouse subsystem at all. The shortlist below is kept as the record of the reasoning, NOT as an open question. Consequences: brief 04 obsolete, `firmware/mouse_gantry_v0` shelved, `agent/mouse_driver.py` shelved, the Wave 2 spreadsheet tab is void, and the Wave 2 V-slot/gantry budget is freed.


- Daniel is open to replacing the XY-gantry + B100 plan; wants viral mix of "looks alive / real feats / absurd".
- Shortlist: (1) **animatronic hand riding the mouse** over hidden gantry — best ROI; (2) **trackball + friction wheels** — **DEAD (no TFT drag)**; (3) **5-bar pantograph** — ~$60–90; (4) **holonomic rover** — highest novelty/risk. $0 gag: macOS Mouse Keys ("robot refuses to touch the mouse") — **driver already written**.
- **TFT requirement decides it:** drag-and-drop needs real 2D precision → gantry or pantograph favored.

---

## Session records

### Camping-trip session (July 2, 2026) — software sprint + trip plan

**Context: camping until Sun Jul 5, MacBook only. Deadlines: 2× Fable usage ends Jul 5; Fable access ends Jul 7. Plan: front-load heavy AI-assisted work.**

**Ultimate goal revealed: the agent plays TFT.** Cost reality: naive Sonnet loop ≈ $4–8/game. Strategy: **develop on local Ollama (free) → play on cheap cloud (Gemini/DeepSeek/Qwen, ~$0.10–0.50/game) → Claude only for hard decisions/tuning.** Levers: observe only during planning phases (~70% fewer calls), cheap model for routine turns, downscaled screenshots, spend cap.

Built (committed & verified):
- **`firmware/keyboard_v1/keyboard_v1.ino`** — 88-channel production firmware: 11-cell cascade, FIRE N → cell(N/8+1)/OUT(N%8+1), TYPE with real LShift chords, KEY/CHORD/HOLD/RELEASE, WALK mode, EEPROM-persisted keymap (MAP/SAVE/LOAD — no recompile during solder-time logging), per-channel 60ms cooldown + MAX_ON=7 PSU guard. Mock-compile clean (-Wall -Wextra). **Read the header before flashing: power-on rule (USB first, THEN 12V — 595s output random data until cleared) and CASCADE_REVERSED flag.**
- **`agent/`** — observe→decide→act stack, hardware-free-testable: `keyboard_driver.py` (serial wrapper, dry-run, `load_map_from_log()`), `vision.py` (capture → rectification → multi-scale template match + OCR), `agent_loop.py` (`--scripted --dry-run` = zero-cost plumbing test), `llm.py` (provider-pluggable: ollama/gemini/deepseek/qwen/anthropic/openai, robust JSON extraction).
- Commits: `7023389`, `41bc82c`, `11a5193`.

Daniel's machine setup (done): repo pushed through `41bc82c`; `agent/.venv` (Python 3.9) with requirements incl. opencv 5.0; Homebrew + tesseract 5.5.2; Ollama via brew, `qwen3-vl:8b` pulled; Anthropic API key in Notes. **Reminder: venv re-activation every new Terminal — #1 predicted failure mode.**

### July 4 session — full production stack (Fable sprint, campsite)

**Complete software stack now exists; all 20 ladder tests pass hardware-free.** Scope confirmed via questions: full production stack + gantry-backed mouse abstraction + generic TFT layer with editable set data.

- **`agent/actions.py`** — single action vocabulary (keyboard + mouse), validation, `Actuators` dispatch. New action types: add here once, work everywhere.
- **`agent/mouse_driver.py`** — `MouseDriver` interface; backends: `dry`, **`mousekeys`** (macOS Mouse Keys pressed BY THE SOLENOIDS — real click/drag with Wave 1 only; auto-toggles off around typing via 5×Option), `gantry` (serial, px→mm affine). `fit_affine`/`apply_affine`.
- **`agent/runtime.py`** — `Session` engine: JSONL + per-turn-frame logging under `agent/logs/` (gitignored, as is `agent/calibration/`), budget guards (`--budget-usd`/turns/minutes), stuck detection (frame dHash), validation-error feedback to the model, escalation tier (`--escalate-to`, or plan `"escalate": true`), clean Ctrl-C. `agent_loop.py` = thin CLI (new flags: `--mouse`, `--still`, `--budget-usd`, `--calib`, `--escalate-to`).
- **`llm.py` upgraded** (retries+backoff, JSON-repair re-ask, token/$ metering — `PRICES` editable ballpark); **`vision.py` upgraded** (`still=` mode, `frame_hash`/`wait_settle`, normalized-region OCR, screen-quad save/load).
- **`agent/tft/`** — `layout.json` (normalized coords, EYEBALLED DEFAULTS — verify with calibrate overlay), `set_data.json` (**placeholder — fill live set before games**), `tft_agent.py` (tft_buy/sell/place/move/bench/roll/level/lock/augment → primitives; hotkeys D/F/E/W via physical keyboard, only buys/placements need mouse; combat-phase hook skips LLM calls once `tft/templates/combat_marker.png` captured — the 70% cost lever), `play_tft.py` (defaults: ollama, 800 turns).
- **`agent/calibrate.py`** — screen / tft (overlay PNG) / gantry (3-probe affine) / mousekeys (speed) flows, prompt-driven, no GUI.
- **`firmware/mouse_gantry_v0/`** — Wave 2 firmware AHEAD of the hardware decision; serial protocol (HOME/MOVE/JOG/BTN/CLICK/SPEED/STATUS/STOP → OK/ERR) is the contract with `GantryMouse` — a pantograph swap only rewrites motion code. CNC-shield pins, zero deps, `HAVE_ENDSTOPS 0` until switches wired. Mock-compiles clean.
- **`agent/tests/run_tests.py`** — 20-test ladder; zero hardware/network/keys. All pass; all files Python 3.9-verified (`ast` feature_version — his venv is 3.9).
- **Verify on his Mac next session:** `cd agent && source .venv/bin/activate && python tests/run_tests.py`.
- TFT pre-game checklist in `agent/README.md`.
- Commit: `e6a46fb` — **was ahead of origin by 1 at handoff time; confirm pushed.**

### July 4 session (later) — Fable→Opus handoff package

Daniel asked Fable to "leave part of its brain" for Opus before access ends Jul 7. Built: this restructured CLAUDE.md (rules + current state up top), `docs/PLAYBOOK.md` (12 reasoning patterns distilled from the project's real errors), `docs/briefs/` (5 milestone briefs + README), `.claude/commands/` (session-start / session-end / verify / brief). All facts preserved from the pre-handoff CLAUDE.md (in git history if needed).

### July 4 session (Opus) — push + Mac verification of the handoff

First Opus session. Two UNVERIFIED items closed (struck through above):
- **Handoff package was uncommitted and unpushed.** Caught via `git status -sb`: CLAUDE.md modified + `.claude/`, `docs/PLAYBOOK.md`, `docs/briefs/` all untracked — i.e. Fable's entire brain existed only in the working tree, one crash from gone before the Jul 7 cliff. Staged + committed as `353494b` (cleared a stale `.git/index.lock` first), then Daniel pushed origin/main from his own Terminal (sandbox network blocks GitHub). Repo now in sync; nothing ahead of origin.
- **Test ladder verified on the real machine.** Ran green in the sandbox (Py 3.10 / numpy 2.2 / cv2 4.13, 20/20 OK) as a pre-check, then Daniel confirmed on his Mac venv (Py 3.9): `Ran 20 tests ... OK`. Software stack now verified end-to-end on the machine it runs on — no version-drift surprises.

Still open for any remaining Fable time (hardware-free genius work): brief 03 interior-row fastening scheme (unsolved) and `agent/tft/set_data.json` (placeholder). Everything else is gated on hardware (cell #1 solder → first fire, WALK/MAP). **Reminder: this CLAUDE.md edit is itself an unpushed change — push again after this session.**

### July 5 session (Fable) — interior-row fastening SOLVED (design only, no hardware)

Brief 03's open problem worked out and written into `docs/briefs/03_84key_plate_cad.md` (§"Fastening scheme"). Summary:

- **Root cause of the non-scaling:** the 2×2's fastener axis is horizontal (Y) — interior screws would have to be driven inside the 16.55mm inter-wall slot (~320mm long, closed ends), and any interior swap = teardown of the rows behind. One cause, both symptoms.
- **Scheme: rotate everything to Z — drop-in pockets + top clamp bars.** Y captured by the existing wall sandwich (16.55 slot / 16 body / 0.55 float — geometry already validated on the 2×2; only new part: front stub rail at y=−46.65 for the space row). X captured by 3mm printed ribs in the inter-body gaps (CSV-verified min gap 4.04mm across all 84; positions generated from `Full_84Key_Hole_Coordinates.csv`). Z down-stop by seat ledges of height **7−d** where d = body-bottom→lower-tab-hole (proved d ≤ 7 from the in-hand 2×2, so always feasible). +Z recoil taken by per-row-half clamp bars (M3 heat-set inserts in raised-wall bosses, M3×8 vertical, 3mm EVA foam ~1mm crush) — fastener on the load axis; bars can bridge the L/R plate seam for free rigidity.
- **Payoffs:** rows order-independent; any solenoid swaps by lifting one bar; deletes all 168 horizontal tab screws → open question #9 (M3×3 in ~1mm tab) moot for the 84-key build.
- **Fallback documented:** T-stud keyhole hang (exact datum, but 168 depth-set screws + 1.2mm webs) if the coupon shows slop. Other rejects (bolt-on walls, snap clips, magnets) written into the brief.
- **Gates before CAD (10 min calipers on the 2×2):** d; body-top height (sets wall raise, ≈Z36 if d=7 since body top hits Z34 > current Z32); lead exit points (bar slots). Then the 3-wall × 2-column coupon incl. a swap cycle + fire with cell #1.
- Also edited: CLAUDE.md milestone 5 + open question #9; brief 03 assembly-order note + definition of done. Spreadsheet impact (row 39 qty drop; new inserts/pan-heads/foam) NOTED in the brief only — not edited, per ask-first.
- UNVERIFIED: everything above is paper until the coupon. **Push after this session (milestone).**

### July 7 session (Fable) — 84-key plate populated; as-built correction; wiring tidy plan; cell-#1 test strategy

**MILESTONE: full 84-key plate printed and fully populated — all 84 solenoids mounted.** Session was Q&A + record-keeping; no files built besides this CLAUDE.md update.

- **As-built correction (was X, now Y):** was = brief 03 drop-in pockets + clamp bars (Jul 5 design, never built). Now = **6 walls + M3×3 flat-head tab screws + flat counterbores, i.e. the 2×2 scheme scaled up.** Daniel confirmed: counterbores clear the adjacent bodies; assembly order bottom (front) row → top (back) row, same as the 2×2. Brief 03's pocket/clamp scheme is SHELVED (kept on file as the swap-friendly alternative). Consequences: (a) open question #9 CLOSED — ~2-thread engagement holds across all 168 screws; (b) interior-row solenoid swap = unscrew the rows behind it — accepted cost, 16 spares on hand; (c) brief 03's clamp-bar hardware (inserts/pan-heads/foam) no longer needed for Wave 1.
- **Wiring state:** all 168 leads factory-length, tangled, frayed tips. **Tidy plan agreed (uses the locked §Harness design unchanged):** Phase 0 snip/tape every frayed tip (168). Phase 1 velcro per-row bundles, one wall at a time; no wire labels (holes get labels, not wires). Phase 2 build the +12V buses NOW — bare 16 AWG along each of the 6 walls, trunk at one end, one 18 AWG orange pigtail taped off until the board rail exists; per solenoid, trim the more convenient lead to ~5cm at the moment of soldering (kills 84 of 168 danglers; coil is non-polarized so either lead works). Phase 3 low sides stay parked full-length until cells are soldered — golden rule unchanged (cut only at landing; Sharpie key at hole; log `cell · OUT · key`). Routing rule new to the 84-key: interior-row leads exit **up and over the wall top**, never along the slot floor. Phase 4 optional printed wall-top combs (offered, not requested yet).
- **Cell #1 test strategy (decided):** nothing soldered yet. Do NOT solder any solenoid for testing. Sequence: solder cell #1 → cold-continuity gate → first fire with **one SPARE solenoid on alligator clips** (high side to +12V rail, low side to OUT1; USB before 12V) → walk the same spare across OUT1–OUT8 → only then land the first 8 plate solenoids permanently (8 convenient keys, cut-to-length, label + log). The clipped spare = reusable test rig for all 11 cells.
- **PSU:** BOSYTRO 12V confirmed IN HAND — nothing blocks brief 01. (Spreadsheet rows 33/34 still not edited, per ask-first.)
- Next steps: brief 01 (cell #1 solder → fire), Phases 0–2 of the wire tidy in parallel.
- **Push after this session — populated-plate milestone + this record are unpushed.** *(Done — `61b63d5` pushed, verified Jul 10.)*

### July 10 session (Fable) — perfboard cancelled → custom PCB; breadboard fire test plan

**Trigger:** Daniel hit a wall soldering cell #1 — component soldering fine, point-to-point interconnects (jumper fan, rails, cascade) not tenable ×11 cells. Researched alternatives, decided with Daniel via options question.

- **Decision (was X, now Y):** was = 11 perfboard cells (3-board split). Now = **custom PCB: one 6-cell design (595→ULN canonical, DIP sockets, 5.08mm screw terminals), ordered ×5 bare from JLCPCB, boards A (cells 1–6) + B (cells 7–11, last slot empty at END of cascade), 3 spare boards.** All interconnects become traces; remaining solder = sockets/terminals/caps (easy THT). ~$35–60 total, within ~$134 headroom. Full spec in `docs/briefs/06_driver_pcb.md` — nets match the keyboard_v1.ino header; ZERO firmware changes (canonical Q→IN kept; FIRE N → cell(N/8+1)/OUT(N%8+1) preserved).
- **Rationale over alternatives:** fully-assembled PCBA (~$60–100) unnecessary — DIP sockets reuse his chips and keep chip-swap repair; off-the-shelf modules ruled out (combined 595+ULN modules basically not sold; 22 breakouts + dupont = new rat's nest); stripboard/wire-wrap = still 10 more cells of hated handwork. Proven pattern: Electronics-Lab's 72-ch 595+ULN board = same design, 9 cells.
- **PCB design improvements over perfboard as-built:** OE bus + 10k pullup to 5V routed to a 6-pin cascade header (5V·GND·DATA·CLK·LATCH·OE) → wire OE to a Mega pin (D10 suggested), set `PIN_OE`, kills the power-on random-fire risk properly (USB-first rule stays as habit). "ULN flipped" + jumper-fan lengths are perfboard artifacts — irrelevant on copper, do not re-litigate.
- **Solenoid → board connection:** screw terminals, strip-and-screw, no crimp/solder; silkscreen `S{n}-OUT{m}` + Sharpie box per terminal. §Harness and MAP discipline unchanged (84 grey + 1 orange; cut at landing; log `cell · OUT · key`).
- **Interim (THIS WEEK): breadboard fire test** — dry-fit cell #1 chips onto Daniel's breadboard, Mega D11/12/13, BOSYTRO 12V, clipped spare solenoid; USB first, then 12V; FIRE 0 → walk OUT1–8. Closes UNVERIFIED #3 (force at ~5mm bottom-out) ~2wk before boards land. Film it. Brief 01's failure modes apply.
- **Also in the wait window:** wire-tidy Phases 0–2, vision calibration (milestone 3 non-driver parts), `set_data.json`.
- Stale note to fix later: keyboard_v1.ino header comment "Cells 1-4 = Board A, 5-8 = B, 9-11 = C" → 2-board split; comment-only, edit when boards verified.
- Spreadsheet NOT edited (ask-first); brief 06 buy list added to Pending TODOs above.
- Next session: **EasyEDA design session (Claude drives via Chrome; Daniel needs a JLCPCB account)** → DRC → order.
- **Push after this session — brief 06 + this record are unpushed (milestone: driver route decision).** *(Found still uncommitted Jul 13 — committed then.)*

### July 13 session (Fable) — soldering unblocked; cell #1 built; breadboard fire test CONFIRMED DONE; PCB order greenlit

**Two milestones + one record correction.** Session was live soldering coaching + decision re-check; no code changes.

- **Soldering unblocked (root cause found).** Daniel opened wanting to abandon the PCB and "solder like a man" — symptoms: solder wouldn't stick, dull weak joints, melted insulation. Diagnosis: technique loop, not gear (YIHUA 939D+ / leaded / flux all fine; HiFind 22 AWG tinned-copper PVC wire fine, PVC just punishes dwell). Root causes: (a) oxidized/untinned iron tip; (b) top-side **lap joints** — tacking wire into an anchor hole then reheating old flux-spent solder on an already-soldered pin. **Working protocol now:** 350°C, tip tinned shiny (brass wool), pre-tin all wire ends (flux + heat-bridge blob + feed fresh solder into the wire), both wire ends terminate THROUGH a hole adjacent to the target pin, tail bent to lie against the pin's SIDE (clinch = mechanical hold, no tack joint), fresh flux + fresh solder, iron touching both, 2–3s, solder off first then iron. Perpendicular-to-row bends only (2.54mm neighbor bridge hazard).
- **Cell #1 fully soldered on perfboard (~4 hours)** — interconnect fan + components done; remaining at session end: rail taps 595 pins 16/10→+5V, 13→GND, 14→Mega DATA jumper, ULN pin 10 (COM)→+12V (the never-skip flyback joint); 595 pin 9 (cascade out) deliberately left empty. Hookup decisions: **spare DIP socket soldered on-board as the Mega connector** (logic only — DATA/CLK/LATCH, Mega 5V, Mega GND; 22 AWG solid press-fits both DIP sockets and Mega female headers); **PSU 12V/GND stay soldered** (18 AWG silicone to rails, stranded-lands-at-board rule) — DIP contacts ~1A, never for solenoid current. Single common ground: PSU V− and Mega GND both on the GND rail; +5↔+12 must meter open.
- **Record correction (was X, now Y):** was = "FIRE test still pending" (Jul 10). Now = **breadboard fire test was DONE during the Jul 10–13 wait window, exactly per brief 06 §Interim: dry-fit cell #1 chips, full Mega→595→ULN chain, solenoid at real 2×2 mounting geometry, repeated reliable key presses, characters on screen. UNVERIFIED #3 CLOSED.** Claude argued from the stale record until Daniel corrected it — the architecture and force questions were already answered; cell #1's electrical validation was partially redundant in hindsight.
- **PCB decision RE-CONFIRMED, now with data:** 4h for cell #1 (first-cell learning curve included) → even at ~2.5h/cell, 10 more cells ≈ 25h + 84 soldered low-side landings vs. screw terminals. Perfboard route declined from competence, not defeat. **Cell #1's actual value, honestly re-derived:** soldering skill (needed for buses/PSU/repairs regardless), the 4h data point, a permanent interim driver for the PCB lead window, and a known-good reference cell. Not: design validation (breadboard got there first).
- **Test plan for cell #1 (workmanship gate, not design gate):** bare-wire stubs soldered into OUT1–8 landing holes as clip points → chips-out continuity gate (3 shorts tests incl. +5↔+12 open; all nets; canonical Q0→IN1…Q7→IN8; adjacent-pin isolation) → chips in (notch!) → flash keyboard_v1 → USB first THEN 12V → clipped spare walks FIRE 0–7 → **order PCBs the same day the walk passes** → land 8 real keys during the lead (label + log `cell · OUT · key`).
- Also covered: solder-fume safety (rosin irritant not lead vapor — lead risk is hands→mouth; use the 80mm USB fan crosswind, wash hands).
- Git: Jul 10 work (brief 06, CLAUDE.md, briefs README) found **uncommitted** in the working tree at session start — committed with this record. **Daniel: push origin/main from your Terminal (sandbox can't reach GitHub). Two milestones in this one: fire test + soldering unblock.**
- Next steps: (1) finish the 5 remaining cell #1 joints; (2) continuity gate + walk; (3) EasyEDA design session → DRC → order 5 boards; (4) wait-window work: land 8 keys + MAP/WALK, wire-tidy Phases 0–2, vision calibration, `set_data.json`.

### July 13 session (later, Fable) — cell #1 PARKED; capacitor inventory locked; FULL PLATE REBUILD decided

- **Cell #1 parked as-is** (Daniel declined the remaining taps/caps for a board that retires in ~2wk). Value already banked: soldering skill + 4h data point. 8-key interim, if wanted, runs on the breadboard. **PCB order is NOT gated on cell #1** — the breadboard fire test was the design gate; "order same day the walk passes" is superseded: **order ASAP.**
- **Capacitor inventory recorded** (see §Driver design + brief 06): 0.1µF 104 ceramic 5.08mm + 4700µF 25V electrolytic (~16mm can, pitch to re-measure in mm). Nothing else — stop speccing other values. Brief-06 "100µF on 5V" → skip.
- **Cascade connector: dupont** (owns jumpers, zero purchase).
- **DECISION — FULL PLATE REBUILD NOW (was: 6-wall tab-screw plate as-built Jul 7).** Daniel's drivers: wiring dread + repair fear + no PCB home + elegance. New requirements: (a) removable walls → **revive brief 03's drop-in pocket + clamp-bar scheme** (designed Jul 5, shelved Jul 7 — geometry already 2×2-validated); (b) **wires route straight UP** (not sideways over walls) to (c) a **top deck carrying both PCBs** (new part to design: PCB M3 mounts + wire pass-through slots). Old plate's 168 screws come out one-time; rebuild lands during the ~2wk PCB lead. Wire-tidy Phases 1–2 obsolete; Phase 0 (snip frayed tips) still do. §Harness plate-side +12V bus design carries over (buses now on/under the deck — detail in CAD). Sequence: EasyEDA + order FIRST (deck is designed around the board outline + mounting-hole coords) → brief 03 caliper gates + coupon → full CAD + print during lead → boards arrive → populate → one rebuild session.
- UNVERIFIED: pocket/clamp scheme is still paper until the coupon swap-cycle test passes.
- **Push still pending on Daniel's side (sandbox git locks): commits `4f86700` + cap-inventory + this record.**

### July 15 session (Fable) — rebuild plan written: brief 07 + brief 03 amendments + resequenced milestones

Planning session for the Jul 13 rebuild decision; no hardware, no code. Three choices confirmed with Daniel via options question:
- **Deliverable = written plan + updated briefs** (not discussion-only, not straight to EasyEDA).
- **Teardown gate: old plate stays fully assembled until the coupon passes swap + fire.** Coupon fails → T-stud fallback, old plate untouched.
- **PCB order first, deck after** — deck is designed around the ordered board's exported outline + mounting-hole coords; nothing CAD blocks the order.

Built/edited:
- **`docs/briefs/07_plate_rebuild_deck.md` — NEW, the master plan.** Three tracks: A = EasyEDA → DRC → order ASAP (critical path); B = Phase-0 tip snips → caliper gates → coupon (= teardown gate) → full CAD (plate/walls/bars/deck) → print, all inside the ~2wk lead; C = boards populate/WALK → one rebuild session → MAP/WALK 88. Deck requirements section (8 items: PCB M3 mounts from EasyEDA coords, chamfered wire slots per row, 12V bus relocation, clearance stack, airflow, removability, cascade/Mega reach, L/R split). Key harness consequence documented: **boards live ON the plate assembly → the 85-wire desk harness is gone; both leads per solenoid route straight up (~40–80mm runs).**
- **`docs/briefs/03_84key_plate_cad.md` amended [Jul 15]:** status header (revived, subordinate to 07); bar lead-slots are now VERTICAL pass-throughs; wall-top +12V bus SUPERSEDED (bus moves to deck); coupon fires on the breadboard driver (cell #1 parked) and doubles as the teardown gate.
- **CLAUDE.md:** key-files line + Next milestones resequenced into tracks A/B/C; this record.
- Spreadsheet still NOT edited (ask-first). Delta noted in brief 07: brief 03 clamp hardware (inserts ~30, M3×8 pan heads ~30, EVA foam) is back on the buy list; row 39 M3×3 goes legacy after the rebuild.
- UNVERIFIED (inherited): pocket/clamp scheme until coupon; deck clearance stack has zero measured numbers until caliper gates; 4700µF can dia/pitch unmeasured.
- Next session: **EasyEDA design session → DRC → order** (Track A step 1). Daniel: create a JLCPCB account beforehand.
- **Push: Jul 13 commits (`4f86700` + cap-inventory/rebuild record) were still pending Daniel's push at last record — plus this session's brief 07 + amendments. Milestone (plan locked) → commit and push from your Terminal.**

### July 15 session (later, Fable) — fastening scheme replaced: GROOVE-SANDWICH removable walls (brief 08)

Daniel uploaded `Air75_84Key_Plate_Left/Right.stl` ("this plate design works — correct tilt, stagger") and described his own rebuild scheme, replacing brief 03's drop-in pockets.

- **Mesh audit of the uploaded STLs (trimesh, in-sandbox), then FULL cross-check vs `Full_84Key_Hole_Coordinates.csv` at Daniel's request:** watertight; 84 Ø10 holes (41 L + 43 R) — **all XY positions match the CSV, mean err 0.067mm**; wall mounting faces at hole_y+8 with **0.000 deviation** (all 12 walls, both halves; both STLs live in the CSV coordinate frame); wall thickness 2.5 exact; **all 168 tab holes** at key-x ±0.003, Z11/Z26, Ø3.30, 15mm c-t-c; plate Z0–4; walls Z32. **Two as-built corrections (was X, now Y — as-built wins, 84 solenoids mounted and working): (a) tilt was "~4.5° measured, build to measurement" → now = 4.0° exactly (leg contacts: Z−33.5 @ y≈79 back, Z−23.9 @ y≈−58.5 front, 9.6/137.5mm); (b) counterbore was "1mm deep from back face" → now = floor 1.0mm from the MOUNTING face (1.5mm deep from back face).** Note: first-pass audit hit a trimesh `to_2D()` arbitrary-frame artifact that made walls look mis-offset — direct 3D face-normal measurement is the method of record.
- **Decision (was X, now Y):** was = brief 03 drop-in pockets + clamp bars (revived Jul 13). Now = **groove-sandwich (Daniel's design): tab-screw mount KEPT; each wall is a separate part keyed into 2.75mm grooves in the plate (2mm deep) and matching grooves in the deck underside; rows assemble to their walls on the BENCH (kills the interior-access problem at the root); service = deck off, lift wall+row straight out.** Recoil load path explained to Daniel (body→wall→deck, straight up); hold-down confirmed via options question: **end posts (4 corners + 2 at seam, heat-set inserts) + wall-top pads (3/wall, insert + M3×8 through deck)**.
- **Built: `docs/briefs/08_groove_sandwich_cad.md`** — parameter table (groove datum rule: wall mounting face = hole_y+8 EXACTLY, all clearance on the back face; groove_width 2.75 coupon-validated; tab holes Z11/Z26 untouched), staged Fusion instructions (Stage 1 now: grooves, wall components, pads, posts, coupon; Stage 2 gated on body_top_z caliper gate + EasyEDA export: deck, wire slots, PCB mounts), assembly sequence, buy-list delta (~45 inserts + ~45 M3×8; EVA foam/clamp hardware dropped; M3×3 tab screws live on).
- **Amended:** brief 03 (drop-in scheme → FALLBACK #2; locked params/tilt/CSV guidance still current) + brief 07 (scheme pointer → brief 08; caliper gate `d` no longer needed, body-top + lead exits still are; coupon = groove coupon, still the teardown gate).
- **Caliper gates now easier:** measure body_top_z + lead exits on the POPULATED plate (all rows in situ) — no 2×2 needed; `d` obsolete (no seat ledges in this scheme).
- UNVERIFIED: groove clearance 0.25 until the coupon; body_top_z + lead exits unmeasured; PCB coords pending Track A; deck-lift-with-wires service flow paper (60–80mm loops = mitigation).
- Sandbox git is still lock-blocked (`index.lock` undeletable). **Daniel: from your Terminal — `rm .git/index.lock`, then commit everything (Jul 13 + both Jul 15 sessions) and push. Milestone: rebuild scheme locked.**

### July 16 session (late night) — Track A started: KiCad (not EasyEDA); cell 1 in progress; reset video scripted

- **Video:** `Video_Script_Big_Reset.md` — NEW, 45–60s short on the big reset (plate rebuild + perfboard→PCB). Post AFTER the JLCPCB order (needs the order-confirmation shot). Footage on hand: cell #1 soldering clip.
- **Tool change (was X, now Y):** was = EasyEDA via Claude-driven Chrome (Jul 10/15 plan). Now = **KiCad, Daniel driving, Claude guiding + file-verifying.** Trigger: Daniel preferred guided mode over Chrome control; KiCad's text-format files in-repo let Claude mechanically verify every net (the EasyEDA path had Claude blind without Chrome). Accepted cost: first-time KiCad learning curve. Same Gerbers → same JLCPCB order.
- **Built: `docs/briefs/06a_kicad_build_sheet.md`** — KiCad recipe companion to brief 06: symbols/footprints table, ref-designator scheme (cell n: U{n}1=595, U{n}2=ULN, J{n}1–4, C{n}1; J70/J71/J72/R1/CB1–3 board-level), pin-by-pin tables, KiCad-vs-datasheet pin-name translation (SER=DS etc.), 10-step workflow with verification gates.
- **MEASURED: 4700µF cap = Ø17mm can × 25mm tall, lead pitch ~8mm → footprint `CP_Radial_D18.0mm_P7.50mm`.** The 25mm height = first real number in brief 07's deck clearance stack (likely tallest part on the board).
- **State: KiCad project at `pcb/solenoid_driver/solenoid_driver.kicad_pro`** (Claude fixed a macOS colon-in-filename from typing "pcb/solenoid_driver" as the project name). U11 (74HC595) + U12 (ULN2803A) placed, refs verified in-file. **Cell 1 wiring NOT started — Daniel went to sleep (good call over 2am wiring).**
- **Verification protocol agreed (5 gates before ordering):** Claude file-checks cell 1 → paste ×5 → Claude re-checks all nets → ERC zero → DRC zero → 1:1 paper print with real parts. Nothing ordered until all pass.
- **Next session (pick up exactly here):** open `solenoid_driver.kicad_pro` → wire cell 1 per the 06a pin tables (8 Q→IN wires, power symbols, 5 net labels, J11–J14, C11) → say "verify" → paste ×5 + cascade-label edits → board-level parts → ERC → footprints → layout → order. Build sheet 06a §Workflow is the checklist.
- **Push:** everything from Jul 13 onward is still unpushed (sandbox git lock) — plus tonight's video script, build sheet, and pcb/ folder. From your Terminal: `rm .git/index.lock`, commit, push.

### July 22 session (Opus) — schematic verified complete; screw-terminal + Mega + board-count decisions; layout gated on a board-size fork

Daniel opened the finished KiCad **PCB** (all 6 cells wired since Jul 16) and asked what the board is / whether it's correct, then how to finish, how many boards, and how to lay out the terminals.

- **Schematic VERIFIED complete + correct** (parsed `.kicad_sch`/`.kicad_pcb` pin-by-pin, not eyeballed). Parts: 6× 74HC595 (U11–U61, DIP-16 sockets) · 6× ULN2803A (U12–U62, DIP-18) · 24× 2-pos output terminals (J11–J64 = 48 ch) · J70 12V-in · J71 cascade-IN · J72 cascade-OUT · R1 10k OE pullup · CB1 4700µF · CB2/CB3 100nF · C11–C61 per-595 100nF. Checks that PASSED: cascade DATA_IN→U11→CASC1…CASC5→U61→DATA_OUT (clean cell 1→6 daisy-chain); Q0–Q7→IN1–IN8 canonical on all cells; every ULN COM(10)→+12V (flyback); 595 VCC/MR→+5V, OE(13)→~OE bus; R1 ~OE→+5V; +5V and +12V are separate nets. **ERC 0 errors / 65 warnings (all cosmetic** — lib_symbol_mismatch + a stale `TerminalBlock:bornier` link since reassigned to `TerminalBlock_CUI:TB007-508-02` which exists). PCB has all 49 footprints placed but **NOT routed (0 tracks/0 vias/0 zones)** and **NO Edge.Cuts outline** yet — that's the remaining layout work.
- **Screw-terminal placement DECIDED:** mount terminal **bodies on the TOP (component) side, soldered on the bottom** — so screws are reachable from above once the deck is installed (the only real constraint). Current footprint is horizontal **side-entry** (`..._Horizontal`), which is correct here: mouths face **OUTBOARD** off the nearest edge; the straight-up solenoid wire rises through a deck slot just outside the board edge and turns into the mouth. Terminals line the board **edges**, chips on a **center spine**. All same orientation; `S{n}-OUT{m}` silkscreen + Sharpie box between block and edge. Keep terminals clear of the 25mm CB1 cap and the corner M3 holes. Rejected alt: bottom-mount facing the solenoids (straightest wire, but screws unreachable after assembly → sealed-module-only).
- **Mega hookup DECIDED:** keep the 6-wire **J71 header** (DATA D11 / CLK D12 / LATCH D13 / OE D10 / +5V / GND); swap loose dupont for a **JST-XH 6-pin latching connector** + **mechanically mount the Mega** on the deck. **NOT** a Mega shield (would bloat this first board for no gain).
- **Board count — measured `keyboard length = 318.9mm`.** For straight-up wiring the boards should tile the length (~106mm each → 3 boards). **KEY consequence surfaced (correction to my earlier bare "go 3 boards" rec):** 3 boards only makes sense with a **smaller ~4-cell board** — 11 cells ÷ 3 ≈ 4/board; three 6-cell boards waste capacity and are ~120–130mm (too wide to tile 3-across a 318.9mm keyboard). So the real fork, ASKED Daniel: (A) **redesign to a 4-cell board** (~100mm, tiles 3× cleanly — delete cells 5&6 = U51/U52/U61/U62 + J51–J64 + C51/C61, rewire cascade so cell-4 Q7'→DATA_OUT) vs (B) keep 6-cell / 2 boards. **→ Daniel chose (A): 4-cell × 3 boards.** Execution split (matches the "Daniel drives KiCad, Claude verifies" mode): Daniel deletes cells 5&6 in the schematic GUI + relabels U41 Q7' `CASC4`→`DATA_OUT` (safer than Claude text-editing `.kicad_sch`, which Claude can't test-open in-sandbox) → F8 Update PCB from Schematic → close KiCad → **Claude places the 4 cells + draws Edge.Cuts on the `.kicad_pcb` directly (self-rendered matplotlib verify), then Daniel reopens.** Board target ~105×62mm (16 terminal positions/long edge = 81mm, interlocking 5.08 blocks butt at pitch; 3×105≈319 tiles the keyboard). Firmware: NUM_CELLS/cascade unchanged; board is now 4-cell, populate 4/4/3 across the 3 boards, last board's 4th socket empty (chain tail).
- **Backup:** `pcb/solenoid_driver/solenoid_driver.kicad_pcb.bak_20260722` written before any layout edit.
- **Blocker:** KiCad is **OPEN** on Daniel's Mac (lock file) — my direct file edits won't take until he **closes KiCad**, else his in-memory copy overwrites them on save.
- **Layout plan (once fork answered + KiCad closed):** place cells in a row (cascade L→R, J71 left / J72 right), chips center, all output terminals on the long edges mouths-outboard (top layer), board-level parts by function → draw Edge.Cuts → **route: pour GND (bottom) + +12V (top), then hand-route the short signal/cascade traces, repeat per cell** → DRC 0 → 1:1 paper print → Gerbers → order 5 (2-layer, 1oz, HASL) → export outline + 4 M3 mount-hole coords to deck CAD (brief 07/08).
- **Push:** pcb/ changes + this record unpushed. Milestone (schematic verified) → from your Terminal: commit + push.
- **RESUME HERE (next session):** schematic trim NOT yet started — board is still 6-cell on disk. Daniel's to-do when back: in Eeschema, delete cells 5&6 (`U51/U52/J51–J54/C51`, `U61/U62/J61–J64/C61`), rename `U41` pin-9 label `CASC4`→`DATA_OUT`, save → say "saved" → **Claude verifies the `.kicad_sch` netlist** → Daniel F8 (Update PCB from Schematic) + quit KiCad → **Claude places the 4 cells + Edge.Cuts (~105×62mm) on `.kicad_pcb`, self-renders to verify** → reopen → route (GND/+12V pours + short signals) → DRC → paper print → order 5. Backup on disk: `solenoid_driver.kicad_pcb.bak_20260722`. KiCad was OPEN at session end.

### July 23 session (Opus) — 4-cell trim executed, board placed + routed (50/64 auto), 4/14 hand-routed

Long hands-on KiCad session; the Jul 22 RESUME plan executed end-to-end through routing. Daniel drives KiCad, Claude verifies every step from the file.

- **Schematic trimmed to 4 cells (Daniel, Eeschema):** deleted cells 5&6, renamed `U41` pin-9 `CASC4`→`DATA_OUT`. Claude verified `.kicad_sch`: only U11–U42, cascade `DATA_IN→U11→CASC1→U21→CASC2→U31→CASC3→U41→DATA_OUT→J72`, C11–C41 only. ✓
- **F8 gotcha (documented):** "Update PCB from Schematic" leaves deleted footprints unless **☑ Delete footprints with no symbols** is checked (leave "Re-link by reference" UNCHECKED). First attempt Daniel hit "discard changes" on quit → PCB stayed 6-cell; redo with the checkbox + ⌘S fixed it. Now 35 footprints (U11–U42, J11–J44, J70/71/72, CB1–3, R1, C11–C41).
- **Placement — Claude edited `.kicad_pcb` directly** (targeted `(at …)` rewrites via paren-matched parser, self-rendered with matplotlib to verify; KiCad NOT installable in sandbox — apt kicad 6 too heavy, no pcbnew/kicad-cli). Cascade L→R, chips center spine, 16 output terminals lining both long edges, J71 logic-in left, right column = CB1(4700µF)/J70(12V-in)/J72(cascade-out), R1 bottom-left, 4 corner M3 holes. **BOARD SIZE (was X→now Y): target ~105×62 → actual `120×66mm`** (cell pitch 20.5 to clear DIP courtyards; forced by 4 side-by-side DIP pairs ~80mm + 18mm bulk-cap column). **Daniel ACCEPTED 120×66** via options question — deck (brief 07/08) sizes to match; 3×120=360 on the deck overhangs the 318.9 keyboard, fine (deck holds boards, wire slots placed individually).
- **Edge.Cuts:** rectangle (100,100)-(220,166) + 4 corner Ø3.2 mount holes, appended as `gr_line`/`gr_circle` on Edge.Cuts. File paren-balance verified after every edit. Format = KiCad 10 (version 20260206; pad/segment nets are `(net "name")` with NO numeric index — earlier regex missed them).
- **Terminal mouth orientation:** silkscreen analysis of `TB007-508-02` → wire-entry mouth on **+Y** side. At rot 0 that points "down." Bottom row (near bottom edge) already correct; **top row flipped to rot 180**, recentered about body center (`at = old_x+5.68, 109.45, 180`) so bodies stay in place, mouths now point off the top edge. Confirmed by mouth-arrow render + Daniel's 3D view. J70 (12V-in) mouth faces down — Daniel accepted (single power pair from bottom edge).
- **GND pour (guided, Daniel drew it):** B.Cu filled zone, drawn oversized (98.5..221 / 98.5..168.5) → KiCad auto-clips to board edge. Verified in file: `(zone (net "GND")(layer "B.Cu")(fill yes)…)`, 4 filled_polygons. Handles ALL ground pins via the plane (~30 connections, no traces) — that's why GND-side legs (e.g. CB1 leg 2) show no trace, correct.
- **Routing = HYBRID** (Daniel chose via options: guided pours + autoroute rest). Autorouter = **Freerouting v2.2.4 on Daniel's Mac** (macOS installer bundles Java; sandbox GitHub BLOCKED so Claude can't run it headless). Flow: KiCad `File→Export→Specctra DSN` (`solenoid_driver.dsn`: 35 comp, 75 nets, **GND exported as a `(plane …)` on B.Cu**) → Freerouting autoroute (the b-roll money-shot) → `File→Export Specctra Session` (`.ses`, 100 wires/5 vias; "save rules as separate file? → No") → KiCad `File→Import→Specctra Session`. **Import gotcha:** looked like "nothing happened" — traces imported fine, view just needed **Home/zoom-to-fit**. Board now 336 segments (119 F.Cu / 217 B.Cu) + 5 vias.
- **Autoroute result: 50 of 64 signal connections done, 14 open.** Claude's connectivity audit (union-find over pads[abs-pos]+segments+vias, GND excluded as plane) reproduced exactly 14. The 14: **6 output hops** (U12/U22/U32 O3,O4 → J12/J22/J32) + **8 bus fills** (SCLK pin11 / RCLK pin12 / OE pin13 not fully chained across the four 595s — GND-plane-on-bottom crowds signals onto top).
- **Daniel hand-routed 4 of the 6 easy output hops** (U12.16→J12.1, U12.15→J12.2, U22.16→J22.1, U22.15→J22.2), on F.Cu; taught: X=route, click pad→pad (KiCad walks around obstacles), V=via to bottom when a terminal is crowded on top, length/shape don't matter (slow signals). **Saved: 368 segments, 10 open.** Then stopped for the night (~3:40am).
- **Teaching notes for beginner KiCad (Daniel):** copper pour = ground plane concept; F.Cu vs B.Cu (route signals on top to keep the bottom plane intact, V to dip under); "nothing changed" was always zoom/refresh; the `.ses` (not `.kicad_pcb`) is what Freerouting opens.

**RESUME HERE (next session) — finish the last 10 connections, then order:**
Open the PCB editor. 10 airwires remain. Route each (X, click pad→pad; use **V** to drop to B.Cu where the top is blocked — several bus ones weave past the ULNs):
- **2 output hops (route via bottom near the terminal — top is jammed):** `U32 pin16 → J32 pin1`, `U32 pin15 → J32 pin2`.
- **8 bus fills** (595 right-column pins; these weave past the ULNs → drop to B.Cu with V for the crossings):
  - SCLK (pin 11): `U21.11→U31.11`, `U31.11→U41.11`
  - RCLK (pin 12): `U11.12→U21.12`, `U21.12→U31.12`, `U31.12→U41.12`
  - OE (pin 13): `U11.13→U21.13`, `U21.13→U31.13`, `U31.13→U41.13`
Then **Inspect→Design Rules Checker** (expect 0 unconnected, 0 clearance errors) → Claude re-audits the file → **1:1 paper print + dry-fit real parts** (sockets, 5.08 terminals, 25mm CB1 cap) → export Gerbers → **order 5 (2-layer, 1oz, HASL) from JLCPCB** → export board outline + 4 M3 mount-hole coords to deck CAD (brief 07/08). **Fallback if the 8 bus fills are painful by hand:** delete GND zone → re-export DSN → Freerouting (2 free layers → likely 0 unrouted) → re-import → re-add GND zone.
- Backups on disk: `solenoid_driver.kicad_pcb.preplace` (4-cell, pre-layout), `.bak_20260722` (original 6-cell).
- **Git:** Claude committed the 4-cell trim + placement as `aa0b684` mid-session; end-of-session commit (routing import + 4 hand-routes + this record) pending. **Daniel: push origin/main from your Terminal** (sandbox can't reach GitHub; if a lock complains, `rm -f .git/HEAD.lock .git/index.lock` first). KiCad was OPEN at session end (lock files present).

### July 24 session (Opus) — ROUTING COMPLETE: last 10 connections closed in-file, GND repaired, +12V widened, board DRC-clean

Daniel: "im back. lets finish this pcb." Claude drove the whole routing close-out directly in `.kicad_pcb` (Daniel chose this over re-running Freerouting or hand-routing), then audited it numerically. **The board is now fully routed: 0 open connections, 0 clearance violations.**

- **Confirmed the Jul 23 state from the file, not the record:** union-find over pads+segments+vias (GND excluded as plane) reproduced **exactly 10 open** — the 2 U32→J32 output hops + 8 bus fills (SCLK ×2, RCLK ×3, OE ×3). File unchanged since Jul 23 03:36; KiCad lock file still present.
- **Key geometric discovery (why the bus fills were hard, and how they're possible at all):** the 74HC595 (16-pin) and ULN2803A (18-pin) pad rows are offset by **exactly half a 2.54 pitch** — every 595 pin-y (124.11+n·2.54) falls midway between two ULN pin-y (122.84+n·2.54), and vice versa. So a bus trace at a 595 pin's y slips cleanly between ULN pads, and must dodge ±1.27 only where it crosses the *destination* 595's left pad column. The one bus hop Freerouting DID complete (U11.11→U21.11) uses exactly this dogleg — it was the proof the pattern works. **The hard constraint is the 2.38mm gap between the ULN right pad column (x=132.12) and the next 595 left column (x=134.5): too narrow for a via (needs 1.42mm to each pad, only 1.19mm available), so the crossing must be a trace dodge, not a layer change.**
- **Method: custom A* grid router written in-sandbox** (0.1mm grid, both layers, via cost 60, turn penalty, obstacle rasterization from real pad/segment/via geometry), then string-pull simplification, then numeric clearance verification. **Netclass honoured: 0.2mm track / 0.2mm clearance / 0.6mm via / 0.3mm drill** — routes were *verified* at 0.25mm width (conservative) and *written* at 0.2mm.
- **Bug caught by the audit, not by eye:** first pass routed all 10 nets independently against the original board → **162 violations, all three new bus nets colliding with each other** in the same free band. Fix = route **sequentially**, appending each finished route to the obstacle set. Tried 6 orderings; **"gapwise RCLK→SCLK→OE" (column gap by column gap, middle lane first) is the one that solves all 10.** Second bug: two same-net /RCLK vias landed 0.07mm apart (hole-to-hole fail) → merged the second hop onto the first hop's via at (136.62,134.97).
- **Result: 97 segments + 22 vias added for the 10 connections.** Paths run 19–45mm through the free band below the chip row — long and not pretty, but SCLK/RCLK are slow shift-clock signals and OE is static, so length is irrelevant. Green traces in `pcb/solenoid_driver/routing_final_verify.png`.
- **GND repair (Daniel asked for the audit).** Simulated the zone refill on a 0.1mm raster (0.5mm zone clearance) and flood-filled: the new traces cut **U21.8, U31.8, U41.8** (595 GND pins) onto small plane islands; **J72.2 was already orphaned before this session** (pre-existing, would have shipped broken). Fixed with 4 explicit GND traces (17 segs + 3 vias, 0.3–0.4mm): U21.8→U12.9, U31.8→U32.9, U41.8→U32.9, J72.2→CB3.2. **All 18 GND pads now verify as one electrical group** (union-find over pads + GND traces + plane islands).
- **High-current path measured, not assumed.** Solenoid return is ULN pin 9 → B.Cu plane → J70.2. Widest-path/bottleneck analysis (distance transform on the simulated fill): narrowest neck **1.13mm (U12/U22/U32), 1.00mm (U42)** ≈ **2.4–2.6A at 10°C rise** by IPC-2221. Worst case is 7 solenoids on one board = 2.1A (firmware MAX_ON=7, and that's global across 3 boards, so realistically ≤3–4/board ≈ 0.6–1.2A). **Adequate — left as-is.**
- **+12V widened as free insurance:** Freerouting had left the whole +12V net at 0.2mm. Widened 14 of 15 segments to the max each location allows (0.8mm mostly, one 0.6, two long 18.2mm runs limited to 0.3mm). ULN COM flyback current now has real margin. +5V left at 0.2mm (logic only). **The two 0.3mm runs are the +12V bottleneck (~1.3A @10°C) — fine for flyback, worth knowing.**
- **Full-board DRC replicated in-sandbox: 0 violations.** Checked seg-seg, seg-pad, via-pad, via-seg, via-via, hole-to-hole, board-edge, across all 482 segments / 30 vias / 198 pads. **Method note (was X, now Y): a square-envelope pad model reported 64 false violations; pads are 1.6mm circles (170), roundrect (26, rratio 0.156/0.104 → 0.25mm corner radius), rect (2). With true shapes all 64 clear** — the 4 tightest (0.300–0.381mm vs 0.300 required) are pre-existing Freerouting traces at roundrect pin-1 pads, legal but with no margin.
- **CRITICAL — the zone's stored fill was stale and would have shorted the new B.Cu traces in the Gerbers.** Claude **stripped all 4 `filled_polygon` blocks** from the GND zone so the board cannot be plotted with a stale fill. **Consequence: the zone is now UNFILLED on disk — Daniel must press `B` (Edit→Fill All Zones) after opening, before DRC and before plotting.** Failure mode is now fail-safe (missing plane → DRC screams) instead of fail-dangerous (silent copper short).
- Backup written before any edit: `solenoid_driver.kicad_pcb.prefinal` (368 segs / 5 vias = the Jul 23 state). Earlier backups `.preplace` and `.bak_20260722` still on disk.

**RESUME HERE (next session) — 4 steps to an ordered board:**
1. **Quit KiCad first if it's open** (lock file was present all session) choosing **discard changes**, then reopen `solenoid_driver.kicad_pro` → PCB editor.
2. **Press `B`** to fill zones (the fill was stripped on purpose — see above). Then **Inspect→Design Rules Checker**. Expect **0 unconnected, 0 clearance**. If anything appears, it is almost certainly a zone-fill or netclass difference, not geometry — send Claude the DRC text.
3. **1:1 paper print + dry-fit real parts**: DIP sockets, 5.08mm screw terminals (check the mouths face outboard off the edges), CB1 4700µF Ø17×25mm can.
4. **Plot Gerbers → order 5 (2-layer, 1oz, HASL) from JLCPCB.** Same day: export board outline (**120×66mm**) + the 4 corner M3 mount-hole coords → deck CAD (briefs 07/08). Board is 120×66, so 3 boards tile to 360mm over a 318.9mm keyboard — deck sizes to the boards, wire slots placed individually.


**AMENDMENT (same session, after Daniel ran DRC in KiCad) — 2 real shorts found; checker bug owned and fixed.**

Daniel filled zones (`B`) and ran DRC: **220 violations, but 0 unconnected pads.** Breakdown: 193 `silk_overlap` (warnings — adjacent terminal-block silk outlines butting; JLCPCB clips silk, ignore), 14 `courtyards_overlap` (the 5.08 blocks interlock by design — pre-existing from placement), 8 `lib_footprint_mismatch` (the known TB007-508-02 relink, cosmetic), 3 `starved_thermal`, and **2 `tracks_crossing` — actual copper shorts, and mine.**

- **Root cause (my bug, not KiCad's):** `seg_seg_dist()` returned `min(endpoint→segment distances)`. For two segments that cross in an X, every endpoint is far from the other segment, so the function returns a large value and the crossing is invisible. The A* router itself was fine — it rasterizes obstacles and can't cross them. The crossings were introduced by the **string-pull simplification step**, which validated its shortcuts with that same blind function. **Lesson: a distance function is not an intersection test. Any clearance checker needs an explicit segment-intersection predicate.** Fixed with a CCW-orientation test (plus collinear-overlap case), unit-tested on 4 synthetic cases, and patched into *both* copies (the router's and the standalone DRC's — the second copy shadowed the first and silently kept the bug through one whole verify cycle).
- **Redone from `.prefinal` with the fixed checker.** Same sequential gapwise RCLK→SCLK→OE order still solves all 10; two paths changed (J32-Pin_2 30.9mm was 24.1, RCLK mid-hop 45.5 was 44.6) because the crossing shortcuts are no longer allowed. Same-net RCLK via merge at (136.62,134.97) reapplied.
- **`starved_thermal` addressed properly.** KiCad flagged U22.9, U42.9, C11.2 as connected to the plane by a single spoke onto an isolated island — my raster sim had scored them "connected," so **KiCad's fill is stricter than my simulation; trust KiCad's fill over the raster.** GND traces extended from 4 links to **8**: U21.8→U12.9, U31.8→U32.9, U41.8→U32.9, U22.9→U12.9, U42.9→CB3.2, J72.2→CB3.2, C41.2→CB2.2, C11.2→C21.2 (34 segs + 8 vias, 0.3–0.4mm). Every GND pad now has explicit copper, not just plane. All 18 still verify as one group; J70.2 (PSU ground) is in it.
- **Re-verified: 503 segments / 35 vias, 0 open connections, 0 clearance violations, 0 crossings.** The only 4 items my checker still reports are the pre-existing Freerouting traces at roundrect pin-1 pads (0.202–0.277mm by a plain-rect model); with the true 0.25mm corner radius they measure 0.300–0.381mm and pass — and KiCad's own DRC did not flag them, which confirms it.
- Zone fill stripped **again** (the `.prefinal` restore brought the Jul 23 stale fill back with it). Press `B` before DRC and before plotting, every time.

**DRC3 (post-fix, 15:10) — CLEAN. `tracks_crossing` 0, `starved_thermal` 3→1, `0 unconnected pads`.** Remaining 216 = 193 silk_overlap + 14 courtyards_overlap + 8 lib_footprint_mismatch (all pre-existing/cosmetic, see above) + 1 starved_thermal on **C11.2**. Diagnosed: four B.Cu traces (U11-QB, U11-QD, J11-Pin_1/2) fence the pad in, leaving one thermal spoke into a small pocket — but the pad carries the explicit 0.4mm × 21.7mm GND trace to C21.2 on the main plane, which is why connectivity passes. **Second confirmation that KiCad's fill is stricter than my raster (my sim scored C11.2 as sitting directly on the main island); trust KiCad.** Not chased further: DIP packages put VCC/GND on opposite corners so the decoupling loop is inherently large here, and 100nF on a slow 595 is forgiving. **Daniel's call: exclude the violation and proceed.** Board is GO for paper print → Gerbers → order.

**SILKSCREEN GAP CAUGHT WHILE TRIAGING THE 216 (pre-order save).** Answering "do I ignore the 216?" meant checking what the silk items actually were — all 361 overlapping items are footprint *outlines* (terminal blocks butting at 5.08 pitch) plus a few reference fields, so yes, ignorable. **But the check exposed that every useful label existed only as a footprint Value field on `F.Fab`, hidden — and F.Fab is not manufactured.** The boards would have arrived with `J11`–`J44` designators and nothing saying which OUT is which, directly undermining the MAP discipline (label holes, log `cell · OUT · key`) during the 84-wire landing session. The Jul 22 plan had called for `S{n}-OUT{m}` silkscreen; it was never actually on a manufactured layer.
- **Fix: 19 board-level `gr_text` items added on `F.SilkS`** (0.9mm height / 0.15 thickness — above JLC's 0.8mm minimum). Chose board-level `gr_text` over unhiding the Value properties deliberately: footprint text inherits the footprint's 180° rotation and would print upside-down on the whole top row.
- **Labels are per-cell, not bare OUT numbers:** `C1-OUT1/2` … `C4-OUT7/8`. First pass generated bare `OUT1/2`, which reads identically on J11/J21/J31/J41 — ambiguous across all four cells. Cell numbering is board-local by necessity (global channel depends on cascade position: board A = cells 1–4, B = 5–8, C = 9–11), so the silk cannot carry global channel numbers. Plus `12V-IN` (J70), `CASC-IN` (J71), `CASC-OUT` (J72).
- **Placement: outboard of the blocks** — top row at y=102.5 (above), bottom row at y=164.2 (below), both in empty silk bands. Inboard was rejected: the y≈117 band puts text within 0.7mm of the C11/C21/C31/C41 cap pads. Verified programmatically against every pad (0.35mm), every silk line/arc/circle/rect (0.25mm — CB1's Ø18.2 silk circle clears `12V-IN` by 0.375mm), the board edge, and the labels against each other.
- **Copper untouched: still 503 segments / 35 vias, 0 open, 0 clearance violations.** Render: `pcb/solenoid_driver/silkscreen_labels.png`.

**DRC4 (15:31) — silkscreen labels verified clean: 216 violations, byte-identical makeup to DRC3** (193 silk_overlap UNCHANGED → the 19 new labels added zero overlaps; 14 courtyards_overlap; 8 lib_footprint_mismatch; 1 starved_thermal on C11.2, excluded by Daniel). **0 unconnected pads.** **PCB IS DONE — 503 segments / 35 vias / 120×66mm / 0 open / 0 clearance / 0 crossings.**

**NUMBERS FOR DECK CAD (briefs 07/08) — hand these to Fusion, no need to reopen KiCad:**
- Board outline: **120.0 × 66.0 mm** (Edge.Cuts x 100–220, y 100–166 in KiCad absolute).
- **4 × M3 mount holes, Ø3.20mm, board-relative: (4, 4) · (4, 62) · (116, 4) · (116, 62)** — i.e. 4mm inset from each corner, 112 × 58mm hole pattern.
- Tallest part: **CB1 4700µF, Ø17 × 25mm can** — drives the deck clearance stack.
- Terminal mouths face **outboard off both long edges** (top row y≈104 side, bottom row y≈162 side) → deck wire slots go just outside those edges, not over the board.
- 3 boards × 120mm = 360mm across a 318.9mm keyboard: deck sizes to the boards; wire slots placed individually per brief 07.

**Git: Claude committed this session's routing + record. Daniel — push origin/main from your Terminal** (sandbox can't reach GitHub). Everything from Jul 13 onward may still be unpushed; if a lock complains, `rm -f .git/HEAD.lock .git/index.lock` first. **Milestone: PCB routing complete — this is the last gate before the order.**

### July 24 session (later) — beginner Q&A captured as build knowledge; +12V bus feed refined

End-of-session Q&A with Daniel (self-described PCB beginner). Answers verified against the board file, not given generically. Recording them because they are the assembly instructions for when the boards land.

- **"If the back is all GND, isn't every component connected to GND?" — NO, and the numbers matter: 18 of 198 pads are on the GND net; the other 180 sit in a 0.5mm clearance moat carved out of the pour.** The zone is not a solid sheet — KiCad's fill computes an isolation gap around every non-GND pad and trace, and thermal spokes into every GND pad. This holds for through-hole parts because the plated hole has a pad on both faces, and on B.Cu the plane simply isn't present at the non-GND ones. Worked example given: U11 pin 8 (GND) sits in copper; pins 11/14/16 (SCLK/DATA_IN/+5V) are isolated.
- **Sockets vs chips: solder the EMPTY sockets, press chips in afterward** — the whole reason sockets were specified (brief 06). No soldering heat into the chips, and a dead ULN channel becomes a screwdriver swap rather than desoldering 18 pins.
- **Assembly order recorded (shortest part first, so the board lies flat while soldering):** R1 (10k) → 100nF ceramics (C11–C41, CB2, CB3) → DIP sockets, notch left, matching silkscreen → screw terminals, mouths outboard → **CB1 4700µF last (25mm tall, fouls everything)**. Chips in last, notch matching socket notch.
- **Terminal maths confirmed from the file: 16 blocks × 2 screws = 32 outputs per board.** 3 boards = 96 positions; 84 solenoids land; board 3 populates only 3 cells (11 cells × 8 = 88 channels, last socket = chain tail).
- **PROPOSED REFINEMENT — needs Daniel's confirmation next session (was X, now Y).** Was (§Harness, Jul 2026): deck/plate +12V bus "fed by ONE 18 AWG +12V wire **from the board rail**." Now proposed: **feed the bus DIRECTLY from the PSU, in parallel with each board's J70 pair.** Rationale: keeps the ~2.1A solenoid supply current out of board copper entirely, so board +12V carries only ULN COM flyback — which is what the Jul 24 current analysis assumed when it declared the widened +12V (0.8mm, two 0.3mm necks) adequate. Under the old wording the board's +12V traces would have carried full solenoid supply current and 0.3mm would be marginal. **Claude stated the new topology as fact when answering Daniel; flagging it here as a refinement to confirm rather than burying it.** J70 is still required on every board regardless — it powers the ULN COM pins and therefore the flyback diodes.
- Current loop, as explained: `PSU +12V → deck bus → solenoid high side` / `solenoid low side → grey 22 AWG → screw terminal → ULN → B.Cu ground plane → J70 pin 2 → PSU −`. The plane carries the full solenoid return; that is the path measured at 1.13mm / ~2.5A vs 2.1A worst case.

**RESUME HERE — the PCB is DONE, nothing blocks the order:**
1. **Paper print** (File → Print, scale 1:1, F.Cu + F.Silkscreen + Edge.Cuts). **Measure the printout — must be 120mm wide**, else the printer scaled it. Dry-fit DIP sockets, 5.08 terminals (mouths outboard), CB1 Ø17×25mm can.
2. **Plot Gerbers**: format Gerber, layers F.Cu/B.Cu/F.Silkscreen/F.Mask/B.Mask/Edge.Cuts, coordinate format 4.6, **uncheck** "Use extended X2 format" and "Include netlist attributes" → Plot → **Generate Drill Files** (Excellon, **check "Merge PTH and NPTH into one file"**, mm, absolute origin) → zip the output folder.
3. **Order 5 from JLCPCB**: 2-layer, 1.6mm, 1oz, HASL. ~$10–20 shipped.
4. Same day: hand the deck-CAD numbers (above) to Fusion — brief 07/08 Stage 2 unblocks the moment the order is placed.
5. Confirm the +12V bus feed refinement above.
6. **Standing rule discovered this session: press `B` to fill zones before every DRC and before every plot.** A stale fill is invisible and would short the new B.Cu traces in the Gerbers.

**Git: everything from Jul 13 onward is staged but UNCOMMITTED — the sandbox cannot delete `.git/HEAD.lock` (stale since Jul 23 01:31). Daniel, from your Terminal:**
```
cd ~/Documents/Claude/Projects/Physical\ AI\ Agent
rm -f .git/HEAD.lock .git/index.lock
git commit -m "PCB complete: routing closed, GND repaired, +12V widened, silkscreen labels, DRC clean"
git push
```
**Milestone: the driver PCB is finished and verified. This is the last gate before spending money.**

### July 26 session (Opus) — pre-order assembly Q&A; power topology finalized; J70 polarity silk added

Daniel came back with assembly questions *before* ordering. No routing changes; one silkscreen addition. Every answer below was verified against `solenoid_driver.kicad_pcb` (pad-by-pad net extraction), not given generically. **Nothing has been ordered yet.**

**Q1 — screw terminals.** Confirmed: each terminal position is one ULN2803A output = the **low side** of a solenoid (the ULN is a low-side switch to ground). Coils aren't polarized, so "high"/"low" lead is whichever is convenient. **Count, corrected for the 3-board plan: 16 blocks × 2 screws = 32 positions/board → 96 physical, but only 88 are DRIVEN** (board C populates 3 cells, so its 4th cell's blocks J41–J44 are dead copper), **84 used, 4 driven spares.**

**Q2 — do NOT bundle 84 high-side wires to the PSU.** §Harness already answers this: bare 16 AWG bus, ~5cm hop per solenoid, one feed. Restated for Daniel with the full loop.

**POWER TOPOLOGY — FINALIZED (see the corrected §Harness bullets above; this is the substantive decision of the session).** Daniel confirmed "bus direct from PSU," then surfaced the real constraint: **his PSU has only 3× V+ and 3× V−.** Four wires on V+ (bus + 3 boards) doesn't fit. Resolution: make the **bus the trunk** — 1 wire on V+ to the bus; each board's J70 pin 1 stubs off the bus; 3 wires on V− (one per board). Fits with 2 V+ terminals spare, and is *better* than the 4-wire version because it makes each board a dead-end leaf. Full rationale + the CB1 consequence written into §Harness.

**Full power system, as explained (two supplies, meeting only at ground):**
- **12V rail:** AC → BOSYTRO 480W/40A → V+ → one 18 AWG → deck bus → ~5cm hop → solenoid high lead. Low lead → grey 22 AWG → screw terminal → ULN output → B.Cu ground plane → J70 pin 2 → V−. Separately: bus stub → J70 pin 1 → board +12V net → 4× ULN COM + CB1. **Peak 2.1A against 40A = ~5% loaded.**
- **5V rail:** MacBook USB → Mega → 6 wires (5V/GND/D11 DATA/D12 CLK/D13 LATCH/D10 OE) → board A J71 → 595 VCC/MR + R1 pullup → passed onward via J72→J71 to boards B, C. **~10mA total** — trivial for the Mega's regulator.
- **They meet at GND only.** Mega GND arrives at board A on J71 pin 2; board A's plane reaches V− on J70 pin 2 → same node. Mandatory: a 595 output only means anything to a ULN input if both reference the same ground. **+5V and +12V must meter OPEN.** Mega needs no PSU terminal of its own.
- **Power-on order: USB first, THEN 12V** (595s hold garbage until clocked). The R1/OE-to-D10 pullup is the real fix; keep the habit anyway.

**Q3 — cascade connectors. Verified from file: J71 and J72 are both `PinHeader_1x06_P2.54mm_Vertical`, straight-through pinout — 1:+5V · 2:GND · 3:DATA · 4:SCLK · 5:RCLK · 6:~OE** (J71 pin 3 = DATA_IN, J72 pin 3 = DATA_OUT). So a **pin-1-to-pin-1 6-wire cable, no crossover**. Chain: Mega → A.J71 · A.J72 → B.J71 · B.J72 → C.J71 · C.J72 unused.
- **Gotcha found: Daniel's dupont stock (M-M and M-F only) cannot span board-to-board.** Male headers on both boards would need **F-F**, which he doesn't own.
- **DECIDED (Daniel: "cheapest and easiest") — board-to-board links are HARDWIRED:** solder 6 short 22 AWG solid wires directly through J72's holes into the next board's J71 holes. Zero purchase, no contact resistance, can't vibrate loose; the 3 boards bolt to one deck and never separate. Cost: 6 desolder joints if a board ever comes out.
- **Mega → A.J71 stays connectorized:** solder a 6-pin male header into J71, use 6× **male-to-female** dupont (female on the board pin, male into the Mega). Works with what he already owns. *(Supersedes the Jul 22 "JST-XH for the Mega link" note — not bought, not needed.)*

**Q4 — J70. "12V-IN" names the whole 2-position block, not one screw; BOTH screws are used.** From the file: **pin 1 = +12V, roundrect pad, inboard at x=201.00**; **pin 2 = GND, circular pad, at x=206.08** (nearer the right board edge). Mouth faces +Y.

**CAUGHT AND FIXED BEFORE ORDERING — J70 had no polarity marking.** The Jul 24 silkscreen pass added `12V-IN` but nothing saying which screw is which. Reversing the pair forward-biases all 8 ULN flyback diodes straight to ground = dead short through the chip. Fix: **two `gr_text` items on F.SilkS — `+12V` at (201.00, 146.2) and `GND` at (206.08, 146.2)**, directly beneath their screws on the wire-entry side, size 0.9 / thickness 0.15 (same as the Jul 24 batch). Verified numerically: nearest pad 2.48mm, nearest silk 1.60mm, no text-to-text collision, edge clear. **Copper untouched — still 503 segments / 35 vias, so DRC is unchanged.** Backup: `solenoid_driver.kicad_pcb.presilk2`. Render: `pcb/solenoid_driver/j70_polarity_labels.png`. Commit **`ae34946`**.
- *Method note (holds up): board-level `gr_text` again, not unhidden footprint Value fields — footprint text inherits footprint rotation. And the free band **below** J70 (y 143.5–148.6) was chosen over the band above (y 129.1–133.0), which is only 2.9mm tall and already holds `12V-IN`.*

**Assembly notes restated for when boards land** (from the Jul 24 later record, re-confirmed): solder **empty sockets**, press chips in after; order shortest-part-first — R1 → 100nF ceramics → DIP sockets (notch left) → screw terminals (mouths outboard) → **CB1 4700µF last** (25mm, fouls everything).

**Files changed this session:** `pcb/solenoid_driver/solenoid_driver.kicad_pcb` (+2 gr_text), new `j70_polarity_labels.png`, new `.presilk2` backup, CLAUDE.md §Harness correction + this record.

**UNVERIFIED / open:**
- KiCad lock files (`~*.lck`) were still on disk from Jul 24 15:23 at session end — **stale, but unconfirmed.** If KiCad is open when Daniel returns, **quit discarding changes** before reopening, or the in-memory copy overwrites the new silk.
- DRC not re-run after the silk addition (expect DRC4's exact 216 makeup, 0 unconnected — the labels sit in an empty silk band).
- Deck bus stub lengths/gauge unbuilt; everything in §Harness is still paper.

**RESUME HERE — nothing blocks the order:**
1. Quit KiCad if open (discard) → reopen → **press `B`** to fill zones → DRC (expect 216 known/cosmetic, 0 unconnected).
2. **1:1 paper print** (F.Cu + F.SilkS + Edge.Cuts). **Measure it: must be 120mm wide.** Dry-fit DIP sockets, 5.08 terminals (mouths outboard), CB1 Ø17×25mm.
3. **Plot Gerbers** — format Gerber, layers F.Cu/B.Cu/F.SilkS/F.Mask/B.Mask/Edge.Cuts, coords 4.6, **uncheck** "Use extended X2 format" and "Include netlist attributes" → Plot → **Generate Drill Files** (Excellon, **check "Merge PTH and NPTH"**, mm, absolute origin) → zip. *(Daniel asked me to walk these settings when he gets there.)*
4. **Order 5 from JLCPCB:** 2-layer, 1.6mm, 1oz, HASL. ~$10–20.
5. Same day: deck CAD numbers → Fusion (briefs 07/08 Stage 2 unblocks): **outline 120×66mm · 4× Ø3.20 M3 holes board-relative (4,4)/(4,62)/(116,4)/(116,62) · tallest part CB1 Ø17×25mm · terminal mouths outboard off both long edges.**
6. Then: `Video_Script_Big_Reset.md` short can post (needs the order-confirmation shot).

**Git: committed `ae34946` (silk) — this record + the §Harness correction still need committing. Daniel, from your Terminal:**
```
cd ~/Documents/Claude/Projects/Physical\ AI\ Agent
rm -f .git/HEAD.lock .git/index.lock
git add -A && git commit -m "Power topology finalized (bus from PSU, boards as leaves); J70 polarity silk; Jul 26 record"
git push
```
*(Sandbox git can create commits but cannot delete the stale lock files or reach GitHub — the push is always Daniel's.)*

### July 26 session (later, Opus) — GERBERS PLOTTED, AUDITED, ZIPPED; firmware OE bug caught; rev-2 declined

Daniel asked for an exhaustive pre-order check ("so i dont waste $100+ and weeks"). Everything below was re-derived from `solenoid_driver.kicad_pcb` and the plotted Gerbers by parsing them, not from this record.

- **DRC10 (22:59) = byte-identical makeup to DRC4**: 216 = 193 silk_overlap (warning) + 14 courtyards_overlap + 8 lib_footprint_mismatch (warning) + 1 starved_thermal (C11.2). **0 unconnected pads, 0 footprint errors.** The J70 polarity silk added **zero** new silk_overlap — confirms it landed in the empty band.
- **FIRMWARE BUG CAUGHT — would have silently killed a bring-up session.** `keyboard_v1.ino` line 60 had `PIN_OE = 255` ("OE hard-wired to GND, as-built") — true of the breadboard, **false of the PCB**, which carries R1 (10k) holding ~OE HIGH = **all outputs disabled**, with ~OE routed to J71 pin 6. Firmware never drove it → serial responds, WALK prints all 88 channels, **nothing ever fires**, no diagnostic. Fixed: `PIN_OE = 10`; power-on-safety header rewritten (the mod is installed, not hypothetical, and a floating ~OE is now called out explicitly); per-cell wiring note updated. setup() sequence re-read and correct (pinMode→HIGH→clear registers→LOW), and D10 is Hi-Z between reset and pinMode so **R1 makes that window fail-safe**. Mock-compiled in-sandbox against stub Arduino.h/EEPROM.h with `-Wall -Wextra`: **clean, zero warnings.** Chosen via options question over strapping J71 pin 6 to GND. **Header note "Cells 1-4 = Board A, 5-8 = B, 9-11 = C" — flagged stale Jul 10 (2-board split), is ACCURATE AGAIN under 4-cell × 3 boards populated 4/4/3. No edit needed.**
- **FULL PRE-ORDER AUDIT — 23 checks, all pass.** Netlist: 595 VCC16/GND8/MR10/SHCP11/STCP12/OE13/DS14 correct ×4; cascade DATA_IN→U11→CASC1→U21→CASC2→U31→CASC3→U41→DATA_OUT→J72 unbroken; **32/32 canonical Q→IN** (Q0=pin15, Q1–Q7=pins1–7 → IN1–IN8); **32/32 ULN OUT→terminal** (pin18=OUT1 … pin11=OUT8 → J{c}1..J{c}4); ULN COM(10)=+12V and GND(9)=GND ×4; CB1 pin1(+)=+12V pin2(−)=GND; R1 +5V↔~OE; J70 pin1=+12V pin2=GND; J71/J72 straight-through, **both run pin1→pin6 in the same +y direction** → pin-1-to-pin-1 link cable, no crossover; **0 floating pads**. Geometry: outline **closed**, exactly **120.000 × 66.000**; 4× Ø3.20 M3 at board-rel (4,4)(4,62)(116,4)(116,62); pad drills 0.8/1.0/1.2/1.6, vias 0.30 drill / 0.60 pad = **0.150mm annular** (JLC min 0.13); tracks 0.20–0.80 (JLC min 0.127); **0 track crossings**; **0 open non-GND nets**; copper→board-edge **2.45mm**, copper→M3-hole **7.50mm**; +5V↔+12V min gap 0.211mm; silk crossing a pad **0** (min 0.18mm); no text on copper; no duplicate refdes; **all 32 output screws on a uniform 5.08 grid, both rows**. The 13 "0.20mm" pairs are exactly *at* the netclass rule, not under it (JLC process limit 0.127 → 57% margin).
- **DEFECT FOUND AND FIXED — silk digit order (was X, now Y).** Was: all 16 block labels read low-OUT-first (`C1-OUT1/2`). **Top row is rot 180, so its pin 1 is the RIGHT screw** — the label read backwards against the physical screws while the bottom row read correctly. DRC cannot see this; the cost would have landed during the 84-wire session as pairwise-swapped top-row channels (recoverable via WALK, but half a MAP log to reconcile). Now: **8 top-row labels swapped to `C1-OUT2/1`, `C1-OUT4/3`, …** so the whole board obeys one rule — **left digit = left screw**. Verified by tracing each label digit through the actual ULN pin nets to the physical screw x-position: **16/16 correct.** Copper untouched (503 segs / 35 vias), label lengths identical so no new silk collisions possible. Backup `solenoid_driver.kicad_pcb.presilk3`. Confirmed live in Daniel's 3D render.
- **Terminal-block orientation question — RESOLVED, and it is a non-issue.** Daniel pushed on whether the mouths really face outboard. Re-derived: **J13's pads are at local (0,0) and (5.08,0) — collinear and symmetric, so a block drops into the same two holes at either 180° rotation. Mouth direction is chosen at soldering time, not fixed by the board.** The silk labels describe the *holes* (copper-defined) so they stay correct regardless. Body fits either way: top row reaches y=104.10 (4.10mm inside the edge) / 114.35 (8.5mm clear of the DIPs); bottom row 162.35 (3.65mm inside) / 152.10. Two signs point to +Y being the mouth face (KiCad "Horizontal" = side entry; the +Y face has a 1mm protruding funnel lip vs a plain 1.5mm wall at −Y). **3D viewer could NOT confirm — TerminalBlock_CUI has no 3D model installed on Daniel's Mac** (terminals render as bare pads; DIPs/CB1/caps/R1/headers all render). Settle it physically when parts arrive.
- **TERMINALS NOT YET PURCHASED** (confirmed with Daniel). Buy spec recorded: **pitch exactly 5.08mm — NOT 5.0** (5.0 accumulates 15 × 0.08 = 1.2mm across a 16-screw row and the last block misses its holes), 2-position, **side/horizontal wire entry** (screws driven from above — top-entry is unreachable once the deck is on), **interlocking/spliceable** (footprint body is 10.76mm = 10.16 + a **0.60mm dovetail**, and the layout butts them at exactly 5.08 so the dovetails nest), through-hole pin ≤1.3mm (pads drilled 1.60). Search "KF301-5.08 2P". **Qty: A=16, B=16, C=12 (its 4th cell is unpopulated) + 3× J70 = 47; buy 60.**
- **GERBERS PLOTTED AND AUDITED.** Plot settings walked live: 6 layers (F.Cu, B.Cu, F.Silkscreen, F.Mask, B.Mask, Edge.Cuts), no drawing sheet, drill marks None, 1:1, absolute origin, **☑ check zone fills before plotting**, coords 4.6mm, **X2 and netlist attributes UNCHECKED**; drill = Excellon, **☑ PTH and NPTH in single file**, absolute, mm, decimal. Audit of the output: Edge.Cuts **120.000 × 66.000**, 4 mount-hole circles **Ø3.20 at (104,−104)(104,−162)(216,−104)(216,−162)** (Gerber Y negated); drill **233 holes** = 35@0.30 + 138@0.80 + 24@1.00 + 2@1.20 + 34@1.60, exactly matching the board, header `MixedPlating` = merged; F.Cu 233 flashes / 235 draws; **B.Cu 15 filled regions → the ground plane IS in the Gerbers** (the fail-dangerous item, caught by the zone-fill checkbox); F/B.Mask 198 openings each (all THT pads both sides, vias tented); F.SilkS 2885 draws; **%TO net attributes = 0 on every layer**. Zipped to **`pcb/solenoid_driver/solenoid_driver_gerbers.zip`** (8 files, 82KB).
- **Friend's critique (UT EE student), answered honestly and worth keeping:** *"if you're filling the back with ground you shouldn't need ground traces."* Correct as a default. Reality on this board: **34 GND segments (6.8% of routing, 0.3–0.4mm vs 0.20 signal, 25 on F.Cu / 9 on B.Cu, 8 vias) in 5 runs** — U21.8→U12.9→U22.9, U31.8→U32.9→U41.8, U42.9→CB3.2→J72.2, C41.2→CB2.2, C11.2→C21.2. Cause: **217 of 503 segments are on B.Cu**, and each cuts a 0.5mm isolation slot, fencing 8 GND pads onto isolated islands. KiCad's `starved_thermal` named them; they are *repairs to* the plane, not routing *instead of* it. J72.2 was orphaned pre-existing. Root fix is upstream — keep signals off the plane layer — which the 32 edge-lining terminals made impossible here.
- **REV-2 DECLINED (options question).** A cleaner rev (taller board, spread chips, B.Cu kept solid) buys no measured benefit: signals are a few hundred kHz (loop-area effects start tens of MHz); worst case 2.1A (MAX_ON=7 could all land on one board) against a measured **1.13mm narrowest plane neck ≈ 2.4–2.6A** by IPC-2221, which is a 10°C-rise limit not a failure point; voltage drop is single-digit mV. Cost would be 1–2 full sessions of re-place/re-route/re-verify **plus restarting the 2-week fab clock that is supposed to run underneath Track B**. Noted for the record: the two previous resets (perfboard→PCB, plate rebuild) were each triggered by something *demonstrated*; this one would have been the first triggered by a hypothetical. Decision: order now; a rev informed by actually assembling one is worth far more.

**Files changed:** `firmware/keyboard_v1/keyboard_v1.ino` (PIN_OE=10 + header), `pcb/solenoid_driver/solenoid_driver.kicad_pcb` (8 silk labels), new `gerbers/` (8 files), new `solenoid_driver_gerbers.zip`, new `.presilk3` backup, this record.

**UNVERIFIED / open:** terminal blocks unpurchased (buy spec above) and mouth direction unconfirmed physically; `PIN_OE=10` never run on hardware — **J71 pin 6 must actually land on Mega D10 or nothing fires**; 3× CB1 = 14,100µF total bus inrush may make the BOSYTRO hiccup at switch-on (cause, not fault); 3× R1 = 3.3k effective ~OE pullup (fine, 1.5mA); board C's J41–J44 are dead copper — Sharpie an X at build.

**★ BOARDS ORDERED — July 26, 2026, ~01:00.** `solenoid_driver_gerbers.zip` submitted to JLCPCB: 2-layer, 1.6mm, 1oz, HASL, **qty 5**. (Hiccup on the way: a back-button re-submit produced "order cannot be submitted repeatedly" — the first submission had landed; resolved via My Orders.) **The ~2-week fab clock starts now and Track B is what fills it.** Money is spent; the driver is out of Daniel's hands until the boards land.

**RESUME HERE (Track B, the lead window):**
1. **Order 60 × 5.08mm interlocking side-entry 2P terminals** ("KF301-5.08 2P") — pitch exactly 5.08, NOT 5.0. Not yet purchased. ~$8. Also confirm mouth direction physically the moment they arrive.
2. **Deck CAD → Fusion** (brief 07/08 Stage 2, now unblocked): outline **120×66mm** · 4× Ø3.20 M3 board-relative **(4,4)(4,62)(116,4)(116,62)** · tallest part **CB1 Ø17×25mm** · terminal mouths outboard off **both** long edges → wire slots go just outside those edges, not over the board. 3 boards × 120 = 360mm over a 318.9mm keyboard; deck sizes to the boards, slots placed individually.
3. **Caliper gates on the populated plate** (brief 08): `body_top_z` + lead exit points. Still zero measured numbers in the deck clearance stack.
4. **Groove coupon** → swap cycle + fire on the breadboard driver = **the teardown gate**. Old plate stays fully assembled until it passes.
5. **Wire-tidy Phase 0** — snip/tape all 168 frayed tips.
6. **`Video_Script_Big_Reset.md` can post** once the order-confirmation shot is captured.
7. Hardware-free in parallel: C920 tripod + `Vision.calibrate_screen()` + template capture; Mouse Keys first mouse-free click; `agent/tft/set_data.json`.

**Git: still lock-blocked in the sandbox (`.git/HEAD.lock` + `index.lock`, stale since Jul 23 01:31 — `rm` returns Operation not permitted). Everything from Jul 13 onward plus this session is uncommitted. Daniel, from your Terminal:**
```
cd ~/Documents/Claude/Projects/Physical AI Agent
rm -f .git/HEAD.lock .git/index.lock
git add -A && git commit -m "Gerbers plotted + audited; silk digit order fixed; PIN_OE=10; pre-order audit; Jul 26 records"
git push
```
**Milestone: the board is finished, verified, and ready to order — the last gate before spending money.**

### July 27 session (Opus) — Track B opened in Fusion; DECK HEIGHT WAS WRONG BY 20mm; coupon scripted + verified

Daniel: "connect to fusion." No Fusion MCP connector exists in the registry (checked — only "Autodesk Product Help", docs only), so the mode was chosen explicitly with him: **Fusion API Python scripts in the repo, Daniel runs them, Claude owns and verifies the file.** Same division of labour as KiCad, and better than GUI-clicking because the coupon is entirely coordinate-driven from data already on disk.

**NEW: `cad/`** — `fusion_groove_coupon.py` (builds the whole brief-08 coupon in a fresh Fusion document), `verify_coupon_geometry.py` (runs outside Fusion; **0 failures / 0 warnings**), `README.md` (Fusion click-path, slicer orientation, test sequence, groove-clearance tuning log).
- Script robustness pattern worth reusing: **every solid is sketched at mid-height and extruded SYMMETRICALLY, and every cut straddles a reference face so overshoot lands in air.** That makes the script independent of Fusion's construction-plane normal directions — the usual source of silent sign errors in API scripts. Plane placement is also self-checking (create at +offset, read `plane.geometry.origin`, flip if it landed wrong). Point placement uses `modelToSketchSpace` so it works on any plane orientation.
- The one tunable, `GROOVE_CLEARANCE`, is a top-of-file constant, not a Fusion user parameter — for a reprint loop, "edit constant, re-run, fresh document" beats parametric sketch dimensions.

**STL cross-check (independent confirmation of the as-built record).** `verify_coupon_geometry.py` parses `Air75_84Key_Plate_Left.stl` by face normal and area, and confirms on **all six** wall rows: mounting face at `hole_y + 8` exactly, back face at +2.50, and **a planar face at datum + 1.00 = the counterbore floor.** Also tab-hole rings at Z11/Z26, plate slab Z0–Z4, and Z-min −33.50 = the back leg contact (not the plate bottom — an earlier assertion of mine got that wrong and was corrected). The as-built counterbore number is now confirmed by geometry, not just by the Jul 15 note.

**★ MEASUREMENTS (Daniel, calipers, mounted solenoid, from the plate's TOP face):**
- body top **30mm** → **`body_top_z = Z34`**. Bodies rest on the plate top; **`d = 7mm` exactly**. The old June note "body sits flush with the plate BOTTOM" is WRONG — as-built wins. Brief 08's assumption was right.
- plunger top **50mm** → **`plunger_top_z = Z54`**. Back-solving against the ball tip at Z−4 gives a **58mm plunger**, matching the figure recorded as "confirmed" months ago. Two independent paths agree.
- keycap clearance: **1–2mm** above the caps (partially closes open question #7).

**★ THE FINDING — brief 08's deck height was 20mm too low, and the caliper gate measured the wrong feature.** Triggered by Daniel's photo of a loose solenoid: the plunger is double-ended, and its upper end (shaft + return spring + clevis) stands **20mm above the body top**. So the tallest at-rest point on the populated plate is **Z54**, not Z34. Brief 08's `deck_underside_z = body_top_z + 8 = Z42` would have driven the deck 12mm *into* 84 plungers. The plunger only travels DOWN when fired, so rest is the worst case. **Was Z42, now Z58.** Full amendment box written into brief 08.

**Consequences, all decided with Daniel:**
- **Deck stays overhead** (option 1 of three presented). Boards directly above the keyboard, all 84 leads straight up, brief 07 intact. A low deck at Z38 with Ø10 plunger clearance holes was genuinely competitive on wall height and board access, but rejected: the PCBs sit on the deck and would still have to clear Z54, so it saves nothing.
- `wall_top_z` **Z60**; walls **58mm tall**, 34mm of that above the upper tab screw.
- **Wall is now STEPPED.** 2.50mm only below Z36 where it must fit the 16.55mm inter-body slot; **flared to 5.05mm above Z36.** A plain 2.5×58mm fin is 23:1 and floppy; the flare makes it a T-section for free. Datum rule untouched — the flare grows BACKWARD only. Its back face is limited by the **next row's return spring**: `hole_y + 19.05 − spring_OD/2 − 1.0`.
- **Two groove widths now:** plate **2.75** (thin section), deck **5.30** (flare). Same datum rule for both.
- **Wall-top pads DELETED → insert boss.** A 5mm flare can't hold a Ø4 insert (0.5mm walls), so a local boss thickens to `datum + 10` — but only in a ~7mm x band that slips between two of the next row's springs (9.05mm gap on 19.05 pitch). Anywhere else fouls a spring. 1 boss per wall instead of 3 pads: **6 tie-downs per half instead of 18.** Justified by load — MAX_ON=7 globally means any one wall sees ~10N.
- **Pad-pocket problem resolved (Claude's call, flagged for override).** Brief 08's 2mm pocket left 2mm of deck above the screw *and* made an M3×8 bottom out in a 6mm insert before its head touched the deck — it would feel tight while clamping nothing. Boss top now stops at the deck underside: full 4mm slab, 4mm of insert bite, 2mm margin. Daniel deferred this twice; the bottoming-out failure is unambiguous so it was implemented the working way. **Honest re-derivation logged: I originally also claimed the 2mm shelf would peel in the load direction — at 5N per solenoid that claim was overweighted and I walked it back.**
- **Deck→plate: metal M3 male-female standoffs, 54mm BODY length**, 6 positions (4 corners + 2 at the seam). Over brief 08's printed posts because the length is exact and pickable *after* measurement, and a 54mm printed column would be the weakest thing in the assembly. **Open gotcha: the stud must clear plate + washer + nut (~9mm for a 6mm plate) and standard M-F studs are 6mm** — either pocket the nut into the plate underside or use F-F standoffs with an M3×10 up from below. Also considered and rejected: extending the side rails to catch the deck (kills the open-sides rationale AND lengthens the tolerance chain from plate→post→deck to plate→rail→deck; short chain wins).

**Daniel's own design description, compared to the record (he asked).** He independently re-derived brief 08's scheme — walls in plate divots, top plate with matching divots to sandwich them, top plate carrying the PCBs and cable management, open question being how to clamp the two plates. All correct. **His one addition is a real catch the brief got wrong:** don't accept a 2mm groove floor, add the thickness back. **Correction to his version: the plate must grow DOWNWARD** (bottom face Z0 → Z−2, legs 2mm shorter, tab holes and leg contacts unchanged). Growing upward would eat the bottom 2mm of every solenoid body, since the bodies sit at Z4. His measured 1–2mm keycap clearance makes downward affordable (ball protrusion below the plate goes 4mm → 2mm and the tip doesn't move). **Still an open decision.**

**UNVERIFIED / open:**
- **`spring_OD` unmeasured** — estimated 10mm from a photo, and it sets the flare thickness. Measure before printing; the coupon then tests the 1.0mm clearance physically.
- Plate 4mm → 6mm downward: undecided.
- Standoff stud length: unresolved (see gotcha above).
- Lead exit positions: still unmeasured (sets the deck wire-slot positions).
- 58mm walls: printability/stiffness are paper until the coupon. **Print them laid flat, not upright.**
- Groove clearance 0.25 on both widths: the coupon's whole purpose.

**RESUME HERE:**
1. Measure `spring_OD` on a loose solenoid.
2. Run `cad/fusion_groove_coupon.py` in Fusion (`cad/README.md` has the click-path), eyeball the assembly, export 4 STLs, print the coupon.
3. Coupon test sequence in `cad/README.md` — **mount a solenoid on BOTH walls** so the flare-vs-spring clearance gets tested. Pass = old-plate teardown authorised.
4. Decide the plate 4→6mm question and the standoff stud arrangement; then order standoffs + inserts + M3×8.
5. Still outstanding from Jul 26: order 60 × KF301-5.08 2P terminals (pitch exactly 5.08, NOT 5.0); `Video_Script_Big_Reset.md` can post.

**Git: sandbox still lock-blocked. `cad/` is a brand-new untracked folder — Daniel, from your Terminal:**
```
cd ~/Documents/Claude/Projects/Physical AI Agent
rm -f .git/HEAD.lock .git/index.lock
git add -A && git commit -m "cad/: Fusion coupon generator + geometry verifier; deck height corrected Z42->Z58 (plunger, not body); brief 08 amended"
git push
```
**Milestone: a 20mm design error caught before it reached a printer, and Track B has executable CAD.**

### September 10, 2026 session (Opus) — six-week gap closed; rebuild PARKED; old plate becomes the vehicle

**Daniel returned after ~6 weeks away.** He opened with a design question (could breadboard power rails serve as the +12V high-side distribution?) and then asked whether the record still knew where he was. It did not, entirely — **no session record exists for Jul 28 – Sep 9**, and the last commit (`360b141`, Aug 28) contains only *plans*, never outcomes.

**Status established by asking, not assuming:** the Aug 10–18 "84 keys before college" sprint **did not run at all.** No coupon, no boards soldered, no rebuild. Old 84-key plate still fully assembled and populated (84 solenoids, 168 tab screws). PCBs and FULARR 5.08 terminals both arrived. **Daniel is at college and brought everything** — YIHUA station + supplies, BOSYTRO PSU, Mega + breadboard + dupont, 22 AWG grey and 16 AWG bus wire. Campus makerspace printing available.

- **★ DECISION — brief 07/08 rebuild PARKED until a home printer.** This is Gate 2's documented abort branch, taken deliberately rather than under deadline pressure. Rationale: 12 walls at 64mm ≈ 27h of printing is not a shared-makerspace job (queue, per-gram fees, no babysitting an overnight run); and the rebuild's entire payoff is *serviceability*, not capability — with 16 spare solenoids on hand. The old plate's tilt/stagger/84 hole positions were STL-verified against the CSV on Jul 15 (mean err 0.067mm). It works; it is merely annoying to service. `cad/fusion_groove_coupon.py` and its 0-failure verifier keep until December.

- **★ RECORD CORRECTION (was X, now Y) — §Harness reverts to the desk form.** Was (Jul 15, brief 07): boards on a top deck, 85-wire desk harness gone, both leads straight up ~40–80mm. **Now: no deck → the 85-wire desk harness is BACK**, i.e. the original early-July §Harness design, unchanged in substance. Boards sit on the desk directly behind the keyboard (3 × 120mm = 360mm vs the 318.9mm keyboard), terminals facing it. **Low-side runs go ~40–80mm → ~300–450mm ≈ 34m of 22 AWG total — confirm the spool.** Wire-tidy **Phase 1 (velcro per-row bundles) comes back**, having been made obsolete by the deck plan. **Carries over untouched:** the Jul 26 power topology (one 18 AWG PSU V+ → bus trunk, each board's J70 pin 1 stubs off the bus, 3 wires on V− one per board → boards stay dead-end leaves, no coil current through board copper), CB1 electrically on the bus, MAP discipline, cut-at-landing.

- **Breadboard-rails question answered — NO for the build, YES for bring-up.** Three reasons, in order of severity: (a) **the solenoid factory leads are stranded** (which is why the tips fray) — strands splay in a breadboard clip, some miss the contact, and one stray strand reaching the adjacent rail is a 12V short; tinning makes it worse (solder is soft, deforms the spring), and crimping a solid pigtail onto each is 84 operations, i.e. the work being avoided; (b) **no retention** — 84 friction-fit contacts on an assembly whose purpose is to slam, and an intermittent during MAP/WALK means chasing ghosts across 84 channels; (c) **current** — rail strip is ~1–2A aggregate against a 2.1A worst case (MAX_ON=7), mitigable by feeding each rail segment separately but a poor thing to design around on a 40A supply.

- **★ Bus scheme re-derived for the no-deck geometry, and my own earlier pick walked back.** Four options were laid out (screw-terminal strip + soldered bus / bare 16 AWG wall-top bus / WAGO 221 cluster / breadboard interim). I first recommended the **terminal strip** — correct reasoning *for the deck world*, where all 84 leads converge upward and a strip sits where they arrive. **With the deck gone that inverts.** The governing principle is **the bus comes to the solenoid, not the solenoid to the bus**: on the old plate each high lead makes a ~5cm hop to a wire directly above it, whereas any centralized block means 84 long runs converging on one point — exactly the rat's nest being avoided. **Decision: bare tinned 16 AWG along each of the 6 wall tops**, trunk at one end, per the original §Harness. The old plate's walls are the mount, already printed, free. Cost ~84 wrap-and-flow joints ≈ 90 min; each has no hole, no clinch, nothing behind it — the easy joint the Jul 13 protocol breakthrough was for, not the 2.54mm point-to-point work that broke the perfboard. Payoff: 84 of 168 danglers gone in one session.

- **★ SAFETY ITEM RAISED — the BOSYTRO is an open-frame 480W supply with exposed 120VAC terminals, now in a dorm room.** Highest-risk object in the project and very likely against housing rules. Three mitigations, ordered: printed terminal shroud (top of the makerspace queue), switched power strip / never energized unattended, off carpet and away from bedding.

- **Built: `docs/Session_Card_Sep10_College_Restart.md`** — the working plan. Eight sessions: (1) Board A alive, 5V logic + multimeter, no 12V (the Aug 2 card is still valid word for word); (2) boards B/C + hardwired cascade links + WALK 0–87 on the bench — **the gate that matters, all 88 switching before a single solenoid wire lands**; (3) first fire from a real board with a clipped spare, USB-then-12V (and the video's payoff shot); (4) the six wall-top buses; (5–7) land the 84 low sides by row, MAP log at landing; (8) MAP → WALK 88 → TYPE. Plus a 3-part makerspace queue (PSU shroud · **wall-top wire combs ×6** · board tray) and an explicit NOT-now list.

- **Wall-top comb caliper gate flagged before any CAD:** bodies top at **Z34**, wall top is **Z32** — bodies stand 2mm proud, so a comb straddling the wall fouls them unless its spine is ≤2.5mm below Z34 with the head above. Needs `M3c` (clear gap, wall back face → bodies behind) from the Caliper Gate Card first.

- **Firmware re-verified from file this session:** `PIN_OE = 10` present at line 66, `NUM_CELLS = 11`, `NUM_CHANNELS = 88`, `MAX_ON = 7`. The J71-pin-6 → D10 wire remains the silent-failure trap — without it the board answers on serial, WALK prints all 88, and nothing ever switches with no diagnostic.

**UNVERIFIED / open:**
- 22 AWG grey spool length vs the ~34m the desk harness now needs.
- Terminal mouth direction still unconfirmed physically (settle it the moment a block is in hand — screw on TOP face, wire hole on SIDE face).
- `PIN_OE = 10` has still never run on hardware.
- 3× CB1 = 14,100µF bus inrush may make the BOSYTRO hiccup at switch-on (cause, not fault).
- Board C's J41–J44 are dead copper — Sharpie an X at build.
- Wall-top comb geometry is paper until `M3c` is measured.

**Next: Session 1 of the new card — Board A alive.** Everything needed is in the room.

**Git: `main` is ahead of origin by 1 and the sandbox still cannot clear `.git/index.lock`. Daniel, from your Terminal:**
```
cd ~/Documents/Claude/Projects/Physical AI Agent
rm -f .git/HEAD.lock .git/index.lock
git add -A && git commit -m "Sep 10: college restart; rebuild parked, old plate is the vehicle; harness reverts to desk form; wall-top bus decided"
git push
```
**Milestone: the six-week hole in the record is closed and the project has an executable path to 84 typing keys without a single printed part.**

### September 19–20, 2026 session (Opus) — ★ PROJECT REDEFINED: TFT and Wave 2 dropped; board-assembly reference; first lab build session

Daniel went to the campus lab to start populating the driver PCBs, asked assembly questions from the bench, then mid-session redefined the project. **This is the largest scope change in the project's history and it makes the finish line closer, not further.**

**★ THE DECISION — "a keyboard that plays itself" replaces "an AI agent that plays TFT."** Daniel's framing: a personal fun project in the Mark-Rober self-playing-piano vein, not an AI-agent demo. Confirmed via options question, three answers:
- **Wave 2 / mouse gantry: DROPPED ENTIRELY.** Brief 04 itself said the TFT drag requirement was what would decide the mouse architecture — that requirement is gone, so the whole subsystem goes with it. Not parked, dropped.
- **Name: KEEP "Physical AI Agent"** for the folder and repo (least disruption). The name is now a historical artifact; the docs carry the real description.
- **v1 DONE = all 84 keys type any sentence on command.** WALK → MAP → TYPE, nothing after it.

**Why this is not a retreat, honestly derived:** the hardware critical path is *identical* under both goals — boards → solder → WALK 0–87 → MAP → TYPE. What changed is only what happens at the finish line, and the self-playing demo arrives one step EARLIER, because TYPE already exists in `keyboard_v1.ino`. TFT additionally required vision calibration, an LLM loop with per-game cost management, and an unresolved mouse subsystem stacked on top. Dropping it removes three unstarted workstreams and zero hardware.

**Kept on disk, explicitly off the critical path** (see the amended §Project overview): the entire `agent/` stack (20-test ladder still passes), `agent/tft/`, `mouse_driver.py`, `firmware/mouse_gantry_v0`. No future session should treat any of it as work owed. Deleting it buys nothing; re-earning it would cost weeks.

**Optional post-v1, recorded so it isn't re-invented:** a score player — timestamped key events streamed over serial, i.e. a piano roll for a keyboard, ~100 lines of Python. Design constraints already baked into the firmware: **`MAX_ON = 7`** caps simultaneous keys (no dense chords), and the **60ms per-channel cooldown** caps a single key at ~16 hits/sec. Neither limits percussive/rhythmic use. Not started, not required for v1.

**BOARD ASSEMBLY REFERENCE — extracted from `solenoid_driver.kicad_pcb` this session, not from memory.** Orientation for every statement below: **J71 (CASC-IN) on the LEFT edge, CB1/J70/J72 on the RIGHT edge.** Solder order is shortest-part-first so the board lies flat:
1. **R1** 10k — bottom-left, below J71. 2. **Six 100nF**: C11/C21/C31/C41 above their 595s; CB2 top-right beside C41; CB3 right side below the chips near J72. 3. **Four DIP-16 sockets**: U11/U21/U31/U41 (595s, left chip of each cell pair, centre spine). 4. **Four DIP-18 sockets**: U12/U22/U32/U42 (ULNs, right chip of each pair). 5. **Sixteen output terminals** — top edge L→R: J11 J12 J21 J22 J31 J32 J41 J42 (= each cell's OUT1/2 and OUT3/4); bottom edge L→R: J13 J14 J23 J24 J33 J34 J43 J44 (= OUT5/6 and OUT7/8). 6. **J70** 12V-in, right side below CB1 — **pin 1 (+12V) is the INBOARD screw, pin 2 (GND) the one nearer the right edge** (silk says so). 7. **J71** 6-pin male header, **board A only**, left edge, pin 1 (+5V) at top. 8. **CB1** 4700µF **last** (25mm, fouls everything) — **pin 1 (+) inboard/left, pin 2 (GND) nearer the edge; striped leg goes right.**
- **Per board: 1 resistor · 6 ceramics · 1 electrolytic · 4× DIP-16 · 4× DIP-18 · 17 terminal blocks (16 output + J70) · 1 header on board A only.**
- **Left empty by design:** J72 on boards A and B, J71 on boards B and C (the 6 hardwired board-to-board links pass through these, pin 1 → pin 1), and J72 on board C permanently.
- **Board C:** 3 cells populated. Skip the U41/U42 chips, Sharpie an X across J41–J44 (dead copper). Its socket and C41 can still be fitted.

**CORRECTION (was X, now Y) — DIP notch orientation.** Was: Claude told Daniel "sockets, notch left," carried over from the Jul 24 assembly note. **Now: pin 1 of every DIP is at the LOW-Y end, so all eight notches face the TOP edge of the board** (the same edge as the J11/J12 terminal row), in the J71-left orientation. Verified by extracting pad-1 coordinates from the `.kicad_pcb`, not by eye. Silkscreen is authoritative at the bench.

**Also settled at the bench:** flux pen (thin alcohol-carried rosin, low solids) vs. his gel syringe — pen is the better tool for fresh plated through-holes, one swipe per row, solder that row immediately; wait ~1–2s for the alcohol to flash off so it doesn't spit, but no longer than ~30s or the film is spent. Gel is reserved for the six board-to-board cascade wires and any rework, where flux must survive a long dwell. Per-board gate before chips go in, unchanged: visual bridge check, then **+5V↔GND, +12V↔GND, and +5V↔+12V must all read OPEN.**

**Content/brand consequences:**
- **`Video_Script_Big_Reset.md` is STALE and must not be posted as written** — its closer is "6 days until the PCB shows up," written Jul 30. The boards arrived weeks ago. The footage it lists is still good and should be recycled.
- **New hook direction for the comeback post: "I brought 84 solenoids to college."** Chosen over a generic "day in the life of an engineer" (saturated, and it discards the one asset nobody else has) and over the GPA-sacrifice angle (better as a recurring caption joke than as a video's spine). The self-playing framing is also strictly better for reach than TFT ever was: "a keyboard that types by itself" needs no explanation, "an AI agent that plays Teamfight Tactics" needs the viewer to know what TFT is.
- Shot list given for the lab session: fixed-angle timelapse (the non-negotiable one), bare-board beauty rotate, parts-laid-out overhead, macro of a joint forming, the 16-terminal row going in, board-flip reveal, multimeter continuity beep, one face-cam line; plus dorm-desk overhead of the populated plate as the cold open. Warned about LED/fluorescent flicker banding at 60fps.
- **OPEN QUESTION, unanswered:** does footage exist of the breadboard fire test (solenoid pressing a key, characters appearing)? That is the payoff shot the comeback video needs. If not, it is a ~10-minute reshoot at the dorm with the breadboard and one spare solenoid, and it is worth more than the rest of the shot list combined.

**UNVERIFIED / open (inherited, still true):** terminal mouth direction unconfirmed physically (settle it the moment a block is in hand); `PIN_OE = 10` has still never run on hardware — **J71 pin 6 must actually land on Mega D10 or nothing fires, with no diagnostic**; 3× CB1 = 14,100µF bus inrush may make the BOSYTRO hiccup at switch-on (cause, not fault); 22 AWG grey spool length vs the ~34m the desk harness needs; BOSYTRO open-frame 120VAC terminals in a dorm room still need the printed shroud.

**Next: unchanged, and now the whole project.** Session 1 — Board A alive, 5V logic only, no 12V. Then boards B/C + hardwired cascade links → **WALK 0–87 on the bench, the gate that matters** → first fire with a clipped spare → six wall-top +12V buses → land the 84 low sides by row with the MAP log → MAP → WALK 88 → TYPE. Done.

**AMENDMENT (Sep 20, at the bench) — board-to-board links: HARDWIRED → CONNECTORIZED (was X, now Y).** Was (Jul 26): 6 short 22 AWG solid wires soldered straight through J72 into the next board's J71, chosen because Daniel owned only M-M and M-F dupont and the link needs F-F. **Now: male 6-pin headers on BOTH ends of every link + F-F dupont cables** — he has F-F after all. Better for bring-up (boards unplug freely during WALK debugging) and costs only contact resistance, irrelevant at ~10mA of logic current.
- **Header count is 5, not 3:** A.J71 (Mega, M-F) · A.J72 → B.J71 → B.J72 → C.J71. C.J72 stays empty (chain tail).
- Cable is **pin 1 → pin 1, no crossover** (both connectors run 1→6 in the same +Y direction, verified from the PCB Jul 26): 1 +5V · 2 GND · 3 DATA · 4 SCLK · 5 RCLK · 6 ~OE.
- **New failure mode introduced by this change: off-by-one seating.** Six loose dupont strands plugged one pin over is invisible and gives bizarre half-working behaviour. Mitigations agreed: keep the six F-F wires as a bonded ribbon, Sharpie a pin-1 dot on every header, and tape/hot-glue each connector once WALK 0–87 passes (84 solenoids shake the desk; an intermittent on CLK or LATCH is the worst thing on this board to debug).
- Unchanged: **J71 pin 6 must land on Mega D10** (`PIN_OE = 10`) or nothing fires, silently.

**★ MILESTONE (Sep 20, ~evening, campus lab) — BOARD A FULLY POPULATED AND PASSED THE COMPLETE CONTINUITY GATE, chips out, never powered.** First driver board in the project's history to be finished and verified. Soldered in one lab session: R1 · C11/C21/C31/C41/CB2/CB3 · 4× DIP-16 + 4× DIP-18 sockets · 16 output terminals + J70 · J71 header · CB1 last.

**The 7-part gate, as run (reusable verbatim for boards B and C — this is now the standard board acceptance test):**
1. **Rails OPEN:** U11.16↔U11.8 (+5V/GND) · U12.10↔U12.9 (+12V/GND) · U11.16↔U12.10 (+5V/+12V). *CB1 makes the +12V/GND pair beep briefly while the meter charges it — not a short; use resistance mode and watch the number climb if unsure.*
2. **R1 in circuit:** U11.13↔U11.16 in resistance mode. **MEASURED 9.94 kΩ** (0.6% off nominal — pass). One reading proves R1's value, both its joints, and that ~OE is pulled to +5V.
3. Adjacent-pin sweep on all 8 sockets — all silent. **Board fact worth keeping: no two adjacent pins share a net on ANY socket, so the rule is simply "no neighbour pair may ever beep."**
4. Adjacent-screw sweep along both terminal edges — all silent.
5. **32 output paths:** ULN right column top→bottom = OUT1…OUT8 then +12V at pin 10; OUT1/2→J{c}1, OUT3/4→J{c}2 (top edge), OUT5/6→J{c}3, OUT7/8→J{c}4 (bottom edge). All beeped.
6. **6 Mega-interface paths:** J71 pin1→U11.16 · 2→U11.8 · 3→U11.14 · 4→U11.11 · 5→U11.12 · 6→U11.13. All beeped. *Note the non-sequential tail: header 4/5/6 → chip 11/12/13.* J71 pin 1 is the TOP pin; its pad is square on the underside.
7. **Power in:** J70 `+12V` (inboard screw) → U12/U22/U32/U42 pin 10, all four beeped (per-chip check, because COM is what enables the flyback diodes); J70 `GND` → U11.8; CB1 + leg → J70 `+12V`; CB1 − leg → J70 `GND`.

**Probing technique that made this work, worth repeating:** probe **from the TOP, into the socket holes / at header pins / on screw heads** — never on the solder joints underneath, because the entire bottom is a ground plane and a probe slipping half a millimetre off a pad reads ground-to-ground and makes *everything* beep. That false alarm happened once this session and cost a few minutes of panic.

**Board A status: electrically sound, chips NOT yet inserted, never powered.** Next action is chips in (notch toward the TOP edge — see the notch correction above) then 5V-only bring-up with the Mega, no PSU.

**Git: milestone (project redefined). Daniel, from your Terminal:**
```
cd ~/Documents/Claude/Projects/Physical\ AI\ Agent
rm -f .git/HEAD.lock .git/index.lock
git add -A && git commit -m "Sep 20: project redefined (self-playing keyboard, TFT+Wave2 dropped); BOARD A built and passed full continuity gate"
git push
```

### September 21, 2026 session (Opus) — ★ BOARD A ALIVE: first powered driver board, 32/32 channels switching, PIN_OE proven on hardware

Short bench session, deliberately bounded (chemistry quiz next morning). **Decision at the top of the session: do NOT solder board B yet.** Board A had never been powered, so soldering B first would have replicated any systematic error before finding it once. Board A was already at its cheapest test point — populated, continuity-gated, nothing left to buy. Validate before replicating.

**★ RESULT: all 32 channels on board A switch. Board A is electrically complete and verified.**

**The gate as run (reusable for boards B and C):**
1. **Chips in** — 4× 74HC595 (DIP-16: U11/U21/U31/U41, left chip of each pair) + 4× ULN2803A (DIP-18: U12/U22/U32/U42, right chip). **All eight notches toward the TOP edge** (the J11/J12 terminal-row edge, J71 on the left). Factory legs squared on a table edge first; pin count at the socket edge after each insertion.
2. **Three rails OPEN re-checked WITH chips seated** — probed at connectors, not chip pins: +5V↔GND at J71 pin1↔pin2; +12V↔GND at J70's two screws; +5V↔+12V at J71 pin1↔J70 `+12V`. **+12V↔GND measured 30.86 MΩ after the CB1 ramp** — the climb is the 4700µF charging through the meter, not a fault. *Technique worth keeping: swap the probes to confirm a ramp is a capacitor — a resistor reads the same both ways, a cap restarts from the bottom.*
3. **Mega → J71, six M-F dupont**, then — new step, and the one that retired the project's longest-standing silent-failure risk — **all six verified END-TO-END with continuity from the Mega pin to U11's chip pin**: D10→U11.13, D11→U11.14, D12→U11.11, D13→U11.12, 5V→U11.16, GND→U11.8. All six beeped. This tests dupont + header + trace + socket in one measurement and kills the entire class of off-by-one seating errors *before* power.
4. **Flash `keyboard_v1`, 115200, USB only, no 12V.** `STATUS` → `pulse=22ms lead=1500ms fires=0 on=0 mapped=0/84`. Firmware live.
5. **32 × `HOLD <ch>`, diode mode**, black probe clipped to J70 `GND` throughout. **ch 0 = 0.655V**, all 32 in the 0.6–0.9V band, `RELEASE ALL` → OL.

**★ UNVERIFIED #`PIN_OE` CLOSED.** `PIN_OE = 10` had never run on hardware since the Jul 26 fix. It works. R1 holds ~OE high by default (outputs disabled, fail-safe at power-on) and the firmware pulls D10 low in `setup()`. Had the J71 pin 6 → D10 wire been missing, the board would have answered on serial, printed all 88 channels on WALK, and switched nothing, with no diagnostic. The step-3 end-to-end continuity check is now the standard way to retire that risk on every board.

**★ METER-MODE CORRECTION (was X, now Y) — the session card was wrong and would have read as a dead board.** Was: "multimeter **continuity**: reads near-short to GND." **Now: DIODE-TEST mode, never the beeper.** A ULN2803A output is a Darlington; its ON-state floor is ~0.6–0.9V, not a short. In resistance mode at ~1mA a DMM reads that as several hundred Ω — above every continuity-beeper threshold (~30–50Ω) — so **a perfectly good channel does not beep.** Diode mode displays the drop directly: ON = 0.6–0.9V, OFF = OL. Written into `docs/Session_Card_Sep10_College_Restart.md`.

**★ WALK IS NOT A METER TEST (new).** `WALK` *pulses* each channel (`firePulse`, min gap 200ms) — far too brief for a DMM to settle. All meter checks use `HOLD` / `RELEASE ALL`. `WALK` is only meaningful with a visible load (LED + ~330Ω from +5V to a terminal). The card previously implied WALK was part of the meter sweep; corrected.

**`HOLD` auto-releases after 10s** (`MAX_HOLD_MS = 10000`, line 86) — a thermal safety for real 300mA coils, **not to be removed.** It breaks batched multi-channel holds (each channel's timer starts at its own HOLD), so the working rhythm is: probe on the screw FIRST, then send `HOLD <n>`, read, move on. No `RELEASE ALL` needed between channels.

**SCOPE CALL — all 32 checked, not the card's 8 spot checks.** Daniel pushed back on the 8 and was right. The 8 prove each cell is alive at both ends (systematic faults: dead chip, bad socket, broken OE, cascade break), and the Sep 20 cold gate already proved all 32 copper paths ULN-pin→screw. But the *one* physical change since that gate is chip insertion, whose failure mode is a folded-under pin — and the 8 only exercise ULN pins 18 and 11, the two ENDS of the right column. A pin folded under at pins 12–17 sails through all eight and surfaces later as one dead key. **Asymmetry decides it: a bad channel costs one probe touch now, versus unlanding bundled wires later.** ~12 minutes. **New standard: sweep all 32 on boards B and C too.**

**Terminal map VERIFIED from `solenoid_driver.kicad_pcb` this session** (pad coords + net tracing, not from the record): **top-edge blocks are rot 180 → pin 1 is the RIGHT screw; bottom-edge blocks are rot 0 → pin 1 is the LEFT screw.** Top edge L→R = J11 J12 J21 J22 J31 J32 J41 J42 (OUT1/2, OUT3/4); bottom edge L→R = J13 J14 J23 J24 J33 J34 J43 J44 (OUT5/6, OUT7/8). `ch → cell = ch/8+1, OUT = ch%8+1`; ULN right column top→bottom = OUT1(pin18)…OUT8(pin11). Full 32-row probe order is in the session card.

**Also settled:** Mega is USB-B, MacBook Pro M4 has no USB-A → a USB-C→USB-B cable or a USB-A→USB-C adapter is required; if serial drops out mid-session, suspect a beat-up bench hub before the board.

**Board A status: populated, continuity-gated, powered, 32/32 channels verified switching. Chips in. Never seen 12V.**

**UNVERIFIED / open (inherited, still true):** terminal mouth direction unconfirmed physically; 3× CB1 = 14,100µF bus inrush may make the BOSYTRO hiccup at switch-on (cause, not fault); 22 AWG grey spool length vs the ~34m the desk harness needs; BOSYTRO open-frame 120VAC terminals in a dorm still need the printed shroud — **print it before Session 3, when 12V first enters.**

**Next: Session 2 — populate boards B and C, connectorized cascade (5 male headers + F-F ribbons; A.J71 Mega · A.J72→B.J71 · B.J72→C.J71; C.J72 empty), then `WALK 0–87` on the bench.** Board boundaries are the spot checks that matter: **ch 31, 32, 63, 64, 87.** If channels light but in the wrong order, that is the `CASCADE_REVERSED` flag, not a wiring fault.

### September 25, 2026 session (Opus, ~1am, planning) — ★ OVERHEAD SHELF PLAN: printed shelf halves + barrier-strip power; wall-top bus DROPPED

Planning session before a ~4h lab day. Daniel came in with his own plan (a second "power PCB" with screw terminals, boards held above the solenoids so every lead routes UP, clear of the plunger shafts) and asked what the lab could make. **Priority stated explicitly: finish as fast as possible.**

**State confirmed:** boards B and C are SOLDERED (not yet tested — the Mega has touched only board A). B and C both have male 6-pin headers fitted; F-F ribbons in hand. Board A's build list shows J71 only → **A.J72 header likely missing, check at the bench.** Daniel is not concerned about the PSU shroud (his call; dropped from the plan).

**Decisions (was X, now Y):**
- **+12V distribution: was bare 16 AWG along the 6 wall tops (Sep 10). Now: off-the-shelf barrier terminal strips with jumper bars** (~7–8 × 12-position = 84 high-side screw positions), mounted on the shelf. Zero soldering, zero design. Topology unchanged: PSU V+ → strips (the trunk), each J70 pin 1 stubs off the strips, each J70 pin 2 → its own PSU V−; boards stay dead-end leaves.
  - Path to it: custom power PCB considered → **lab can't fab one**: NeoDen machines only ASSEMBLE SMD; Carvera approved list excludes copper-clad (FR-4 = "fibrous", explicitly barred; FR-1 = composite, "pending approval"). Claude first overstated Carvera feasibility (single-net board = drilling only, true) and corrected after reading the lab's Carvera page. JLC = 1–2 wk. Barrier strips beat all of them on speed.
- **Boards: was on the desk behind the keyboard (Sep 10 desk harness). Now: on an OVERHEAD SHELF above the plate** → low-side runs short again (~40–80mm), the ~34m 22 AWG spool concern is void, wire-tidy Phase 1 obsolete again.
- **Shelf = two 3D-printed halves (Daniel's call, Bambu X1C at the lab, overnight prints allowed).** Each half free-standing on its own **integral printed legs** (no joint between halves needed — split can follow the plate's own L/R split). Rejected en route: long 1/4-20 bolt legs (Daniel disliked), pegboard + separate legs (valid, more forgiving, but more parts/drilling), cardboard (crushes under 84 terminal screws, sags, scorches).
  - **Design content (Claude to generate STLs, cad/ script like the coupon):** integral legs landing on the desk OUTSIDE the plate footprint (4 corners + 4 mid-side per half ≈ anti-sag); printed PCB standoffs at the board's **112 × 58mm Ø3.2 pattern**, ~10mm tall (clears underside joints); **wire slots directly above each solenoid row from `Full_84Key_Hole_Coordinates.csv`**; barrier-strip mounting holes at the purchased part's spacing; Mega mounts (default: Mega on the shelf).
  - **Hard constraint: shelf underside ≥ Z58 (plate top = Z0 datum + 4 → i.e. ≥58mm above plate TOP face)** — plunger tops at rest Z54 (Jul 27 finding). From the STL: plate top ≈ 27.9mm (front) / 37.5mm (back) above desk → underside ≈ ≥100mm above desk. **Derived, not measured.**
- **Why this is fastest:** after the B/C/chain gate, everything left (first fire, strips, 84 high sides, 84 low sides, MAP/WALK/TYPE) is screwdriver work in the dorm — no more lab soldering.

**UNVERIFIED / blocking the shelf CAD:**
1. Factory solenoid lead length + exit point (GO/NO-GO for routing up; if too short → 168 splices and the wall-top bus wins again).
2. Plate top height above desk (front + back) and plate outer footprint incl. legs.
3. Exact barrier-strip product (length, width, mounting-hole spacing).
4. A.J72 header present?

**Today's plan: `docs/Session_Card_Sep25_BoardsBC_Chain.md`** — B gate → C gate → chain A→B→C with unpowered end-to-end checks through the chain → HOLD 0/31/32/63/64/87 → PASS = all 88 channels proven.

**Remaining path to v1:** (1) today: B/C/chain gate · (2) tonight: measurements + strip pick → Claude generates shelf STLs · (3) print 2 halves overnight · (4) dorm: first fire with a clipped spare · (5) dorm: mount shelf, 84 high sides → strips · (6) dorm: 84 low sides → terminals, MAP log at landing · (7) MAP → WALK 88 → TYPE.

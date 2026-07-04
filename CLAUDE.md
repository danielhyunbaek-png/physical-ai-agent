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

12-week summer build of a physical AI agent that types on a real keyboard and moves a real mouse, observed by a webcam. The agent runs on a MacBook Pro M4 and controls a Nuphy Air75 V3 keyboard (84 keys, Blush Nano linear switches) via an 84-solenoid matrix mounted above the keyboard. A second subsystem (Wave 2) is a Cartesian XY gantry that moves a Logitech B100 mouse, with SG90 servos for L/R click — **under re-evaluation, see Wave 2 brief**. Vision via a Logitech C920 webcam with template matching + OCR. **Ultimate goal: the agent plays TFT (Teamfight Tactics).**

Budget ceiling: $1,500. Current estimate: ~$1,366.

## Owner

Daniel. Comfortable with basic Python and basic Arduino, beginner CAD (Fusion), owns an FDM 3D printer. Give exact click-paths and commands; don't explain fundamentals.

## Key files in this folder

- `docs/PLAYBOOK.md` — **Reasoning patterns + working style.** The "how to think" half of this brain.
- `docs/briefs/` — Milestone briefs: 01 cell-#1 solder/fire · 02 WALK/MAP · 03 84-key plate CAD · 04 Wave 2 mouse decision · 05 TFT bring-up.
- `.claude/commands/` — Claude Code slash commands: session-start, session-end, verify, brief.
- `PRD_v2_Physical_AI_Agent.docx` — Product Requirements Document. Source of truth for *what* and *why*.
- `Build_Walkthrough_Physical_AI_Agent.docx` — Week-by-week operational guide. Source of truth for *how* and *when*.
- `Wave_1_Order_Checklist.xlsx` — Parts spreadsheet with audit trail. Wave 1 (essentials), Wave 2 (deferred), Tools, Optional. Audit Trail tab maps every line to PRD/walkthrough.
- `Project_Timeline.md` — **The project's history**: every phase, mistake, dead end (incl. the abandoned card-cage architecture), and fix, plus the July 2026 folder-cleanup record. Old planning docs were deleted (recoverable from commit `84a796c`).
- `2x2_Prototype_Dimensions.md` — Master dimension reference for the finished 2×2 prototype (`Prototype_2x2.stl`). Use for any 2×2 dimension question.
- `firmware/` — `keyboard_v1` (production, 88ch), `mouse_gantry_v0` (Wave 2 contract), `keyboard_v0`, `sr_led_walk` (bring-up aids).
- `agent/` — the complete software stack (see `agent/README.md`; `tests/run_tests.py` = 20-test hardware-free ladder).
- Driver-board docs: `Soldering_Plan.md`, `OneCell_595_ULN_Build_and_Fire_Guide.md`, `TopSide_Wiring_CutList.md`, `Cell_TopSide_Routing.svg`, `Driver_Board_3Board_Layout.svg`, `Driver_Cell_Perfboard_Layout.svg`, `Driver_Board_Wiring_Map.svg`.
- Content/social files: `Content_Calendar.xlsx`, `Social_Media_Strategy.md`, `Video_Scripts.md` + Video3/Video4 files.

---

## CURRENT STATE — as of July 4, 2026 (end of Fable campsite sprint)

**Context:** Daniel camping until Sun Jul 5, MacBook only. 2× Fable usage ends Jul 5; Fable access ends Jul 7 (this handoff exists because of that).

**Software: COMPLETE production stack, all 20 ladder tests pass** (in the build sandbox — see UNVERIFIED). Firmware `keyboard_v1` + `mouse_gantry_v0` mock-compile clean. Full detail in the July 2/July 4 session records below.

**Hardware:** 2×2 prototype printed and redesigned (fit+fastening fixes locked); solenoids partially mounted on plate (leads need triage — see wiring section); driver cell #1 dry-fit with canonical Q→IN order; **soldering not started**. FIRE test (reliable key presses) still pending.

**UNVERIFIED — ask Daniel / check first:**
1. Did `python tests/run_tests.py` (20 tests) run clean on HIS Mac (venv is Python 3.9)? Also the 3 earlier campsite tests + camera permission.
2. Is the repo fully pushed? Last known state: ahead of origin by 1 (commit `e6a46fb`, the production stack). **Remind him to push.**
3. FIRE test of the 2×2 (reliable presses at ~5mm bottom-out) — pending hardware time.
4. M3×3 flat-head actually holds in the re-measured ~1mm tab (~2 threads) — confirm at assembly.

**Pending TODOs gated on ask-first (spreadsheet NOT yet edited):**
- Row 39: hardware → **M3×3 flat-head** (history: M2 → M2.5 → M3×6 cap → M3×3 flat-head + counterbore) + refresh search link.
- Row 33: PSU → "Ordered"; row 34 (IEC cord) → "Skip" (bundled with BOSYTRO).
- Row 40 (M5 standoffs): SKIP — replaced by side rails. M5 *screws* still needed (260pc assortment covers plate→rails, rails→base, Wave 2 V-slot).

**Next milestones (each has a brief in `docs/briefs/`):**
1. Back home: cell #1 rails→solder→cold-continuity gate→first fire from soldered board (film it) — brief 01.
2. Flash keyboard_v1, MAP via solder-time CSV, WALK verification — brief 02.
3. C920 tripod + `Vision.calibrate_screen()` + template capture; enable Mouse Keys + `calibrate.py mousekeys` → first physical mouse-free click (film — the "robot refuses to touch the mouse" gag).
4. Wave 2 mouse decision (TFT drag requirement decides it) — brief 04.
5. 84-key plate CAD (tilt accuracy + interior-row fastening are the problems) — brief 03.
6. TFT bring-up — brief 05.

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
- **Stroke check (supersedes "~3mm useful"):** key bottoms out at ~5mm of ball-tip travel, ~5mm buffer. Fine: keycap limits the plunger, buffer prevents missed presses, and this pull solenoid is weakest at start of extension / strongest near seat, so bottoming at 5mm is well up the force curve. **FIRE test still pending.**
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
9. Screw thread engagement in tab — **RESOLVED (M3 bites). Committed screw now M3×3 flat-head; tab re-measured ~1mm → ~2-thread engagement. Confirm the M3×3 holds at assembly.**
10. Mounting hole size/thread — **RESOLVED: tapped M3. Wall clearance Ø3.3.**

## Driver board + solenoid wiring architecture (July 2026)

### Driver design

- Chain: **Arduino Mega → 11× 74HC595 (cascaded off D11/D12/D13) → 11× ULN2803A → 84 solenoids** (88 channels, 4 spare). ULN2803A = "the driver": 8 Darlington channels, 500mA each, built-in flyback diodes enabled by COM (pin 10) → +12V — **never skip**.
- Current build: **cell #1, top-side wire-art routing, ULN FLIPPED** (notch RIGHT → IN row faces the 595, OUT row faces the outputs), 2-2-2-2 middle-rail spacing, 11-row chip gap. Source docs: `TopSide_Wiring_CutList.md`, `Cell_TopSide_Routing.svg`, `OneCell_595_ULN_Build_and_Fire_Guide.md`, `Soldering_Plan.md`.

### Q→IN wiring with the flipped ULN — CANONICAL (as-built)

- **AS-BUILT (cell #1 dry-fit, July 1, 2026): canonical order — Q0→IN1, Q1→IN2 … Q7→IN8. Applies to all 11 cells.** (Nearest-IN was the cut list's recommendation; Daniel chose canonical.)
- Physical result: with the flipped IN row running right-to-left, the 8 jumpers form a **symmetric crossing fan** — **70/65/60/55/50/50/55/60 mm** (Q0…Q7; verified against `Cell_TopSide_Routing.svg`, chips left-aligned). Solder longest-first (IN1→IN8), layer crossings consistently.
- Payoff: **FIRE N → OUT(N+1)**, sequential — no scramble table; firmware `keymap[]` only maps channels→keys for TYPE.
- OUT landing holes run **right-to-left (OUT1 far right)** regardless of jumper scheme — chip-internal.

### MAP discipline — label holes, not wires

All 84 solenoid leads are identical black → **position is identity**. Sharpie the key name beside each landing hole; log `cell · OUT · key` **at solder time**, one line per wire; type the table into firmware MAP when done. WALK mode is the final verification pass, not the primary method.

### Harness: plate-side +12V distribution (DECIDED)

- Board's +12V rail **stays** (ULN COMs + reservoir cap). Added: **+12V distribution on the plate** — bare ~16 AWG bus wire along each mounting wall, walls tied by a trunk at one end, fed by **ONE 18 AWG +12V wire from the board rail**. **No ground wire to the plate** — return current comes back through the 84 low-side wires.
- Per solenoid: high side → ~5cm hop to its wall bus; low side → 22 AWG stranded grey, cut to length, → its ULN OUT landing hole. Plate↔board harness = 84 grey + 1 orange = **85 wires (vs 168)**.
- Peak bus load ≈ 7 × 300mA ≈ 2A — 16 AWG has big margin. If ringing/resets under heavy typing: optional 470µF across the plate bus.
- Solid→stranded transition **at the landing hole** (solid on board, stranded off-board), never mid-run.

### Bench triage for the wire mess (photo on file: plate ~half-populated, leads frayed + tangled)

1. Snip/tape every frayed bare tip immediately — shed strands are a 12V short waiting to happen.
2. Velcro leads into per-row bundles; work one wall at a time.
3. **Golden rule: cut each wire to length only at the moment it's landed. Never pre-cut.** Length = label.
4. Optional: snap-on printed combs over the wall tops (plate already printed, so integrated troughs are out).

### Wave 2 mouse — brainstorm only (NO decision yet) → see `docs/briefs/04`

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

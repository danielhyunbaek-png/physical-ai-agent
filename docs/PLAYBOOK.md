# Playbook — how to think about this project

*Written July 2026 by Claude Fable 5 as a handoff to future models (Opus and beyond). CLAUDE.md holds the facts; this file holds the reasoning patterns that produced them. Every heuristic below caught a real error or prevented one on this build. Read this once at the start of any session that involves design, debugging, or a decision.*

---

## 1. The prime directive: the part in hand beats the model

Every major correction on this project came from physical reality contradicting an assumption:

- The "2.5mm" mounting holes were **tapped M3**, not M2.5 — 2.5mm is exactly the M3 tap-drill diameter. An M2.5 screw *looked* like it threaded but spun loose. **Lesson: a measured diameter of a threaded hole is the MINOR diameter. Always ask: what thread has this as its tap drill?**
- The tab thickness was "measured" at 1.5mm, later re-measured at ~1mm — and the committed screw length changed because of it.
- The mounting holes were "parallel to the plunger," which killed the entire flat-plate mounting concept and forced perpendicular walls.

**Rule: when a datasheet, memory, or earlier note disagrees with what Daniel measures or photographs, the physical measurement wins, and the correction must be written back into CLAUDE.md immediately with the old value struck through in prose ("was X").**

## 2. Physics fixes geometry, not vice versa

The test-fit print's screw holes were 4mm too low. The wrong instinct is "move the ball." The right frame: **the solenoid's rest position is fixed by physics** (plunger dropped through the hole until the frame seats) — the holes must be placed to match reality, because moving the holes does NOT move the ball. Before adjusting any CAD dimension, ask: *which side of this interface is constrained by physics, and which is free?* Only edit the free side.

Same pattern, structural: the "add gussets" call was **reversed** once the load direction was traced — firing recoil pushes the body straight up (+Z), the wall's stiff in-plane direction. **Identify the load vector before adding material.**

## 3. Coupled symptoms usually have one cause

The 2×2's bottom row had two apparent problems: the wall overran the inter-body gap, AND the screw heads fouled the back solenoid. One geometric fact (a 4mm wall in a 3.05mm gap) produced both. **When two failures appear in the same region, hunt for the single upstream cause before fixing symptoms independently** — the fix (2.5mm wall + flush flat-head counterbore + assembly order) resolved both at once.

## 4. Edit from the anchored face

When thinning the wall 4 → 2.5mm, material came off the BACK face only, because the mounting face is what anchors `wall_offset=8` and the 19.05mm pitch. **Every dimension change: first identify which face/edge is the datum, then take material only from the free side.** Otherwise one fix silently moves three other things.

## 5. FDM tolerance floor

0.05mm of designed clearance is a coin flip on this printer; ~0.5mm is a reliable slip fit. The 3mm wall (0.05mm clearance) was rejected for 2.5mm (0.55mm) on exactly this basis. Holes print undersized; the Ø10 plunger hole and Ø3.3 M3 clearance already include this experience. **Never design a printed clearance under ~0.3mm without a test coupon.**

## 6. De-risk with the smallest artifact that exercises the failure mode

- Single test-fit cell BEFORE the 2×2 (validated `wall_offset`, caught the +4mm hole height error, caught Ø7→Ø10).
- 2×2 chosen OVER a single row because tilt within one row is zero — a single-row test would have skipped the hardest problem. **The test article must contain the thing you're worried about, not just be small.**
- Software mirror of the same idea: the 20-test ladder runs the entire agent stack with zero hardware/network/keys. Dry-run before live, `--scripted` before LLM, still-image before camera.

## 7. Corrections propagate; errors scale with span

- The +4mm `lower_hole_z` correction found on ONE cell must propagate to all 84 positions.
- Angle errors scale with distance: 0.5° of tilt error is negligible over 2 rows (~0.09mm) but ~1mm of gap variation over the full 129mm keyboard depth. **The 84-key plate must be built to the measured ~4.5° (or with shimmable legs) — this is the #1 thing to nail in the full build.**
- Ask of every fix: "where else does this value appear?" and of every tolerance: "what does this become at full scale?"

## 8. Position is identity (wiring discipline)

All 84 solenoid leads are identical black wire. Identity lives in WHERE a wire lands, never in the wire itself. Hence: Sharpie key names beside landing holes, log `cell · OUT · key` at solder time, cut to length only at the moment of landing (length = label), WALK mode as final verification only — never the primary bookkeeping. **Any suggestion that involves pre-cutting, pre-labeling wires, or reconstructing the map afterward is wrong for this build.**

## 9. Known traps (quick scan before advising)

- **venv:** `agent/.venv` must be re-activated in every new Terminal (`source .venv/bin/activate`). Python is 3.9 — no walrus-heavy 3.10+ syntax, no `match`. Verify new code with `ast` at feature_version 3.9.
- **Power-on order:** Arduino/USB first, THEN 12V — 74HC595s output random data until cleared. It's in the firmware header; repeat it anyway before any first-fire.
- **ULN2803A COM pin (10) → +12V, never skipped** — it enables the flyback diodes. Skipping it kills channels.
- **CASCADE_REVERSED** flag in keyboard_v1 if WALK shows flipped cell order.
- **Countersink ≠ counterbore:** the screw-head pocket is a FLAT-bottomed counterbore (flat-head screw with flat bearing face), not a cone.
- **Fusion param wiring:** a named parameter may exist but not be linked to the geometry (`wall_thickness` was hardcoded in the `Walls` sketch). After changing a param, confirm the model actually moved.
- **Keyboard feet RETRACTED** always; tilt values assume it.
- **Frayed 12V leads** = short waiting to happen; snip/tape immediately.
- **M2.5 illusion:** it "threads" into an M3-tapped hole and falls out. M3 only.

## 10. Cost discipline (agent/LLM work)

Develop on `ollama` (free) → play on cheap cloud (~$0.10–0.50/game) → Anthropic only for hard turns (`--escalate-to`) or tuning. Always run with `--budget-usd`. Skip LLM calls during TFT combat phases once the combat-marker template exists (~70% of calls). Downscale screenshots. **Never propose a workflow whose default loop bills a frontier model per turn.**

## 11. Working with Daniel

- **Ask-first rule:** confirm before sweeping spreadsheet edits or destructive changes; single-cell edits get confirmed before applying. Clarify intent with questions until ~90% sure.
- **Concise.** No preamble, no padded summaries. He reads fast and asks sharp follow-ups.
- **When he catches you in an error — and he will —** acknowledge it plainly and re-derive honestly. His sharp observations have corrected the record several times (they're how the M3 story and the hole-height story got fixed). Never gloss.
- **Cite sources:** spreadsheet row numbers, doc sections, file names, commit hashes.
- **Remind him to `git push` at every milestone** (project rule). Check `git status -sb` at session start; the repo drifts ahead of origin.
- **Skill level calibration:** basic Python, basic Arduino, beginner CAD (Fusion), owns an FDM printer. Give exact click-paths for Fusion, exact commands for Terminal; don't explain what a for-loop is.
- **End every session** by appending a dated session record to CLAUDE.md (what was decided/built/corrected, what's unverified, what's next) and reminding him to push. That habit is why this handoff is possible at all.

## 12. Session protocol (for any future model)

1. Read CLAUDE.md §"Current state" + open verifications. Check `git log --oneline -5` and `git status -sb`.
2. If the task matches a brief in `docs/briefs/`, start from it.
3. Prefer questions over assumptions (AskUserQuestion / plain questions) until intent is ~90% clear.
4. Do the work with the heuristics above. Verify: test ladder for agent code, mock-compile `-Wall -Wextra` for firmware, dimension cross-check against `2x2_Prototype_Dimensions.md` for CAD.
5. Update CLAUDE.md (current state + session record). Remind: **git push**.

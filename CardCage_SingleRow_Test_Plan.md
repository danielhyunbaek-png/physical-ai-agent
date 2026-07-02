# Single-Row Card-Cage Test — Design & Print (Today's Goal)

*Mentor brief, written to be done in one day: ~1.5 h CAD, ~2.5–3 h print (mostly unattended), ~1 h assemble + test. This validates the **new mounting architecture** (removable walls in a slotted base, clamped by a slim comb lid) on 3 keys before we scale it to 84 and before I rewrite the Week 4 plan around it.*

---

## 0. Why this test exists (read first)

You already proved three things on the 2×2: the solenoid-on-a-wall mount, the tilt, and the stagger. **Do not re-test those.** This coupon isolates only what's *new* in the card-cage idea:

1. **Groove slip-fit** — does a wall foot drop into a slot in the base plate and seat cleanly?
2. **Bench-populate → drop-in** — can you bolt the solenoids onto the wall *on the open bench*, then lower the finished module into the base with all plungers finding their holes? (This is the whole payoff: it moves the screwing out of the cramped gap.)
3. **Comb-lid capture + clamp** — does a grooved lid, screwed to two end posts, grab the wall tops and make the assembly rigid?
4. **Serviceability** — can you lift one populated wall straight out and reinsert it? (The reason we're doing removable walls at all.)
5. **X-registration** — does the closed-end groove stop the wall sliding sideways so the plungers stay centered?

**What this coupon deliberately does NOT test:** tilt and stagger (already validated — this sits flat), full-row racking with 13 solenoids (a later step), and firing reliability (optional add-on below). Keep the scope tight; that's what makes it a one-day de-risk.

> Engineering note: a single row has *zero* internal tilt and *zero* stagger by definition, which is exactly why it's the right coupon for the mounting mechanics alone — nothing else is varying.

---

## 1. Today's timeline

| Block | Time | Do |
|---|---|---|
| A. CAD | ~1.5 h | Model 3 parts in Fusion: base (with posts + groove), wall, comb lid. |
| B. Print | ~2.5–3 h | All three, PLA, 0.2 / 30% / 4 walls. Mostly unattended — start it, then prep hardware. |
| C. Assemble + test | ~1 h | Populate wall on bench, drop in, lid on, run the 6 acceptance checks. |
| D. Record | ~15 min | Note pass/fail + any tweaks. Send me the results and I rewrite Week 4 from them. |

---

## 2. Parameters

Convention (same as your 2×2 master dims): **plate bottom = Z0, plate top = Z4. X = right, Y = toward keyboard back, Z = up.** Origin = center of the **left** plunger hole.

### Carry-over — validated on the 2×2, do not change

| Name | Value | Note |
|---|---|---|
| `key_pitch` | 19.05 | 3 keys: X = 0, 19.05, 38.1 |
| `plate_thickness` | 4 | Z0→4 |
| `plunger_hole` | Ø10 | + **new** 1×45° chamfer on the top mouth (drop-in lead-in) |
| `wall_thickness` | 2.5 | hardcoded in the wall sketch (param was never wired — same gotcha as 2×2) |
| `wall_offset` | 8 | plunger-hole center → wall mounting face |
| `wall_height` | 28 above top | wall top at **Z32** |
| `screw_hole` | Ø3.3 | M3 clearance through wall |
| `counterbore` | Ø6 × 1 deep | flat-bottom, on the **back/head** face, M3×3 flat head sits flush |
| `screw_spacing` | 15 | holes at **Z11 and Z26** (7 and 22 above plate top) |
| screws | M3×3 flat-head | into the solenoid's tapped ~1 mm tab |

### New — the card-cage features this coupon validates

| Name | Value | Note |
|---|---|---|
| `n_keys` | 3 | enough to catch racking + multi-plunger drop-in |
| `groove_width` | 2.9 | wall 2.5 + **0.4 slip-fit** (verified). Tune ±0.1 after first fit. |
| `groove_depth` | 2.5 | blind; leaves a **1.5 mm floor** in the 4 mm plate |
| `wall_foot_len` | 2.3 | foot tip clears the groove floor by 0.2; the **shoulder seats on plate top** (Z4) and sets height |
| `lid_thickness` | 6 | the comb bar |
| `lid_groove_depth` | 3 | captures the wall-top tongue (Z29→32) |
| `post_height` | 24.8 above top | post top at **Z28.8** = 0.2 below where the lid seats → screws preload the lid onto the wall |
| `lead_in_chamfer` | 0.5×45° | on: groove mouth, foot tip, wall-top edge, lid-groove mouth, plunger-hole top mouths |
| module footprint | ~70 × 32 | trivially fits your 256 bed |

**Dimensional chain — all checks passed** (I computed the full Z-stack): groove floor 1.5 mm, foot clearance 0.2 mm, slip-fit 0.4 mm, wall-after-counterbore 1.5 mm, 6 mm of material above the top screw hole, lid grabs above the holes, 0.2 mm lid preload, 2 mm plunger slop in the Ø10 hole.

> **One measure-confirm:** the lid sits at **Z29** (25 mm above plate top). Your installed solenoid body-top should be at/under that so the lid clears it. If your bodies stand taller, just raise `wall_height` and the lid by that same delta — the lid rides above the wall, so it's a one-number bump. Check it with calipers before you print; everything else is locked.

---

## 3. Fusion 360 — modeling steps

**Fastest path:** open your 2×2 file, Save-As to a new name, delete the back row + legs, keep one wall + its plate strip, stretch it to 3 keys, then add the new groove/foot/posts/lid below. **Or** build fresh from the steps below — both land in the same place. Model everything **flat** (no tilt — a single row doesn't need it).

### Part 1 — Base plate (one body)
1. Sketch a rectangle on the XY plane, **X −16 → 54, Y −14 → 18** (≈70 × 32). Extrude up `plate_thickness` = 4.
2. New sketch on the top face: three circles **Ø10** at (0,0), (19.05,0), (38.1,0). Extrude-**Cut → All**. Add a **1×45° chamfer** to each hole's **top** edge (this is the plunger lead-in for drop-in).
3. **Groove (new):** sketch a slot on the top face, centered at **Y 9.25**, width **2.9** (Y 7.8→10.7), running **X −10.25 → 48.25** (closed ends — those ends are your X-stop). Extrude-**Cut down 2.5** (blind; stops at Z1.5). Chamfer the groove's top mouth 0.5.
4. **End posts (new):** two posts, footprint ~8 × 8, centered at **(X −13, Y 9.25)** and **(X 51, Y 9.25)**, extruded **up to Z28.8** (24.8 above the plate top). On each post top, sketch a **Ø2.5** circle and cut a blind hole **6 deep** — the M3 lid screw self-taps into PLA here. *(Optional upgrade: model Ø4.0 and melt in a heat-set insert for the real build; self-tap is fine for the coupon.)*

### Part 2 — Wall (separate component — keep it its own body so it lifts out)
1. On a plane at **Y 8** (the mounting face), sketch the wall outline: **X −10 → 48**, **Z 4 → 32**. Extrude **back +Y by 2.5** (→ back face at Y10.5).
2. **Foot (new):** extend the wall downward into the groove — add **Z 1.7 → 4** to the same 2.5-thick profile (foot length 2.3). Chamfer the foot tip 0.5 on both long edges.
3. **Mount holes:** on the wall front face, per key (X 0, 19.05, 38.1) two **Ø3.3** holes at **Z11 and Z26**, centered in X on the key. Extrude-Cut through. Then on the **back face** (Y10.5) add a **Ø6 × 1 deep flat counterbore** at each of the 6 holes so the flat heads sit flush.
4. **Top tongue:** chamfer the wall's top edge (Z32) 0.5 on both long sides — this is the lead-in into the lid groove.

### Part 3 — Comb lid (separate body)
1. Sketch a bar: **X −15 → 53, Y 5.25 → 13.25** (width 8, centered on the wall). Extrude **Z 29 → 35** (thickness 6).
2. **Underside groove:** on the bottom face (Z29), cut a slot centered **Y 9.25**, width **2.9**, **3 deep** (Z29→32) running the full bar length. Chamfer its mouth 0.5. This is what hugs the wall tops.
3. **Screw holes:** two **Ø3.4** clearance holes through the lid at the post centers (X −13 and X 51, Y 9.25). Optional: a shallow counterbore on top so the heads sit flush.

### Export
Each body → **Save As Mesh → STL, High refinement**. Three files: `base`, `wall`, `lid`.

---

## 4. Print settings

PLA, **0.2 mm layer, 30 % infill, 4 walls** (your standard). No supports needed.

| Part | Orientation | Why |
|---|---|---|
| Base | flat, **groove and posts up** | plunger holes print vertical = accurate; posts self-support |
| Wall | **lay it flat** (the 58 × 28 face on the bed, 2.5 mm as height) | the M3 holes then print perpendicular to the bed = most accurate alignment; fast |
| Lid | flat, **groove up** (print it upside-down vs. use) | the capture slot prints as a clean upward pocket, no overhang |

> The flat wall orientation trades a little inter-layer strength for hole accuracy — the right call for a *fit* test. We'll revisit wall orientation/strength for the real build.

Rough times: base ~1.5–2 h, wall ~30–45 min, lid ~30–45 min. Start the base first; prep hardware while it runs.

---

## 5. Hardware for today

- **3 ×** JF-0530B solenoids (you have plenty)
- **6 ×** M3×3 flat-head screws (solenoid → wall; from your 2×2 stock)
- **2 ×** M3×8 or ×10 screws, any head (lid → posts, self-tap into PLA). *No long M3 on hand? A binder clip or tape across the lid is fine for the fit test.*
- **3 ×** silicone tips (~5 mm tubing) for the ball tips
- A **real** M3 driver/hex — **not** a printed one. You don't need your stubby-screwdriver experiment here; bench-populating gives you full access. Save the stubby test for in-situ work later.
- Calipers; (optional fire test) the Week-2 breadboard rig.

---

## 6. Assembly

1. **Populate the wall on the bench** (open access — this is the point): bolt all 3 solenoids to the wall front face with the M3×3 flat-heads, ball-tips down, silicone tips on. Snug, not cranked (PLA strips).
2. **Drop the populated wall into the base groove.** It should lower straight down: foot into the slot, **shoulder flat on the plate top**, all 3 plungers passing through their Ø10 holes. The end-stops set its X position.
3. **Fit the comb lid:** wall-top tongues into the lid groove, lid down onto the posts, drive the 2 M3 screws. The posts are 0.2 mm short on purpose, so tightening pulls the lid down onto the wall.

---

## 7. Acceptance tests — pass/fail

Run these in order. Write down the result of each.

1. **Groove slip-fit.** Wall foot seats fully by hand, shoulder flat, no rocking, slop ≤ ~0.3 mm. *Fail → §8.*
2. **Drop-in alignment.** All 3 plungers enter their holes together with no forcing. *Fail → §8.*
3. **X-registration.** Wall can't slide sideways; each plunger looks centered in its Ø10 hole. *Fail → §8.*
4. **Lid clamp earns its place.** With the lid screwed down, grab a solenoid and wiggle — it should be noticeably rigid. Now loosen the lid and wiggle again: it should be visibly floppier. That delta is the proof the comb lid does real work. *Pass = clearly stiffer with the lid on.*
5. **Serviceability (the headline).** Unscrew the lid, lift the whole populated wall straight out, set it down, and reinsert it. Clean, repeatable, no fighting it. *This is the capability the whole redesign is for — it must pass.*
6. **(Optional) Fire test.** Place the coupon over 3 adjacent real keys (e.g., A S D), wire the 3 solenoids to breadboard channels 0–2, `FIRE 0..2 @ 30 ms`. You should get all three letters. Confirms the cage didn't change the firing geometry.

**Overall pass:** 1–5 clean (6 is a bonus). Then we scale the architecture in Week 4.

---

## 8. Tuning guide (if something fails)

- **Foot too tight in groove** → widen `groove_width` +0.1–0.2 (or sand the foot). **Too loose** → −0.1, or a strip of tape on the foot.
- **Plungers catch on entry** → enlarge/deepen the plunger-hole top chamfer; confirm the wall actually seated (shoulder flat).
- **Foot bottoms before the shoulder seats** → shorten the foot or deepen the groove (keep ≥1 mm floor).
- **Lid rocks / won't clamp** → shorten the posts another 0.2–0.3 so the lid bottoms on the wall, not the posts.
- **Wall shifts in X** → tighten the groove's end-stops, or add a small keyed notch at one end.
- **Body top fouls the lid** → raise `wall_height` + lid by the measured overshoot (one number).

---

## 9. Record this (feeds the Week 4 rewrite)

Jot: which of tests 1–6 passed, the final `groove_width` that gave a good slip-fit, any post-height tweak, and whether body-top clearance held at Z29. Send me those and I'll rewrite the full Week 4 on this card-cage basis — base-comb + slim vented top-comb + drop-in per-half wall modules, with the chamfers, X-stops, and the brick-bonded bed-split baked in.

---

## 10. Checklist

- [ ] Parameters confirmed; body-top ≤ Z29 checked with calipers
- [ ] Base modeled (3 Ø10 holes + chamfers, groove with closed ends, 2 posts)
- [ ] Wall modeled (foot, 6 holes + counterbores, top tongue, chamfers) — separate body
- [ ] Lid modeled (underside groove, 2 screw holes)
- [ ] All three printed (0.2 / 30% / 4 walls; wall laid flat)
- [ ] Solenoids bolted to wall on the bench
- [ ] Wall drops into groove; 3 plungers centered
- [ ] Lid clamps; rigid with lid, floppy without
- [ ] Wall lifts out and reseats cleanly (serviceability)
- [ ] (Optional) FIRE 0..2 @ 30 ms → 3 keystrokes
- [ ] Results recorded → ping me for the Week 4 rewrite

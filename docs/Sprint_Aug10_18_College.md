# Sprint plan — Aug 10 → Aug 18, 2026 · "84 keys before college"

**Goal:** full plate rebuild (brief 08 groove sandwich + deck) AND all 84 keys firing on command, before Daniel leaves on the 18th.

**Capacity:** 8 days × 3–4h = 24–32 hours. **Estimated work: ~31 hours.** There is no slack. This plan exists to make sure the slack that *does* appear goes to the right place, and that the abort path is taken early enough to still leave with a working keyboard.

**Scope chosen deliberately, with the numbers on the table (Aug 10).** Deck-only was recommended and declined. That's a legitimate call — but it means the gates below are not suggestions. Miss a gate, take the branch.

---

## The one thing that determines whether this works

**The printer is the bottleneck, not your hands.**

| Part | Est. mass | Est. print |
|---|---|---|
| Coupon | ~25g | ~1.5h |
| 12 walls @ 64mm tall | ~400g | **~27h** |
| Plate L + R | ~155g | ~12h |
| Deck L + R | ~60g | ~5h |
| **Total** | **~640g** | **~45h** |

45 hours of printing across 8 days means the machine runs **most of every night starting Aug 11**. Nothing about your hands matters if the printer is idle. Every decision below is subordinate to keeping it fed.

Corollary: **CAD is the critical path, not soldering.** Boards can be soldered at midnight while the printer runs. CAD cannot be done in parallel with anything.

---

## Do these three checks before anything else (20 minutes, today)

If any fails, the plan changes today rather than on Aug 15.

1. **Filament.** You're borrowing. You need **~700g with margin**, in one colour, ideally one spool. A spool that ends at hour 18 of a 20-hour deck print is the single worst failure mode in this plan. *Confirm the actual gram count on the spool before you start.*
2. **Parts on hand.** Standoffs and terminals arrived. Also required, and **none of it can be re-ordered in time**:
   - M3 heat-set inserts (~24 needed) + **heat-set tip for the YIHUA**
   - M3×8 flat-head countersunk (~30)
   - 16 AWG bare tinned bus wire (~3m) and 18 AWG silicone
   - 2.54mm male header strips (need 5 × 6-pin)
   - 22 AWG stranded grey (the 84 low-side runs — the big one)
   - Verify the standoff kit actually contains **F-F 20mm ×6 and M-F 20mm ×12**
3. **Printer health.** First layer, bed adhesion, nozzle. Find out on a 25g coupon, not on a 27-hour wall batch.

---

## Printer queue — this order, no substitutions

```
Coupon  →  [GATE 1]  →  12 walls  →  plate L+R  →  deck L+R
```

Walls go first after the coupon because they are 27 of the 45 hours. The deck goes last because it's the only part with zero dependency on the coupon result — if you run out of days, a missing deck is survivable for a week (boards sit on the desk on standoffs); a missing wall is not.

---

## Day by day

### Mon Aug 10 — today · CAD (3–4h)
- The three checks above (20 min).
- **Measure `spring_OD`** on a loose solenoid. 30 seconds, and it sets the wall flare thickness. Still the last unmeasured number in the design.
- Caliper gate card (`docs/Caliper_Gate_Card.md`) — **M4a is the one that matters**: real printed wall thickness, three spots. `groove_width = 2.75` assumes walls come out at exactly 2.50. If yours are 2.62, the groove leaves 0.13mm and nothing seats.
- Report both to Claude → constants updated → **run `cad/fusion_groove_coupon.py` in Fusion** (click-path in `cad/README.md`) → export 4 STLs.
- **Coupon on the printer before bed.** Walls laid flat, not upright.

> Already done for you this session: the script is amended to **Z64** (60mm standoff column, walls 64mm) and `cad/verify_coupon_geometry.py` passes **0 failures / 0 warnings** including the STL cross-check. The plunger-clearance rule that caught the Jul 27 error is now a live assertion, so a future standoff change can't silently drive the deck into 84 plungers.

### Tue Aug 11 — GATE 1, then CAD Stage 2 (3–4h)
- **Morning: coupon test** (sequence in `cad/README.md` §The test sequence). Mount a solenoid on **both** walls — that's what tests flare-vs-spring clearance.
- **GATE 1 — groove fit.**
  - *Pass* → walls on the printer **immediately**. This is the moment the 27-hour clock starts and it cannot slip past today.
  - *Fail on fit* → adjust `GROOVE_CLEARANCE` ±0.05–0.10, reprint coupon only (~1.5h), retest same day.
  - *Fail twice* → **abort the rebuild, go deck-only.** Two failures means you'd be starting a 27-hour print on Aug 12 at the earliest, and the arithmetic stops closing.
- Rest of the day: CAD Stage 2 — full plate L/R with grooves + 6 standoff holes, 12 walls, deck L/R with grooves, PCB mounts, wire slots.
- **Evening while walls print: solder board A** (`docs/Session_Card_Aug02_BoardA.md` §2). Shortest part first, CB1 last.

### Wed Aug 12 — boards (3–4h) · walls printing
- **Board A logic bring-up, 5V only, no 12V** (session card §3). J71 pin 6 → **D10** is not optional — miss it and nothing ever fires with no error message.
- Solder board B.
- Finish any CAD loose ends. Plate STLs queued behind the walls.

### Thu Aug 13 — boards (3–4h) · walls finish → plate starts
- Board B bring-up. Solder board C. **Sharpie an X across J41–J44 on board C** — its 4th cell is never populated.
- **Wire-tidy Phase 0: snip and tape all 168 frayed lead tips.** Low-attention work; do it while tired. Shed strands are a 12V short waiting to happen.

### Fri Aug 14 — GATE 2 (3–4h) · plate finishes → deck starts
- Board C bring-up. Solder the 3 cascade header links. Mark **pin 1 with a Sharpie dot on both ends** of every hop.
- **`WALK 0 87` across all three boards on the bench.** Multimeter spot checks.
- **GATE 2 — the decision point.** By end of today you need: (a) all 88 channels switching, **and** (b) 12 walls + both plate halves printed and dimensionally checked.
  - *Both pass* → teardown is authorised. Proceed.
  - *Either fails* → **abort the rebuild.** Land wires on the old plate, which is still fully assembled and populated because teardown is tomorrow, not today. **This is the entire reason teardown is scheduled this late.** You lose the grooves; you keep a working keyboard.

### Sat Aug 15 — teardown + remount (4h, the physical day)
- Heat-set 12 wall inserts + ~12 deck PCB inserts. Use the proper tip.
- **Teardown: 168 screws out of the old plate.** Keep the solenoids in row order — bag and label per row.
- **Bench-mount 84 solenoids onto the 12 new walls.** This is the payoff of the whole scheme: full access, no driving screws inside a 16mm slot.

### Sun Aug 16 — assembly + wiring starts (4h)
- Walls into plate grooves, deck on, standoff columns, 3 boards mounted.
- **Build the 6 +12V buses** — bare 16 AWG along each wall, trunk at one end, one 18 AWG feed straight from PSU V+.
- **Start landing wires.** Golden rule: **cut each wire to length only at the moment it lands.** Sharpie the key name beside each terminal, log `cell · OUT · key` one line per wire, at solder time. Do **not** tin the tips going into screw terminals — solder cold-flows under clamp pressure and shows up months later as intermittent dead keys with no visible cause.

### Mon Aug 17 — finish wiring + bring-up (4h+) · GATE 3
- Land the remaining wires.
- Type the MAP table into firmware, `WALK` all 88, `TYPE` a real sentence.
- **GATE 3, midday:** if fewer than ~half the wires are landed by noon, stop expanding. Land a **coherent subset** — home row, WASD, the alphabet — verify it, film it, and finish the rest at college. A keyboard that types 40 keys is a finished demo. 84 half-landed wires is a box of loose parts.
- **Commit and push.** See below.

### Tue Aug 18 — leave
- Transport: the deck assembly is now a tall, tippy thing on 60mm brass columns. Pack the plate assembly and the keyboard **separately**, plungers supported, not resting on the keycaps.

---

## The three gates, in one place

| Gate | When | Test | Fail → |
|---|---|---|---|
| **1** | Tue Aug 11 AM | Coupon groove fit + flare clears spring | Retune ±0.05, reprint once. Second fail = deck-only. |
| **2** | Fri Aug 14 EOD | All 88 channels WALK **and** walls + plate printed | **Abort rebuild.** Old plate is still intact — land wires on it. |
| **3** | Mon Aug 17 noon | ≥50% of wires landed | Stop expanding, finish a coherent key subset, film it. |

---

## What is explicitly NOT in this sprint

- The mouse subsystem. Wave 2 is out, by your call.
- TFT bring-up, vision calibration, `set_data.json`. All hardware-free — they're dorm-room work, and they're genuinely better use of a college evening than anything on this list.
- The `plate 4→6mm downward` open question. Leave it at 4mm. It's an elegance fix and it costs a reprint.
- Rev-2 of the PCB.

---

## Git — this is now overdue by a month

Everything since **Jul 13** is uncommitted, including all of `cad/`, `media/`, the Aug 2 session cards, and this file. The sandbox cannot delete the stale lock files. From your Terminal, tonight:

```
cd ~/Documents/Claude/Projects/Physical\ AI\ Agent
rm -f .git/HEAD.lock .git/index.lock
git add -A
git commit -m "Aug 10 sprint: coupon script Z58->Z64 (60mm standoff column), verifier parametric, 8-day plan to college"
git push
```

Do this **before** the teardown on the 15th, not after. If anything goes wrong in the next week, the design record is the part you cannot reprint.

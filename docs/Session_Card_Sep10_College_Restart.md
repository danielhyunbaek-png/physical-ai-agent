# Session card — Sep 10, 2026 · College restart: "the old plate is the vehicle"

**Status check that produced this card:** the Aug 10–18 sprint did not run. Nothing was built. The old 84-key plate is still fully assembled and populated (84 solenoids, 168 tab screws). The 5 PCBs arrived, the FULARR 5.08 terminals arrived, and **everything is now at college with Daniel** — soldering station, BOSYTRO PSU, Mega, breadboard, 22 AWG grey, 16 AWG bus wire. Campus makerspace printing is available.

**No CLAUDE.md session record exists for Jul 28 – Sep 9.** This card opens the record again.

---

## THE DECISION — rebuild parked, old plate carries the project

Brief 07/08 (groove sandwich + overhead deck) **parks until Daniel is back at a home printer.** This is Gate 2's documented abort branch, taken deliberately rather than under time pressure:

- 12 walls at 64mm = **~27 hours of printing**. That is not a shared-makerspace job — queue times, per-gram fees, and no ability to babysit an overnight run.
- The rebuild's entire payoff is **serviceability** (swap an interior solenoid without unscrewing the rows behind it). It is not a capability. 16 spare solenoids are on hand.
- Everything blocking a *typing keyboard* is physically in the dorm room right now.

**The old plate is not a compromise vehicle.** Tilt 4.0°, stagger, and all 84 hole positions were verified against `Full_84Key_Hole_Coordinates.csv` (mean err 0.067mm, Jul 15). It works. Its only flaw is that servicing it is annoying.

### ⚠ RECORD CORRECTION (was X, now Y) — §Harness reverts

- **Was** (Jul 15, brief 07): boards live on a top deck above the plate → the 85-wire desk harness is gone, both leads route straight UP (~40–80mm runs).
- **Now:** no deck. **The 85-wire desk harness is BACK** — i.e. the original §Harness design from early July, unchanged in substance. Boards sit on the desk behind the keyboard. Low-side runs go from **~40–80mm back to ~300–450mm**.

**What carries over untouched:** the Jul 26 power topology (one 18 AWG from PSU V+ → bus trunk; each board's J70 pin 1 stubs off the bus; 3 wires on PSU V−, one per board's J70 pin 2 — boards stay dead-end leaves, no coil current through board copper). CB1 still sits electrically on the bus. MAP discipline unchanged. Cut-at-landing rule unchanged.

**What comes back with the desk harness:** wire-tidy **Phase 1 (velcro per-row bundles)**, which the deck plan had made obsolete. At ~40cm per run × 84 runs that is **~34m of 22 AWG grey** — confirm the spool before starting, and bundle per row or the mess returns.

**Board placement:** three boards × 120mm = 360mm, keyboard is 318.9mm. Line them up **directly behind the keyboard**, terminals facing it, to keep the runs as short as the geometry allows.

---

## ★ DO THIS BEFORE ANYTHING ELSE — the PSU

The BOSYTRO is a **480W open-frame supply with exposed 120VAC terminals**, and it is now in a room you sleep in. This is the single highest-risk object in the project and dorm housing rules almost certainly have something to say about it.

Three things, in order:

1. **Cover the mains end.** Top of the makerspace queue — a printed terminal shroud over the L/N/⏚ block. Until that exists: a strip of thick acrylic or even a taped-down plastic box. Nothing bare.
2. **Switched power strip**, so the PSU is de-energized by a switch you can see, and **never energized unattended**.
3. **Off carpet and away from bedding.** Hard surface, clear airspace around the case vents.

Not negotiable, and it costs one evening.

---

## Session 1 — Board A alive (2–3h, no 12V, no solenoids)

`docs/Session_Card_Aug02_BoardA.md` was written for exactly this and is **still valid word for word.** Work from it. Summary:

1. **Inspect the bare boards** — must measure 120.0 × 66.0mm. Read the silk: `C1-OUT2/1` style on the top row, `C1-OUT1/2` on the bottom (left digit = left screw, both rows). Sharpie a big **X across J41–J44 on one board** — that's board C, its 4th cell is never populated.
2. **Solder, shortest part first:** R1 → 100nF ceramics (C11/C21/C31/C41/CB2/CB3) → DIP sockets **empty, notch matching silk** → 6-pin male header into J71 → screw terminals, mouths outboard → **CB1 4700µF LAST** (25mm tall, stripe = GND).
3. **Mega → J71, six M-F dupont:** 1=+5V, 2=GND, 3=DATA→D11, 4=SCLK→D12, 5=RCLK→D13, **6=~OE→D10**.

> **The one wire that silently kills the session: J71 pin 6 → D10.** R1 (10k) holds ~OE HIGH = all outputs disabled. Miss it and the board answers on serial, `WALK` prints all 88 channels, and *nothing ever switches, with no error message.* `PIN_OE = 10` is already in the firmware (verified at line 66).

4. **The test, no extra parts:** chips in (notch!), flash `keyboard_v1`, serial 115200, USB power only. Black probe on a fixed GND (**J70 `GND` screw** — the one nearer the right board edge — or U11 pin 8). Red probe into the terminal screw hole, or into a short wire stub clamped in that terminal (much easier than a bare probe).

> **⚠ METER-MODE CORRECTION [Sep 21] (was X, now Y).** Was: "multimeter **continuity**, reads near-short to GND." **Now: use DIODE-TEST mode, not the beeper.** A ULN2803A output is a Darlington, and its ON-state floor is ~0.6–0.9V, not a short. In resistance mode a DMM sourcing ~1mA reads that as **several hundred Ω**, which is above every continuity beeper threshold (~30–50Ω) — so a **perfectly good channel will not beep**, and the old wording would have been read as a board failure. Diode mode (red on terminal, black on GND) displays the drop directly:
> - `HOLD 0` → **~0.6–0.9V**  (channel ON)
> - `RELEASE ALL` → **OL** (channel OFF)
>
> Resistance mode also works if you judge by *contrast* (OL vs a few hundred Ω), never by the beeper. Tiebreaker for an ambiguous reading: 1–10kΩ from +5V to the terminal, then read DC volts — OFF ≈ 5V, ON ≈ 0.1–0.9V.

> **⚠ WALK IS NOT A METER TEST [Sep 21].** `WALK` *pulses* each channel (`firePulse`, default ~`defaultPulseMs`, min gap 200ms) — far too brief for a DMM to settle on. Use **`HOLD <ch>` / `RELEASE ALL`** for every meter check. `WALK 0 31 300 200` is only meaningful with a **visible** load: LED + ~330Ω from +5V to the terminal (the ULN sinks it, ~10mA — and it is the best video shot on this board).

5. **Spot-check channels 0, 7, 8, 15, 16, 23, 24, 31** with `HOLD`. Terminal map verified from `solenoid_driver.kicad_pcb` [Sep 21] — **top-edge blocks are rot 180 (pin 1 = RIGHT screw), bottom-edge blocks are rot 0 (pin 1 = LEFT screw):**

| ch | cell/OUT | ULN pin | terminal | screw | edge |
|---:|---|---|---|---|---|
| 0  | C1-OUT1 | U12.18 | J11 pin1 | RIGHT | TOP |
| 7  | C1-OUT8 | U12.11 | J14 pin2 | RIGHT | BOTTOM |
| 8  | C2-OUT1 | U22.18 | J21 pin1 | RIGHT | TOP |
| 15 | C2-OUT8 | U22.11 | J24 pin2 | RIGHT | BOTTOM |
| 16 | C3-OUT1 | U32.18 | J31 pin1 | RIGHT | TOP |
| 23 | C3-OUT8 | U32.11 | J34 pin2 | RIGHT | BOTTOM |
| 24 | C4-OUT1 | U42.18 | J41 pin1 | RIGHT | TOP |
| 31 | C4-OUT8 | U42.11 | J44 pin2 | RIGHT | BOTTOM |

General rule (all 32): `ch → cell = ch/8+1, OUT = ch%8+1`; OUT1/2→J{c}1, OUT3/4→J{c}2 (**top edge**), OUT5/6→J{c}3, OUT7/8→J{c}4 (**bottom edge**). ULN right column top→bottom = OUT1(pin18)…OUT8(pin11).

6. **Before powering: re-run the 3 rail-OPEN checks** (+5V↔GND, +12V↔GND, +5V↔+12V) *with the chips seated.* A pin folded under a DIP on insertion is the single most common chip-insertion failure and it is invisible from above — count 8 pins a side before you press, and bend the splayed factory legs square on a flat surface first.

**Pass = 8/8 spot checks switch.** The board is DRC-verified, so any failure is a solder bridge or cold joint, not the design.

## Session 2 — Boards B and C, cascade, WALK all 88 (3h)

- Populate B and C the same way. C gets **3 cells only** (12 terminals + J70), 4th socket empty = chain tail.
- **Cascade links are CONNECTORIZED** — **CORRECTION [Sep 20/21] (was X, now Y).** Was (Jul 26): six 22 AWG solid wires soldered straight through J72 into the next board's J71, chosen because only M-M/M-F dupont was owned. **Now: male 6-pin headers on BOTH ends of every link + F-F dupont cables** — Daniel has F-F after all (confirmed Sep 21). Boards unplug freely during WALK debugging; cost is contact resistance, irrelevant at ~10mA of logic.
  - **Header count is 5, not 3:** A.J71 (Mega, M-F) · A.J72 → B.J71 · B.J72 → C.J71. **C.J72 stays empty** (chain tail).
  - Cable is **pin 1 → pin 1, no crossover** (both connectors run 1→6 in the same +Y direction, verified from the PCB Jul 26): 1 +5V · 2 GND · 3 DATA · 4 SCLK · 5 RCLK · 6 ~OE.
  - **New failure mode this change introduces: off-by-one seating.** Six loose F-F strands plugged one pin over is invisible and gives bizarre half-working behaviour. Mitigations: keep the six wires as a **bonded ribbon**, **Sharpie a pin-1 dot on every header**, and **tape/hot-glue each connector once WALK 0–87 passes** (84 solenoids shake the desk; an intermittent on CLK or LATCH is the worst thing on this board to debug).
- Chain: Mega → A.J71 · A.J72 → B.J71 · B.J72 → C.J71 · C.J72 unused.
- `WALK 0 87` on the bench, 5V only. Meter checks use **`HOLD`, not `WALK`** (see the Session 1 correction); `WALK 0 87` itself is the LED/visual pass.

**This is the gate that matters.** All 88 channels switching on the bench, before a single solenoid wire is landed.

## Session 3 — First fire from a real board (1h) · 12V enters the picture

One **spare** solenoid on alligator clips: high side to the PSU +12V, low side into `C1-OUT1`. **USB first, THEN 12V.** `FIRE 0`. Walk it across OUT1–OUT8.

This is the moment the PCB replaces the breadboard rig. Film it — it's the payoff shot the Big Reset video has been waiting on, and it beats the order-confirmation screenshot the script originally called for.

## Session 4 — The +12V buses (2h)

**Decision, re-derived for the no-deck geometry: bare 16 AWG bus along each of the 6 wall tops.** Not a terminal strip, not breadboard rails.

The reason is that **the bus comes to the solenoid, not the solenoid to the bus** — each high lead makes a ~5cm hop straight up to the wire directly above it. Any centralized block (terminal strip, WAGO cluster, breadboard rail) means 84 long runs converging on one point, which is precisely the rat's nest being avoided. The old plate's six walls are the mount, already printed, free.

- Bare tinned 16 AWG along each wall top, six walls, **tied by one trunk at one end**.
- **One 18 AWG from PSU V+ to the trunk.** Each board's J70 pin 1 takes a short stub off the bus. Three wires on PSU V−, one per board J70 pin 2. (BOSYTRO has 3× V+ / 3× V−; this fits with two V+ spare.)
- **No ground wire to the plate** — return comes back through the 84 low-side wires.
- Per solenoid: trim the more convenient lead to ~5cm **at the moment of soldering** and wrap-and-flow it onto the bus. Coil is non-polarized, either lead works.

**Cost: ~84 solder joints, ~90 minutes.** Each is a wrap-around-exposed-wire-and-flow — no hole, no clinch, nothing behind it. This is the *easy* joint, and it is what the Jul 13 protocol breakthrough was for. What broke the perfboard was point-to-point interconnects in a 2.54mm grid; this is not that.

**Payoff: 84 of the 168 danglers disappear in one session.**

## Sessions 5–7 — Land the 84 low sides (4–6h, split by row)

MAP discipline, unchanged since July: **label holes, not wires.** All 84 leads are identical black; position is identity.

- **Golden rule: cut each wire to length only at the moment it lands. Never pre-cut.** Length is the label.
- Sharpie the key name in the box beside each terminal. Log `cell · OUT · key`, one line per wire, **at landing time**.
- **Do NOT tin the tips going into screw terminals.** Solder cold-flows under sustained clamp pressure; the joint loosens over months and presents as intermittent dead keys with no visible cause. Twist strands, strip 4.5–5mm, clamp.
- Velcro each row into a bundle as you finish it.
- Work one wall at a time. A row per session is a real session.

## Session 8 — MAP, WALK, TYPE

Type the MAP table into firmware (or `MAP`/`SAVE` over serial — EEPROM-persisted, no recompile), `WALK 0 87`, then `TYPE` a real sentence. **Push. This is the milestone of milestones.**

---

## Makerspace queue — three small parts, all aimed at the roadblock

None of these are on the critical path, and all three are 1–3 hour prints.

1. **PSU terminal shroud** — safety, print first, see above.
2. **★ Wall-top wire combs ×6** — the direct fix to "organizing the wires is my biggest roadblock." A comb that clips the 2.5mm wall top, captures the 16 AWG bus in a channel, and lanes the low-side leads out one end. Offered as optional back in July; with the desk harness back and runs at ~40cm, it is now worth real time.
   - **Caliper gate before designing this:** solenoid bodies top out at **Z34**, wall top is **Z32** — bodies stand 2mm proud. A comb straddling the wall will foul the bodies unless its spine is ≤2.5mm wide below Z34 and the comb head sits above it. Measure the actual clear gap between a wall's back face and the bodies behind it (`M3c` on the Caliper Gate Card) before any CAD.
3. **Board tray** — holds the three PCBs in a row behind the keyboard, stops them sliding into each other or onto metal.

---

## Explicitly NOT now

- **The plate rebuild** (briefs 07/08). Parked, not cancelled. `cad/fusion_groove_coupon.py` is written and its verifier passes 0/0 — it will still be there in December.
- **Wave 2 mouse**, TFT bring-up, `set_data.json`. All hardware-free dorm-evening work, and genuinely good uses of a college evening — but they don't compete with getting 84 keys firing.
- **PCB rev-2.** Declined Jul 26 on the numbers; nothing has changed.

## Git — overdue

`main` is **ahead of origin by 1** and the sandbox cannot clear the stale lock. From your Terminal:

```
cd ~/Documents/Claude/Projects/Physical\ AI\ Agent
rm -f .git/HEAD.lock .git/index.lock
git add -A && git commit -m "Sep 10: college restart card; rebuild parked, old plate is the vehicle; harness reverts to desk form"
git push
```

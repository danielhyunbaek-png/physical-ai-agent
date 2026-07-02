# Soldering & Assembly Guide — Physical AI Agent Driver Board

*Comprehensive build guide for a **first-time solderer**, focused on the part that's actually hard: **the connections** — how to lay power rails, route every wire, and land the capacitors on perfboard. Source of truth for the netlist is `firmware/keyboard_v0/keyboard_v0.ino`, `firmware/README.md`, and `Driver_Board_Wiring_Map.svg`. This doc turns that netlist into physical, hole-by-hole actions.*

**The chain:** Arduino Mega → 11× 74HC595 shift registers → 11× ULN2803A drivers → 84 solenoids (88 channels, 4 spare). The whole board is **one cell repeated 11×**: build one perfect cell (Stage 2), then it's stamina (Stage 3).

---

## Table of contents

1. [Safety](#1-safety)
2. [Soldering technique — the short version](#2-soldering-technique--the-short-version)
3. [Perfboard, explained](#3-perfboard-explained)
4. [The three ways to make a connection](#4-the-three-ways-to-make-a-connection)
5. [Wire: gauge + color code](#5-wire-gauge--color-code)
6. [Power rails / bus bars — the core skill](#6-power-rails--bus-bars--the-core-skill)
7. [Capacitors — decoupling + reservoir](#7-capacitors--decoupling--reservoir)
8. [Stage 1 — practice](#8-stage-1--practice)
9. [Stage 2 — wire ONE cell + fire the 2×2](#9-stage-2--wire-one-cell--fire-the-22)
10. [Stage 3 — the full 88-channel board](#10-stage-3--the-full-88-channel-board)
11. [First power-up + continuity testing](#11-first-power-up--continuity-testing)
12. [The 5 gotchas](#12-the-5-gotchas-that-kill-driver-boards)
13. [Pin reference](#13-pin-reference)
14. [Pacing + GitHub](#14-pacing--github)

---

## 1. Safety

Review this every session for the first month.

- **Glasses on.** Iron back in its stand the instant it leaves your hand. 30-min timer.
- **Ventilate** — a fan pushing flux fumes away, or an open window. Don't lean into the smoke.
- **Leaded solder** → wash hands before eating; don't eat at the bench.
- **Never solder a powered board.** Unplug the 12 V PSU before *any* wiring change — those terminals can weld a screwdriver.
- **5 V and 12 V never touch.** Only the grounds tie, at one point. (This is electrical, not a burn — but it's the one that smokes chips.)

---

## 2. Soldering technique — the short version

You said first time, so the muscle-memory matters more than theory. Two rules: **a clean tinned tip, and you heat the joint, not the solder.**

**Tin the tip:** as soon as the iron hits temp (~325–340 °C for 60/40 leaded), melt a bit of solder onto the tip and wipe on brass wool. Re-tin whenever it looks dull/grey. A bright, wetted tip transfers heat; a dull one doesn't.

**The five-count joint:**

1. Press the iron against **both** the copper pad **and** the component lead at once.
2. Count ~1–2 s (let the joint heat).
3. Feed solder into the **joint**, on the side away from the iron — not onto the tip.
4. ~1 s, pull the solder away.
5. Pull the iron away. **Don't move it** for 2–3 s while it freezes.

**Reading the result:**

| Looks like | Verdict | Fix |
|---|---|---|
| Shiny little volcano, hugs pad + lead | Good | — |
| Dull, grainy, lumpy | Cold joint (moved or too little heat) | Reheat, add a touch of fresh solder |
| Ball sitting on top, not stuck to pad | No wetting (didn't heat the pad) | Reheat the pad longer, add flux |
| Solder linking two pads you didn't want joined | Bridge | Flux + drag wick across it |
| Pad lifted off the board | Overheated / too long | Avoid — use a jumper to the next pad to recover |

Flux pen helps any joint wet faster. Keep the wick handy — bridges are normal, clearing them is a 5-second move once you've practiced it (Stage 1).

---

## 3. Perfboard, explained

Your BOM perfboard is **single-sided, through-hole** (10×15 cm). Two flavors exist — know which you have:

- **Pad-per-hole** (most common, almost certainly yours): every hole has its own isolated copper ring on the bottom. **Nothing is connected** until you connect it. Maximum freedom, you make every link by hand. *This guide assumes this.*
- **Stripboard / Veroboard:** copper runs in continuous strips across whole rows. You *cut* a strip (with a drill bit or knife) to break it where you don't want a connection. If yours is strips, the rails are half-built for you — but you must cut gaps under each IC so opposite pins aren't shorted. Tell me if it's strips and I'll adapt the steps.

**Orientation:** components sit on the **top** (plain) side, legs poke through, you solder on the **bottom** (copper) side and route most jumpers there. The hole grid is **0.1″ (2.54 mm)** pitch — the exact spacing of DIP IC pins, so sockets drop straight in.

**Read the board like graph paper.** Pick a corner as (col 1, row 1). Plan on paper in those coordinates before you solder anything — "595 #1 socket spans cols 3–4, rows 5–12" — so you don't run out of room or trap yourself. A pencil sketch saves an hour of desoldering.

---

## 4. The three ways to make a connection

Every link on the board is one of these:

1. **Bent lead.** A component's own trimmed leg, bent over on the solder side to reach an adjacent pad, then soldered. Good for a cap spanning two neighboring pins. Free, but only reaches ~1–3 holes.
2. **Solder bridge.** Deliberately blob solder across 2–3 *adjacent* pads to join them. Useful for short rail segments. **Use sparingly** — as a beginner you'll make accidental ones, so don't rely on intentional ones over distance.
3. **Jumper wire** (your workhorse). A cut piece of 22 AWG solid wire, stripped both ends, routed on the solder side from pad A to pad B, soldered at each end. **Insulated** for any run that crosses other connections; **bare/tinned** for buses (next section). 90% of your connections are jumpers.

**Beginner rule of thumb:** sockets and component legs go through from the top; everything else is a **jumper on the bottom**. Resist long solder-bridge trails — they look fast and fail slow.

How to make a clean jumper:
- Cut to length with ~5 mm extra. Strip ~3 mm each end. Tin both ends (melt a little solder into the strands/wire so it's pre-wetted).
- Hold one end on the target pad, touch iron, the pre-tinned wire fuses in ~1 s. Repeat the other end.
- Route flat against the board; don't leave loops that can snag or short.

---

## 5. Wire: gauge + color code

You have three wire types — each has a job:

| Wire | Use it for | Why |
|---|---|---|
| **22 AWG solid** (multi-color) | On-board jumpers + the +5 V / GND / signal rails | Solid holds its shape in holes and routes neatly |
| **18 AWG silicone stranded** (red/black) | The 12 V feed PSU→board, and board GND→PSU | Carries the big current; flexible |
| **22 AWG stranded** (multi-color) | Board output header → each solenoid (off-board runs) | Flexes without fatiguing; solid-core would crack at the solder joint over time |

**Color code** — adopt the one already on your wiring map so the board matches the drawing:

- **Red** = +5 V logic
- **Orange/Yellow** = +12 V power
- **Black** = GND (common)
- **Blue** = DS (serial data)
- **Green** = SH_CP (shift clock)
- **White** = ST_CP (latch)

Pick a color *per net* and never reuse it for something else. On a 260-joint board, color discipline is the difference between a 10-minute fault hunt and a 2-hour one.

---

## 6. Power rails / bus bars — the core skill

A **rail** (bus) is one continuous conductor that many chips tap for the same net. You will build **three power rails** (+5 V, GND, +12 V) plus **two signal rails** (SH_CP, ST_CP). Get this right and the rest is just taps.

### How to physically lay a rail

**Method — bare bus wire along a row** (do this):

1. Cut a length of **22 AWG solid** wire spanning the full width you need (for the full board, edge to edge). Strip **all** the insulation off — you want bare wire. (Or use bare tinned bus wire if your kit has it.)
2. Lay it flat on the **solder side**, running straight along **one row of holes**.
3. Tack it down: solder it to the pad at the **first** hole, pull it taut and straight, solder the **last** hole, then solder **every** hole (or at minimum every hole you'll tap + every 3rd hole for mechanical hold). Now that entire row is one continuous conductor.
4. A component or jumper "joins the rail" by soldering to **any pad along that row.**

That's it — a rail is just a wire soldered down a row, with everything for that net soldered onto it.

### Where each rail goes (floor plan)

Lay them out so the 5 V side and 12 V side are physically separated, with GND as the shared spine between:

```
 top edge   ───────────────────  +5V rail   (red)        ← feeds every 595 VCC + MR
            [ 595 #1 ][ 595 #2 ] ... [ 595 #11 ]          ← shift-register row
            ───────────────────  SH_CP rail (green)       ← clock, every 595 pin 11
            ───────────────────  ST_CP rail (white)       ← latch, every 595 pin 12
            ───────────────────  GND  rail  (black)  ★    ← the spine: every chip GND, PSU GND, Mega GND
            [ULN #1 ][ULN #2 ] ... [ ULN #11 ]            ← driver row
            ═══════════════════  +12V rail  (orange) ▓    ← heavy: every ULN COM + every solenoid high side
 bottom     [========= 88-pin OUTPUT HEADER =========]    ← ULN outputs → solenoids
```

- **+5 V rail** (red, top): feeds each 595's VCC (pin 16) and MR (pin 10).
- **SH_CP rail** (green) and **ST_CP rail** (white): the two clock/latch signals are shared by all 11 shift registers, so they're rails too — tap every 595 pin 11 to the green rail, every pin 12 to the white rail.
- **GND rail** (black, the spine ★): every chip's GND, plus the reservoir cap, plus the one tie to PSU GND and Mega GND. Make this generous.
- **+12 V rail** (orange, heavy ▓): every ULN COM (pin 10) and every solenoid's high-side lead. **This one carries real current** — fired solenoids pull 300 mA each, several at once. Use a **doubled 22 AWG run or a thick tinned wire**, and feed it from the PSU with the **18 AWG silicone**. Keep it on the driver side, away from the 5 V rail.

### Star ground (do this, it prevents weird faults)

"Star ground" = all grounds meet at **one** point, not in a daisy chain. In practice: your **GND rail is the spine**, and you tie **PSU GND** and **Arduino Mega GND** to that rail **at one spot each** (ideally near each other). Every chip's GND pin taps the same rail. This keeps the heavy solenoid return current from flowing *through* your logic ground and corrupting the signals. The single most common "it works on the breadboard but the soldered board glitches" cause is a sloppy ground — so build the spine first and tap everything to it.

> **The cardinal rule, physically:** the +5 V rail and the +12 V rail must have **zero** copper between them. The *only* electrical connection between the 5 V world and the 12 V world is the shared **GND rail**. Before powering up you'll meter +5 V↔+12 V and expect infinite resistance (open).

---

## 7. Capacitors — decoupling + reservoir

Two kinds, two completely different jobs and rules.

### A) Decoupling caps — 0.1 µF ceramic (NON-polarized) — one per chip, 22 total

**Job:** when a chip switches, it gulps a spike of current. The 0.1 µF sits right at the chip's power pins and supplies that spike locally, so the rail doesn't dip and ring. Skipping them → random glitches that are *miserable* to debug. They're cheap insurance; never omit.

**Placement — as close to the chip's power pins as physically possible:**

- **74HC595:** across **VCC (pin 16) ↔ GND (pin 8).**
- **ULN2803A:** it has no logic VCC — put its 0.1 µF across **COM (pin 10, +12 V) ↔ GND (pin 9)** to snub the inductive switching noise from the solenoids. (This is the ULN's entry in the "22 total.")

**How to land it (non-polarized, so either way round):**

1. Bend the two legs so they straddle the two target pads (e.g., the pads right at pin 16 and pin 8).
2. Push it down close to the board, legs through the holes.
3. Solder both legs on the bottom, **trim flush.** Keep the legs **short** — long legs add inductance and defeat the cap.

If the two power pins aren't on adjacent holes, put the cap on the two nearest empty holes and run two **short** jumpers to VCC and GND. Short is the whole point.

### B) Reservoir / bulk cap — electrolytic (POLARIZED) — on the 12 V rail

**Job:** a local tank of charge on the 12 V rail so the inrush when a solenoid energizes doesn't sag the whole rail. Single cell: **470 µF** (or larger). Full board: **4700 µF 25 V** across the 12 V input.

**POLARITY — this one bites:**

- Electrolytics have a **+** and a **−** leg. The **stripe/arrow** printed on the can marks the **NEGATIVE (−)** leg. The **longer** leg is **POSITIVE (+)**.
- **+ leg → +12 V rail (orange). − leg (stripe) → GND rail (black).**
- **Reverse it and it overheats and can burst** (loud pop, hot electrolyte). Double-check before soldering and again before first power.
- **Voltage rating:** a 25 V cap on a 12 V rail is correct (rule of thumb: rating ≥ ~1.5–2× the rail). Never use one rated *below* the rail.

**How to land it:**

1. Identify + (long leg) and − (stripe side). Decide which holes are +12 V and which are GND **before** inserting.
2. Insert legs (it stands vertical), bend them slightly on the bottom so it won't fall out.
3. Solder both — these legs carry more current, so give a solid joint — then trim.
4. Place it **near the ULN COM / output side** on the full board (where the inrush happens), close to the 12 V input.

---

## 8. Stage 1 — practice (scrap only, ~1–2 h)

Before any real part, get the motion. On scrap perfboard + spare header pins:

1. Solder **20–30 header pins.** Cut them off, do it again. Goal: a clean pin in **under 90 s** without thinking.
2. Solder **10 wires to header pins** (tin the wire end first). This is exactly the jumper move from §4.
3. **Lay a 10-hole bus wire** (§6) and solder every hole — this is the rail skill, rehearsed on scrap.
4. **Make 2 bridges on purpose and clear them with wick.** You'll make real ones; own the fix.
5. **Desolder a pin** with wick/sucker and re-seat it.

**Move on when:** consistent shiny cones, you can run a straight tacked-down bus, and you can clear a bridge on demand.

---

## 9. Stage 2 — wire ONE cell + fire the 2×2 (Week-2 milestone)

This is the whole board in miniature. Get it perfect; Stage 3 is this ×11.

### 9a. Breadboard first (no soldering)

Prove the circuit before committing it (straight from `firmware/README.md`):

- **`sr_led_walk.ino`** — 1× 595 + 8 LEDs (330 Ω each, Q0–Q7→LED→GND). A bit should walk across the LEDs → proves DS/SH_CP/ST_CP.
- **`keyboard_v0.ino`** — swap LEDs for 1× ULN2803A → your 4 prototype solenoids on 12 V. `FIRE 0`…`FIRE 3` → four crisp clicks.

### 9b. Solder the cell — exact build order

Place the cell at the **left** of the board; leave room to the right (this is cell #1 of 11). Coordinates are yours from the §3 sketch; pin numbers below are the connections.

**Step 1 — Sockets.** Drop in the **DIP-16** socket (for the 595) and the **DIP-18** socket (for the ULN), a few rows apart. Note the **notch = pin-1 end**; orient both the same way. Tack **2 diagonal corners** of each, check they sit dead flat, then solder all pins. **The ICs themselves go in last — never solder a chip.**

**Step 2 — Rails first** (before the board gets crowded). Lay these as bare bus wires (§6):
- **+5 V** rail (red feed) along the top.
- **GND** rail (black) — the spine.
- **+12 V** rail (orange, heavier) on the ULN side.
Keep +5 V and +12 V apart.

**Step 3 — 595 power + decoupling:**
- pin 16 (VCC) → +5 V rail
- pin 8 (GND) → GND rail
- pin 13 (OE̅) → GND rail (outputs always enabled)
- pin 10 (MR̅) → +5 V rail (don't reset)
- **0.1 µF** across pin 16 ↔ pin 8, legs short.

**Step 4 — ULN power + decoupling:**
- pin 9 (GND) → GND rail
- pin 10 (COM) → +12 V rail (**enables the flyback diodes — never skip**)
- **0.1 µF** across pin 10 ↔ pin 9.

**Step 5 — Logic, 595 → ULN, one-to-one** (eight insulated jumpers). Q0–Q7 map to IN1–IN8:

| 595 output (pin) | → | ULN input (pin) |
|---|---|---|
| Q0 (15) | → | IN1 (1) |
| Q1 (1) | → | IN2 (2) |
| Q2 (2) | → | IN3 (3) |
| Q3 (3) | → | IN4 (4) |
| Q4 (4) | → | IN5 (5) |
| Q5 (5) | → | IN6 (6) |
| Q6 (6) | → | IN7 (7) |
| Q7 (7) | → | IN8 (8) |

**Step 6 — Control lines to the Mega** (flying leads to a 3-pin header, or Dupont):
- pin 14 (DS) → Mega **D11** — *blue*
- pin 11 (SH_CP) → Mega **D12** — *green*
- pin 12 (ST_CP) → Mega **D13** — *white*
- one **GND** wire: Mega GND → GND rail (this is the logic-side half of the star ground).

**Step 7 — Outputs:** ULN OUT1–OUT8 (pins 18→11) → an **8-pin output header**. Then each solenoid: **one lead → a header pin, other lead → +12 V rail.**

**Step 8 — Reservoir cap:** **470 µF** across +12 V ↔ GND, **+ leg to +12 V, stripe to GND** (§7B). Near the ULN.

**Step 9 — Star-ground tie:** PSU GND → GND rail, at one point (Mega GND already tied in Step 6).

→ Then **§11** (test cold, power 5 V only, then add 12 V) and `FIRE 0 40`…`FIRE 3 40`. Tune with `PULSE` (firmware found **~22 ms** good on the 2×2; 30–40 ms safe start).

> **Milestone:** first fire from a *soldered* board. Film the click; commit the working-cell photo + firmware tweak to GitHub.

---

## 10. Stage 3 — the full 88-channel board (Week 5, ~260 joints)

You've built 1 of 11 cells. Now repeat it, sharing the rails. **Work in horizontal passes across all 11**, not one whole cell at a time — it's faster and more uniform.

**Plan on paper first:** 11 DIP-16 + 11 DIP-18 sockets in two rows; rails per the §6 floor plan; an **88-pin output header** along the bottom (84 → solenoids, 4 spare). Measure your Stage-2 cell width × 11 — if it won't fit one board, bridge two before you start.

**Build order (pass by pass):**

1. **All 22 sockets.** Diagonal-tack, check flat, finish. Same pin-1 orientation across the row.
2. **All five rails, full width:** +5 V, GND spine, +12 V (heavy), SH_CP, ST_CP (§6).
3. **All 22 decoupling caps** (§7A) — 595s across 16↔8, ULNs across 10↔9.
4. **Per-cell power taps ×11:** each 595 pin16→+5 V, pin8→GND, pin13→GND, pin10→+5 V; each ULN pin9→GND, pin10→+12 V.
5. **Per-cell logic ×11:** the eight Q0–Q7 → IN1–IN8 jumpers (the §9 Step-5 table), repeated for every cell.
6. **The SR cascade chain:** jumper **Q7′ (pin 9) of chip N → DS (pin 14) of chip N+1**, for N = 1…10. Chip **#1's DS (pin 14) → Mega D11** (blue). This is the only DS that goes to the Mega; the rest chain.
7. **Common clock + latch:** tap **every** 595 pin 11 → SH_CP rail (green, → Mega D12); **every** pin 12 → ST_CP rail (white, → Mega D13).
8. **Output header (88 pins):** ULN outputs → header; +12 V distributed to every solenoid high side.
9. **4700 µF reservoir** across the 12 V input (+ to +12 V, stripe to GND).
10. **Star ground:** PSU GND + Mega GND → the GND spine, one point.

**Test each cell as you finish its column** — continuity-check it then and there. Finding one bad joint in 60 is easy; in 260 it's misery.

→ Then **§11**, then flash **walk mode** (cycle channels 0–83, ~100 ms each) and run **one** test solenoid down the 88-pin header: every channel should click; 84–87 do nothing (or a status LED).

**Acceptance:** all 84 channels click in sequence on the roving test solenoid → cleared for Week 6 (mount + wire all 84). Time-lapse it for the "260 joints" reel.

---

## 11. First power-up + continuity testing

**Always test cold (unpowered) with the multimeter on continuity (the beep) before applying any power.**

Check, in order:
1. **Shorts that must NOT exist** (expect silence / open):
   - +5 V rail ↔ +12 V rail
   - +5 V rail ↔ GND rail
   - +12 V rail ↔ GND rail
   - any output/header pin ↔ its neighbor
2. **Connections that MUST exist** (expect beep):
   - every 595 pin 16 ↔ +5 V rail; every pin 8 ↔ GND rail
   - every ULN pin 10 ↔ +12 V rail; every pin 9 ↔ GND rail
   - the cascade unbroken: chip N pin 9 ↔ chip N+1 pin 14, all the way down
   - SH_CP rail ↔ every 595 pin 11; ST_CP rail ↔ every 595 pin 12
   - GND rail ↔ PSU GND ↔ Mega GND (one common net)
3. **Reservoir cap polarity:** + leg on +12 V, stripe on GND. Look twice.

**Power-up sequence:**
1. **5 V logic only** — no 12 V, no solenoids. Seat the ICs (pin-1 right). Power the Mega/5 V rail. Feel each chip: **anything hot or any smell → cut power immediately** and recheck. Run the LED-walk / a no-solenoid FIRE; outputs should toggle.
2. **Add 12 V last** — PSU off, connect the 12 V feed, then power on. Connect a test solenoid and `FIRE`. Crisp click, full retract, no buzz.

Keep one hand near the kill switch on every first power. The PSU is conservatively rated but mechanical things surprise you.

---

## 12. The 5 gotchas that kill driver boards

Tape this above the bench.

1. **ULN COM (pin 10) → +12 V on every chip.** No flyback = a dead driver on the first solenoid.
2. **5 V and 12 V never touch.** Only the grounds tie, at one star point.
3. **Socket every IC.** Never solder the chip itself.
4. **0.1 µF across every chip's power pins** — all 22, legs short.
5. **Reservoir cap polarity** (+ to 12 V, stripe to GND) and **test cold → 5 V-only → 12 V last.**

---

## 13. Pin reference

### 74HC595 shift register — DIP-16

| Pin | Name | Connect to |
|----:|------|------------|
| 1 | Q1 | ULN IN2 (pin 2) |
| 2 | Q2 | ULN IN3 (pin 3) |
| 3 | Q3 | ULN IN4 (pin 4) |
| 4 | Q4 | ULN IN5 (pin 5) |
| 5 | Q5 | ULN IN6 (pin 6) |
| 6 | Q6 | ULN IN7 (pin 7) |
| 7 | Q7 | ULN IN8 (pin 8) |
| 8 | GND | GND rail |
| 9 | Q7′ | **DS (pin 14) of the NEXT 595** (cascade) |
| 10 | MR̅ | +5 V rail (don't reset) |
| 11 | SH_CP | SH_CP rail → Mega **D12** (green) |
| 12 | ST_CP | ST_CP rail → Mega **D13** (white) |
| 13 | OE̅ | GND rail (outputs always on) |
| 14 | DS | from **prev 595 Q7′** (or Mega **D11** blue, for chip #1) |
| 15 | Q0 | ULN IN1 (pin 1) |
| 16 | VCC | +5 V rail (+ 0.1 µF to GND) |

### ULN2803A Darlington array — DIP-18

*Outputs run in reverse: IN1→OUT1 is pin 1→pin 18; IN8→OUT8 is pin 8→pin 11.*

| Pin | Name | Connect to |
|----:|------|------------|
| 1 | IN1 | 595 Q0 (pin 15) |
| 2 | IN2 | 595 Q1 (pin 1) |
| 3 | IN3 | 595 Q2 (pin 2) |
| 4 | IN4 | 595 Q3 (pin 3) |
| 5 | IN5 | 595 Q4 (pin 4) |
| 6 | IN6 | 595 Q5 (pin 5) |
| 7 | IN7 | 595 Q6 (pin 6) |
| 8 | IN8 | 595 Q7 (pin 7) |
| 9 | GND | GND rail (common) |
| 10 | COM | **+12 V rail** (enables internal flyback diodes) |
| 11 | OUT8 | solenoid 8 low side |
| 12 | OUT7 | solenoid 7 low side |
| 13 | OUT6 | solenoid 6 low side |
| 14 | OUT5 | solenoid 5 low side |
| 15 | OUT4 | solenoid 4 low side |
| 16 | OUT3 | solenoid 3 low side |
| 17 | OUT2 | solenoid 2 low side |
| 18 | OUT1 | solenoid 1 low side |

*Each solenoid's other lead → +12 V rail. The ULN sinks the low side to GND when its input goes high.*

### Arduino Mega → board

| Mega pin | Net | Color | Goes to |
|---|---|---|---|
| D11 | DS | blue | 595 **#1** pin 14 only |
| D12 | SH_CP | green | SH_CP rail (all 11) |
| D13 | ST_CP | white | ST_CP rail (all 11) |
| GND | GND | black | GND rail (star point) |

---

## 14. Pacing + GitHub

| Session | Time | Do |
|---|---|---|
| 1 | ~1–2 h | Stage 1 practice — clean pin <90 s, run a bus, clear a bridge. |
| 2 | ~2–3 h | Stage 2 — breadboard, then wire one cell, then fire the 2×2. |
| 3 | ~6–10 h (splittable) | Stage 3 — full board in passes + walk-mode on all 84. |

**Commit this guide now.** Then commit a photo + the passing-test note at each milestone — first clean joint, first soldered-cell fire, walk-mode pass. Those are exactly the weekly-retro milestones your repo is built around.

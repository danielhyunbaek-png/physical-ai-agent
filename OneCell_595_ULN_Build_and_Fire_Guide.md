# One-Cell Driver Test — Build & Fire Guide

**Scope:** build and fire a single driver cell — **one 74HC595 + one ULN2803A driving 4 solenoids** — on real perfboard, from bare board to four clicks. This is **cell #1 of Board A**, so build it as the real thing: the rails you lay here will later extend rightward to cells 2–4.

**The chain:** Arduino Mega → 74HC595 (shift register, turns 3 Mega pins into 8 outputs) → ULN2803A (driver, switches the 12 V solenoid current) → 4 solenoids.

**Milestone:** this is your "first fire from a soldered board." Film it; commit a photo + any pulse tweak to GitHub when it works.

**Realistic time:** 4–6 h for a first solder job. It splits cleanly: Session 1 = all soldering (§3) + cold test (§4); Session 2 = power-up (§5) + fire (§6). Don't rush — a hurried cold joint costs more to find later than it saves now.

> Convention: **595 pin N** and **ULN pin N** always mean the chip's pin number. You solder to the matching **socket** pin. Chips stay OUT of the sockets until §5.

---

## 0. Parts, tools, safety

### 0.1 Parts for this one cell

- [ ] 1× 74HC595 shift register (DIP-16)
- [ ] 1× ULN2803A Darlington driver (DIP-18)
- [ ] 1× 16-pin DIP socket  ·  1× 18-pin DIP socket
- [ ] 2× 0.1 µF ceramic capacitor (decoupling — non-polarized)
- [ ] 1× 4700 µF 25 V electrolytic capacitor (reservoir — polarized) *(you own 2; use one)*
- [ ] 22 AWG **solid** hookup wire for rails + jumpers, in net colors (red/orange/black/blue/green/white)
- [ ] 18 AWG silicone wire (red/black) for the 12 V PSU feed
- [ ] 22 AWG **stranded** wire for the 4 solenoid runs (off-board — flexes without cracking)
- [ ] 4× prototype solenoids (the 5 N fast-ship kit)
- [ ] Your perfboard (Board A), pad-per-hole, ~33 rows
- [ ] 1× 8-pin header (optional, for the outputs — or solder solenoid wires straight to the OUT pads)
- [ ] Arduino Mega + USB cable  ·  12 V PSU (BOSYTRO) + IEC cord

### 0.2 Tools

- [ ] Soldering iron + stand, 60/40 leaded solder, flux pen, brass wool
- [ ] Solder wick **and/or** solder sucker (for bridges / rework)
- [ ] **Multimeter with continuity (beep) mode** — used heavily in §4
- [ ] Wire strippers, flush cutters, needle-nose pliers, tweezers
- [ ] Safety glasses, a fan or open window, a 30-min iron timer
- [ ] An accessible switch on the 12 V (your "kill switch")

### 0.3 Safety — non-negotiable

- **Glasses on.** Iron back in the stand the instant it leaves your hand.
- **Ventilate** — fan pushing flux fumes away or a window open. Don't lean into the smoke.
- **Leaded solder:** wash hands before eating; don't eat at the bench.
- **Never solder a powered board.** Unplug the 12 V before any wiring change.
- **5 V and 12 V never touch.** Only the grounds tie, at one star point. (This is the one that smokes chips.)

---

## 1. Soldering technique (the 60-second version)

You skipped the practice stage, so these first joints *are* your practice — go slow on the first dozen.

**Tin the tip:** at temp (~325–340 °C), melt a little solder on the tip and wipe on brass wool. Re-tin whenever it looks dull. A bright wetted tip transfers heat; a dull one doesn't.

**The five-count joint:**

1. Press the iron against **both** the copper pad **and** the pin at once.
2. Count ~1–2 s (heat the joint).
3. Feed solder into the **joint**, on the side away from the iron — not onto the tip.
4. ~1 s, pull the solder away.
5. Pull the iron away. **Don't move it** for 2–3 s while it freezes.

**Reading the joint:**

| Looks like | Verdict | Fix |
|---|---|---|
| Shiny little volcano, hugs pad + pin | Good | — |
| Dull, grainy, lumpy | Cold joint | Reheat, add a touch of fresh solder |
| Ball sitting on top, not stuck | No wetting | Reheat the **pad** longer, add flux |
| Solder linking two pads you didn't want | Bridge | Flux + drag wick across it |
| Pad peeling off the board | Overheated | Stop; jumper to the next pad to recover |

---

## 2. Plan it on paper first (your board)

Pad-per-hole means **nothing is connected until you solder it** — so a sketch keeps you from trapping yourself. You measured ~33 rows; here's the cell stacked top-to-bottom (matches your 7 / 4 / 10 / 4 / 8 placement):

```
row 1–6    top margin            ← +5V rail lives here (row ~6, just above the 595)
row 6      ───── +5V rail (red)
row 8–11   [ 74HC595  DIP-16 ]   ← top pins row 8, bottom pins row 11; NOTCH LEFT = pin 1
row ~14    ───── SH_CP rail (green)
row ~16    ───── ST_CP rail (white)
row ~19    ───── GND rail (black) ★ spine
row 22–25  [ ULN2803A DIP-18 ]   ← top pins row 22, bottom pins row 25; NOTCH LEFT = pin 1
row ~27    ═════ +12V rail (orange, heavier)
row ~29    [ 8-pin OUTPUT header ]  → solenoids
row 30–33  bottom margin         ← leave clear for output wires to exit
```

- Both chips: **long axis horizontal, notch/pin-1 to the LEFT**, top pin-row facing the +5 V rail.
- A DIP's two pin-rows sit **3 holes (0.3″) apart** — that's why the 595 lands on rows 8 & 11, the ULN on 22 & 25.
- This vertical layout **repeats for cells 2–4** later; measure it once here and match it.

---

## 3. Build — exact order (chips stay OUT)

Work top-to-bottom, rails before the board gets crowded. **Wire colors** (adopt and never reuse): red = +5 V, orange = +12 V, black = GND, blue = DS, green = SH_CP, white = ST_CP, grey = signal (Q→IN, OUT→solenoid).

### Step 1 — sockets

Drop the **DIP-16** and **DIP-18** sockets in from the top, notch/pin-1 LEFT, both the same way. **Tack two diagonal corners** of each, check it sits **dead flat**, then solder **every** pin (all 16, all 18). The chips themselves go in last (§5) — never solder a chip.

### Step 2 — the five rails (bare 22 AWG bus wire)

Lay each as a straight bare wire soldered down a row (§2 positions). For this single cell they're short; they'll extend right later.

- [ ] **+5 V** (red) — top, ~row 6
- [ ] **SH_CP** (green) — ~row 14
- [ ] **ST_CP** (white) — ~row 16
- [ ] **GND** (black, the spine ★) — ~row 19 — make this generous
- [ ] **+12 V** (orange, heavier) — ~row 27 — keep it well away from +5 V

### Step 3 — 595 power + decoupling cap

| 595 pin | Name | Connect to |
|--:|---|---|
| 16 | VCC | **+5 V** rail |
| 10 | MR̅ | **+5 V** rail (don't reset) |
| 8 | GND | **GND** rail |
| 13 | OE̅ | **GND** rail (outputs always enabled) |

- [ ] **0.1 µF** across **pin 16 ↔ pin 8**, legs short. (Non-polarized — either way round. If the pins aren't on adjacent holes, put the cap on the two nearest empty holes and run two short jumpers. *Short is the whole point.*)

### Step 4 — ULN power + decoupling cap

| ULN pin | Name | Connect to |
|--:|---|---|
| 9 | GND | **GND** rail |
| 10 | COM | **+12 V** rail — **enables the internal flyback diodes; never skip** |

- [ ] **0.1 µF** across **pin 10 ↔ pin 9**, legs short.

### Step 5 — logic jumpers, 595 → ULN (8 insulated jumpers)

Q0–Q7 map one-to-one to IN1–IN8:

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

*(595 pin 9 = Q7′ is left open on a single cell — it's the cascade out for the next chip.)*

### Step 6 — control leads to the Mega + power feeds

| From | → To | Color |
|---|---|---|
| 595 pin 14 (DS) | Mega **D11** | blue |
| 595 pin 11 (SH_CP) | Mega **D12** | green |
| 595 pin 12 (ST_CP) | Mega **D13** | white |
| Mega **GND** | GND rail (star point) | black |
| Mega **5 V** pin | +5 V rail | red |

*(The Mega is powered by USB from your laptop; its 5 V pin feeds the +5 V rail. Do NOT also feed +5 V from the 12 V PSU.)*

### Step 7 — outputs + solenoids

ULN OUT1–OUT8 are pins **18 → 11** (outputs run in reverse of inputs). Land them on the 8-pin header (or wire directly). For the 4 prototype solenoids use channels 0–3:

| Channel | ULN OUT (pin) | Solenoid |
|---|---|---|
| 0 | OUT1 (18) | solenoid 1 low side |
| 1 | OUT2 (17) | solenoid 2 low side |
| 2 | OUT3 (16) | solenoid 3 low side |
| 3 | OUT4 (15) | solenoid 4 low side |

- [ ] Each solenoid: **one lead → its OUT/header pin**, **other lead → +12 V rail** (use 22 AWG stranded for these off-board runs).
- [ ] Bring the **12 V feed** in with 18 AWG silicone: **PSU +12 V → +12 V rail**.

### Step 8 — reservoir cap (POLARITY MATTERS)

- [ ] **4700 µF 25 V** across **+12 V ↔ GND**, placed **near the ULN**.
- **+ leg (longer) → +12 V rail (orange).**
- **− leg (stripe/arrow on the can) → GND rail (black).**
- Reverse it and it overheats and can **burst** (loud pop, hot electrolyte). Double-check now, and again before first power. 25 V rating on a 12 V rail is correct.

### Step 9 — star ground

- [ ] **PSU GND → GND rail** at one point (Mega GND already tied in Step 6). All grounds meet at this one spot — that's the star. Sloppy grounding is the #1 "works on breadboard, glitches when soldered" cause.

---

## 4. Cold continuity test — multimeter, NOTHING powered, chips still OUT

This is the step that saves chips. Unplug everything. Set the meter to **continuity (the beep / ♪ symbol)**: touch the two probes together first to hear the beep so you know it works. Then check, in order.

### 4.1 Shorts that must NOT exist — expect **silence / OL (open)**

| Probe A | Probe B | Want |
|---|---|---|
| +5 V rail | +12 V rail | **no beep** |
| +5 V rail | GND rail | **no beep** |
| +12 V rail | GND rail | **no beep** |
| any output/header pin | its neighbor pin | **no beep** |

A beep here = a bridge or a misroute. Find and clear it (flux + wick) before going on. **+5 V ↔ +12 V must be open** — meter it twice.

### 4.2 Connections that MUST exist — expect **beep**

| Probe A | Probe B | Want |
|---|---|---|
| 595 pin 16 | +5 V rail | beep |
| 595 pin 10 | +5 V rail | beep |
| 595 pin 8 | GND rail | beep |
| 595 pin 13 | GND rail | beep |
| ULN pin 10 | +12 V rail | beep |
| ULN pin 9 | GND rail | beep |
| GND rail | Mega GND | beep |
| GND rail | PSU GND | beep |
| 595 pin 14 | Mega D11 | beep |
| 595 pin 11 | Mega D12 | beep |
| 595 pin 12 | Mega D13 | beep |
| each 595 Q (15,1–7) | its ULN IN (1–8) | beep (all 8) |
| each ULN OUT (18,17,16,15) | its solenoid low-side lead | beep |

### 4.3 Capacitor polarity — eyeball, don't meter

- [ ] Reservoir **4700 µF**: + (long leg) on **+12 V**, stripe on **GND**. Look twice.
- [ ] Both **0.1 µF** sit right across their chip's power pins (595 16↔8, ULN 10↔9), legs short.

**Pass criteria:** every "no beep" is silent, every "beep" beeps, polarity confirmed. Only then apply power.

---

## 5. Power-up — exact sequence (do not reorder)

### 5.1 Seat the chips

With power **off**, press the **74HC595** and **ULN2803A** into their sockets. **Notch/pin-1 must match the socket** (and your §2 sketch). Pins often splay — rock each chip on a flat surface to bend them in slightly so they seat without bending under.

### 5.2 5 V logic only — no 12 V yet

1. Leave the 12 V PSU **off/disconnected**.
2. Power the Mega over USB (this drives the +5 V rail).
3. **Feel both chips.** Anything warm, or any smell → **cut power immediately** and re-check §4. Cold chips = good.
4. Flash `firmware/keyboard_v0/keyboard_v0.ino`. Open Serial Monitor at **115200 baud, line ending = Newline**. You should see: `keyboard_v0 ready (pulse 40 ms)…`.
5. Sanity-check the logic with no solenoids: type `FIRE 0`. The board can't click yet (no 12 V), but the meter on **ULN pin 1 (IN1)** should blip, or probe **595 Q0 (pin 15)**. If outputs respond, your shift register + wiring are alive.

### 5.3 Add 12 V last

1. PSU **off**. Connect the 12 V feed (+12 V → +12 V rail, GND → GND star). Connect your 4 solenoids.
2. **Hand near the kill switch**, then switch the PSU on.
3. Quiet board, no smell, no heat = good. Any pop/smell/heat → kill instantly.

---

## 6. Fire the solenoids

With `keyboard_v0` running and 12 V live (Serial Monitor, 115200, Newline):

```
FIRE 0      ← fires channel 0 at the default pulse (40 ms)
FIRE 1
FIRE 2
FIRE 3
```

Each returns `OK FIRE <ch> <ms>` and gives one crisp click. Or sweep all four at once:

```
BURST 4     ← fires channels 0–3 in sequence (100 ms gap)
```

If a fire ever hangs on: `ALLOFF` forces every channel low.

**Pass criteria:** 4 clicks in order, plungers fully retract between fires, **no buzzing, no missed clicks**. That's the milestone.

### 6.1 Tune the pulse

- `PULSE 30` sets the default to 30 ms; `PULSE` alone reports the current value. Or override per-shot: `FIRE 0 30`.
- Start at **40 ms**, try **30 ms** and **50 ms**, and listen. Shorter = less heat. Your 2×2 prototype ran well as low as **~22 ms**.
- Guardrails baked into the firmware: pulses are clamped to **200 ms max**, with a forced **20 ms gap** between fires.

### 6.2 Optional — measurements while it's live (feeds your Week-3 CAD)

While the cell is firing, capture: plunger **rest extension** (mm), **force** at 30/50/80 ms (push against a tared kitchen scale), and **body temperature** after ~200 fires at 50 ms / 100 ms gap (touch test — flag if uncomfortably hot).

---

## 7. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| No `OK` in Serial Monitor | Wrong baud/port, or sketch not flashed | 115200 + Newline; reselect port; re-flash |
| `OK FIRE` but **no click** | No 12 V, or **COM (pin 10) not on +12 V**, or cold output joint | Confirm 12 V on; reflow COM→+12 V; check solenoid leads |
| **One** channel dead | That Q→IN jumper, or that OUT joint / solenoid | Continuity-test that single path (§4.2) |
| **All** dead, but outputs toggle on the meter | 12 V missing, or COM not tied | Check the 12 V feed and COM→+12 V |
| Weak / buzzing click | Pulse too short, low 12 V, or sagging rail | Raise pulse; verify 12 V; confirm reservoir cap present + correct polarity |
| Chip **hot** or any **smell** | Short (5 V↔12 V), reversed reservoir cap, or COM miswired | **Kill power.** Re-run §4 shorts + cap polarity |
| Random / glitchy fires | Missing 0.1 µF decoupling, sloppy ground, or a bridge | Add/secure both 0.1 µF; verify single star ground; wick any bridge |
| Plunger stuck extended at rest | Solenoid orientation / mechanical, not the driver | Energize behavior: the ball-tip extends on fire, retracts at rest — re-check mounting |

---

## 8. The 5 gotchas (tape above the bench)

1. **ULN COM (pin 10) → +12 V.** No flyback = a dead driver on the first solenoid.
2. **5 V and 12 V never touch.** Only the grounds tie, at one star point.
3. **Socket every IC.** Never solder the chip itself.
4. **0.1 µF across every chip's power pins** (595 16↔8, ULN 10↔9), legs short.
5. **Reservoir polarity** (+ to 12 V, stripe to GND) and **test cold → 5 V-only → 12 V last.**

---

## 9. Pin reference

### 74HC595 (DIP-16)

| Pin | Name | Connect to |
|--:|---|---|
| 1 | Q1 | ULN IN2 (2) |
| 2 | Q2 | ULN IN3 (3) |
| 3 | Q3 | ULN IN4 (4) |
| 4 | Q4 | ULN IN5 (5) |
| 5 | Q5 | ULN IN6 (6) |
| 6 | Q6 | ULN IN7 (7) |
| 7 | Q7 | ULN IN8 (8) |
| 8 | GND | GND rail |
| 9 | Q7′ | open (cascade out — unused on one cell) |
| 10 | MR̅ | +5 V rail |
| 11 | SH_CP | Mega D12 (green) |
| 12 | ST_CP | Mega D13 (white) |
| 13 | OE̅ | GND rail |
| 14 | DS | Mega D11 (blue) |
| 15 | Q0 | ULN IN1 (1) |
| 16 | VCC | +5 V rail (+ 0.1 µF to GND) |

### ULN2803A (DIP-18)

| Pin | Name | Connect to |
|--:|---|---|
| 1–8 | IN1–IN8 | 595 Q0–Q7 |
| 9 | GND | GND rail (+ PSU GND) |
| 10 | COM | +12 V rail (+ 0.1 µF to GND) |
| 11 | OUT8 | solenoid 8 low side |
| 12 | OUT7 | solenoid 7 low side |
| 13 | OUT6 | solenoid 6 low side |
| 14 | OUT5 | solenoid 5 low side |
| 15 | OUT4 | solenoid 4 (ch 3) low side |
| 16 | OUT3 | solenoid 3 (ch 2) low side |
| 17 | OUT2 | solenoid 2 (ch 1) low side |
| 18 | OUT1 | solenoid 1 (ch 0) low side |

*Each solenoid's other lead → +12 V rail.*

### Serial command cheat-sheet (`keyboard_v0`, 115200, Newline)

| Command | Does |
|---|---|
| `FIRE <ch> [ms]` | fire one channel 0–7 (`FIRE 0` = default pulse; `FIRE 0 30` = 30 ms) |
| `BURST [n [pulse [gap]]]` | fire channels 0…n-1 in sequence (default `BURST 4`) |
| `PULSE [ms]` | set / report the default pulse |
| `ALLOFF` | force every channel low (use if a fire hangs) |
| `MAP`, `TYPE`, `LEAD` | key-mapping + typing (not needed for the fire test) |

---

## 10. Done

Four crisp clicks from a soldered cell = **Stage 2 complete.** Film it. Commit the working-cell photo + any `PULSE` value you settled on to GitHub. Then repeat this exact cell for #2–#4 on Board A (rails just extend right), continuity-testing each column as you finish it.

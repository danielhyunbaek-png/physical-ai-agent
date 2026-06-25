# Physical AI Agent — Part 3: Shooting Script

**Format:** Vertical 9:16 · ~60 sec · Instagram Reel / X
**Style:** Documentary build-log — honest, process-forward
**Structure:** Cold open on the payoff (typing **FREED**), rewind through the build, tease next week
**Payoff word:** FREED — keys E, R (top row) + D, F (bottom row); fires all four solenoids, E twice
**Gear:** phone + tripod (overhead), clip-on lavalier mic, CapCut

---

## 1. Script + shots (beat by beat)

| # | Time | Voiceover | Caption | What to shoot / B-roll |
|---|------|-----------|---------|------------------------|
| **Hook** | 0–3s | "This machine just typed the word FREED — completely by itself." | FREED | Macro of solenoids hammering + screen capture of F‑R‑E‑E‑D landing in TextEdit. *(Retention trick: cut away before the word finishes; complete it at the end.)* |
| **Turn** | 3–9s | "This is part 3 of building my physical AI agent. Last week I got the electronics firing a solenoid on the breadboard. This week I printed the housing that holds them over the keys — and it fought me." | PART 3 · this week: the housing | Quick clip of last week's breadboard solenoid click → cut to the 3D printer starting a print. |
| **Beat 1** | 9–22s | "First, a little holder for one solenoid, just to nail the screw-hole spacing. The screws I bought off the spec were too loose — they'd thread on, then spin right back out — so I sized up to a bigger screw. Once that one fit solid, I printed the 2×2 prototype: four solenoids, two rows." | screws too loose → sized up | **CAD: test-fit cell (slow orbit).** Printer peeling the part. Macro: screw threading on, then spinning loose / falling out. Bigger screw biting + holding. |
| **Beat 2** | 22–38s | "But the first 2×2 missed something — the screw heads. They stuck out and jammed into the solenoid sitting behind them, and the wall between the rows was too thick to fit in the gap. That row couldn't even bolt down." | screw heads jammed | **CAD: first 2×2 (slow orbit) — punch in on the cap-screw head hitting the body behind it.** Physical: the failed 2×2, head fouling the neighbor; wall too fat for the gap. |
| **Beat 3** | 38–52s | "So I redesigned it: a counterbore at each hole — a flat-bottomed pocket the head sinks into — shorter, flat-topped screws so they sit flush, and a thinner wall to give the solenoids room. And that's how it typed FREED." | counterbore = flush | **CAD: redesigned 2×2 (slow orbit) — close-up on the counterbore pockets; v1-vs-v2 side-by-side.** Physical: flush heads (finger drags across), 4 solenoids seated, block lowering onto E/R/D/F → return to the firing + FREED on screen. |
| **Close** | 52–60s | "Next week, I scale this up — from four keys to all 84. Four down, eighty to go." | NEXT: 84 keys · 4 down, 80 to go | Slow push on the full Nuphy keyboard; optional 1-sec flash of all three CAD designs in sequence (the evolution). |

> Runtime note: VO is ~160 words — tight for 60s. If it feels rushed, trim Beat 1 (the screw line) or shorten the Turn.

---

## 2. CAD design-iteration montage ("every design")

Record each model in Fusion 360 and play them **in the order they happened** so the montage *is* the iteration story — the viewer watches the design evolve:

1. **Test-fit cell** (`TestFitCell.stl`) — single-solenoid holder → plays at **Beat 1**.
2. **First 2×2** (the failed design — 4 mm wall, M3×6 cap screws) → plays at **Beat 2**, punched in on the screw head colliding with the body behind it. *(If you didn't keep this CAD state, roll the Fusion timeline back to it, or just show the physical failed print.)*
3. **Redesigned 2×2** (`Prototype_2x2.stl` — 2.5 mm wall, counterbore, M3×3 flat-top) → plays at **Beat 3**, close-up on the counterbore pockets.

How to capture:

- Screen-record with the model **slowly orbiting** (drag the ViewCube, or set up an orbit animation). 3–5 sec per model is plenty.
- Shoot one **v1-vs-v2 side-by-side** (or a quick cross-dissolve) so the counterbore + thinner wall pop — that's the whole redesign in one shot.
- Hero shot: a tight **punch-in on a single counterbore pocket** with a screw dropping in flush.
- Optional: a 1-sec **"all three in a row"** flash at the Close to show the evolution.

---

## 3. Master B-roll checklist

**CAD (Fusion 360 screen-records)**

- [ ] Test-fit cell — slow orbit
- [ ] First 2×2 — slow orbit + punch-in on screw-head collision
- [ ] Redesigned 2×2 — slow orbit + counterbore close-up
- [ ] v1 vs v2 side-by-side
- [ ] (Optional) all-three evolution flash

**Printing**

- [ ] Printer starting a print (nozzle moving)
- [ ] Test-fit cell peeling off the bed
- [ ] 2×2 building up (time-lapse)

**Solenoid + assembly**

- [ ] Macro of the JF-0530B solenoid in hand (plunger, ball tip)
- [ ] Seating a solenoid into the holder / wall
- [ ] Loose screw threading on, then spinning out / falling
- [ ] Bigger screw biting + holding
- [ ] Flush counterbored heads (finger drag across)
- [ ] 4 solenoids mounted in the 2×2
- [ ] Block lowering onto the keyboard (E / R / D / F)

**Payoff**

- [ ] Wiring to the breadboard / Arduino
- [ ] Solenoids firing in sequence — **high frame rate for slo-mo**
- [ ] Screen capture: FREED appearing letter by letter in TextEdit
- [ ] Hand-vs-rig on the same four keys (side-by-side)
- [ ] Slow push on the full Nuphy keyboard (for the Close)

---

## 4. Captions / on-screen text (muted viewing)

FREED → PART 3 → screws too loose → 2×2 prototype → screw heads jammed → counterbore = flush → NEXT: 84 keys

---

## 5. Production notes

- **Vertical 9:16, 1080p.** Phone on the tripod overhead for bench/process shots; get **macro** on the solenoid and the screen.
- **Audio is the star:** capture clean **solenoid clack** separately, and record VO with the lavalier. The clack sells it on muted feeds.
- **Slo-mo** the firing (highest frame rate your phone allows). Lock manual exposure so lighting doesn't shift between clips.
- **Pace:** ~6 beats, brisk cuts, light music bed under VO. Cut on the clacks where you can.
- **Capture the real first successful run** — that's the honest beat — but shoot a few takes as backup.
- **Diction:** the script says "flat-topped screws" on purpose. "Flat-head" formally means a *countersunk, conical* head (pairs with a countersink, not a counterbore). Yours is a flat-bottomed cap-style head in a counterbore — so "flat-topped / low-profile screws" stays accurate if a maker is watching. "Counterbore" is the correct term for the pocket.

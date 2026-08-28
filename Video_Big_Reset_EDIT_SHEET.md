# BIG RESET — VO ↔ B-ROLL EDIT SHEET
**Source script:** Daniel's Jul 28 VO revision · **Companion:** `Video_Script_Big_Reset.md`
**Runtime estimate:** ~62s at a natural pace (~2.9 words/sec). Target was 55–65s — you're at the top end. Trim candidates flagged with ✂.
**Assets already rendered:** `media/new_plate_broll_vertical.mp4` (10.7s loop), `media/new_plate_exploded_still*.png`

Timecodes assume you start on the first word. Shift everything if you add a cold-open beat.

---

## 0:00 – 0:05 · LINE 1

> "This one cell drives 8 solenoids — so 8 keys on my robot keyboard."

| Phrase | Shot |
|---|---|
| "This one cell" | **HOOK — cell #1 in hand, slow rotate, good light.** Hold this one shot for the whole line. Don't cut. |
| "drives 8 solenoids" | Optional 0.5s insert: finger points at the two chips |
| "so 8 keys on my robot keyboard" | Whip to the populated plate, or stay on the cell |

**On-screen text:** `1 cell = 8 keys`

> ⚠️ **Your hook is now a technical statement.** The earlier draft opened with "took me 4 hours to solder, and honestly, it looks very pretty" — pride before the fall, which is what makes the next 50 seconds land. Consider adding it back as a 3s cold open before this line.

---

## 0:05 – 0:13 · LINE 2

> "If I want it to drive 84 solenoids, I need 11 of these chips, that's over 170 wires and 700 joints I need to solder"

| Phrase | Shot |
|---|---|
| "If I want it to drive 84 solenoids" | Wide/overhead of the fully populated plate — all 84 mounted |
| "I need 11 of these" | Cut back to cell #1, or lay 11 perfboards/chips out on the desk |
| "over 170 wires and 700 joints" | **Cell #1 soldering clip (footage on hand), speed-ramped hard** |

**On-screen graphic (the credibility beat):** `170+ wires · 700+ joints · 25+ hrs` — hits on "700 joints," stays up ~2s

> ⚠️ **Fix before you record: "11 of these chips" is wrong.** Each cell is *two* chips — a 74HC595 shift register and a ULN2803A driver. 11 cells = 22 chips. Say **"11 of these"** or **"11 of these cells."** A commenter will catch this.

---

## 0:13 – 0:23 · LINE 3

> "Instead of doing that, I decided to design a custom PCB instead. All those wires just become copper traces printed on the board, and every cell comes out identical."

| Phrase | Shot |
|---|---|
| "I decided to design a custom PCB" | **KiCad screen recording** — slow pan across the routed board. Record fresh; it's DRC-clean and final |
| "all those wires just become copper traces" | The money shot: KiCad 3D viewer rotating, or the Freerouting autoroute replay if you still have it |
| "every cell comes out identical" | Zoom on the 4 identical cells in a row, then **JLCPCB order confirmation** (blur address/payment) |

**On-screen graphic:** the wire/joint numbers strike through → `$40 · 2 weeks`

> ✂ **Trim option:** "Instead of doing that... instead" is doubled. Cut to *"So instead, I designed a custom PCB."* Saves ~1.5s.
>
> 📌 **Number check:** bare boards were ~$10–20 for 5 from JLCPCB. `$40` is fine if you're counting terminals + sockets, but the lower number is a stronger flex if you want it.

---

## 0:23 – 0:34 · LINE 4

> "Speaking of problems to fix, the current wiring on my plate is a complete mess. Trying to organize over 168 wires through these thin walls is going to be a pain in the ass."

| Phrase | Shot |
|---|---|
| "the current wiring on my plate is a complete mess" | **Wide/overhead of the plate with the tangle fully visible.** Shoot this BEFORE Phase 0 tip-snipping — the mess is the argument |
| *(one second of silence)* | **Hold. Deadpan.** This is the comedic beat — let the shot breathe |
| "over 168 wires through these thin walls" | Low-angle close-up down the wall slot, leads crossing everywhere. Slow push-in |
| "pain in the ass" | Cut to your face, or a hand giving up on a bundle |

**On-screen text:** `168 leads · 6 walls · 16.55mm slot`

---

## 0:34 – 0:43 · LINE 5

> "Another problem is repairability. Because the rows can only screw from front to back, swapping one solenoid in the middle means unscrewing every row behind it"

| Phrase | Shot |
|---|---|
| "Another problem is repairability" | Close-up: finger taps an interior-row solenoid |
| "the rows can only screw from front to back" | Macro on a counterbored screw head, then pan showing the head pointing into the next body |
| "swapping one solenoid in the middle" | Same finger taps the middle solenoid again |
| "means unscrewing every row behind it" | **Slow pan across all the rows behind it.** Optional: back one screw out with the driver (tease, don't tear down) |

**On-screen text:** `swap 1 → unscrew 3 rows`

> 📌 The teardown gate is still the groove coupon. One screw out is the honest amount of tease.

---

## 0:43 – 0:51 · LINE 6

> "That's why I designed a new plate which has interchangeable walls, and a top deck where my PCB will sit, so the wires run straight up."

**This is the render.** `media/new_plate_broll_vertical.mp4` — it's a seamless loop, so start anywhere.

| Phrase | Shot (timecode into the clip) |
|---|---|
| "That's why I designed a new plate" | Clip ~0:00 — assembled, slow orbit |
| "which has interchangeable walls" | Clip ~3:00–5:00 — the six wall modules fanning out into the staircase. **The orange one is the callout** |
| "and a top deck where my PCB will sit" | Clip ~1:00–2:00 — the deck lifting away with the 3 green boards on it |
| "so the wires run straight up" | Hold on the exploded state — the 84 vertical leads read clearly. Optional freeze on `new_plate_exploded_still_labeled.png` |

**On-screen text:** `removable walls · top deck · wires straight up`

> If you'd rather not use the render for the whole line, cut the last phrase to the real plate and gesture upward. But the render is the only asset that shows the deck, which doesn't exist yet.

---

## 0:51 – 1:02 · LINE 7 (CTA)

> "This is a pretty big reset. But once the boards arrive in 2 weeks, I'm tearing down the old plate, rebuilding it, and getting all 84 keys typing on their own. Stick around."

| Phrase | Shot |
|---|---|
| "This is a pretty big reset" | **Face cam.** First time your face is on screen — that's why it lands |
| "once the boards arrive in 2 weeks" | Quick insert: JLCPCB order/shipping screen |
| "tearing down the old plate, rebuilding it" | One screw coming out with the driver |
| "getting all 84 keys typing on their own" | Back to face cam, or the wide plate shot |
| "Stick around" | Face cam, hold, cut on the word |

**End card:** `Rebuild starts when the boards land — ~Aug 9`

---

## Shot list, deduplicated (what to actually capture)

- [ ] Cell #1 in hand, slow rotate, good light — **the hook, shoot it well**
- [x] Cell #1 soldering clip — already have it
- [ ] Plate wide/overhead WITH the wire mess — **shoot before Phase 0 tip-snipping**
- [ ] Low-angle down the wall slot, leads crossing
- [ ] KiCad screen recording: 2D routed board pan + 3D viewer rotate
- [ ] JLCPCB order confirmation screenshot (blur address/payment)
- [ ] Interior-row finger tap + pan across the rows behind
- [ ] Macro of a counterbore screw head
- [ ] One screw backing out with the driver
- [ ] Face cam for the CTA
- [x] New-plate visual — `media/new_plate_broll_vertical.mp4`

## Facts checklist (all verified against the project record)

- 84 solenoids mounted, 168 tab screws, 168 leads
- 1 cell = 8 solenoids = 8 keys; **11 cells** (22 chips) for the full matrix
- ~170 wires / 700+ joints to hand-build all 11 cells; **4 hours measured** for cell #1
- PCB: 120 × 66mm, 4 cells per board, **3 boards**, 5 ordered Jul 26, ~2-week lead
- New plate: groove-sandwich removable walls, deck underside at Z58, wires straight up
- Say "84 solenoids," not 88 — 88 is the channel count (4 spares)

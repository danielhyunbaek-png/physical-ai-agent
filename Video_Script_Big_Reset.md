# VIDEO: The Big Reset
**Title options:** "I'm tearing apart a robot that works" · "84 solenoids, and I'm starting over" · "The most productive step backwards I've ever taken"
**Platform:** All 4 (TikTok, Reels, Shorts, X)
**Length:** 55–65 seconds
**When to post:** After the KiCad design passes its gates and the JLCPCB order is placed (you want the order-confirmation shot). Ideally within days of ordering so "boards arrive in 2 weeks" sets up the next video.
**Content pillar:** The Struggle / Pivot (historically your most relatable, best-performing bucket)
**Status (Jul 17):** Not postable yet — KiCad cell 1 isn't wired and no order is placed. Script + shot list are ready; the only missing footage is the KiCad-layout screen recording and the JLCPCB order-confirmation shot. Shoot/finish the moment you order.

---

## Script

**[HOOK — 0:00–0:04]**
*Beauty shot: finished perfboard cell #1 in hand, slow rotate, good light.*

> "This is driver cell number one. Took me 4 hours to solder, and honestly, it looks very pretty."

**[WHAT IT IS — 0:04–0:10]**
*Hold on the cell, quick point at the chips.*

> "This one cell drives 8 solenoids — so 8 keys on my robot keyboard."

**[THE PROBLEM — 0:10–0:18]**
*Cut to the cell #1 soldering clip (footage on hand), speed-ramped. On-screen graphic: "170+ wires · 700+ joints · 25+ hrs."*

> "Then I realized, in order to drive 84 solenoids, I need to solder over 170 wires and 700 joints."

**[PIVOT 1: THE PCB — 0:18–0:28]**
*Screen recording: KiCad schematic/board with traces, then the JLCPCB order confirmation. Graphic: the wire/joint numbers crossed out → "$40 · 2 weeks."*

> "That's why I decided to design a custom PCB instead. All those wires just become copper traces printed on the board, and every cell comes out identical. 40 bucks, 2 weeks."

**[PROBLEM 2: THE WIRING MESS — 0:28–0:36]**
*Cut to the plate. Gesture at the tangle. Let the mess get a deadpan beat — it's funny.*

> "Speaking of problems to fix, the current wiring on my plate is a complete mess. Trying to organize over 168 wires through these thin walls is going to be a pain in the ass."

**[PROBLEM 3: REPAIRABILITY — 0:36–0:44]**
*Finger taps an interior-row solenoid, then pan across the rows behind it.*

> "Another problem is repairability. Because the rows can only screw on front to back, swapping one solenoid in the middle means unscrewing every row behind it — so repairability is a mess as well."

**[THE NEW PLATE — 0:44–0:55]**
*Cut to CAD / rough sketch / the coupon. Point out the removable walls, then the deck up top.*

> "That's why I designed a new plate which has interchangeable walls, and a top deck where my PCB will sit, so the wires run straight up."

**[CTA — 0:55–1:00]**
*Face cam.*

> "This is a pretty big reset. But once the boards arrive in 2 weeks, I'm tearing down the old plate, rebuilding it, and getting all 84 keys typing on their own. Stick around."

---

## Shot List

- [ ] **HOOK SHOT:** finished perfboard cell #1 in hand, slow rotate, good light — this opens the video now
- [ ] **HAVE:** cell #1 soldering clip (the 4-hour session) — speed-ramp for the PROBLEM section
- [ ] Wide/overhead of the fully populated plate WITH the wire mess visible (don't tidy it first — the mess is the argument)
- [ ] Screen recording: KiCad board layout (even 5 seconds of the traces looks great — the schematic view with the 595→ULN chain also reads well)
- [ ] Screenshot: JLCPCB order confirmation (blur address/payment)
- [ ] Close-up: finger tapping an interior-row solenoid, then panning across the rows "behind" it
- [ ] New-plate visual for PIVOT 3: CAD screengrab, a rough sketch, or the printed coupon — anything that shows removable walls + the top deck
- [ ] Optional: one screw coming out with the driver (tease the teardown — even if the real teardown waits for the coupon gate, one screw is honest)
- [ ] Face cam for the closer only (rest of the video is b-roll + voiceover)

## Edit Notes

- **The hook is now pride-before-the-fall** — open on the pretty cell, then the video spends 50 seconds explaining why it (and the plate) are obsolete. That reversal is the story.
- On-screen math graphic at 0:14: `170+ wires · 700+ joints · 25+ hrs` → hard cut to `$40 · 2 weeks`. Specific numbers are your credibility engine.
- Say "84 solenoids," not 88 — 88 is the channel count (4 spares); pedants will notice.
- The wire-mess gesture at ~0:30 should be the comedic beat. One second of silence, deadpan.
- Do NOT actually tear the plate down for this video — the coupon test gates the real teardown. One screw out is plenty of tease.
- End card: "Rebuild starts when the boards land" + date estimate.
- This sets up a 3-video arc: (1) this reset video → (2) boards arrive + first WALK across all 88 channels → (3) the rebuild timelapse + full-matrix fire. Tell the algorithm a story.

## Caption

```
ripping apart a robot that already works lol

4 hours to hand-solder ONE driver cell. i need 11. no thanks.
so: custom PCB ($40) + redoing the whole plate while the boards ship.
168 screws coming out. on purpose.
.
.
.
#buildinpublic #robotics #engineering #diy #pcb #arduino #maker
```

## Facts checklist (say these, they're all true)

- 84 solenoids mounted, 168 screws
- 1 driver cell = 8 solenoids (8 keys); 11 cells needed for the full board
- ~170 wires and 700+ solder joints to hand-build all 11 cells (breakdown: 8 signal jumpers × 11 = 88 wires + 84 solenoid leads ≈ 170; joints = ~344 wire ends + 374 chip pins [16 per 595 + 18 per ULN, × 11] = 700+). Power/cascade jumpers push the wire count higher.
- 4 hours to solder cell #1
- Custom PCB: ~$40, ~2-week lead, 5 boards ordered, 2 used
- New plate: removable walls (groove-sandwich) for easy solenoid swaps, PCB sits on a top deck, wires route straight up instead of out the side
- Interior-row swap on the current plate = unscrew the rows behind it

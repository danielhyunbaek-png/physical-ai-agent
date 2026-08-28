# Caliper Gate Card — brief 08 rebuild

**Datum for everything below: Z0 = plate BOTTOM. Plate top = Z4. Wall top = Z32. Tab holes Z11 / Z26.**
(All three verified from `Air75_84Key_Plate_Left/Right.stl`, Jul 27.)

Take these, report the numbers, and the deck height + wire slots stop being placeholders.

---

## M1 — Spare solenoid, on the bench (drives deck height)

Use a **spare** JF-0530B, not one on the plate. Orient it as mounted: **ball-tip end = BOTTOM**.

| # | Measure | Nominal | Your number |
|---|---|---|---|
| M1a | Overall body height, bottom face → top face (NOT including plunger) | 30 | |
| M1b | Body bottom face → **center of the LOWER mounting hole** | ~7 | |
| M1c | Mounting hole spacing, center-to-center (sanity check) | 15.00 | |
| M1d | Body width across the mounting face | 16 | |

Then `body_top_z = 11 − M1b + M1a`. If M1b = 7 and M1a = 30 → body top = Z34, i.e. **2mm proud of the wall top.**
Measure M1b twice from opposite reference edges — it's the one that's easy to get wrong.

## M2 — Lead exits, same spare (drives deck wire slots)

With the solenoid held mounting-face-toward-you, ball-tip down:

| # | Measure | Your number |
|---|---|---|
| M2a | Which face do the two wires leave? (top face / back face / side — name it relative to the mounting face) | |
| M2b | Body bottom → the exit point, in mm | |
| M2c | Offset of the exit point across the body width, from the mounting-face edge | |
| M2d | Do both leads exit at the same point, or two separate points? Gap between them if separate | |

## M3 — On the POPULATED plate (1 minute, no disassembly)

| # | Check | Your answer |
|---|---|---|
| M3a | For a middle row (y = 0 or 19.05), which way do the leads currently point — toward +Y (back) or −Y (front)? | |
| M3b | Is the solenoid body visibly **above** the wall top, flush, or below? (eyeball is fine — M1 gives the number) | |
| M3c | Clear gap between the back face of one wall and the bodies on the wall behind it | |

## M4 — FDM reality check (sets `groove_width` — the scheme's #1 risk)

On the **printed** plate, with calipers. Three spots each, report all three.

| # | Measure | Nominal | Your numbers (×3) |
|---|---|---|---|
| M4a | Wall thickness | 2.50 | |
| M4b | Plate thickness | 4.00 | |
| M4c | Overall plate depth, front edge → back edge (one half) | 164.00 | |
| M4d | Overall plate width of the LEFT half | 158.65 | |

**Why this matters:** `groove_width = 2.75` assumes walls print at exactly 2.50. If your walls actually come out at 2.62, the groove leaves 0.13mm and the wall will not seat. M4a is what sets the real groove width, and it's the difference between one coupon print and four.

---

Report back as plain numbers (e.g. "M1a 30.15, M1b 6.85, ..."). Nothing else in the rebuild is blocked on anything but these.

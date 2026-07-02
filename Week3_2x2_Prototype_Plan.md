# Week 3 — 2×2 Tilted-Plate Prototype Plan

*Supersedes the earlier single-row plan. This version tests four keys in a 2×2 block so it also exercises the keyboard tilt and the row stagger — the two hardest parts of the full 84-key build — on a small, cheap print.*

**Goal:** Design a tilted parametric mounting plate in Fusion 360, print it, mount 4 solenoids over a 2×2 key block (S, D front / W, E back), and have the rig type those four letters using the Week 2 breadboard rig. Passing this validates solenoid-to-switch behavior **and** the tilt + stagger mounting approach before the full plate (Week 4) and the driver-board solder (Week 5).

**Time:** ~2 hr CAD, ~2–4 hr print (unattended), ~1.5 hr assembly + test.

---

## Confirmed inputs (all measured / from spec — no more measuring needed)

**Solenoid — JF-0530B (verified on your unit):**

| Property | Value |
|---|---|
| Body | 30 × 16 × 15 mm |
| Plunger | Ø6 × 58 mm, 10 mm stroke |
| Mounting holes | Ø2.5 mm, on **one side face only**, **15 mm** apart, axis parallel to plunger |
| Lower-hole → ball tip, at rest | **15 mm** |
| Actuation | energize → **ball end extends** (push); spring retracts it at rest |

**Keyboard — Nuphy Air75 V3 (spec + measured):**

| Property | Value |
|---|---|
| Tilt (feet retracted) | **4°** (Type Angle base) |
| Key pitch, both axes | **19.05 mm** |
| Row stagger (back row left of front) | **4.76 mm** (0.25u; your ~5 mm read) |
| Front-row keycap top above desk | ~18 mm placeholder (tuned with shims) |

---

## Design overview

A single **flat plate tilted 4°** so it sits parallel to the keycap plane. Because the whole plate leans with the keyboard, every key has the same gap — the tilt is solved once, not per row. Four **plunger clearance holes** in a 2×2 grid pass through it; the back pair is shifted **4.76 mm left** for the stagger. The plungers strike the keys perpendicular (straight in).

Because the solenoid's mounting holes are on its **side face**, the solenoids can't bolt flat to the plate. Instead, two short **mounting walls** stand up perpendicular to the plate — one behind the front-row holes, one behind the back-row holes — and each solenoid bolts to its wall by the side face, body standing up, plunger hanging down through its hole.

The plate is held at the 4° tilt and the right height by **two side legs** that rest on the desk straddling the keyboard. Leg height is shimmed to set the final 1–2 mm gap.

**Target keys:** front row **S, D**; back row **W, E** (the 2×2 block directly above S/D).

```
        W       E          <- back row (shifted 4.76mm LEFT, +tilt higher)
            S       D       <- front row
```

---

## Fusion 360 — parameters

`Modify` → `Change Parameters` → add these User Parameters:

```
pitch_x              mm     19.05
pitch_y              mm     19.05
stagger              mm     4.76      // back row shifts -X (left)
tilt_angle           deg    4
plate_thickness      mm     4
plunger_hole_dia     mm     7         // Ø6 plunger + 1mm clearance
mount_hole_dia       mm     2.7       // 2.5mm tab + clearance for M2.5 screw
mount_hole_spacing   mm     15        // measured, vertical spacing on the wall
wall_offset          mm     8         // hole center -> mounting wall face (≈ half body depth)
wall_thickness       mm     4
lower_hole_z         mm     3         // lower screw hole height above plate top
wall_height          mm     24        // hosts 2 holes 15mm apart + margin
leg_height_front     mm     28        // placeholder, shim to set gap
```

> `lower_hole_z = 3` with your 15 mm rest figure and a 4 mm plate means the ball hangs ~8 mm below the plate at rest (15 − 3 − 4). That's a healthy poke-through; the keycap stops the plunger long before it bottoms out. If you'd rather the ball hang less, raise `lower_hole_z`.

---

## Fusion 360 — modeling steps

Model everything **flat** (in the plate's own plane); the 4° tilt is created later by the legs, so the plunger holes stay perpendicular to the plate and therefore perpendicular to the keycaps automatically.

### A. Plate
1. `Create Sketch` on the XY plane. Draw a rectangle roughly 60 × 60 mm centered on the origin (gives margin around the 2×2). `Finish Sketch`.
2. `Extrude` up by `plate_thickness`.

### B. Plunger holes (the 2×2 grid with stagger)
1. New sketch on the plate's top face. Place four circles of diameter `plunger_hole_dia`:
   - **S** at (0, 0)
   - **D** at (`pitch_x`, 0)
   - **W** at (`-stagger`, `pitch_y`)
   - **E** at (`pitch_x - stagger`, `pitch_y`)
2. `Finish Sketch` → `Extrude` → **Cut**, "All", through the plate.

### C. Mounting walls (one per row)
1. New sketch on the plate top. Behind the **front row** (offset +Y by `wall_offset` from the S–D line), draw a rectangle `wall_thickness` deep, spanning a bit past S and D in X. Do the same behind the **back row** (offset `wall_offset` from the W–E line).
2. `Extrude` both up by `wall_height`.
3. On each wall's face, sketch the screw holes (Ø `mount_hole_dia`): for each solenoid, two holes stacked vertically at heights `lower_hole_z` and `lower_hole_z + mount_hole_spacing` above the plate top, centered in X on that solenoid's plunger hole. Front wall gets 4 holes (S, D), back wall gets 4 holes (W, E). `Extrude` → **Cut** through the wall.

### D. Legs (set the 4° tilt)
1. Add two legs under the left and right edges of the plate. Make the **back edge taller than the front** so the plate tilts up toward the back at `tilt_angle`. The height difference = `tan(tilt_angle) × (front-to-back leg span)`; for a ~50 mm span that's ~3.5 mm taller at the back.
2. Keep legs as a **separate body/component** so you can reprint or shim them alone to dial in the gap.

### E. Test-fit cell FIRST, then export
- Before printing the whole thing, **isolate one cell** (one plunger hole + its piece of wall with 2 screw holes) and print just that. Mount one real solenoid to it and confirm: the side face sits flush, the M2.5 screws bite, and the plunger drops cleanly through the Ø7 hole, centered. This catches any `wall_offset` / hole-position error for the cost of a 15-minute print. Adjust parameters, then export the full 2×2.
- Export: right-click body → `Save As Mesh` → **STL**, High refinement → `cad/` folder.

---

## Print settings

PLA, **0.2 mm layer, 30 % infill, 4 walls.**
- Plate + mounting walls: print with the plate flat on the bed, walls pointing up. The walls are self-supporting at this size; no supports needed.
- Legs: separate small prints, flat on the bed.

---

## Assembly

1. **Fix the keyboard down** with VHB tape, **feet retracted**. It cannot shift during 50 trials.
2. **Mount the 4 solenoids** to the walls with **M2.5 × 8 mm screws** through the side-face holes — front wall: S, D; back wall: W, E. Bodies stand up, ball tips hang down through the plate holes. Snug, not over-torqued (PLA strips).
3. **Silicone tip** (~5 mm tubing) on each ball tip.
4. **Set the assembly over the block** so the four plungers sit over S, D, W, E. Rest the legs on the desk.
5. **Shim the legs** until each ball tip rests **1–2 mm above its keycap**. Because the plate is tilted with the board, all four gaps should come out even — if the back two differ from the front two, your tilt is off, which is exactly the kind of thing this prototype is meant to surface.

---

## Wire to the Week 2 breadboard rig

No new soldering. Connect the four solenoids to ULN2803A channels 0–3 (one leg to each ULN output, the other to +12V), keyboard into the MacBook, TextEdit open and focused, 12 V from the PSU with common ground to the Arduino.

Suggested channel map: **0 = S, 1 = D, 2 = W, 3 = E.**

---

## Acceptance test

In the serial console, fire each at **30 ms** (calibrated for Blush Nano — not 50 ms):

```
FIRE 0 30   -> s
FIRE 1 30   -> d
FIRE 2 30   -> w
FIRE 3 30   -> e
```

You should see `s d w e` appear. **Pass = all four register with zero misses across 50 trials.** This proves both rows fire reliably despite sitting at different tilt heights and the staggered offset.

### Tuning
- Missed / mushy press: drop to 20 ms, or shim that end down 0.5 mm.
- Back two weaker than front two: tilt is slightly off — recheck leg height difference.
- Sticking / double-type: raise slightly or trim the silicone tip.
- Plunger won't return: confirm the spring rests it clear of the key (push-on-energize orientation).

> Don't move to the full 84-key plate (Week 4) until the 2×2 passes 50/50.

---

## Document it

- Film **s, d, w, e** appearing as the rig types them — and get a top-down shot showing the tilted plate hugging the angled keyboard, since the tilt+stagger handling is the interesting engineering story here.
- Side-by-side: your hand vs. the rig on the same four keys.
- Save clips for Sunday's edit ("first robot keystrokes").

---

## Checklist

- [ ] Parameters entered in Fusion
- [ ] Plate + 4 staggered plunger holes modeled
- [ ] Two mounting walls with 8 screw holes modeled
- [ ] Legs modeled with 4° tilt (separate body)
- [ ] **Single test-fit cell printed; one solenoid mounts flush, plunger centered**
- [ ] Full 2×2 + legs printed (0.2 / 30% / 4 walls)
- [ ] Keyboard VHB'd, feet retracted; 4 solenoids mounted (M2.5×8), silicone tips
- [ ] Legs shimmed to even 1–2 mm gap on all four
- [ ] Solenoids wired to ULN channels 0–3 (S, D, W, E)
- [ ] FIRE 0..3 @ 30 ms → "sdwe", 50/50 clean
- [ ] Filmed the first keystrokes

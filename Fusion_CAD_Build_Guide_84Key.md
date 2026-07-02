# Fusion 360 Build Guide — Full 84-Key Split Plate

A complete, beginner-paced walkthrough to model the full Air75 V3 plate, split into two printable halves, in Fusion 360. Written to be done in **six phases** — each is one sitting. Don't rush ahead; finish a phase, save, then start the next.

**Files you need open/handy** (all in your project folder):
- `Plate_Holes_Air75.dxf` — the 84 plunger holes + plate outline, pre-placed with S at (0,0). You import this; you do **not** hand-place holes.
- `Seam_Air75.dxf` — the stepped split line (used in Phase 3).
- `Full_84Key_Split_Plate_Design_Brief.md` — the numbers/reference.
- `Layout_Map_84Key_Split.svg` — the picture, for orientation.

**Coordinate convention (memorize this):** origin = center of the **S key** hole. **X = right, Y = toward the keyboard's back, Z = up.** Plate **bottom = Z0, top = Z4**. Everything is in **millimeters**.

**Phase map:**
0. Setup + the origin idea (read this — it's the whole trick)
1. Plate + 84 holes (one import, one extrude)
2. The six mounting walls + screw holes
3. Split into Left/Right halves (the stepped seam)
4. The removable join (tabs, bosses, insert holes)
5. Legs + tilt
6. Export STLs + print

> UI note: menus are described for current Fusion 360. If a command sits in a slightly different spot in your version, the name is still the search term — press **S** in Fusion to search any command by name.

---

## PHASE 0 — Setup, and the one idea that makes all of this easy

### 0.1 New file + millimeters
1. **File → New Design.** It opens an empty workspace called *Untitled*.
2. **Save now:** Ctrl/Cmd+S → name it `Air75_84Key_Plate`. Save often after this.
3. **Set units to mm:** in the left browser, expand **Document Settings** → double-click **Units** → choose **Millimeter**. (If it already says mm, good.)

### 0.2 THE ORIGIN — what it is, and why we hang every hole off the S key

This is the question you asked, and it's the backbone of the whole model, so here's the full picture.

**What the origin is.** Every Fusion file has one fixed reference built in, called the **Origin**. It's a single point at coordinates **(0, 0, 0)**, plus three planes (XY, XZ, YZ) and three axes (X, Y, Z) that pass through it. Find it now: in the browser, expand the **Origin** folder and click the **lightbulb** to show it. You'll see a little point and three colored axes — **red = X (points right), green = Y (points away from you), blue = Z (points up)**. This origin **never moves**. It is the one thing the entire model is measured from.

**Why we put the S-key hole exactly on it.** Our whole coordinate table was built with the **S key at (0, 0)**. Every other hole is listed as *how far it is from S* — e.g. D is `(19.05, 0)`, W is `(−4.76, 19.05)`. So if the real S hole sits exactly on Fusion's origin, then **every number in the table is already correct with no conversion** — the model and the paperwork speak the same language.

**Why one fixed datum beats "chaining."** There are two ways to lay out 84 holes:

- *Chained (relative):* "D is 19.05 right of S; E is 19.05 right of D; F is 19.05 right of E…" Each hole is measured from the previous one. Three problems: (1) **errors pile up** — a 0.1 mm slip early on pushes everything after it (this is called tolerance stack-up); (2) it's **fragile** — move or delete one hole and the whole chain downstream shifts; (3) it **doesn't match our table**, so you'd be doing mental math 84 times.
- *Datum (absolute) — what we do:* **every** hole is measured from the **one** origin (the S datum). Nothing depends on its neighbor, so nothing piles up and nothing breaks if you edit a hole. The numbers are exactly the table. This is how the surveyor does it — every elevation in a city is measured from **one** benchmark, not fence-post-to-fence-post.

**Everything else in this build also references that same origin** — the seam X-positions, the wall offsets, the leg spacing, the tilt. That shared datum is *why* the parts line up when you split and rejoin.

**How S actually lands on the origin (the good news):** you don't have to find or click the S hole. The `Plate_Holes_Air75.dxf` file is already drawn with **S at (0, 0)**. When you import it (Phase 1) onto Fusion's XY plane with no offset, the DXF's (0,0) drops straight onto Fusion's origin — so the S hole's center sits exactly on (0,0,0) automatically, and all 83 other holes fall into their correct spots around it. (If you were ever sketching by hand instead, you'd draw the S circle and add a **Coincident** constraint between its center and the origin point — same end result, one hole at a time.) There's a tiny **"S" cross marker** on the DXF's ORIGIN layer so you can *see* that S landed on the origin; you'll delete that marker before extruding.

### 0.3 Create the User Parameters (set the recipe once)

Parameters are named numbers you can reuse and change globally. Set these now: **Modify → Change Parameters** → under *User Parameters* click **+** for each row below.

| Name | Unit | Value | What it's for |
|---|---|---|---|
| `plate_thickness` | mm | 4 | slab thickness (Z0→Z4) |
| `wall_thickness` | mm | 2.5 | mounting-wall thickness |
| `wall_offset` | mm | 8 | hole center → wall front face (toward +Y) |
| `wall_height` | mm | 28 | wall height above plate top (top ends at Z32) |
| `mount_hole_dia` | mm | 3.3 | M3 clearance hole in walls |
| `mount_hole_spacing` | mm | 15 | vertical gap between the two screw holes |
| `lower_hole_z` | mm | 7 | lower screw hole height above plate top → Z11 |
| `cbore_dia` | mm | 8 | flat counterbore Ø for the M3 flat head |
| `cbore_depth` | mm | 1.5 | counterbore depth (leaves a 1.0 mm wall web) |
| `tilt_angle` | deg | 4 | keyboard "type angle" (spec, feet retracted) — used for legs |
| `insert_hole_dia` | mm | 5 | pilot Ø for M3 heat-set inserts (join) |

You won't wire all of these to geometry, but having them written down keeps every later step consistent with the brief. Save the file.

> ✅ **End of Phase 0:** mm units set, you can see the origin axes, parameters entered, file saved. Next phase is the satisfying one — the whole key field appears at once.

---

## PHASE 1 — The plate + all 84 holes (one import, one extrude)

### 1.1 Import the holes (this is where S lands on the origin)
1. **Insert → Insert DXF.**
2. **File:** browse to `Plate_Holes_Air75.dxf`.
3. **Plane:** click the **XY plane** (red-green plane, the flat ground). 
4. Leave the position at default — **do not** add an X or Y offset. (That default is what drops the DXF's (0,0) onto Fusion's origin, putting S exactly on (0,0,0).)
5. If asked about units, choose **mm**. Click **OK**.

You'll now see the full keyboard: the outer plate rectangle, 84 circles, and a little **"S" cross** at the origin. 

**Verify the origin worked (10-second check):** turn on the Origin axes (Phase 0.2) and confirm the **S cross sits exactly on the point where the red and green axes meet**. Hover the S-row, 3rd hole — its center should read **0.00, 0.00**. If it's off, you added an offset on import — undo and re-insert with zero offset.

### 1.2 Clean up the marker
The "S" cross and text are just a visual aid and would clutter the extrude. In the browser open the new sketch, or just on screen: **select the two short cross lines and the "S" text at the origin and delete them.** (Leave every circle and the outer rectangle alone.)

### 1.3 Extrude the plate **with** the holes in one shot
1. **Create → Extrude** (shortcut **E**).
2. **Select the profile:** hover **inside the plate but not on any circle** — Fusion highlights the whole rectangle-minus-84-circles region (it looks like Swiss cheese). Click it once. *(Do not click inside the little circles — those are the holes; you want the web around them.)*
3. **Direction:** up (+Z). **Distance:** type `plate_thickness` (it resolves to 4).
4. **Operation:** New Body. **OK.**

You now have a 4 mm slab with all 84 holes already cut, bottom at Z0, top at Z4. Rename the body: in the browser, double-click *Body1* → `Plate_full`.

> If the whole rectangle extruded as a solid with no holes, you accidentally selected every region. Undo, restart Extrude, and click only the outer web (or shift-click to deselect the 84 disc regions).

> Optional nicety: add a tiny lead-in chamfer on the **top** mouth of the holes so plungers drop in easily — **Modify → Chamfer**, pick the top edges, 1 mm. Skip if you want to keep it simple; the Ø10 holes already have 2 mm of slop.

> ✅ **End of Phase 1:** a flat plate with 84 perfectly placed holes. Save. This alone is most of the precision work, and the origin did the heavy lifting.

---

## PHASE 2 — The six mounting walls + screw holes

Each row gets one wall the solenoids bolt to — identical to your 2×2, just repeated six times. A wall is a thin upright slab standing **8 mm behind** its row's holes, from the plate top (Z4) up to Z32, **2.5 mm** thick.

### 2.1 Draw all six wall footprints in one sketch
1. **Create Sketch** → click the **top face** of `Plate_full` (Z4).
2. Draw **six rectangles** (Create → Rectangle → 2-Point), one per row, using this table. Each rectangle is the wall's footprint: its **front face** (toward the keys) is at `Y_front`, and it's `2.5` deep toward the back, spanning X from `X_left` to `X_right`.

| Wall (row) | X_left | X_right | Y_front | Y_back (= front + 2.5) |
|---|---|---|---|---|
| Function | −61.39 | 242.36 | 65.15 | 67.65 |
| Number | −61.39 | 242.36 | 46.10 | 48.60 |
| QWERTY | −56.62 | 242.36 | 27.05 | 29.55 |
| Home | −54.24 | 242.36 | 8.00 | 10.50 |
| ZXCV | −49.48 | 242.36 | −11.05 | −8.55 |
| Bottom | −59.01 | 242.36 | −30.10 | −27.60 |

*(Y_front = each row's hole-Y + `wall_offset` 8. The numbers are pre-computed for you.)* Finish Sketch.

### 2.2 Extrude the walls up
1. **Create → Extrude.** Select all six rectangle regions (click each).
2. Direction up (+Z), **Distance = `wall_height`** (28) → tops land at Z32.
3. **Operation: Join** (so the walls fuse to the plate as one body). **OK.**

### 2.3 Screw holes — one wall in full, then repeat
The screws drive from the **back** of each wall (head flush in a counterbore) and thread into the solenoid's tab on the front. Each solenoid needs **two** holes stacked **15 mm** apart, at heights **Z11** and **Z26**, centered on **that key's X** (the screw X equals the plunger-hole X — same datum).

Do the **Home-row wall** first as your template:
1. **Create Sketch** on that wall's **back face** (the +Y face at Y 10.50).
2. The sketch's horizontal axis is global X; vertical is Z. Draw two **construction lines** (horizontal): one **7 mm** above the wall's bottom edge (Z11) and one **22 mm** above it (Z26).
3. Place a **sketch point** on the Z11 line at each Home-row key's X, and one on the Z26 line at the same X. Home-row key X's: **−45.24, −19.05, 0, 19.05, 38.10, 57.15, 76.20, 95.25, 114.30, 133.35, 152.40, 171.45, 202.41, 233.36.** *(Tip: the middle keys are an even 19.05 apart — place the first pair, then **Create → Pattern → Rectangular Pattern** along X at 19.05 spacing to fill the uniform run, and add the wide-key/nav ones individually.)* Finish Sketch.
4. **Create → Hole.** Select all those points. Set: **Counterbore**, counterbore Ø = `cbore_dia` (8), counterbore depth = `cbore_depth` (1.5), hole Ø = `mount_hole_dia` (3.3), extent **All** (through the 2.5 mm wall). **OK.** This makes flush-head M3 holes in one move. *(A 1.5 mm-deep counterbore leaves a 1.0 mm wall web — fine, the flat head bears on the Ø8 pocket bottom. Two checks: don't go deeper than 1.5 mm (keep ≥1 mm web), and note the M3×3 tip now sticks ~1 mm past the solenoid tab instead of 0.5 mm — confirm it clears the body behind, or use an M3×2.5.)*
5. **Repeat 1–4 for the other five walls,** using each row's key-X list from the brief's §5 table (the screw X's *are* the plunger-hole X's). The backmost wall (Function) has nothing behind it, so its counterbore is optional.

> Why back-face + counterbore: it's the fix from your 2×2 — the flush head clears the body of the row behind, which is what lets you keep the screw-in walls on the interior rows. **Always populate front row first, then work backward** at assembly.

> Don't want to hand-place ~190 screw holes? Say the word and I'll generate a per-wall DXF (wall outline + screw holes) you can import onto each wall face, the same way you did the plunger holes.

> ✅ **End of Phase 2:** one solid body — plate + 6 walls + all screw holes. Save.

---

## PHASE 3 — Split into Left and Right halves (the stepped seam)

You'll cut the whole body (plate + walls) with the staircase seam. Same origin trick: the seam DXF is drawn with S at (0,0), so it lands in exactly the right place.

### 3.1 Bring in the seam line
1. **Insert → Insert DXF** → `Seam_Air75.dxf` → plane **XY** → no offset → OK.
2. You'll see the red staircase line crossing the key field, plus the S marker. **Delete the S cross/text** (leave the staircase).

### 3.2 Turn the seam line into a cutting surface
1. **Create → Extrude.** Select the **staircase line** (click each segment, or window-select just the seam — it's an open line, so Fusion will make a **surface**, not a solid).
2. **Direction: Two Sides.** Side 1 (up) = **35**, Side 2 (down) = **5**. That makes a wall of surface spanning Z −5 to Z +35 — taller than your real part (which tops out at Z32), so it cuts cleanly through the plate **and** all the mounting walls.
3. **Operation: New Body** (it'll be a surface body). **OK.** Hide the seam sketch.

### 3.3 Split
1. **Modify → Split Body.**
2. **Body to Split:** click `Plate_full`.
3. **Splitting Tool(s):** click the seam **surface** you just made.
4. **OK.** You now have two solid bodies.
5. In the browser you'll see two bodies — click each to see which side lights up. Rename them **`Plate_Left`** and **`Plate_Right`**.
6. Hide or delete the seam surface (right-click → **Remove**) — its job is done.

> If the split only cut the plate but left a wall joined, your seam surface wasn't tall enough — redo the extrude taller (Side 1 = 40). The surface must fully pass through Z32.

> ✅ **End of Phase 3:** two separate bodies that interlock along the steps. Save. Each half is now under ~165 mm wide — comfortably inside the P2S bed.

---

## PHASE 4 — The removable join (tabs + heat-set inserts)

Four little **tabs** bridge the seam on the **top** of the plate (clear of the keys), in the open troughs between walls. Each tab is fused to one half and screws into the other with an M3 heat-set insert. The interlocking steps already stop the halves sliding — the tabs just clamp them together and flat.

**The four bridge points** (each sits in a hole-free trough between two walls):

| Tab | Y (along depth) | seam X here |
|---|---|---|
| T1 | +67 (behind Function wall) | 90.48 |
| T2 | +33 (Number↔QWERTY trough) | 90.48 |
| T3 | −1 (Home↔ZXCV trough) | 85.72 |
| T4 | −45 (front of Bottom wall) | 90.48 |

### 4.1 Model one tab (then repeat ×4)
Work on **T2** first (Y = +33, seam X = 90.48):
1. **Create Sketch** on the plate **top face** (Z4), near T2.
2. Draw a rectangle for the tab: about **24 mm in X** (centered on the seam X 90.48, so X ≈ 78.5 → 102.5) and **12 mm in Y** (centered on Y 33, so Y ≈ 27 → 39). Finish sketch.
3. **Extrude** it **up +Z by 4 mm** (Z4→Z8), **Operation: Join — but join it to `Plate_Left` only** (in the Extrude dialog, set the target body to `Plate_Left`). Now the tab is part of the Left half and lies flat across onto the Right half's top.
4. **Insert hole (into the Right half):** **Create → Hole** on the tab top, placed at about **8 mm to the Right of the seam** (X ≈ 98, Y 33). Type: **simple, Ø `insert_hole_dia` (5)**, depth **3.5 mm**, pointing **down**. This Ø5 pocket goes through the tab and into the Right plate to host a **short M3 heat-set insert**.
5. **Clearance + counterbore in the tab:** that same hole needs to pass the screw freely through the *tab* portion and let the head sit flush — easiest is to model the tab hole as a **counterbore** (Ø6 × 1 on top) over a Ø3.4 through the tab, sitting directly above the Ø5 insert pocket in the Right plate. (If that's fiddly, just make the tab hole Ø3.4 with a Ø6×1 top counterbore, and the Ø5 insert pocket only in the Right plate below it.)
6. **Repeat for T1, T3, T4** at their coordinates above.

**Hardware:** 4 × short **M3 heat-set inserts** (≤4 mm long — they seat in the 4 mm plate) + 4 × **M3 × 6 screws**. Press the inserts in with a soldering iron at ~240–260 °C.

> Prefer full-depth inserts? Add a small **boss** (raise the Right-half landing to Z9 with a ~12 × 12 pad) under each tab and use standard 5–6 mm inserts; the tab then rests on the boss top. The simple short-insert version above is fine for clamping — the steps carry the real load.

> Optional extra registration: where the seam crosses each **wall**, add a 2 mm tongue on one wall segment and a matching groove on the other (sketch on the cut face, extrude/cut 2 mm). Insurance only — skip on the first build and see if it's needed.

> ✅ **End of Phase 4:** two halves that bolt together and apart. Dry-fit them in CAD (Move/Align) to confirm tabs land in clear troughs. Save.

---

## PHASE 5 — Legs + tilt

Legs are a **separate component** so you can reprint/shim them without touching the plate (the plate is modeled flat — the legs create the 4.5° tilt). Keep these simple; they're meant to be tuned at assembly.

1. **Right-click the top of the browser → New Component.** Name it `Legs`. (Keep it activated while you model the legs so they stay separate from the plate bodies.)
2. **Four corner legs.** Model four blocks under the plate's front and back edges, **outside** the keyboard's 128.9 mm depth (so they straddle the board, not sit on it):
   - **Front legs** (toward −Y): height **23.9 mm** (starting point).
   - **Back legs** (toward +Y): height **≈ 33.7 mm** (= front + tan(4°) × leg-span).
   - Put them near the left and right plate ends (X ≈ −55 and X ≈ +238). Footprint ~15 × 15 mm each.
3. The back legs stand taller than the front by **tan(4°) × leg-span** — about **+9.8 mm over a ~140 mm span** — tilting the plate **4°** back-up so the plungers meet the keycaps square. (The legs straddle the 128.9 mm board, so the plate edges may need to extend in Y to reach them — see brief §7; legs are the iterative, shim-tuned part.)
4. **Attach:** a single screw hole up through each leg top into the plate edge (M3 or M5). Or print the legs with a shallow socket the plate edge drops into. Either is fine — these get shimmed.
5. **Shim to the gap:** at assembly, slide thin shims under the legs until every ball-tip rests **1–2 mm** above its keycap. A 0.5° tilt error ≈ 1 mm of gap drift over this depth, so check front and back rows.

*(See brief §7 — legs are deliberately the loosest, most iterative part. Don't over-engineer them in CAD.)*

> ✅ **End of Phase 5:** plate halves + legs. Save.

---

## PHASE 6 — Export STLs + print

1. **Export each body separately.** In the browser, right-click `Plate_Left` → **Save As Mesh** → format **STL**, **Refinement: High** → OK → save as `Plate_Left.stl`. Repeat for `Plate_Right` and each leg.
2. **Print settings (PLA, your standard):** 0.2 mm layer, 30 % infill, 4 walls (perimeters).
3. **Orientation:**
   - **Plate halves:** flat on the bed, **mounting walls pointing up** (the walls self-support; plunger holes print vertical = accurate). Each half is ~159 × 117 and ~163 × 117 mm — both clear the 256 mm bed with > 90 mm to spare.
   - **Legs:** flat, printed separately.
4. **Slicer check:** confirm each half fits the plate and there are no stray un-cut bodies. Slice, print.

> ✅ **End of Phase 6:** two printable STLs + legs. You're ready to print, install heat-set inserts, bolt the halves, and start mounting solenoids front-row-first (brief §4).

---

## Appendix A — The origin, in one line
Every coordinate in this build is measured from **one** point: the S-key hole at Fusion's origin (0,0,0). The DXFs are pre-drawn that way, so importing them with no offset puts S on the origin and every other feature falls into place — no chaining, no tolerance stack-up, and the model matches the paperwork exactly.

## Appendix B — Troubleshooting
- **Imported holes look tiny / huge:** the DXF came in at the wrong unit. Delete it and re-Insert, choosing **mm**.
- **Plate extruded solid (no holes):** you selected the disc regions too. Restart Extrude, click only the outer "web" region.
- **Split didn't separate a wall:** the seam surface wasn't tall enough — re-extrude it to span past Z32 (Side 1 = 40).
- **Can't select the seam as a cutter:** make sure it's a **surface** body (open line extrudes to a surface) and that you picked it under *Splitting Tools*, not *Body to Split*.
- **Tab/insert feels weak:** the steps carry the real load; the tabs only clamp. If you want more, switch to the boss + full-depth-insert option in Phase 4.
- **Search any command:** press **S** in Fusion and type the command name.

## Appendix C — Parameters (recap)
`plate_thickness` 4 · `wall_thickness` 2.5 · `wall_offset` 8 · `wall_height` 28 (top Z32) · `mount_hole_dia` 3.3 · `mount_hole_spacing` 15 · `lower_hole_z` 7 (→ screw holes Z11 & Z26) · `cbore_dia` 8 · `cbore_depth` 1.5 · `tilt_angle` 4 · `insert_hole_dia` 5.

## Appendix D — The two custom keys
`Cust1` (X 214.31) and `Cust2` (X 233.36, the ex-knob corner) are real holes in the DXF and get solenoids like any other key. If you decide **not** to actuate them, just don't cut those 2 holes (or leave them and skip the solenoids) → 82 solenoids. Your call — positions are already in the file.

# cad/ — Fusion scripts

Fusion has no MCP connector, so CAD works the same way KiCad does: **Daniel
drives Fusion, Claude owns the file and verifies it mechanically.** These
scripts are the mechanism — geometry lives in Python, so every dimension is
reviewable, diffable, and checkable without opening Fusion.

| File | What it does |
|---|---|
| `fusion_groove_coupon.py` | Builds the brief-08 groove coupon (plate section + 2 walls + mini-deck) in a fresh Fusion document. **The teardown gate.** |
| `verify_coupon_geometry.py` | Runs outside Fusion. Asserts every brief-08 invariant, the Jul 27 measurements, CSV key positions, and cross-checks against `Air75_84Key_Plate_Left.stl`. Currently 0 failures. |

## Running the coupon script in Fusion

1. Open Autodesk Fusion. Any document — the script creates its own.
2. **Utilities** tab → **ADD-INS** panel → **Scripts and Add-Ins** (or `Shift+S`).
3. **Scripts** tab → the **+** beside "My Scripts" → **Create from existing** → pick
   `cad/fusion_groove_coupon.py` from this repo.
   *(If Fusion insists on copying it into its own scripts folder, use the green
   `+` → "Link" option so it keeps reading the repo copy and git stays the source
   of truth.)*
4. Select `fusion_groove_coupon` → **Run**. A dialog reports the key dimensions.
5. Four components appear at true assembly coordinates: `Coupon_Plate`,
   `Wall_A`, `Wall_B`, `Coupon_Deck`. **Look at it first** — the walls should sit
   in their plate grooves with the deck grooves capturing their tops.
6. Export each component: right-click component → **Save as Mesh** → STL, or
   **File → Export** → STL with "one file per body" unchecked.

## Verifying before you print

```
python3 cad/verify_coupon_geometry.py
```

Needs `trimesh` and `numpy` for the STL cross-check (`pip install trimesh numpy`);
everything else runs on stock Python. Exit code 0 = all invariants hold.

## Slicer notes

| Part | Orientation | Notes |
|---|---|---|
| `Coupon_Plate` | flat, as modelled | groove floor is only 2mm — don't skimp on top layers |
| `Wall_A` / `Wall_B` | **lay flat on the wide face** | 58mm tall × 2.5mm thin section; printing upright makes a fragile fin and puts layer lines across the load path |
| `Coupon_Deck` | flat | grooves face up or down, doesn't matter at 2mm |

Same material and same nozzle/layer settings as the 84-key plate print — the
whole point is that the groove fit transfers to the real part.

## The test sequence (brief 08 §Stage 1 item 7)

1. Heat-set an M3 insert into each wall's boss.
2. Screw one solenoid to each wall **on the bench** — full access, no slot-driving.
   Use the M3×3 flat heads, counterbores facing the back.
3. Drop each wall+solenoid into its plate groove, plungers entering their Ø10
   holes first. Check: does the datum face seat? Does the groove bind or rattle?
4. Mini-deck on, 2 × M3×8 down into the inserts.
5. **Check the flare clears the back row's spring** — Wall_A's flare passes
   within 1.0mm of Wall_B's solenoid spring. This is the one clearance derived
   from an estimated spring OD rather than a measurement.
6. Fire both solenoids off the breadboard driver, deck installed.
7. One full swap cycle: deck off, wall out, swap the solenoid, back in.

**Pass = the old plate teardown is authorised.** Fit fail = change
`GROOVE_CLEARANCE` at the top of the script by ±0.05–0.10, re-run, reprint the
coupon only.

## Tuning log

Record each printed value here so the winning number is never re-guessed.

| Date | `GROOVE_CLEARANCE` | Plate groove | Deck groove | Result |
|---|---|---|---|---|
| — | 0.25 | 2.75 | 5.30 | not yet printed |

# Brief 04 — Wave 2 mouse decision

**Goal:** pick the mouse mechanism. This is a DECISION session — end it with one option chosen, a CAD/parts brief, and spreadsheet Wave 2 rows updated (ask first).

## The requirement that already prunes the field

The ultimate goal is the agent playing **TFT**, which is drag-and-drop (bench→board) needing real 2D precision. **The trackball-spinner option is DEAD** (no precise drag). Judge every candidate against: sustained press-move-release drags, ~±5px effective precision after the px→mm affine, and repeatability over an 800-turn game.

## Candidates (state as of July 2026)

1. **Animatronic hand riding the mouse over a hidden XY gantry** — best content ROI ("looks alive"); mechanically = gantry + a prop, so lowest added risk over the original plan.
2. **XY gantry + B100 (original PRD plan)** — parts already in Wave 2 list; V-slot + M5 hardware; boring but proven.
3. **5-bar pantograph arm** — ~$60–90, compact, cool motion; harder kinematics + rigidity risk for drag precision.
4. **Holonomic mouse rover** — highest novelty, highest risk; drag precision doubtful.

Also in hand: **Mouse Keys backend already works in software** (`mouse_driver.py --mouse mousekeys` — solenoids press macOS Mouse Keys; auto-toggles around typing via 5×Option). It's the $0 fallback and the "robot refuses to touch the mouse" content gag. It makes Wave 2 less urgent — but too slow for real TFT play, so it does not remove the decision.

## What's already built for it

`firmware/mouse_gantry_v0/` speaks HOME/MOVE/JOG/BTN/CLICK/SPEED/STATUS/STOP — that serial protocol is the contract with `GantryMouse` in `agent/mouse_driver.py`. **A pantograph swap only rewrites motion code behind the same protocol.** SG90 servos do L/R click in the original plan. `calibrate.py gantry` does the 3-probe px→mm affine.

## Decision criteria (weigh in this order)

1. Drag precision/repeatability (TFT hard requirement)
2. Content value — Daniel wants the viral mix of "looks alive / real feats / absurd"
3. Cost against remaining budget (~$134 headroom under the $1,500 ceiling — recheck the spreadsheet)
4. Build risk given: basic Arduino, beginner CAD, FDM printer
5. Reuse of the already-written firmware/driver contract

## Definition of done

One mechanism chosen with rationale logged in CLAUDE.md; parts list drafted (spreadsheet edits ask-first); CAD brief written if printing is needed; commit + **git push**.

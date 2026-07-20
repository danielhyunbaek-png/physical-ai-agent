# Brief 07 — Full plate rebuild + top deck (master plan)

> **AMENDED July 15 (later): the fastening scheme changed.** Daniel chose his own scheme over brief 03's drop-in pockets: **groove-sandwich removable walls** (tab screws kept; walls are separate parts keyed into plate grooves below and deck grooves above; deck held down by end posts + wall-top screws). Full spec + Fusion steps in **`08_groove_sandwich_cad.md`** — read it wherever this brief says "brief 03 scheme" or "clamp bars". Tracks/gates below are unchanged; the coupon is now brief 08's groove coupon. Caliper gate `d` (ledges) is no longer needed; body-top height + lead exits still are. Clamp-bar buy list (EVA foam) is replaced by brief 08's (inserts + M3×8 still needed, more of them).

**Decision (July 13, 2026, with Daniel; planned July 15):** rebuild the 84-key plate NOW using brief 03's drop-in pocket + clamp-bar scheme (revived), with two new requirements: **wires route straight UP** and a **top deck carries both driver PCBs**. Drivers: wiring dread, repair fear, no PCB home, elegance. The rebuild lands during the ~2wk PCB lead so no calendar time is lost.

**Confirmed choices (July 15):**
- **Teardown gate: the old plate stays fully assembled until the coupon passes** (swap cycle + fire). Zero risk of being stranded plateless if the pocket scheme fails on real plastic.
- **PCB order is NOT blocked by anything CAD.** Order first; the deck is designed around the ordered board's exact outline + mounting-hole coords, not vice versa. (Brief 06's terminal-edge placement is already fixed by that design.)

## What the deck changes about the harness (supersedes part of §Harness in CLAUDE.md)

The boards now live ON the plate assembly, directly above the solenoids. Consequences:

- **The 85-wire plate↔board harness is gone.** There is no "off to the board across the desk" run anymore.
- Per solenoid: **both leads route straight up** — high side to a **+12V bus on/under the deck** (bus wire relocates from wall-tops to the deck; same bare 16 AWG + one 18 AWG feed from the board's 12V terminal), low side up through a **deck pass-through slot** to its screw terminal on the PCB above.
- Wires get dramatically shorter (~40–80mm vs 300+mm), which is most of the wiring-dread win.
- **Unchanged rules:** MAP discipline (Sharpie the terminal's silkscreen box, log `cell · OUT · key` at landing), golden rule (cut to length only at the moment of landing), solid-vs-stranded (stranded into screw terminals, no tinning — ferrules optional).
- Wire-tidy Phases 1–2 (velcro bundles, wall-top buses) are **obsolete**. Phase 0 (snip/tape every frayed tip) is still mandatory before any handling.

## Deck design requirements (new part — CAD during the PCB lead)

1. **Carries both PCBs**: M3 mounts matching the ordered board's mounting-hole coords (export from EasyEDA after DRC; don't guess). Standoffs or printed bosses; boards face terminals-outward/up for screwdriver access.
2. **Wire pass-through slots** aligned with the rows below, sized for 14–16 leads per row plus slack; edges chamfered (no insulation chafe on PLA edges under vibration).
3. **+12V bus routing** on/under the deck: bus wire channels or printed clips; one 18 AWG feed drops to the board's 12V input terminal. No pinch points under the boards.
4. **Clearance stack (bottom-up):** plate → solenoid body tops (≈Z34 if d=7 — caliper gate) → clamp bars + screw heads → lead service loop → deck underside. Leave enough gap to get fingers/driver onto the clamp-bar screws WITHOUT removing the deck, if feasible; otherwise the deck must remove with ≤4 screws.
5. **Airflow**: the 80mm USB fan needs a path; deck must not seal the solenoid bay (thermal risk is documented). Cutouts between wire slots.
6. **Supports**: deck lands on the raised walls (brief 03 raises them to body-top+2mm) or on corner posts off the side rails — decide in CAD after caliper gate #2. Deck must be removable without disturbing landed wires (slots open to an edge, or generous service loops).
7. **Cascade + Mega**: 6-pin dupont cable Board A→B lives on the deck; Board A's IN header needs reach for the Mega jumpers — leave a cable exit toward wherever the Mega sits.
8. Footprint ~320×130 like the plate → **split deck L/R** with the same seam-bridging trick if the bed can't fit it.

## Sequence (gates in bold; nothing starts before its gate)

**Track A — electronics (critical path, start immediately):**
1. EasyEDA design session (Claude drives via Chrome; Daniel needs a JLCPCB account) → netlist beep-check against brief 06 → DRC → 1:1 paper print of layout → **order 5 boards ASAP** (per Jul 13: not gated on cell #1 — the breadboard fire test was the design gate).
2. Same day: export board outline DXF/dims + mounting-hole + terminal coords → feed Track B step 4.
3. Buy list on order day: screw terminals, DIP sockets (reuse perfboard ones if on hand), heat-set inserts + M3×8 pan heads + EVA foam (brief 03 clamp hardware — now needed again).

**Track B — mechanical (runs inside the ~2wk lead):**
1. Wire-tidy Phase 0 only: snip/tape all frayed tips on the populated plate. 10 min, do before any bench work near 12V.
2. **Caliper gates (brief 03, on the 2×2, 10 min):** d = body-bottom→lower-tab-hole; body-top height above plate; lead exit points. These size the ledges, wall raise, and bar slots.
3. Coupon print: 3-wall × 2-column interior section per brief 03 — sandwich fit, ribs, seat ledges, insert boss, bar preload, **one full vertical swap cycle + a fire** (breadboard driver — cell #1 chips; cell #1 board is parked). **GATE: coupon passes → old-plate teardown is authorized.** Coupon fails → fallback is the T-stud keyhole scheme (brief 03 §Rejected); old plate untouched either way.
4. Full CAD: plate L/R (locked params + `Full_84Key_Hole_Coordinates.csv`), walls with pockets/ribs/ledges/bosses, clamp bars **with vertical lead-exit slots (leads go UP through/past the bar, not sideways)**, deck L/R per requirements above. Write the full assembly sequence BEFORE finalizing geometry — anything not reachable vertically is a geometry bug.
5. Print everything. Plate + walls first (longest), bars + deck after.

**Track C — merge (boards arrive, ~Jul 29–Aug 5):**
1. Board A/B: sockets/terminals/caps → cold continuity gate → chips in → WALK 0–87 per brief 06 DoD (roving clipped spare).
2. **One rebuild session:** teardown old plate (168 screws out, one-time) → drop-in populate new plate row by row → foam + bars → mount deck + boards → land all 84 grey wires up through the slots (label + log) → +12V bus + feed → Mega hookup.
3. Flash keyboard_v1 → MAP from the solder-time log → WALK all 88 → first full-plate typing. **git push — this is the milestone of milestones.**

**Parallel, hardware-free (any wait time):** vision calibration (milestone 3 non-driver parts), `agent/tft/set_data.json`, firmware header comment fix (2-board split) once boards verified.

## Spreadsheet impact (NOTE ONLY — ask-first before editing)

All pending TODOs in CLAUDE.md still stand. Delta from this brief: brief 03's clamp hardware (M3 heat-set inserts ~30, M3×8 pan heads ~30, 3mm EVA foam tape) moves from "no longer needed" back to **BUY**. Row 39 M3×3 flat-heads: now legacy (2×2 only) after the rebuild.

## Definition of done

Coupon passed (swap + fire) · new plate populated + deck mounted with both boards · WALK 0–87 green · all 84 wires landed + logged · dimension doc written (like `2x2_Prototype_Dimensions.md`) · CLAUDE.md session record · commit + **git push**.

## UNVERIFIED

- Pocket/clamp scheme is paper until the coupon (inherited from brief 03).
- Deck clearance stack has zero measured numbers yet — everything hangs on caliper gates 1–3.
- 4700µF can diameter/lead pitch still to be measured in mm before PCB layout (brief 06).

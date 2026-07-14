# Brief 06 — Driver PCB: kill the perfboard interconnect

**Decision (July 10, 2026, with Daniel):** perfboard soldering for the driver cells is CANCELLED — cell #1 was dry-fit only, so nothing soldered is lost. Replacement: **one custom 6-cell PCB design, ordered ×5 from JLCPCB, bare boards + DIP sockets, populated with the chips Daniel already owns.** Two boards populated (6 + 5 cells = 11), three spares.

**Why:** Daniel's pain is specifically the point-to-point interconnect soldering (jumper fans, rails, cascade), not component soldering. On a PCB every interconnect is a copper trace; what remains is only through-hole pad soldering (sockets, screw terminals, caps) — the kind he's fine with. The architecture-on-one-PCB pattern is proven (Electronics-Lab published a 72-channel 74HC595+ULN2803 board — same design at 9 cells). Cost ~$35–60 all-in, within the ~$134 budget headroom. Lead time ~7–14 business days; the wait is covered by the breadboard fire test (below), wire-tidy Phases 0–2, and vision work.

**Supersedes for cells 1–11:** `Soldering_Plan.md`, `TopSide_Wiring_CutList.md`, `Cell_TopSide_Routing.svg` (keep on file — historical). `OneCell_595_ULN_Build_and_Fire_Guide.md`'s fire protocol still applies. Brief 01's soldering steps are replaced; its continuity gate, power-on rule, failure modes, and definition of done carry over.

## The board (design once, order 5)

- **6 cells per board** (48 ch). Board A = cells 1–6 (ch 0–47), Board B = cells 7–11 (ch 48–87) with the **6th slot socket left EMPTY — it must be LAST in the cascade** (an empty socket only breaks the chain downstream; nothing is downstream). `NUM_CELLS=11` unchanged.
- ≤100×100mm, 2-layer, 1oz — hits JLCPCB's cheapest tier (~$2–8 for 5 boards).
- Silkscreen: slots **S1–S6**, each OUT labeled `S{n}-OUT{m}` + a blank box to Sharpie the key name. Global cell = slot (Board A) or slot+6 (Board B). MAP discipline unchanged: log `cell · OUT · key` at landing time.
- **"ULN flipped" is a perfboard artifact — irrelevant on a PCB. Do not re-litigate.** Keep canonical Q0→IN1…Q7→IN8 so FIRE N → cell(N/8+1)/OUT(N%8+1) is preserved and firmware needs zero changes.

## Electrical spec (nets per cell — matches keyboard_v1.ino header)

**74HC595 (DIP-16 socket):** VCC(16)→+5V · GND(8)→GND · DS(14)→prev cell's Q7′(9), or board input header for slot 1 · SH_CP(11)→CLK bus · ST_CP(12)→LATCH bus · MR(10)→+5V · **OE(13)→OE bus** (see below — improvement over as-built GND tie) · Q0–Q7→ULN IN1–IN8 canonical · Q7′(9)→next cell's DS · 100nF across VCC/GND at each chip.

**ULN2803A (DIP-18 socket):** IN1–8(1–8)←Q0–7 · OUT1–8(18–11)→screw terminals · GND(9)→GND · **COM(10)→+12V (flyback — never skip)**.

**Per board:** 2-pos 12V input terminal · bulk 470–1000µF/25V on 12V + 100nF · 100µF+100nF on 5V · **6-pin cascade headers** (IN at slot 1, OUT after slot 6): `+5V · GND · DATA · CLK · LATCH · OE`. Board A IN header ← Mega (D11 data, D12 clock, D13 latch); Board A OUT → Board B IN via one 6-wire dupont/JST cable. Each board gets its own 12V+GND run to the PSU (star) — return current (worst case 7×300mA ≈ 2.1A) flows through board GND, so GND/12V as pours or ≥2mm traces; OUT traces ≥0.6mm.

**OE improvement (free on a PCB):** as-built perfboard had OE hard-wired to GND → 595s output random data at power-up (the USB-before-12V rule). On the PCB: **OE bus with 10k pullup to +5V, routed to the cascade header.** Wire it to a Mega pin (D10 suggested), set `PIN_OE` in firmware → outputs disabled until registers clear, power-on random-fire risk gone. Solder-jumper OE→GND as fallback. Keep the USB-first habit anyway.

## Solenoid connection (the "how do wires get to the board" answer)

**5.08mm screw terminal blocks** (interlocking 2/3-pos), one position per channel along three board edges. Strip the grey 22AWG low-side wire, screw it down — no crimping, no soldering, swaps are unscrew-rescrew, vibration-resistant. The §Harness plan in CLAUDE.md is unchanged: high sides → plate +12V bus; 84 grey low-sides + nothing else come to the boards; the plate bus feed (orange 18AWG) taps the board's 12V rail terminal. Golden rule unchanged: cut each grey wire to length only at landing. Optional: ferrule kit (~$15) for cleaner stranded terminations — don't tin wires into screw terminals.

## Ordering path

1. **EasyEDA** (free, browser, native JLCPCB integration): schematic → PCB → DRC clean → "one-click order JLCPCB" → 2-layer, 1oz, HASL, qty 5, cheapest shipping that's ~1wk. Claude can drive/assist via Chrome; Daniel needs a JLCPCB account.
2. No BOM/assembly needed (bare board). If Daniel later wants terminals+sockets pre-soldered: JLC THT service ≈ $3.50 + $0.017/joint (~$13/board + parts) — optional upsell.
3. Design review gate before ordering: beep-check the netlist against this brief, DRC, and print the layout 1:1 on paper to sanity-check terminal spacing.

## Buy list (spreadsheet NOT edited — ask-first; add these lines on confirm)

- 5.08mm screw terminals, ~50× 2-pos interlocking (~$10–15, Amazon)
- DIP-16 sockets ×12 + DIP-18 sockets ×12 (~$6) — **reuse the perfboard sockets if already on hand**
- 6-pin dupont or JST-XH cable (~$5, or existing jumpers)
- PCB order ~$4–15 + shipping ~$15–25
- Optional: ferrule kit ~$15

Total ≈ $35–60. Budget headroom ~$134 → fits.

## Interim: breadboard fire test (do THIS WEEK — amends brief 01)

Move cell #1's dry-fit 595+ULN onto a solderless breadboard (Daniel has one). Same nets as above (OE→GND directly on breadboard, MR→5V). Mega D11/D12/D13 + 5V/GND; BOSYTRO 12V → breadboard rails (18–20AWG from PSU screw terminals); **Mega GND and PSU GND common.** Spare solenoid on alligator clips: high side → +12V rail, low side → ULN OUT1 (pin 18). **USB first, THEN 12V.** `FIRE 0` → walk the clip across OUT1–8 (pins 18…11) with FIRE 0–7. Film it. Breadboard contacts (~1A) are fine for 22ms/300mA pulses — avoid long HOLDs. Brief 01's failure-mode list applies verbatim.

This closes the FIRE-test UNVERIFIED item (force at ~5mm bottom-out) two weeks before the PCB lands.

## Firmware impact

Zero code changes for bring-up. Post-PCB cleanup notes: the header comment "Cells 1-4 = Board A, 5-8 = Board B, 9-11 = Board C (3-board split)" is now stale (2-board split: 1–6 / 7–11) — fix the comment when boards are verified. If WALK shows reversed cell order, use `CASCADE_REVERSED 1`, don't rewire. Optional: define `PIN_OE` once the OE line is wired.

## Definition of done

Boards in hand → sockets/terminals/caps soldered → **cold continuity gate (chips out): 5V/GND/12V no shorts, spot-check Q→IN and OUT→terminal per slot** → chips in → breadboard-validated firmware talks to Board A → roving-solenoid WALK across all 48 ch → Board B same → cascade cable → WALK 0–87 → land real solenoid wires (log `cell · OUT · key`) → commit + **git push** + CLAUDE.md session record.

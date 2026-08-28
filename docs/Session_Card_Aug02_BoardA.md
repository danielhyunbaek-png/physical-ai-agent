# Session card — Aug 2, 2026 · "Board A alive"

**Goal (2–3h, realistic):** one populated driver board that provably switches all 32 channels — verified with a multimeter, no 12V, no solenoids, no terminals.

**Why this and not the coupon:** the boards arrived ~1 week early. Track C jumped the queue. The coupon/plate rebuild has no deadline pressure; the boards do — every day a board sits unpopulated is a day the 84-wire landing session can't be scheduled. Also: soldering board A tells you whether the fab came out right, which is the one thing you can't un-order.

---

## 0 · Order the terminals — DO THIS FIRST (5 min)

You cannot finish a board without them and the lead time is now the critical path.

- **60 × "KF301-5.08 2P"** — pitch **exactly 5.08mm, NOT 5.0** (5.0 drifts 1.2mm across a 16-screw row and the last block misses its holes). Side/horizontal wire entry, interlocking, pin ≤1.3mm. ~$8.
- While the cart is open: **6 × M3 male-female standoffs, 54mm body** + **~45 M3 heat-set inserts (Ø4)** + **~45 M3×8** (deck hardware, brief 08).
  - Standoff gotcha unresolved from Jul 27: the M-F stud is 6mm and must clear plate + washer + nut. If undecided, buy **F-F standoffs + M3×10** instead — that arrangement works regardless of how the plate thickness question lands.

## 1 · Inspect the bare boards (10 min) — film this

- Measure the board: must be **120.0 × 66.0 mm**.
- Read the silk: `C1-OUT1/2` … `C4-OUT7/8`, `12V-IN` with `+12V` / `GND` beneath the screws, `CASC-IN`, `CASC-OUT`. **Left digit = left screw** on both rows — confirm the top row reads `OUT2/1` style (that swap was the Jul 26 catch).
- Dry-fit an empty DIP-16 and DIP-18 into their holes. If they drop in, the fab is good.
- Sharpie a big **X across J41–J44** on ONE board — that's board C, its 4th cell is never populated.

## 2 · Solder board A — everything EXCEPT the screw terminals (~75 min)

Shortest part first so the board lies flat:

1. **R1** (10k)
2. **100nF ceramics** — C11, C21, C31, C41, CB2, CB3
3. **DIP sockets** — 4 × 16-pin, 4 × 18-pin. **Notch matching the silkscreen.** Solder the *empty* sockets; chips go in at the end.
4. **6-pin male header into J71** (the Mega link)
5. **CB1 4700µF LAST** — 25mm tall, fouls everything, and polarity matters (stripe = GND).

Terminals get soldered when they arrive. Nothing else waits on them.

Your Jul 13 protocol still applies: 350°C, tip tinned shiny, fresh flux, iron on both pad and lead, 2–3s, solder off first then iron.

## 3 · Logic bring-up — 5V only, **NO 12V today** (~30 min)

12V does nothing useful without solenoids and one reversed J70 kills all four ULNs. Leave the PSU unplugged.

**Wire Mega → J71** (6 × M-F dupont, female onto the board header):

| J71 pin | net | Mega |
|---|---|---|
| 1 | +5V | 5V |
| 2 | GND | GND |
| 3 | DATA | D11 |
| 4 | SCLK | D12 |
| 5 | RCLK | D13 |
| 6 | ~OE | **D10** |

**Pin 6 → D10 is not optional.** R1 holds ~OE high = all outputs disabled. Miss this wire and the board answers on serial, WALK prints all 88 channels, and nothing ever switches — no error message. (This is the bug caught Jul 26; `PIN_OE = 10` is already in the firmware.)

Then:

1. Chips into sockets — **notch matching the socket notch**. 595s in the 16-pin, ULN2803As in the 18-pin.
2. Flash `firmware/keyboard_v1` (confirm line ~60 reads `PIN_OE = 10`).
3. Serial monitor, 115200. Open it — USB power only.
4. **The test — no extra parts needed.** Multimeter on continuity/diode mode: black probe on a GND point, red probe in a terminal *hole* (the terminals aren't in yet, so the holes are exposed pads).
   - `HOLD 0` → hole `C1-OUT1` should read near-short to GND. `RELEASE ALL` → open.
   - Spot-check ~8 across the board: ch 0, 7, 8, 15, 16, 23, 24, 31.
   - Then `WALK 0 31 300 200` and watch the serial print march. (WALK auto-releases; any key aborts.)
5. If a channel is dead: probe the matching 595 Q pin → ULN IN pin at the socket. The board is DRC-verified, so a failure is a solder bridge or a cold joint, not the design.

**Pass = all 8 spot checks switch.** That's board A alive. Log it.

## 4 · Close out (15 min)

- Append a session record to `CLAUDE.md`.
- **git — you have a week of uncommitted work** (`cad/`, `media/`, `Caliper_Gate_Card.md`, the video edit sheet, CLAUDE.md edits). From your Terminal:

```
cd ~/Documents/Claude/Projects/Physical\ AI\ Agent
rm -f .git/HEAD.lock .git/index.lock
git add -A && git commit -m "Boards arrived; board A populated (no terminals); cad/ + media/ video pipeline"
git push
```

---

## Content, for free

Don't schedule a separate block. Film while you work:

- **The unboxing is a better shot than the order confirmation** the Big Reset script was waiting on. Five bare boards fanned out beats a JLCPCB receipt.
- Solder-session b-roll: sockets going in, CB1 towering over everything, the multimeter beeping on a channel.
- The `media/cell_x11_grid443.mp4` stop-motion already answers "I need 11 of these" — the arrival footage is its payoff shot. The video can post tonight if you want it to.

## Explicitly NOT today

- No 12V. No solenoids. No plate teardown. No coupon.
- Boards B and C stay bare — build one, verify one, then repeat with a known-good procedure.
- The board-to-board hardwired cascade waits until all three are populated.

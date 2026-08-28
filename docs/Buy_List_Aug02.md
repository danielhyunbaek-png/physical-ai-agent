# Buy list — Aug 2, 2026 · terminals + deck hardware + harness wire

**Total core cart: ~$82 (7 lines). With optional lines: ~$102.**
Budget check: ceiling $1,500, last estimate ~$1,366, minus the ~$20 PCB order → **~$114 headroom.** This fits, but it's most of what's left. Everything below is Amazon (your call, for speed).

---

## Core cart — buy all six

### 1 · Screw terminals — the actual blocker · ~$13

**★ CHOSEN (Daniel, Aug 2) — FULARR 80Pcs 2-Position 2-Pin PCB Screw Terminal Block, 5.08mm pitch, green, 300V/10A** — [amazon.com/dp/B07ZP885CT](https://www.amazon.com/FULARR-Premium-Position-Terminal-Connector/dp/B07ZP885CT)

Verified against `solenoid_driver.kicad_pcb`, not the spec sheet:

- **Fit confirmed.** Terminal footprints are placed at **10.16mm centers** (113.00 → 123.16 → 133.32 → … across the bottom row). FULARR body is **10mm** along the pitch axis → 8 blocks butt across the 81.28mm row with 0.16mm slack each. No interference. *(The KiCad footprint body is 10.76mm — 10.16 + a 0.60mm dovetail — which is why DRC reports 14 `courtyards_overlap`. A 10mm non-interlocking block simply sits with a hairline gap instead of nesting. Cosmetic; each block is located by its own solder pads, not by its neighbour.)*
- **"Plug-in" is a mistranslation of 插件 = through-hole, NOT a two-piece pluggable connector.** Confirmed by 1.4g / 10×10×8mm (a real pluggable 2P is ~20mm tall) and by the package contents listing a single item × 80, not header+plug pairs.
- Pitch **5.08mm** stated. Pins clear the 1.6mm drills. Wire range 14–22 AWG covers the 22 AWG grey.
- Qty 80 vs **47 needed** (16 + 16 + 12 output + 3 × J70) → 33 spare.

**Eyeball on the product photo before checkout:** screw head on the **TOP** face, wire hole on the **SIDE** face. Top-entry blocks put the screw where the deck goes and you could never land a wire after assembly.

> **Landing-session note:** 22 AWG is at the thin end of a 14–22 clamp. Twist the strands, strip 4.5–5mm, and **do not tin the tips** — solder cold-flows under sustained clamp pressure and the joint loosens over months, which presents later as intermittent dead keys with no visible cause.

*Rejected alternative (kept for the record): [100pk generic 5.08](https://www.amazon.com/Pieces-2-Pin-Terminal-Connector-5-08mm/dp/B07P7WGHZX). Whatever you buy, the one spec that can waste the order is **5.08 vs 5.0** — at 5.0 the error accumulates 0.08mm per block and the 16th screw in a row lands 1.2mm off its hole. Many near-identical KF301 listings are 5.0.*

### 2 · Deck standoffs — **this resolves the Jul 27 gotcha** · ~$10

**★ FINAL (Aug 2, third revision) — mixed F-F + M-F assortment kit, STACKED.**

**M3 standoff assortment containing BOTH genders** — F-F bodies 6/10/15/20mm (40/30/20/30pcs) · M-F bodies 6/10/15/20mm, all with 6mm stud (30/20/20/20pcs) · M3 nuts 3mm ×120 · thin 1mm ×120 · **pan-head screws M3×6 ×70, M3×12 ×50, M3×20 ×30**.

*History: F-F single-piece 60mm → unobtainable → M-F-only kit (would have needed a nut pocket) → **this kit, which needs no pocket at all.** The presence of F-F pieces is what makes it work.*

### The column: F-F 20mm (bottom) + M-F 20mm + M-F 20mm = 60mm

Starting with an F-F puts a **female end at BOTH ends of the finished column**, so both joints are plain screws and the Jul 27 stud-vs-nut problem never arises.

| Joint | Hardware | Through | Engagement |
|---|---|---|---|
| **Bottom** (plate) | **kit M3×12**, up from below | 4mm plate | **8mm** into the F-F bore |
| **Stack** ×2 | M-F 6mm stud into the female below | — | bodies butt, lengths add |
| **Top** (deck) | **M3×8 flat-head** (line 5), down | 4mm deck | **4mm**, flush for the PCBs |

**No nut, no nut pocket, no CAD feature beyond plain holes.** *(Supersedes the Ø6.5 × 1.5mm nut pocket proposed earlier the same day — that was only ever needed because the previous kit had no F-F pieces.)*

**Quantities, all inside the kit:** 6 × F-F 20mm (30 available) · 12 × M-F 20mm (20 available) · 6 × M3×12 (50 available).

**Why the kit's screws don't cover the top joint** — it's head shape, not length. All three kit screws are **pan head**, which stands ~2mm proud. The six column tops sit *under the PCB footprint* (plate is 308mm wide, the three boards span 360mm), so those heads must be flush → countersunk flat-head. The kit's M3×12 is perfect at the *bottom*, where a proud head hangs in free air below the plate.

**Verify on arrival — two checks:**

1. Stack two pieces and confirm the **bodies butt metal-to-metal**. If a bore is shallower than 6mm the stud bottoms out, the column comes out long, and the six end up uneven.
2. Confirm the **M3×12 doesn't bottom out** in the F-F bore before its head clamps the plate. If it does, use an M3×8 there instead — 4mm engagement is ample for a ~6N per-column load. *(Bottoming out is the dangerous mode: tight under the driver while clamping nothing.)*

**PCB spacers also covered:** use the **F-F 10mm** pieces — not the 6mm, since two screws entering 4mm and 4.4mm would collide inside a 6mm body. M3×8 up from under the deck, kit M3×6 down through the board.

**M3×10 is no longer needed anywhere**, which makes the optional 600pc assortment redundant.

**Brass works despite being soft** — these are in **tension** (holding the deck down against recoil), not compression. Worst case 7 solenoids × 5N = 35N over six columns; an M3 brass rod takes >1000N in tension.

**★ PLACEMENT — put all six directly over the leg lines** (front leg y≈−58.5, back leg y≈79). Load path becomes deck → standoff → plate → leg → desk in a straight column, with no bending moment at plate mid-span. Free to do, and it's the difference between a rigid assembly and a springy one.

**Keycap clearance CHECKED (Aug 2, from `Full_84Key_Hole_Coordinates.csv` + the plate STLs):** plate slab spans y −72..+82; keycap field only reaches y −47.6..+66.7 → **24mm of bare plate at the front, 15mm at the back.** Seam is at x≈88 (L/R plates overlap 80.97..95.25). So the 2 seam standoffs and 4 corners all sit off the key field, over free air. **No counterbore needed in the plate underside** — a socket-cap head protrudes ~3mm and the measured keycap clearance is only 1–2mm, so this would have been a collision anywhere inboard.

**New CAD to-dos this creates**, at each of the 6 positions (none exist — the plate STL predates all of this):

1. Ø3.4 clearance hole through the plate (the M3×12 head bears on the underside, over free air — no counterbore needed).
2. Ø3.4 hole + countersink in the deck for the M3×8 flat-head.

*(The Ø6.5 nut pocket proposed earlier today is no longer required — the F-F bottom piece removed it.)*

> **⚠ CAD consequence — do not miss this.** 60mm sets `deck_underside_z` = plate top (Z4) + 60 = **Z64**, not the Z58 in brief 08. Walls become **64mm tall**, not 58. That's 10mm of clearance above the plungers (Z54) instead of 4 — harmless, and the walls are grooved at both ends so they're a fixed-fixed column, not a cantilever. **Update brief 08 and the coupon script before you print anything.**

### 3 · Heat-set inserts · ~$10

**100 × M3 brass heat-set insert, M3×5×4 (5mm long, 4mm OD)** — [amazon.com/dp/B0CHYT2Z5W](https://www.amazon.com/TAMOSH-Knurled-Threaded-Resistant-Embedment/dp/B0CHYT2Z5W)

Actual need is far below brief 08's "~45": the wall-top **pads** became a single **boss per wall** on Jul 27, so it's 12 wall tie-downs + ~12 PCB mounts in the deck = **~24**. 100pc is $10 and you'll use them on everything else you print.

### 4 · Heat-set tip for your iron · ~$10

**7-piece heat-set insert tip set, 900M/T18 compatible** — [amazon.com/dp/B0CS662NVK](https://www.amazon.com/HANGLIFE-Heat-Set-Soldering-Compatible-Components/dp/B0CS662NVK)

Your YIHUA 939D+ takes 900M-series tips, so these fit. Brief 08 called this "optional but sanity-saving" — with 24 inserts to set, at 4mm OD each, into a part you cannot easily reprint, it's not optional. A bare conical tip pushes inserts in crooked and drags melted PLA up the threads.

### 5 · M3×8 screws · ~$9

**★ CHANGED Aug 2 — buy FLAT-HEAD COUNTERSUNK, not socket cap.**
**100 × M3 × 8mm flat/countersunk head socket screws, 304 stainless** — [amazon.com/dp/B01HBN0UU8](https://www.amazon.com/Countersunk-Socket-Screws-100-piece-Stainless/dp/B01HBN0UU8)

12 wall tie-downs + 6 deck→standoff + ~12 PCB mounts ≈ 30 used.

**Why flat-head:** the plate is 308mm wide but the three boards span 360mm, so the deck overhangs the plate and the **corner standoffs land underneath the board area**. Any proud screw head on the deck top means a board can't sit flat. A socket cap head is 3.0mm tall — counterboring it into a 4mm slab leaves 1mm of deck. A modeled countersink leaves 2.3mm and sits truly flush.

Applies to **everything passing down through the deck**: the 6 standoff screws and the 12 wall tie-downs. Model the countersinks in CAD, don't drill them. Don't overtighten — a flat head is a wedge and will split thin PLA.

*(Socket caps are still fine for the 6 × M3×10 coming up from **under** the plate — those heads hang in free air, outside the keycap field.)*

### 6 · Harness wire — the two gauges you don't have · ~$23

- **16 AWG bare tinned copper bus wire, 1/4 lb (~32 ft)** — [amazon.com/dp/B0050DGPQU](https://www.amazon.com/16AWG-Bare-Tinned-Copper-Wire/dp/B0050DGPQU) · ~$10
  The +12V bus along each of the 6 walls plus the trunk ≈ 3m. 32 ft is ~10m — enough to redo it twice. **Tinned, not bare natural copper**: it won't oxidize on a bench for weeks and it takes solder without fighting you.
- **18 AWG silicone stranded, red + black 25ft each** — [amazon.com/dp/B01KCPKRHS](https://www.amazon.com/BNTECHGO-Gauge-Silicone-Wire-Temperature/dp/B01KCPKRHS) *(check the 18 AWG variant on the listing — the linked SKU family covers 16 and 18)* · ~$13
  Carries the single PSU V+ → bus trunk feed and the three V− → J70 returns. Silicone because it's the only wire in the build that gets bent repeatedly during service, and it survives soldering-iron contact.

You said 22 AWG stranded is covered — that's the 84 low-side runs, the big one.

### 7 · Board-to-board cascade links · ~$7

> **DECISION Aug 2 (was X, now Y).** Was (Jul 26): board-to-board links **hardwired** — 6 short 22 AWG solid wires soldered straight through J72 into the next board's J71, chosen as "cheapest and easiest." Now: **male headers + female-female dupont jumpers.** Daniel's call after the tradeoffs were laid out. Buys instant board removal at the cost of ~$13 and 24 mechanical contacts on a machine that vibrates.

- ~~40pcs × 10cm female-to-female dupont jumper ribbon · ~$6~~ — **NOT NEEDED, Daniel has F-F on hand (Aug 2).** Need 12 (6 per hop × 2 hops).
- **2.54mm breakaway male pin header strips, 40-pin, 10pcs** — [amazon.com/dp/B00U8OCENY](https://www.amazon.com/Gikfun-2-54mm-Single-Breakaway-Arduino/dp/B00U8OCENY) · ~$7
  Snap off 6-pin lengths. Need **5**: A·J71 (Mega link), A·J72 → B·J71, B·J72 → C·J71. C·J72 is the chain tail — leave it empty, or populate it as a probe point.

**Assembly notes for these:**

- The gap is **31mm** (A·J72 at board-relative (103, 50) → B·J71 at (4, 26.65), boards butted at 120mm pitch). A 10cm jumper leaves ~70mm of slack per wire — keep the six together as a flat ribbon, don't peel them apart, and zip-tie the loop.
- **Mark pin 1 on both headers with a Sharpie dot.** A 6-way ribbon plugged in reversed end-for-end lands +5V on ~OE, GND on RCLK, and DATA on SCLK. Boards B and C would go unpowered and a Mega output would sit shorted to ground — probably survivable, definitely a bad afternoon.
- Every hop is **pin-1-to-pin-1, no crossover** (verified: J71 and J72 are identical `PinHeader_1x06_P2.54mm_Vertical` with the same net order and the same pin direction).
- The Mega link stays **male-to-female** dupont, which you already own — female onto A·J71's pins, male into the Mega.

---

## Optional

- **M3 assortment kit, 600pc** (6/8/10/12/16/20/25/30 + nuts + washers) — [amazon.com/dp/B0DYNLT9MK](https://www.amazon.com/Assortment-Socket-Screws-Washer-Stainless/dp/B0DYNLT9MK) · ~$20. You need **6 × M3×10** for the standoff-to-plate screws; if you already have M3×10 from an earlier buy, skip this. Otherwise it's the cheapest way to get them plus everything the rest of the build will want.
- **12 × M3 nylon spacers, ~5mm** to lift each PCB off the deck. The terminal-block solder tails protrude ~2mm; without spacers each board rocks on its own solder joints. Stacked M3 flat washers work too if the kit above is in the cart.

---

## Not buying

- **Filament** — you're borrowing. **Confirm the amount before you start CAD**: plate L/R + 12 walls + deck L/R is roughly 800g–1kg, and a spool that runs out at 90% through a 20-hour deck print is the worst failure mode in this whole plan.
- ~~**Cascade connectors** — decided Jul 26, board-to-board links are hardwired 22 AWG solid through J72→J71. Zero purchase.~~ **SUPERSEDED Aug 2 — see line 7 above.** Headers + F-F dupont, ~$13.
- **EVA foam / clamp-bar hardware** — deleted when brief 03's scheme was replaced.

---

## Open item this list does *not* resolve

`spring_OD` is still unmeasured, and it sets the wall flare thickness. Nothing in the cart depends on it, but the coupon does. Calipers on a loose solenoid, 30 seconds.

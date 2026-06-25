# Firmware — Week 2 Breadboard

Two sketches. Build them in order. Each is its own folder so the Arduino IDE is happy.

## 1. `sr_led_walk/` — sanity-check the shift register

Goal: prove one 74HC595 is wired correctly with 8 LEDs before any solenoids exist.

Wiring (74HC595 → Arduino Mega):

| 595 pin | Name  | Goes to       |
|--------:|-------|---------------|
| 14      | DS    | D11           |
| 11      | SH_CP | D12           |
| 12      | ST_CP | D13           |
| 13      | OE    | GND           |
| 10      | MR    | +5V           |
| 16      | VCC   | +5V (+ 0.1 µF to GND) |
|  8      | GND   | GND           |
| 15, 1–7 | Q0–Q7 | LED → 330 Ω → GND |

Flash, open Serial Monitor at 115200 — you should see a bit walking left-to-right across the 8 LEDs once per second-ish.

## 2. `keyboard_v0/` — drive 4 solenoids

After the LED walk works, swap the LEDs for the ULN2803A → 4 solenoids.

ULN2803A wiring:

- IN1–IN8 ← 595 Q0–Q7 (one-to-one)
- OUT1–OUT8 → low side of each solenoid coil
- Solenoid high side → +12V rail from PSU
- **COM (pin 10) → +12V** (this enables the internal flyback diodes — do not skip)
- GND (pin 9) → PSU GND **and** Arduino GND (common ground star point)
- 470 µF (or larger) bulk cap across the 12V rail near the ULN
- 0.1 µF decoupling across the 595 VCC/GND

Critical: the Arduino 5V rail and the PSU 12V rail must **not** touch. Only the grounds tie.

Open Serial Monitor at 115200 baud, line ending: Newline. Then type:

```
FIRE 0 50
FIRE 1 50
FIRE 2 50
FIRE 3 50
```

Acceptance: 4 crisp clicks in order. Plungers fully retract between fires. No buzzing, no missed clicks.

Also available: `ALLOFF` (force every channel low — useful if a fire hung).

### Pulse-width tuning notes

- 50 ms is the walkthrough default. Try also 30 ms and 80 ms and listen — Blush Nano switches actuate at ~1.4 mm so 30 ms is often enough once geometry is right.
- The firmware clamps any pulse to 200 ms and enforces a 20 ms gap between fires as a coil-protection guardrail.

### What to measure while the breadboard is live (feeds Week 3 CAD)

1. **Mounting tabs** — confirm 2 vs 4 tab layout and tab-hole spacing (calipers).
2. **Plunger rest extension** — mm of plunger sticking out at rest.
3. **Plunger force at 30 / 50 / 80 ms** — push against a kitchen scale tared to zero.
4. **Body temperature** after firing one solenoid 200× at 50 ms with 100 ms gap. Touch test is fine for now; flag if uncomfortably hot.
5. **End-to-end latency** — toggle a free Mega pin HIGH right before the latch and LOW after, scope or logic-analyzer the pin vs the solenoid current rise (optional, nice to have).

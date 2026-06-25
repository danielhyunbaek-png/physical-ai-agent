# Video 3 — Guest Brief: [Friend's name]

*One-pager so you know your role before we film. — Daniel*

## The hook: Aggie builds it, Longhorn keeps it from burning down

I (Texas A&M) spent three prints and two wrong screw sizes getting the mechanical mount right. You (UT Austin) are the electrical engineer I'm trusting to make sure the circuit doesn't release the magic smoke the first time 12V hits four coils. Best friends since high school, opposite sides of the Lone Star rivalry, finally forced to work on the same machine. That's the episode.

**Cold-open idea:** *"I go to A&M. My best friend goes to UT. We agree on almost nothing — but he's the one person I trust to keep my $1,400 build from catching fire."*

## Your role

You're the **electronics guy** for the series. In Video 3 you're not building from scratch — the LED→Solenoid prototype already drives them. Your job:

- Explain the driver circuit the audience already saw, so they understand *why* it works.
- Sanity-check it before we put 12V through four coils.
- Look ahead to the real problem: scaling 4 channels to 84.

One rule: you can be there for the first word, but **I hit the key.** It's an Aggie milestone.

## The segment you own

Right after the mechanical half ("the mount finally fits — now I have to make these things actually fire"), it's yours. Walk through how a 5V Arduino pin ends up slamming a 12V solenoid into a keycap.

## Your talking points (all specific to this build)

- **The flyback diode — your headline.** A solenoid is an inductor; cut the current and the collapsing field kicks back a voltage spike that fries the switching transistor. A diode across the coil (banded end toward +12V) clamps it. Great line: *"This 3-cent diode is the only thing between an Aggie's wiring and a cloud of smoke."* Optional stunt: fry a bare MOSFET without one on camera, then add the diode.
- **Why you can't drive it off the Arduino.** A pin sources ~20mA; the JF-0530B wants ~300mA at 12V. So each channel gets a logic-level N-channel MOSFET as a low-side switch (solenoid + to 12V, solenoid − to drain, source to ground, gate to the Arduino).
- **Common ground.** Arduino GND tied to PSU GND, or the gate has no reference and nothing switches. The classic beginner killer.
- **Gate resistor + pulldown.** ~150Ω in series, 10k gate-to-ground, so the coils don't chatter or fire on power-up while the Arduino boots.
- **Power budget.** Four coils now, but the 480W / 40A PSU is sized for many firing at once at ~300mA each — and explains why solenoids never run off the Arduino's regulator.
- **PWM holding trick.** Full power to pull, lower duty cycle to hold → less heat. Directly addresses our endurance/thermal worry.
- **4 → 84.** Shift registers (74HC595) or driver arrays instead of burning 84 Arduino pins. This plants the seed for future episodes.

## Rivalry beats you can riff on (keep it friendly)

- Maroon wire vs. burnt-orange wire. Each refuses to touch the other's color.
- *"An Aggie built a frame that actually works. I'm as surprised as you are."* → I fire back with Aggie pride.
- First word: classic is "HELLO WORLD," but a rivalry pick ("GIG EM" vs "HOOK EM," or "WHOOP") makes the other one groan on camera. Pick the word for the reaction.
- Gig 'em vs. Hook 'em at the sign-off.

## On camera, please

- Tie every point to a part in your hand or something on the bench — no whiteboard lectures.
- Keep takes tight; we'll cut around the tangents.
- The banter is seasoning. The engineering is the meal.

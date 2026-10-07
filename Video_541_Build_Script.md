# Video 2: "How I built it" (vertical, 1:30–1:45, voiceover + face)
**Drafted Oct 5, 2026.** Posts 3–5 days after Video 1 (the raw 618 run), ideally as a reply to a real "how does it work?" comment.
VO pace ≈ 150 wpm → ~230 words ≈ 1:35. Every VO line also goes on screen as captions (most viewers watch with the sound off).

## Script

| Time | Voiceover | Shot | Have it? |
|---|---|---|---|
| 0:00 | "This keyboard just typed 618 words per minute. Here's how I built it." | 2 s of the 618 run → result screen | ✅ phone clip |
| 0:05 | "Every key gets its own robot: a solenoid. Send it 12 volts and the plunger slams down on the key." | 240 fps slow-mo, one solenoid firing | 🎥 shoot |
| 0:13 | "84 of them, each exactly one key apart, tilted to match the keyboard. It took a test cell, a 2×2 prototype, and a full plate to get right." | Test cell → 2×2 → full plate (CAD renders + real parts) | ✅ renders / 🎥 parts |
| 0:25 | "An Arduino has 54 pins. I needed 84. So eleven shift registers turn a handful of wires into 88 outputs, and eleven driver chips switch the power." | Board close-up; `cell_x11_cascade.mp4` animation | ✅ animation |
| 0:37 | "I hand-soldered the first circuit. One of eleven took four hours. So I learned KiCad and designed my own circuit boards." | Perfboard cell #1 → KiCad screen recording → boards arriving | ✅ soldering clip / 🎥 KiCad screen rec |
| 0:49 | "Then 168 wires. I didn't label a single one, so I wrote a program that fires each solenoid and listens for which key shows up." | Wiring under the table → automap tool screen recording | 🎥 screen rec |
| 1:00 | "1 a.m. The solenoids start firing on their own. Then: *pop*." | Black screen or a dark shot, pop SFX | — |
| 1:05 | "A driver chip melted. New chip, plus a firmware fix that refreshes every chip 200 times a second." | Push in on socket B.U12 (the empty/replaced spot) + a fresh ULN2803A held up ("one of these"); optional red glow / smoke overlay | 🎥 shoot (melted chip was thrown away) |
| 1:13 | "2:37 a.m.: its first sentence." | "the quick brown fox…" typing on screen | ? (reshoot is easy) |
| 1:18 | "For speed, a script reads the words straight off Monkeytype and streams them over USB. Each key fires before the last one has even lifted." | Screen + keyboard; mt_reader panel | ✅ / 🎥 |
| 1:28 | "My goal was 320. It hit 340 with zero mistakes. Then I took the limiter off: 618, still zero mistakes." | 340 result → full run → 618 result | ✅ phone clips |
| 1:38 | "Next: all 84 keys." (or end on the result) | Face cam or plate wide shot | 🎥 |

## Pickups to shoot (one session, ~30 min)
1. 240 fps slow-mo: a single solenoid, then a row firing (`FAST` stream).
2. Socket B.U12 push-in + a spare ULN2803A in hand (the melted one was thrown away; check your phone for any photo from last night first).
3. Screen recordings: KiCad board, automap run, mt_reader panel + Monkeytype.
4. Wide shot under the table (wiring + paper-towel shim, for one honest laugh).
5. Face-cam lines: the opener and the closer at minimum.
6. Clean "quick brown fox" take if there's no footage of it.

## Edit notes
- Cut on solenoid clicks; keep real keyboard audio under the VO at about −18 dB.
- Make the pop the one moment with full silence before it.
- Show the 618 result twice: first as a tease (0:00), then as the payoff (1:30).
- Don't put "Part X" or "Day N" in the opening.

# Brief 10: "Me vs Claude: Tetris" (Video 2)

**Status (Oct 6, 2026, 11pm):** plan approved by Daniel. Nothing built yet. Building starts **after the ENGR midterm (Fri Oct 9)** unless Daniel says otherwise. Replaces `tools/selfwrite/` as the Video 2 build (selfwrite is kept on disk; its Keyboard helper gets reused).

## Why this video
- Answers the top comment on Video 1 (698 likes): "let Claude control it and write its own software."
- "Me vs Claude" format: the outcome is genuinely uncertain, because Claude's player is smart but every move has to go through real solenoids with real lag. That is the "AI vs the real world" theme, shown rather than said.
- The "why not just use software?" comments are NOT addressed in this video (one comment camp per video).

## Video outline (Daniel's structure, with Claude's notes)
1. **0–2s:** the viral 618 WPM clip.
2. **2–4s:** screenshot of the "let Claude control it" comment pops up.
3. **4–5s:** Daniel: "That's an amazing idea. Let's do it."
4. **Swipe to Daniel:** holds the push-to-talk, says "Hey Claude, let's play Tetris."
5. **Swipe to the monitor:** the robot types the whole game into the live editor (sped up). Show at least one Backspace fix + the keystroke counter. Line: "Every key pressed by the robot."
6. **Game launches.** Add the second open loop here: "Claude built this in 20 minutes. Now I have to beat it."
7. **Gameplay:** cut between the screen, the keyboard clacking on Claude's moves, and Daniel's face. Claude trash-talks out loud.
8. **Ending:** "I tried my best, but I've lost 20 times in a row. What should I do next?" **Only if true.** Film first, write the ending second (e.g. "I won 1 out of 20" is just as good).

## The game (Claude writes it; the robot types it)
- pygame window, full monitor, split screen: **DANIEL** left, **CLAUDE** right.
- Daniel: arrow keys on the Mac's built-in keyboard (Up = rotate, Down = soft drop, Space is Claude's, so Daniel hard-drops with Right Shift or Enter on the built-in board; final key choice when writing the spec).
- Claude: **J** left, **L** right, **I** rotate, **K** soft drop, **Space** hard drop, all through the robot. (Already mapped: J=53, L=61, I=51, K=46, Space=31.) Note: both keyboards feed the same Mac and it cannot tell them apart, so the two players MUST use different keys.
- Same piece sequence for both (seeded 7-bag), so it's fair.
- **Win = last one standing.** Clearing 2+ lines sends garbage rows to the opponent. Gravity speeds up every 30s, so a match ends in about 3–5 min.
- Colored pieces, names, scores, next-piece preview, "click to start" screen, 3-2-1 countdown, big WINNER screen, "press R for rematch".
- **Claude's player** lives inside the game: reads its own board, picks a placement (holes / height / bumpiness heuristic), and acts ONLY by pressing robot keys through our helper. After each press it checks the board; if the piece didn't move (missed press), it presses again.
- **Trash talk:** Claude writes its own lines into the game (start, Claude clears 4 lines, garbage sent, Daniel tops out, Claude tops out). Spoken through the Mac's built-in `say` voice via our helper, rate-limited so it doesn't talk over itself. Pre-written by Claude in the code, NOT live API calls (those would lag seconds).

## What we build (our code, not Claude's) in `tools/tetris_vs/`
1. **Typo-proof typer.** Types Claude's code at a steady ~100 WPM (~8 chars/s). Checks each line against what actually arrived; on a wrong/double char it presses **Backspace** back to the mistake and retypes; on a missed char it retypes; presses **Enter** only when the line is perfect. Reuses `tools/selfwrite/` Keyboard (TYPE chunks, leading spaces as `KEY Space`, PULSE 50 / LEAD 0 resent on connect).
2. **Live editor (receiver).** Runs in Terminal, big font, shows the code filling in with a keystroke counter + fix counter. Reports every received key back to the typer and writes the verified file. This is the screen-recording shot.
3. **Pre-flight test.** Before the robot types a single key: run Claude's game headless (SDL dummy driver, fake robot) vs a simulated opponent for a fixed time; must not crash and Claude's player must clear lines. If it fails, send the error back to Claude, up to 2 fix rounds. Also checks every char is typeable from the live MAP.
4. **Robot helper module.** The ONLY way Claude's code can press keys or speak: `press(key)`, `say(text)`. Enforces ~80 ms same-key re-fire (plate-sag value) and MAX_ON. Claude's code may import only `pygame`, `random`, `math`, `time` and this helper.
5. **Voice launcher.** A prompt waits for Daniel's sentence (filled by speech-to-text, below). His words + the built-in game spec go to Claude together. Honest framing: his sentence starts it; the detailed spec is pre-written.

## Speech input
- **Recommended: Wispr Flow (Daniel has the free version).** Zero build, polished, recognizable on camera. The launcher just waits for text in a prompt; Wispr drops Daniel's sentence there. A handful of short commands per session is tiny usage for the free tier (it has a weekly word cap; check it isn't hit before filming).
- Fallback: macOS built-in Dictation into the same prompt.
- Later upgrade, not for this video: our own hold-a-mouse-button push-to-talk with a local speech model.

## Daniel's to-do
- [ ] Anthropic API key (console.anthropic.com, separate from the Pro plan; $5 credit is plenty). `export ANTHROPIC_API_KEY=...` in every new Terminal.
- [ ] Map keys + `SAVE`: **Enter, LShift, Bksp**, digits, and `( ) : = ' " . , - _ [ ] + * < > / #` (Serial Monitor: `FIRE <ch>` → watch → `MAP <ch> <Name>` → `SAVE`). `python3 tools/selfwrite/selfwrite.py check` lists what's missing.
- [ ] `pip install pygame` in the `agent/.venv`.
- [ ] Confirm Wispr Flow can type into Terminal (and whether its hotkey can be a mouse button; otherwise hold its normal key).
- [ ] Find the melted ULN2803A for b-roll (optional).

## Order
1. **Tonight / this week (rig only):** API key + key mapping.
2. **After Fri Oct 9:** Claude builds the typer, editor, pre-flight, helper, launcher; dry-tests everything with no robot and no API (fake modes, like selfwrite).
3. **One rig evening:** rehearsal (short game spec first), then the full filmed run + 20 matches.

## Risks
- **Plate sag:** missed presses make Claude's play sloppier and the typing slower. Survivable (retries), but the permanent plate support would help a lot.
- **Long type:** ~300–400 lines, roughly 15–20 min of typing. The line-by-line fix makes errors recoverable; a stuck key/hardware fault would still stop it.
- **First-try game bugs:** handled by the pre-flight test + fix rounds.
- **Window focus:** Daniel clicks the game window once to start (he's a player anyway).
- **API cost:** pennies per run, under ~$1 across all rehearsals.
- **Safety:** PSU on only while actively running (Oct 5 incident rule).

# Me vs Claude: Tetris — run card (brief 10)

Daniel speaks → Claude writes a versus Tetris game → pre-flight test → the robot
types every line into a live editor (typo-proof) → the robot types
`python3 tetris.py` → Daniel (built-in keyboard) vs Claude (robot keys).

| File | What |
|---|---|
| `play.py` | the whole run, one command |
| `game_spec.md` | the spec sent to Claude with Daniel's sentence (edit to change the game) |
| `robot.py` | the ONLY way the game touches hardware: `press` `pending` `say` `tick` `report` |
| `editor.py` | live editor (curses) + typer that Backspaces/retypes until each line is perfect |
| `preflight.py` | static checks + 40 s headless game vs a simulated player |
| `reference_game.py` | my own working game: `--fake-claude` stand-in and a filming-night fallback |
| `runs/<stamp>/` | every Claude reply, the candidate, and the typed `tetris.py` |

## Setup (every new Terminal)
```
cd ~/Documents/Claude/Projects/Physical\ AI\ Agent
conda deactivate                       # if (base) shows
source agent/.venv/bin/activate
export ANTHROPIC_API_KEY=...           # from Notes
cd tools/tetris_vs
```
Make the Terminal font big for filming (Cmd +). Close Serial Monitor (it holds the port).

## Ladder — run in order, stop at the first failure
1. **Laptop only, no robot, no API:** `python3 play.py --dry --fake-claude`
   Fake keys (with typos) fill the editor at 4× speed, then the game opens with
   a simulated robot. Click → play against Claude with the arrows. *Proves the
   whole pipeline on your Mac.*
2. **API, no typing:** `python3 play.py --preview` → say a sentence. Claude writes
   the game and it must pass pre-flight. Cost about 10–30 cents. Then play it:
   `python3 play.py --dry --game runs/<stamp>/claude_game.py`
3. **Robot, short file:** PSU on. `python3 play.py --file ../selfwrite/gen0.py`
   The robot types a 13-line file into the editor, then launches it (it will
   just error. That's fine, it's a typing test). Watch the fix counter.
4. **Robot plays, no typing:** `python3 play.py --no-type --fake-claude`
   Click the game window → click to start → Claude's moves come through the
   solenoids. *This is the 20-matches setup.*
5. **The filmed run:** `python3 play.py` → press the Wispr key → "Hey Claude,
   let's play Tetris" → Enter. About 1–2 min for Claude + 40 s pre-flight, then
   ~18–22 min of typing.

Rematches: `python3 play.py --game runs/<stamp>/tetris.py` (no retyping).

## During typing
- **Ctrl-P** pause · **Ctrl-R** resume · **Ctrl-C** abort (the robot has no Ctrl key, so these are always you).
- While paused you can fix a line by hand on the built-in keyboard. On resume
  the typer re-reads the screen and keeps anything already correct.
- "STUCK on line N" = 30 attempts on one line. Check the plate under that key, then Ctrl-R.
- Don't touch the built-in keyboard while it's typing: your keys land in the editor too.

## Controls
DANIEL (built-in): ← → move · ↑ rotate · ↓ soft · Right Shift / Return hard drop · R rematch · Esc quit
CLAUDE (robot): J L move · I rotate · K soft · Space hard drop

## Knobs (env)
`CLAUDE_MODEL` (default claude-sonnet-5-5; try claude-opus-5-5 if Sonnet's game is weak) ·
`TETRIS_WINDOW=1440x900` · `TETRIS_VOICE=Daniel` (any `say -v '?'` voice) ·
`TETRIS_SAMEKEY=130` same-key ms · `KB_PULSE=50`

## Safety
PSU on only while something is running (Oct 5 rule). The game sends `ALLOFF`
on exit, but close it with Esc, not by killing Terminal.

## Verified (Oct 7, cloud sandbox, no hardware)
- Pre-flight on `reference_game.py`: 40 s, ~170 sim presses, 13–15 lines cleared.
- Typer vs injected typos, all four runs ended with a byte-perfect file: 0% → 1.00× keystrokes;
  0.9% → 1.24×; 4% → 1.69×; 16% → 2.65× (24 stuck-pauses).
- Full `play.py --dry --fake-claude` in a pseudo-terminal: prompt → pre-flight →
  typing (282 typos fixed) → typed file == Claude's code → `python3 tetris.py` → game ran.
- All files parse as Python 3.9.

**UNVERIFIED:** real Claude API output (needs your key; step 2); real serial
(steps 3–4); curses rendering in Ghostty; pygame window focus on macOS;
`say` voice; whether the real KEY round-trip keeps up with gravity.

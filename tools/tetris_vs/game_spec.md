Write a complete two-player VERSUS Tetris game in ONE Python file.

Context: you are playing against a human, the person who just spoke to you. Every
character of your file will be typed by a physical robot keyboard (84 solenoids
pressing real keys), then run. During the game YOU play too, but you can only
act by pressing real keys through those same solenoids, so every move you make
is physically slow and a press can occasionally be missed. Design for that.

## Hard rules (a test harness enforces these)
- Python 3.9. Allowed imports ONLY: pygame, random, math, time, robot.
- ASCII only. 4-space indents, no tabs. Keep lines under 80 characters.
- Keep it SHORT: aim for 7000-8500 typed characters, hard limit 9500
  (leading indentation is free: the editor auto-indents). Each character
  costs the robot ~0.12 s of typing. Very few comments.
- No file, network or OS access. Fonts: pygame.font.Font(None, size) only.
- The window: screen = pygame.display.set_mode(robot.WINDOW)
- Call robot.tick() exactly once per frame in the main loop. 60 FPS clock.
- QUIT event or the Escape key exits cleanly (pygame.quit(), then return).

## The robot module (already exists, do not write it)
    import robot
    robot.WINDOW            # (width, height) for set_mode
    robot.press(key)        # key is one of "J", "L", "I", "K", "Space".
                            # Queues ONE physical key press. Returns True if
                            # queued. Never blocks.
    robot.pending()         # number of presses queued or still in flight
    robot.say(text)         # speaks text out loud in Claude's voice; skipped
                            # (returns False) if it is already talking
    robot.tick()            # once per frame
    robot.report(name, value)   # status for the test harness, see below

## Controls (two keyboards feed the same Mac, so the keys MUST differ)
- HUMAN (left board, Mac's built-in keyboard): Left/Right arrows move,
  Up rotates clockwise, Down soft-drops one row, Right Shift OR Return
  hard-drops.
- CLAUDE (right board, the robot keyboard): J left, L right, I rotate
  clockwise, K soft drop one row, Space hard drop.
- The game moves Claude's piece ONLY when it receives those KEYDOWN events,
  exactly like a human player. Your AI must never move pieces directly.

## Game rules
- Two 10x20 boards. Standard 7 tetrominoes, colored.
- Both players get the SAME piece sequence: one 7-bag sequence per match
  from random.Random(seed), each player has their own index into it.
- Spawn at the top center. Rotation with simple wall kicks (try x offsets
  0, -1, 1, -2, 2). A piece locks when gravity cannot move it down.
- Gravity starts at 0.8 s per row and gets 20% faster every 30 s (min 0.1 s),
  same for both players.
- Clearing n lines: n >= 2 sends n - 1 garbage rows to the opponent (4 lines
  sends 4). Garbage rows are gray, full except one random gap, and are added
  at the bottom of the opponent's board when their next piece spawns.
- If a new piece cannot spawn, that player tops out and the OTHER player wins.

## Screens
- Menu: big title "HUMAN vs CLAUDE", the controls for both players,
  "click to start". A mouse click starts a 3-2-1 countdown, then play.
- Play: HUMAN board on the left, CLAUDE board on the right, names above them,
  lines cleared, next-piece preview for each, match timer in the middle.
- Game over: a big "CLAUDE WINS" or "HUMAN WINS" overlay plus
  "press R for rematch". R starts a new countdown with a new seed and keeps a
  running match score (e.g. "HUMAN 1 - 3 CLAUDE").

## Claude's player (the important part)
- When Claude's piece spawns, pick a placement: for every rotation and every
  x, simulate a hard drop on the current board and score the result with
  -0.51*aggregate_height + 0.76*lines_cleared - 0.36*holes - 0.18*bumpiness.
  Prefer fewer rotations on ties.
- Then each frame: if robot.pending() > 0, or less than 0.2 s has passed since
  your last press, do nothing. Otherwise look at the ACTUAL piece state and
  press exactly one key toward the goal: "I" until the rotation matches,
  then "J"/"L" until x matches, then "Space".
- Never assume a press worked: always decide from the actual state, so a
  missed press is simply repeated and an extra move is corrected. If the
  same press has had no effect 4 times in a row (blocked), press "Space".
- Re-plan whenever a new piece spawns (track a piece counter).

## Trash talk (robot.say)
Write your own short, funny, PG lines (under 12 words each), several
variants per moment, picked at random:
- when the match starts,
- when Claude clears 2+ lines (sending garbage),
- when Claude clears 4 lines at once,
- when the human tops out (Claude wins),
- when Claude tops out (the human wins; be a gracious but salty loser).
Keep it general: call the opponent "human", never use a name, and never
mention who built the robot or anything about its history. Human-vs-machine
banter, and jokes about you moving only by solenoid, are fine.

## Reports for the test harness (required)
    robot.report("state", s)        # s in "menu","countdown","playing","over"
    robot.report("claude_lines", n) # total lines Claude cleared this match
    robot.report("daniel_lines", n)
    robot.report("winner", w)       # "CLAUDE" or "HUMAN", when a match ends

Reply with ONLY the Python code. No markdown fences, no explanation.

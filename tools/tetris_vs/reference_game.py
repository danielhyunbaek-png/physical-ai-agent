import pygame
import random
import time
import robot

W, H = robot.WINDOW
CS = min(30, (H - 140) // 20)
SHAPES = {
    "I": ["....", "IIII", "....", "...."],
    "O": [".OO.", ".OO.", "....", "...."],
    "T": [".T..", "TTT.", "....", "...."],
    "S": [".SS.", "SS..", "....", "...."],
    "Z": ["ZZ..", ".ZZ.", "....", "...."],
    "J": ["J...", "JJJ.", "....", "...."],
    "L": ["..L.", "LLL.", "....", "...."],
}
COLORS = {"I": (0, 220, 240), "O": (240, 220, 0), "T": (170, 60, 230),
          "S": (60, 220, 80), "Z": (240, 60, 60), "J": (50, 100, 240),
          "L": (250, 150, 30), "G": (110, 110, 110)}
TALK = {
    "start": ["Good luck, Daniel. You built me. Big mistake.",
              "I type 618 words a minute. Tetris is easy.",
              "Let's go. My solenoids are warmed up."],
    "garbage": ["Here, have some garbage. It's a gift.",
                "Special delivery. Mostly gray blocks.",
                "Incoming trash. Like your sleep schedule."],
    "tetris": ["Tetris. Did you see that, Daniel?",
               "Four lines. Even with a sagging plate."],
    "win": ["Game over. The robot wins again.",
            "Maybe study for your midterm instead.",
            "Good game. For a human."],
    "lose": ["Fine. My plate was sagging.",
             "You only won because I melted a chip once.",
             "Rematch. Right now."],
}


def cells_of(name, rot):
    m = SHAPES[name]
    for _ in range(rot % 4):
        m = ["".join(r) for r in zip(*m[::-1])]
    return [(x, y) for y in range(4) for x in range(4) if m[y][x] != "."]


class Player:
    def __init__(self, name, seq):
        self.name, self.seq, self.i = name, seq, 0
        self.board = [[None] * 10 for _ in range(20)]
        self.lines = self.garbage = self.pid = 0
        self.dead = False
        self.spawn()

    def fits(self, rot, x, y, board=None):
        b = board or self.board
        for cx, cy in cells_of(self.p, rot):
            px, py = x + cx, y + cy
            if px < 0 or px > 9 or py > 19 or (py >= 0 and b[py][px]):
                return False
        return True

    def spawn(self):
        while self.garbage:
            self.garbage -= 1
            row = ["G"] * 10
            row[random.randrange(10)] = None
            self.board = self.board[1:] + [row]
        self.p = self.seq.get(self.i)
        self.i += 1
        self.rot, self.x, self.y = 0, 3, -1
        self.pid += 1
        if not self.fits(0, 3, -1):
            self.dead = True

    def move(self, dx, dy):
        if self.fits(self.rot, self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
            return True
        return False

    def rotate(self):
        for k in (0, -1, 1, -2, 2):
            if self.fits(self.rot + 1, self.x + k, self.y):
                self.rot, self.x = (self.rot + 1) % 4, self.x + k
                return

    def lock(self):
        for cx, cy in cells_of(self.p, self.rot):
            if self.y + cy < 0:
                self.dead = True
                return 0
            self.board[self.y + cy][self.x + cx] = self.p
        full = [r for r in self.board if all(r)]
        n = len(full)
        self.board = [[None] * 10 for _ in range(n)] + \
            [r for r in self.board if not all(r)]
        self.lines += n
        self.spawn()
        return n

    def drop(self):
        while self.move(0, 1):
            pass
        return self.lock()


class Bag:
    def __init__(self, seed):
        self.rng, self.items = random.Random(seed), []

    def get(self, i):
        while len(self.items) <= i:
            b = list("IOTSZJL")
            self.rng.shuffle(b)
            self.items += b
        return self.items[i]


def evaluate(board):
    hs, holes = [], 0
    for x in range(10):
        col = [board[y][x] for y in range(20)]
        top = next((y for y in range(20) if col[y]), 20)
        hs.append(20 - top)
        holes += sum(1 for y in range(top, 20) if not col[y])
    bump = sum(abs(hs[i] - hs[i + 1]) for i in range(9))
    return -0.51 * sum(hs) - 0.36 * holes - 0.18 * bump


def plan(pl):
    best = None
    for r in range(4):
        for x in range(-2, 10):
            if not pl.fits(r, x, -1):
                continue
            y = -1
            while pl.fits(r, x, y + 1):
                y += 1
            b = [row[:] for row in pl.board]
            ok = True
            for cx, cy in cells_of(pl.p, r):
                if y + cy < 0:
                    ok = False
                    break
                b[y + cy][x + cx] = pl.p
            if not ok:
                continue
            n = sum(1 for row in b if all(row))
            b = [row for row in b if not all(row)]
            b = [[None] * 10 for _ in range(n)] + b
            s = evaluate(b) + 0.76 * n
            if best is None or s > best[0] + 1e-9:
                best = (s, r, x)
    return best


class Bot:
    def __init__(self):
        self.pid, self.target, self.last = -1, None, 0.0
        self.prev, self.same = None, 0

    def act(self, pl):
        now = time.time()
        if robot.pending() or now - self.last < 0.2 or pl.dead:
            return
        if pl.pid != self.pid:
            self.pid, self.same, self.prev = pl.pid, 0, None
            b = plan(pl)
            self.target = (b[1] % 4, b[2]) if b else (pl.rot, pl.x)
        state = (pl.pid, pl.rot, pl.x)
        tr, tx = self.target
        if pl.rot != tr:
            key = "I"
        elif pl.x < tx:
            key = "L"
        elif pl.x > tx:
            key = "J"
        else:
            key = "Space"
        self.same = self.same + 1 if state == self.prev else 0
        self.prev = state
        if self.same >= 4:
            key = "Space"
        if robot.press(key):
            self.last = now


def draw_board(scr, f, pl, ox, oy, label):
    scr.blit(f[1].render(label, True, (255, 255, 255)), (ox, oy - 50))
    pygame.draw.rect(scr, (40, 40, 50), (ox - 3, oy - 3, CS * 10 + 6, CS * 20 + 6))
    pygame.draw.rect(scr, (15, 15, 20), (ox, oy, CS * 10, CS * 20))
    cells = [(x, y, c) for y, r in enumerate(pl.board) for x, c in enumerate(r) if c]
    if not pl.dead:
        cells += [(pl.x + cx, pl.y + cy, pl.p) for cx, cy in cells_of(pl.p, pl.rot)
                  if pl.y + cy >= 0]
    for x, y, c in cells:
        pygame.draw.rect(scr, COLORS[c], (ox + x * CS + 1, oy + y * CS + 1, CS - 2, CS - 2))
    nx = ox + CS * 10 + 15
    scr.blit(f[0].render("NEXT", True, (180, 180, 180)), (nx, oy))
    nxt = pl.seq.get(pl.i)
    for cx, cy in cells_of(nxt, 0):
        pygame.draw.rect(scr, COLORS[nxt], (nx + cx * 20, oy + 30 + cy * 20, 18, 18))
    scr.blit(f[0].render("LINES %d" % pl.lines, True, (220, 220, 220)), (nx, oy + 120))


def center(scr, font, text, y, color=(255, 255, 255)):
    s = font.render(text, True, color)
    scr.blit(s, (W // 2 - s.get_width() // 2, y))


def main():
    pygame.init()
    scr = pygame.display.set_mode(robot.WINDOW)
    pygame.display.set_caption("DANIEL vs CLAUDE")
    clock = pygame.time.Clock()
    f = [pygame.font.Font(None, s) for s in (30, 48, 110)]
    state, score, players, winner = "menu", [0, 0], None, ""
    t0 = fall = 0.0
    bot = Bot()
    robot.report("state", state)
    while True:
        now = time.time()
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                pygame.quit()
                return
            go = state == "menu" and e.type == pygame.MOUSEBUTTONDOWN
            if state == "over" and e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                go = True
            if go:
                bag = Bag(random.randrange(10 ** 9))
                players = [Player("DANIEL", bag), Player("CLAUDE", bag)]
                bot, state, t0, fall = Bot(), "countdown", now, now
                robot.report("state", state)
                robot.say(random.choice(TALK["start"]))
            if state == "playing" and e.type == pygame.KEYDOWN:
                k = e.key
                for idx, keys in ((0, (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP,
                                       pygame.K_DOWN, (pygame.K_RSHIFT, pygame.K_RETURN))),
                                  (1, (pygame.K_j, pygame.K_l, pygame.K_i,
                                       pygame.K_k, (pygame.K_SPACE,)))):
                    pl, other = players[idx], players[1 - idx]
                    if k == keys[0]:
                        pl.move(-1, 0)
                    elif k == keys[1]:
                        pl.move(1, 0)
                    elif k == keys[2]:
                        pl.rotate()
                    elif k == keys[3]:
                        pl.move(0, 1)
                    elif k in keys[4]:
                        n = pl.drop()
                        if n >= 2:
                            other.garbage += 4 if n == 4 else n - 1
                            if idx == 1:
                                robot.say(random.choice(TALK["tetris" if n == 4 else "garbage"]))
        if state == "countdown" and now - t0 >= 3:
            state, t0, fall = "playing", now, now
            robot.report("state", state)
        if state == "playing":
            speed = max(0.1, 0.8 * 0.8 ** int((now - t0) // 30))
            if now - fall >= speed:
                fall = now
                for idx, pl in enumerate(players):
                    if not pl.move(0, 1):
                        n = pl.lock()
                        if n >= 2:
                            players[1 - idx].garbage += 4 if n == 4 else n - 1
            bot.act(players[1])
            robot.report("daniel_lines", players[0].lines)
            robot.report("claude_lines", players[1].lines)
            if players[0].dead or players[1].dead:
                winner = "DANIEL" if players[1].dead else "CLAUDE"
                score[winner == "CLAUDE"] += 1
                state = "over"
                robot.report("winner", winner)
                robot.report("state", state)
                robot.say(random.choice(TALK["win" if winner == "CLAUDE" else "lose"]))
        scr.fill((8, 8, 14))
        if state == "menu":
            center(scr, f[2], "DANIEL vs CLAUDE", H // 4)
            center(scr, f[0], "DANIEL: arrows move/rotate, Down soft, Right Shift drop",
                   H // 2)
            center(scr, f[0], "CLAUDE (robot): J L move, I rotate, K soft, Space drop",
                   H // 2 + 35)
            center(scr, f[1], "click to start", H * 3 // 4, (255, 220, 80))
        else:
            oy = 90
            draw_board(scr, f, players[0], W // 4 - CS * 5 - 40, oy, "DANIEL")
            draw_board(scr, f, players[1], W * 3 // 4 - CS * 5 - 40, oy, "CLAUDE")
            el = int(now - t0) if state == "playing" else 0
            center(scr, f[1], "%d:%02d" % (el // 60, el % 60), 20)
            center(scr, f[0], "DANIEL %d - %d CLAUDE" % (score[0], score[1]), H - 40)
            if state == "countdown":
                center(scr, f[2], str(3 - int(now - t0)), H // 2 - 50, (255, 220, 80))
            if state == "over":
                center(scr, f[2], winner + " WINS", H // 2 - 70, (255, 220, 80))
                center(scr, f[1], "press R for rematch", H // 2 + 30)
        pygame.display.flip()
        robot.tick()
        clock.tick(60)


main()

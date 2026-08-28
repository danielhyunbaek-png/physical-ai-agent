"""
New-plate b-roll render  -  Physical AI Agent
=============================================
Builds the groove-sandwich rebuild (brief 07/08) as a shaded 3D animation for
the "Big Reset" video, shot #6.

Every dimension is pulled from the project record, not invented:
  * 84 key positions        Full_84Key_Hole_Coordinates.csv (6 rows, real stagger)
  * plate                   Z0-Z4, 4mm
  * wall datum face         hole_y + 8.000 EXACTLY (the datum rule)
  * wall thin section       2.50mm, Z2 (groove floor) -> Z36
  * wall flare              back face = hole_y + 19.05 - SPRING_OD/2 - 1.0
  * deck underside          Z58   (driven by the MEASURED plunger top Z54 + 4)
  * deck                    Z58 -> Z62, 4mm
  * wall top                Z60   (2mm into the deck groove)
  * solenoid body           15(x) x 16(y) x 30(z), Z4 -> Z34
  * plunger                 O6 x 58, ball tip Z-4 -> top Z54
  * PCB                     120 x 66 x 1.6, 3 boards, 4 corner M3 at (4,4)...
  * CB1                     O17 x 25 electrolytic (tallest part)

Pure numpy software rasterizer (z-buffer, flat shading) - no trimesh/vtk in
the sandbox. Output: 1080x1920 vertical MP4 + GIF + labeled still.

Author: Claude (Opus), Jul 28 2026 session.
"""

import csv
import math
import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# GEOMETRY CONSTANTS  (mirrored from cad/fusion_groove_coupon.py)
# ---------------------------------------------------------------------------
PLATE_THICKNESS = 4.0
GROOVE_DEPTH_PLATE = 2.0
WALL_OFFSET = 8.0
WALL_THICKNESS = 2.50
PITCH_Y = 19.05
SPRING_OD = 10.0
SPRING_CLEARANCE = 1.0

BODY_W, BODY_D, BODY_H = 15.0, 16.0, 30.0
BODY_BOTTOM_Z = PLATE_THICKNESS          # Z4
BODY_TOP_Z = BODY_BOTTOM_Z + BODY_H      # Z34
BALL_TIP_Z = -4.0
PLUNGER_TOP_Z = 54.0                     # MEASURED Jul 27
PLUNGER_DIA = 6.0

DECK_UNDERSIDE_Z = 58.0                  # MEASURED-driven correction (was Z42)
DECK_THICKNESS = 4.0
DECK_TOP_Z = DECK_UNDERSIDE_Z + DECK_THICKNESS   # Z62
WALL_TOP_Z = 60.0
WALL_BOTTOM_Z = PLATE_THICKNESS - GROOVE_DEPTH_PLATE   # Z2
FLARE_BOTTOM_Z = BODY_TOP_Z + 2.0        # Z36

BOARD_W, BOARD_D, BOARD_T = 120.0, 66.0, 1.6
TILT_DEG = 4.0

CSV_PATH = "/sessions/dazzling-eloquent-cori/mnt/Physical AI Agent/Full_84Key_Hole_Coordinates.csv"

# ---------------------------------------------------------------------------
# PALETTE
# ---------------------------------------------------------------------------
C_BG_TOP = (16, 18, 22)
C_BG_BOT = (7, 8, 10)
C_PLA = (176, 186, 198)          # printed PLA parts
C_PLA_DECK = (196, 204, 214)
C_WALL_HL = (232, 168, 76)       # the "removable wall" when highlighted
C_SOL_BODY = (58, 63, 70)
C_PLUNGER = (188, 196, 204)
C_SPRING = (128, 136, 146)
C_PCB = (18, 96, 58)
C_CHIP = (26, 26, 30)
C_TERM = (34, 106, 196)
C_CAP = (30, 52, 108)
C_WIRE = (150, 158, 170)
C_BUS = (198, 118, 44)
C_KBD = (30, 33, 38)
C_CAP_KEY = (62, 66, 74)

LIGHT = np.array([-0.42, -0.55, 0.72])
LIGHT /= np.linalg.norm(LIGHT)
FILL = np.array([0.6, 0.25, 0.35])
FILL /= np.linalg.norm(FILL)


# ---------------------------------------------------------------------------
# MESH BUILDING
# ---------------------------------------------------------------------------
class Mesh:
    def __init__(self):
        self.v = []      # vertex list
        self.f = []      # (i0,i1,i2, colorindex, groupid)
        self.colors = []

    def add_color(self, rgb):
        self.colors.append(np.array(rgb, dtype=np.float64))
        return len(self.colors) - 1

    def _vi(self, p):
        self.v.append(p)
        return len(self.v) - 1

    def box(self, x0, y0, z0, x1, y1, z1, ci, gid=0):
        pts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
               (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        base = len(self.v)
        for p in pts:
            self.v.append(p)
        quads = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4),
                 (2, 3, 7, 6), (1, 2, 6, 5), (3, 0, 4, 7)]
        for a, b, c, d in quads:
            self.f.append((base + a, base + b, base + c, ci, gid))
            self.f.append((base + a, base + c, base + d, ci, gid))

    def cyl(self, cx, cy, z0, z1, r, ci, gid=0, seg=8):
        base = len(self.v)
        for k in range(seg):
            a = 2 * math.pi * k / seg
            self.v.append((cx + r * math.cos(a), cy + r * math.sin(a), z0))
        for k in range(seg):
            a = 2 * math.pi * k / seg
            self.v.append((cx + r * math.cos(a), cy + r * math.sin(a), z1))
        for k in range(seg):
            n = (k + 1) % seg
            self.f.append((base + k, base + n, base + seg + n, ci, gid))
            self.f.append((base + k, base + seg + n, base + seg + k, ci, gid))
        ct = len(self.v)
        self.v.append((cx, cy, z1))
        for k in range(seg):
            n = (k + 1) % seg
            self.f.append((base + seg + k, base + seg + n, ct, ci, gid))

    def tube(self, p0, p1, r, ci, gid=0, seg=4):
        """Thin prism between two 3D points - used for wires."""
        p0 = np.array(p0, float)
        p1 = np.array(p1, float)
        d = p1 - p0
        L = np.linalg.norm(d)
        if L < 1e-9:
            return
        d /= L
        tmp = np.array([0, 0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0, 0])
        u = np.cross(d, tmp)
        u /= np.linalg.norm(u)
        w = np.cross(d, u)
        base = len(self.v)
        for end in (p0, p1):
            for k in range(seg):
                a = 2 * math.pi * k / seg
                self.v.append(tuple(end + r * (math.cos(a) * u + math.sin(a) * w)))
        for k in range(seg):
            n = (k + 1) % seg
            self.f.append((base + k, base + n, base + seg + n, ci, gid))
            self.f.append((base + k, base + seg + n, base + seg + k, ci, gid))


def load_keys():
    rows = {}
    with open(CSV_PATH, newline="") as fh:
        for r in csv.DictReader(fh):
            y = float(r["y_mm"])
            rows.setdefault(round(y, 2), []).append(
                (float(r["x_mm"]), r["key"], float(r["seam_x_for_row"])))
    return dict(sorted(rows.items()))


# group ids for animation
G_STATIC = 0     # keyboard, plate, side rails
G_DECK = 1       # deck + boards (lifts as one)
G_ROW0 = 10      # G_ROW0 + i = wall i + its solenoid row + its 12V bus + leads
                 # (each row is ONE serviceable module - that is the whole
                 #  argument for the groove-sandwich rebuild)


def build(keys, hi_row_y):
    m = Mesh()
    ci_pla = m.add_color(C_PLA)
    ci_deck = m.add_color(C_PLA_DECK)
    ci_hi = m.add_color(C_WALL_HL)
    ci_body = m.add_color(C_SOL_BODY)
    ci_plg = m.add_color(C_PLUNGER)
    ci_spr = m.add_color(C_SPRING)
    ci_pcb = m.add_color(C_PCB)
    ci_chip = m.add_color(C_CHIP)
    ci_term = m.add_color(C_TERM)
    ci_cap = m.add_color(C_CAP)
    ci_wire = m.add_color(C_WIRE)
    ci_bus = m.add_color(C_BUS)
    ci_kbd = m.add_color(C_KBD)
    ci_key = m.add_color(C_CAP_KEY)

    all_x = [x for v in keys.values() for x, _, _ in v]
    xmin, xmax = min(all_x), max(all_x)
    ys = sorted(keys.keys())
    y_front, y_back = ys[0], ys[-1]

    plate_x0, plate_x1 = xmin - 14.0, xmax + 14.0
    plate_y0, plate_y1 = y_front - 17.0, y_back + 27.0

    # ---- keyboard underneath (grounds the shot) --------------------------
    m.box(plate_x0 + 2, plate_y0 + 3, -26.0, plate_x1 - 2, plate_y1 - 12, -10.0,
          ci_kbd, G_STATIC)
    for y, lst in keys.items():
        for x, name, _ in lst:
            w = 17.0
            m.box(x - w / 2, y - w / 2, -10.0, x + w / 2, y + w / 2, -6.0,
                  ci_key, G_STATIC)

    # ---- plate, built as per-row bands so the L/R seam is visible --------
    seam_edges = []
    bounds = [plate_y0]
    for i in range(len(ys) - 1):
        bounds.append((ys[i] + ys[i + 1]) / 2.0)
    bounds.append(plate_y1)
    for i, y in enumerate(ys):
        seam = keys[y][0][2]
        by0, by1 = bounds[i], bounds[i + 1]
        m.box(plate_x0, by0, 0.0, seam - 0.4, by1, PLATE_THICKNESS,
              ci_pla, G_STATIC)
        m.box(seam + 0.4, by0, 0.0, plate_x1, by1, PLATE_THICKNESS,
              ci_pla, G_STATIC)
        seam_edges.append(seam)

    # side rails (tilt is baked into the real ones; simplified here)
    m.box(plate_x0 - 6, plate_y0, -34.0, plate_x0, plate_y1, 0.0, ci_pla, G_STATIC)
    m.box(plate_x1, plate_y0, -34.0, plate_x1 + 6, plate_y1, 0.0, ci_pla, G_STATIC)

    # ---- walls + solenoids ----------------------------------------------
    for y, lst in keys.items():
        gid = G_ROW0 + ys.index(y)
        ci_w = ci_hi if abs(y - hi_row_y) < 0.01 else ci_pla
        datum = y + WALL_OFFSET
        flare_back = y + PITCH_Y - SPRING_OD / 2.0 - SPRING_CLEARANCE
        rx = sorted(x for x, _, _ in lst)
        wx0, wx1 = rx[0] - 9.0, rx[-1] + 9.0
        seam = lst[0][2]
        # wall is split L/R exactly like the plate
        for a, b in ((wx0, seam - 0.4), (seam + 0.4, wx1)):
            if b - a < 2:
                continue
            m.box(a, datum, WALL_BOTTOM_Z, b, datum + WALL_THICKNESS,
                  FLARE_BOTTOM_Z, ci_w, gid)                     # thin section
            m.box(a, datum, FLARE_BOTTOM_Z, b, flare_back, WALL_TOP_Z,
                  ci_w, gid)                                     # flare
            # insert bosses, 3 per wall half, in the next row's spring gaps
            for t in (0.18, 0.5, 0.82):
                bx = a + (b - a) * t
                m.box(bx - 3.5, datum, FLARE_BOTTOM_Z, bx + 3.5,
                      datum + 10.0, DECK_UNDERSIDE_Z, ci_w, gid)

        for x, name, _ in lst:
            m.box(x - BODY_W / 2, y - BODY_D / 2, BODY_BOTTOM_Z,
                  x + BODY_W / 2, y + BODY_D / 2, BODY_TOP_Z, ci_body, gid)
            m.cyl(x, y, BALL_TIP_Z, PLUNGER_TOP_Z, PLUNGER_DIA / 2,
                  ci_plg, gid, seg=8)
            m.cyl(x, y, BODY_TOP_Z, BODY_TOP_Z + 14.0, SPRING_OD / 2,
                  ci_spr, gid, seg=8)

    # ---- deck ------------------------------------------------------------
    deck_x0, deck_x1 = plate_x0 - 22.0, plate_x0 - 22.0 + 3 * BOARD_W + 8
    deck_y0, deck_y1 = plate_y0 + 2, plate_y1
    # deck as y-bands so the per-row wire slots are real gaps
    # slots sit in FRONT of each row, where the leads actually exit the body,
    # so every wire is a straight vertical run (brief 07: chamfered slot per row)
    slot_w = 6.0
    slots = [(y - 12.5, y - 12.5 + slot_w) for y in ys]
    cuts = [deck_y0]
    for s0, s1 in slots:
        if deck_y0 < s0 < deck_y1:
            cuts += [s0, s1]
    cuts.append(deck_y1)
    for i in range(0, len(cuts) - 1, 2):
        a, b = cuts[i], cuts[i + 1]
        if b - a > 0.5:
            m.box(deck_x0, a, DECK_UNDERSIDE_Z, deck_x1, b, DECK_TOP_Z,
                  ci_deck, G_DECK)

    # ---- 3 driver PCBs on the deck --------------------------------------
    bz0 = DECK_TOP_Z + 6.0        # M3 standoffs under the boards
    bz1 = bz0 + BOARD_T
    board_y0 = (deck_y0 + deck_y1) / 2 - BOARD_D / 2
    for bi in range(3):
        bx0 = deck_x0 + 4 + bi * BOARD_W
        m.box(bx0, board_y0, bz0, bx0 + BOARD_W, board_y0 + BOARD_D, bz1,
              ci_pcb, G_DECK)
        # 4 corner standoffs at board-relative (4,4)(4,62)(116,4)(116,62)
        for ox, oy in ((4, 4), (4, 62), (116, 4), (116, 62)):
            m.cyl(bx0 + ox, board_y0 + oy, DECK_TOP_Z, bz0, 2.5,
                  ci_deck, G_DECK, seg=6)
        # 4 cells: 595 + ULN pair on a centre spine
        for c in range(4):
            cx = bx0 + 14 + c * 25.5
            m.box(cx, board_y0 + 24, bz1, cx + 8, board_y0 + 44, bz1 + 4.5,
                  ci_chip, G_DECK)
            m.box(cx + 10, board_y0 + 22, bz1, cx + 18, board_y0 + 46,
                  bz1 + 4.5, ci_chip, G_DECK)
        # 16 screw terminals, 8 per long edge, mouths outboard
        for c in range(8):
            tx = bx0 + 16 + c * 10.16
            m.box(tx, board_y0 + 2.5, bz1, tx + 9.8, board_y0 + 13.0,
                  bz1 + 9.5, ci_term, G_DECK)
            m.box(tx, board_y0 + BOARD_D - 13.0, bz1, tx + 9.8,
                  board_y0 + BOARD_D - 2.5, bz1 + 9.5, ci_term, G_DECK)
        # CB1 4700uF, O17 x 25 - the tallest part on the board
        m.cyl(bx0 + BOARD_W - 12, board_y0 + BOARD_D / 2, bz1, bz1 + 25.0,
              8.5, ci_cap, G_DECK, seg=10)

    # ---- +12V bus along each wall top, and the 84 wires straight up ------
    for y, lst in keys.items():
        datum = y + WALL_OFFSET
        rx = sorted(x for x, _, _ in lst)
        m.tube((rx[0] - 8, datum + 4.0, FLARE_BOTTOM_Z + 1.5),
               (rx[-1] + 8, datum + 4.0, FLARE_BOTTOM_Z + 1.5),
               1.2, ci_bus, G_ROW0 + ys.index(y))

    # Wires belong to their SOLENOID's group, so an exploded wall carries its
    # own leads - that is the point of the rebuild (straight up, not sideways).
    for y, lst in keys.items():
        gid = G_ROW0 + ys.index(y)
        sy = y - 12.5 + slot_w / 2
        for x, name, _ in lst:
            m.tube((x, sy, BODY_BOTTOM_Z + 4.0),
                   (x, sy, DECK_UNDERSIDE_Z - 1.0), 1.15, ci_wire, gid)

    v = np.array(m.v, dtype=np.float64)
    f = np.array(m.f, dtype=np.int64)
    cols = np.array(m.colors, dtype=np.float64)

    # global 4 deg keyboard tilt about X
    t = math.radians(TILT_DEG)
    R = np.array([[1, 0, 0],
                  [0, math.cos(t), -math.sin(t)],
                  [0, math.sin(t), math.cos(t)]])
    v = v @ R.T

    centre = np.array([(plate_x0 + plate_x1) / 2 - 12,
                       (plate_y0 + plate_y1) / 2,
                       18.0])
    v -= centre
    return v, f, cols


# ---------------------------------------------------------------------------
# RASTERIZER
# ---------------------------------------------------------------------------
def render(v, f, cols, W, H, az, el, dist, fov=30.0, ss=2):
    """Z-buffered flat-shaded rasterizer.

    Camera space after M: x = right, y = depth (into screen), z = up.
    """
    w, h = W * ss, H * ss
    # NOTE the sign on elevation: the camera sits at cam-space (0, -dist, 0),
    # so a POSITIVE el must map to -e here to put the camera ABOVE the scene.
    a, e = math.radians(az), math.radians(-el)
    Rz = np.array([[math.cos(a), math.sin(a), 0.0],
                   [-math.sin(a), math.cos(a), 0.0],
                   [0.0, 0.0, 1.0]])
    Rx = np.array([[1.0, 0.0, 0.0],
                   [0.0, math.cos(e), math.sin(e)],
                   [0.0, -math.sin(e), math.cos(e)]])
    M = Rx @ Rz
    cam = v @ M.T
    depth = cam[:, 1] + dist
    fl = (h / 2.0) / math.tan(math.radians(fov) / 2.0)
    safe = np.maximum(depth, 1.0)
    sx = w / 2.0 + fl * cam[:, 0] / safe
    sy = h / 2.0 - fl * cam[:, 2] / safe
    # keep the assembly centred in frame as it explodes (a tracking camera)
    sx += w / 2.0 - (sx.min() + sx.max()) / 2.0
    sy += h / 2.0 - (sy.min() + sy.max()) / 2.0

    zbuf = np.full((h, w), 1e18, dtype=np.float32)
    img = np.empty((h, w, 3), dtype=np.float32)
    g = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    for k in range(3):
        img[:, :, k] = C_BG_TOP[k] + (C_BG_BOT[k] - C_BG_TOP[k]) * g

    i0, i1, i2 = f[:, 0], f[:, 1], f[:, 2]
    ax, ay = sx[i0], sy[i0]
    bx, by = sx[i1], sy[i1]
    cx, cy = sx[i2], sy[i2]
    area = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)

    # normals in CAMERA space; camera sits at y = -dist looking toward +y,
    # so a face is visible when its normal has a negative y component.
    n = np.cross(v[i1] - v[i0], v[i2] - v[i0])
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1.0
    n = (n / ln[:, None]) @ M.T
    valid = (n[:, 1] < 0) & (abs(area) > 1e-9) & \
            (depth[i0] > 1) & (depth[i1] > 1) & (depth[i2] > 1)

    Lc = np.array([-0.45, -0.62, 0.64])       # left / toward camera / above
    Lc /= np.linalg.norm(Lc)
    Fc = np.array([0.70, -0.30, 0.30])        # warm fill from the right
    Fc /= np.linalg.norm(Fc)
    shade = (0.26 + 0.66 * np.clip(n @ Lc, 0, 1)
             + 0.24 * np.clip(n @ Fc, 0, 1))
    face_rgb = (cols[f[:, 3]] * shade[:, None]).astype(np.float32)

    zc = (depth[i0] + depth[i1] + depth[i2]) / 3.0
    order = np.argsort(-zc)
    for t in order:
        if not valid[t]:
            continue
        tx0 = max(int(min(ax[t], bx[t], cx[t])), 0)
        tx1 = min(int(max(ax[t], bx[t], cx[t])) + 2, w)
        ty0 = max(int(min(ay[t], by[t], cy[t])), 0)
        ty1 = min(int(max(ay[t], by[t], cy[t])) + 2, h)
        if tx1 <= tx0 or ty1 <= ty0:
            continue
        X, Y = np.meshgrid(np.arange(tx0, tx1) + 0.5,
                           np.arange(ty0, ty1) + 0.5)
        ar = area[t]
        # wC = weight of vertex i2, wA = weight of i0, wB = weight of i1
        wC = ((bx[t] - ax[t]) * (Y - ay[t]) - (by[t] - ay[t]) * (X - ax[t])) / ar
        wA = ((cx[t] - bx[t]) * (Y - by[t]) - (cy[t] - by[t]) * (X - bx[t])) / ar
        wB = 1.0 - wA - wC
        inside = (wA >= 0) & (wB >= 0) & (wC >= 0)
        if not inside.any():
            continue
        z = wA * depth[i0[t]] + wB * depth[i1[t]] + wC * depth[i2[t]]
        sub = zbuf[ty0:ty1, tx0:tx1]
        hit = inside & (z < sub)
        if not hit.any():
            continue
        sub[hit] = z[hit].astype(np.float32)
        img[ty0:ty1, tx0:tx1][hit] = face_rgb[t]

    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    if ss != 1:
        im = im.resize((W, H), Image.LANCZOS)
    return im


# ---------------------------------------------------------------------------
# ANIMATION
# ---------------------------------------------------------------------------
def ease(t):
    return t * t * (3 - 2 * t)


def seg(fr, a, b):
    if fr <= a:
        return 0.0
    if fr >= b:
        return 1.0
    return ease((fr - a) / (b - a))


DECK_LIFT = 150.0
ROW_LIFT = 26.0          # per row index - a staircase, so no row hides another
ROW_FAN = 2.40           # y-splay factor so all six wall modules read separately
AZ_MIN, AZ_MAX = -50.0, 46.0


def make_state(v, groups, deck_t, row_t, y_mid):
    """deck_t / row_t in 0..1 - the two explode axes."""
    vv = v.copy()
    vv[groups["deck"], 2] += DECK_LIFT * deck_t
    for i, vid in enumerate(groups["rows"]):
        vv[vid, 2] += ROW_LIFT * i * row_t
        vv[vid, 1] = y_mid + (vv[vid, 1] - y_mid) * (1.0 + (ROW_FAN - 1.0) * row_t)
    return vv


def fit_exact(vv, az, el, W, H, fov=30.0, margin=0.93):
    """Camera distance that makes THIS state fill `margin` of the frame.

    Called per frame, so the apparent size stays constant while the assembly
    explodes - which reads as a natural dolly-out rather than a size pop.
    """
    a, e = math.radians(az), math.radians(-el)
    Rz = np.array([[math.cos(a), math.sin(a), 0],
                   [-math.sin(a), math.cos(a), 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, math.cos(e), math.sin(e)],
                   [0, -math.sin(e), math.cos(e)]])
    cam = vv @ (Rx @ Rz).T
    ty = math.tan(math.radians(fov) / 2.0)
    tx = ty * W / H
    best = 0.0
    for comp, tt in ((0, tx), (2, ty)):
        ctr = (cam[:, comp].min() + cam[:, comp].max()) / 2.0
        best = max(best, float(np.max(
            np.abs(cam[:, comp] - ctr) / (tt * margin) - cam[:, 1])))
    return best


def fit_distance(states, W, H, fov=30.0, margin=0.93):
    best = 0.0
    for vv in states:
        for az in np.arange(AZ_MIN, AZ_MAX + 1, 8.0):
            for el in (17.0, 27.0):
                a, e = math.radians(az), math.radians(-el)
                Rz = np.array([[math.cos(a), math.sin(a), 0],
                               [-math.sin(a), math.cos(a), 0], [0, 0, 1]])
                Rx = np.array([[1, 0, 0],
                               [0, math.cos(e), math.sin(e)],
                               [0, -math.sin(e), math.cos(e)]])
                cam = vv @ (Rx @ Rz).T
                ty = math.tan(math.radians(fov) / 2.0)
                tx = ty * W / H
                for comp, tt in ((0, tx), (2, ty)):
                    ctr = (cam[:, comp].min() + cam[:, comp].max()) / 2.0
                    best = max(best, float(np.max(
                        np.abs(cam[:, comp] - ctr) / (tt * margin) - cam[:, 1])))
    return best


_JOB = {}


def _init_job():
    if _JOB:
        return _JOB
    keys = load_keys()
    ys = sorted(keys.keys())
    v, f, cols = build(keys, ys[3])
    _JOB.update(
        v=v, f=f, cols=cols,
        deck=np.unique(f[f[:, 4] == G_DECK][:, :3]),
        rows=[np.unique(f[f[:, 4] == G_ROW0 + i][:, :3]) for i in range(len(ys))],
        y_mid=float((v[:, 1].min() + v[:, 1].max()) / 2.0),
    )
    return _JOB


def _frame(args):
    i, N, W, H, outdir = args
    j = _init_job()
    path = "%s/f%04d.png" % (outdir, i)
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        return i
    fr = i / N
    deck_t = seg(fr, 0.10, 0.30) - seg(fr, 0.80, 0.97)
    row_t = seg(fr, 0.32, 0.52) - seg(fr, 0.66, 0.83)
    groups = {"deck": j["deck"], "rows": j["rows"]}
    vv = make_state(j["v"], groups, deck_t, row_t, j["y_mid"])
    s = 0.5 - 0.5 * math.cos(2 * math.pi * fr)
    az = AZ_MIN + (AZ_MAX - AZ_MIN) * s
    el = 19.0 + 6.0 * s
    d = fit_exact(vv, az, el, W, H)
    render(vv, j["f"], j["cols"], W, H, az, el, d).save(path)
    return i


def render_range(start, end, N=320, W=1080, H=1920, outdir="frames"):
    import multiprocessing as mp
    os.makedirs(outdir, exist_ok=True)
    jobs = [(i, N, W, H, outdir) for i in range(start, min(end, N))]
    with mp.Pool(4) as pool:
        for i in pool.imap_unordered(_frame, jobs):
            pass
    print("rendered", start, "-", min(end, N), flush=True)


def encode(outdir="frames", FPS=30):
    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i",
                    "%s/f%%04d.png" % outdir, "-c:v", "libx264", "-pix_fmt",
                    "yuv420p", "-crf", "16", "-movflags", "+faststart",
                    "new_plate_broll_vertical.mp4"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["ffmpeg", "-y", "-i", "new_plate_broll_vertical.mp4",
                    "-vf", "fps=20,scale=540:-1:flags=lanczos,split[a][b];"
                    "[a]palettegen[p];[b][p]paletteuse",
                    "new_plate_broll.gif"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    j = _init_job()
    groups = {"deck": j["deck"], "rows": j["rows"]}
    ex = make_state(j["v"], groups, 1, 1, j["y_mid"])
    asm = make_state(j["v"], groups, 0, 0, j["y_mid"])
    render(ex, j["f"], j["cols"], 1080, 1920, -34, 24,
           fit_exact(ex, -34, 24, 1080, 1920)).save(
        "new_plate_exploded_still.png")
    render(asm, j["f"], j["cols"], 1080, 1920, -40, 20,
           fit_exact(asm, -40, 20, 1080, 1920)).save(
        "new_plate_assembled_still.png")
    render(ex, j["f"], j["cols"], 1920, 1080, -34, 26,
           fit_exact(ex, -34, 26, 1920, 1080)).save(
        "new_plate_exploded_wide.png")
    print("encoded")


def main():
    keys = load_keys()
    ys = sorted(keys.keys())
    hi_row = ys[3]                      # an interior row - the whole point
    v, f, cols = build(keys, hi_row)

    groups = {
        "deck": np.unique(f[f[:, 4] == G_DECK][:, :3]),
        "rows": [np.unique(f[f[:, 4] == G_ROW0 + i][:, :3])
                 for i in range(len(ys))],
    }
    y_mid = float((v[:, 1].min() + v[:, 1].max()) / 2.0)

    W, H = 1080, 1920
    FPS, N = 30, 320

    outdir = "frames"
    os.makedirs(outdir, exist_ok=True)

    for i in range(N):
        path = "%s/f%04d.png" % (outdir, i)
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            continue                      # resumable
        fr = i / N
        # out and back, so the clip loops seamlessly
        deck_t = seg(fr, 0.10, 0.30) - seg(fr, 0.80, 0.97)
        row_t = seg(fr, 0.32, 0.52) - seg(fr, 0.66, 0.83)
        vv = make_state(v, groups, deck_t, row_t, y_mid)

        s = 0.5 - 0.5 * math.cos(2 * math.pi * fr)      # 0 -> 1 -> 0
        az = AZ_MIN + (AZ_MAX - AZ_MIN) * s
        el = 19.0 + 6.0 * s
        dist = fit_exact(vv, az, el, W, H)
        render(vv, f, cols, W, H, az, el, dist).save(
            "%s/f%04d.png" % (outdir, i))
        if i % 20 == 0:
            print("frame", i, flush=True)

    subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i",
                    "%s/f%%04d.png" % outdir, "-c:v", "libx264", "-pix_fmt",
                    "yuv420p", "-crf", "16", "-movflags", "+faststart",
                    "new_plate_broll_vertical.mp4"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["ffmpeg", "-y", "-i", "new_plate_broll_vertical.mp4",
                    "-vf", "fps=20,scale=540:-1:flags=lanczos,split[a][b];"
                    "[a]palettegen[p];[b][p]paletteuse",
                    "new_plate_broll.gif"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # hero stills
    vv = make_state(v, groups, 1, 1, y_mid)
    render(vv, f, cols, W, H, -34, 24,
           fit_exact(vv, -34, 24, W, H)).save("new_plate_exploded_still.png")
    va = make_state(v, groups, 0, 0, y_mid)
    render(va, f, cols, W, H, -40, 20,
           fit_exact(va, -40, 20, W, H)).save("new_plate_assembled_still.png")
    # landscape variant for YouTube / X
    render(vv, f, cols, 1920, 1080, -34, 26,
           fit_exact(vv, -34, 26, 1920, 1080)).save(
        "new_plate_exploded_wide.png")
    print("done")


if __name__ == "__main__":
    import sys as _s
    if len(_s.argv) == 3:                 # render_new_plate.py START END
        render_range(int(_s.argv[1]), int(_s.argv[2]))
    elif len(_s.argv) == 2 and _s.argv[1] == "encode":
        encode()
    else:
        main()

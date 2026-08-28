"""Verify the coupon script's geometry.

Checks arithmetic invariants, the Jul 27 measurements, CSV key positions, and
cross-checks against the as-built 84-key plate STL.

Run from anywhere:  python3 cad/verify_coupon_geometry.py
"""
import csv
import importlib.util
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "coupon", os.path.join(REPO, "cad", "fusion_groove_coupon.py"))
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
assert not C._IN_FUSION, "should not have found adsk outside Fusion"

fails, warns = [], []


def chk(cond, msg):
    print(("  OK   " if cond else "  FAIL ") + msg)
    if not cond:
        fails.append(msg)


def warn(cond, msg):
    if not cond:
        warns.append(msg)
        print("  WARN " + msg)


def head(n, t):
    print("\n" + "=" * 74 + "\n%s. %s\n" % (n, t) + "=" * 74)


head(1, "JUL 27 MEASUREMENTS  (Daniel, calipers, mounted solenoid)")
# Readings were taken from the PLATE TOP face = Z minus plate thickness
chk(abs((C.BODY_TOP_Z - C.PLATE_THICKNESS) - 30.0) < 1e-9,
    "reading A = 30mm above the plate top -> body_top_z = Z%.0f"
    % C.BODY_TOP_Z)
chk(abs((C.PLUNGER_TOP_Z - C.PLATE_THICKNESS) - 50.0) < 1e-9,
    "reading B = 50mm above the plate top -> plunger_top_z = Z%.0f"
    % C.PLUNGER_TOP_Z)
chk(abs(C.BALL_TIP_Z - (-4.0)) < 1e-9,
    "ball tip at Z%.0f, fixed 15mm below the lower tab hole" % C.BALL_TIP_Z)
chk(abs((C.PLUNGER_TOP_Z - C.BALL_TIP_Z) - 58.0) < 1e-9,
    "back-solved plunger length = 58.0mm, matching the recorded spec "
    "(two independent paths agree)")
d = C.TAB_HOLE_Z_LOWER - C.BODY_BOTTOM_Z
chk(abs(d - 7.0) < 1e-9,
    "d (body bottom -> lower tab hole) = %.1fmm" % d)
chk(abs(C.BODY_BOTTOM_Z - C.PLATE_THICKNESS) < 1e-9,
    "body bottom at Z%.0f = plate top; the old 'flush with the plate bottom' "
    "note is WRONG" % C.BODY_BOTTOM_Z)

head(2, "DECK HEIGHT  (driven by the PLUNGER, not the body)")
chk(C.DECK_UNDERSIDE_Z > C.PLUNGER_TOP_Z,
    "deck underside Z%.0f clears the plunger top Z%.0f by %.1fmm"
    % (C.DECK_UNDERSIDE_Z, C.PLUNGER_TOP_Z, C.DECK_PLUNGER_CLEARANCE))
brief08_deck = C.BODY_TOP_Z + 8.0
chk(brief08_deck < C.PLUNGER_TOP_Z,
    "brief 08's rule (body_top + 8 = Z%.0f) sits %.0fmm BELOW the plunger "
    "top -> collision confirmed, brief 08 superseded"
    % (brief08_deck, C.PLUNGER_TOP_Z - brief08_deck))
chk(C.WALL_TOP_Z - C.DECK_UNDERSIDE_Z == C.GROOVE_DEPTH_DECK,
    "wall top engages exactly %.1fmm into the deck groove"
    % C.GROOVE_DEPTH_DECK)
standoff = C.DECK_UNDERSIDE_Z - C.PLATE_THICKNESS
chk(abs(standoff - C.STANDOFF_COLUMN) < 1e-9,
    "standoff BODY length = %.0fmm (plate top Z%.0f -> deck underside Z%.0f)"
    % (standoff, C.PLATE_THICKNESS, C.DECK_UNDERSIDE_Z))
# Aug 2: the column is stacked from an assortment kit, F-F 20 + M-F 20 + M-F 20.
# Starting with the F-F puts a FEMALE end at both ends of the column, so both
# joints are plain screws and the Jul 27 stud-vs-nut-pocket problem disappears.
chk(abs(C.STANDOFF_COLUMN - 3 * 20.0) < 1e-9,
    "column = 3 x 20mm kit pieces (F-F + M-F + M-F), female at BOTH ends -> "
    "no nut pocket in the plate")
chk(C.DECK_UNDERSIDE_Z - C.PLUNGER_TOP_Z >= C.DECK_PLUNGER_CLEARANCE,
    "plunger clearance %.0fmm >= the %.0fmm minimum (now a check, since the "
    "deck height is set by a purchased part)"
    % (C.DECK_UNDERSIDE_Z - C.PLUNGER_TOP_Z, C.DECK_PLUNGER_CLEARANCE))
wall_h = C.WALL_TOP_Z - (C.PLATE_THICKNESS - C.GROOVE_DEPTH_PLATE)
print("  NOTE wall is %.0fmm tall overall; %.0fmm of that is above the upper "
      "tab screw" % (wall_h, C.WALL_TOP_Z - C.TAB_HOLE_Z_UPPER))

head(3, "DATUM RULE  (mounting face = hole_y + 8 EXACTLY, at every height)")
for r in C.GEO:
    n = r["name"]
    chk(abs(r["datum_y"] - (r["hole_y"] + 8.0)) < 1e-12,
        "%s mounting face = hole_y + 8.000  (y=%.3f)" % (n, r["datum_y"]))
    chk(abs(r["groove_front_y"] - r["datum_y"]) < 1e-12,
        "%s PLATE groove front == datum face (no clearance on the datum)" % n)
    chk(abs(r["deck_groove_front_y"] - r["datum_y"]) < 1e-12,
        "%s DECK groove front == datum face too" % n)
    chk(r["flare_back_y"] > r["datum_y"],
        "%s flare grows BACKWARD only (%.2fmm thick)"
        % (n, r["flare_thickness"]))
    chk(abs((r["groove_back_y"] - r["wall_back_y"]) - C.GROOVE_CLEARANCE)
        < 1e-12,
        "%s plate-groove slip = %.2fmm, on the back face"
        % (n, C.GROOVE_CLEARANCE))
    chk(abs((r["deck_groove_back_y"] - r["flare_back_y"])
            - C.GROOVE_CLEARANCE) < 1e-12,
        "%s deck-groove slip = %.2fmm, on the back face"
        % (n, C.GROOVE_CLEARANCE))

head(4, "STEPPED WALL  (thin in the slot, flared above the bodies)")
chk(C.FLARE_BOTTOM_Z > C.BODY_TOP_Z,
    "flare starts at Z%.0f, %.0fmm above the body tops"
    % (C.FLARE_BOTTOM_Z, C.FLARE_BOTTOM_Z - C.BODY_TOP_Z))
front, back = C.GEO[0], C.GEO[1]
chk(abs(front["wall_back_y"] - front["datum_y"] - 2.50) < 1e-12,
    "thin section is 2.50mm - fits the 16.55mm inter-body slot")
gap = back["body_front_y"] - front["wall_back_y"]
chk(abs(gap - 0.55) < 1e-9,
    "thin section -> next body float = %.2fmm (2x2-validated)" % gap)
spring_front = back["hole_y"] - C.SPRING_OD / 2.0
clr = spring_front - front["flare_back_y"]
chk(abs(clr - C.SPRING_CLEARANCE) < 1e-9,
    "flare back y=%.2f clears the next row's spring (front y=%.2f) by %.2fmm"
    % (front["flare_back_y"], spring_front, clr))
chk(front["flare_thickness"] > C.WALL_THICKNESS,
    "flare %.2fmm vs thin %.2fmm -> %.1fx the section thickness"
    % (front["flare_thickness"], C.WALL_THICKNESS,
       front["flare_thickness"] / C.WALL_THICKNESS))
warn(front["flare_thickness"] >= 4.0,
     "flare is only %.2fmm; if the measured spring OD exceeds %.0fmm the "
     "flare shrinks further" % (front["flare_thickness"], C.SPRING_OD))

head(5, "INSERT BOSS  (must sit in the gap between the next row's springs)")
chk(C.BOSS_TOP_Z == C.DECK_UNDERSIDE_Z,
    "boss top Z%.0f == deck underside -> bears on the flat slab, NO pocket"
    % C.BOSS_TOP_Z)
deck_over_screw = C.DECK_TOP_Z - C.BOSS_TOP_Z
chk(abs(deck_over_screw - C.DECK_THICKNESS) < 1e-9,
    "full %.1fmm of deck above the screw head (brief 08 left 2.0mm)"
    % deck_over_screw)
m3x8_bite = 8.0 - deck_over_screw
chk(0 < m3x8_bite < C.INSERT_HOLE_DEPTH,
    "M3x8: %.1fmm through the deck + %.1fmm into a %.0fmm insert = %.1fmm "
    "thread margin" % (deck_over_screw, m3x8_bite, C.INSERT_HOLE_DEPTH,
                       C.INSERT_HOLE_DEPTH - m3x8_bite))
chk(C.BOSS_TOP_Z - C.INSERT_HOLE_DEPTH >= C.FLARE_BOTTOM_Z,
    "insert hole (%.0fmm) fits inside the boss height (%.0fmm)"
    % (C.INSERT_HOLE_DEPTH, C.BOSS_TOP_Z - C.FLARE_BOTTOM_Z))
for r in C.GEO:
    fw = (r["insert_center_y"] - C.INSERT_HOLE_DIA / 2.0) - r["datum_y"]
    bw = r["boss_back_y"] - (r["insert_center_y"] + C.INSERT_HOLE_DIA / 2.0)
    chk(fw >= 2.5 and bw >= 2.5,
        "%s insert has %.1fmm front / %.1fmm back of boss material"
        % (r["name"], fw, bw))
chk((C.BOSS_SIZE_X - C.INSERT_HOLE_DIA) / 2.0 >= 1.4,
    "insert has %.1fmm either side in X"
    % ((C.BOSS_SIZE_X - C.INSERT_HOLE_DIA) / 2.0))
b0 = C.BOSS_CENTER_X - C.BOSS_SIZE_X / 2.0
b1 = C.BOSS_CENTER_X + C.BOSS_SIZE_X / 2.0
gapw = C.PITCH_X - C.SPRING_OD
chk(C.BOSS_SIZE_X < gapw,
    "boss %.1fmm wide fits the %.2fmm spring gap" % (C.BOSS_SIZE_X, gapw))
for r in C.GEO:
    if r["next_keys_x"] is None:
        print("  NOTE %s has no row behind it in the coupon - boss X "
              "unconstrained there" % r["name"])
        continue
    for kx in r["next_keys_x"]:
        s0, s1 = kx - C.SPRING_OD / 2.0, kx + C.SPRING_OD / 2.0
        sep = max(s0 - b1, b0 - s1)
        chk(sep > 0,
            "%s boss x[%.2f,%.2f] clears the spring at x=%.2f by %.2fmm"
            % (r["name"], b0, b1, kx, sep))
chk(C.FLARE_BOTTOM_Z > C.BODY_TOP_Z,
    "flare and boss both start above Z%.0f, so no body collision is possible"
    % C.BODY_TOP_Z)

head(6, "TAB HOLES + COUNTERBORE  (as-built numbers)")
chk(C.TAB_HOLE_Z_LOWER == 11.0 and C.TAB_HOLE_Z_UPPER == 26.0,
    "tab holes at Z11 / Z26 absolute")
chk(C.TAB_HOLE_Z_UPPER - C.TAB_HOLE_Z_LOWER == 15.0,
    "spacing 15.0 c-t-c (rigid pair on the solenoid)")
chk(C.TAB_HOLE_DIA == 3.30, "tab hole O3.30 (M3 clearance)")
chk(abs((C.WALL_THICKNESS - C.COUNTERBORE_FLOOR_FROM_DATUM) - 1.5) < 1e-12,
    "counterbore 1.5mm deep from the back face")
for r in C.GEO:
    chk(abs(r["counterbore_floor_y"] - (r["datum_y"] + 1.0)) < 1e-12,
        "%s counterbore floor = 1.0mm from the mounting face" % r["name"])
chk(C.TAB_HOLE_Z_UPPER < C.FLARE_BOTTOM_Z,
    "both tab holes (Z%.0f max) sit in the THIN section, below the flare at "
    "Z%.0f - counterbore geometry unaffected"
    % (C.TAB_HOLE_Z_UPPER, C.FLARE_BOTTOM_Z))

head(7, "PLATE / GROOVE / EXTENTS")
chk(C.PLATE_THICKNESS - C.GROOVE_DEPTH_PLATE == 2.0,
    "plate groove leaves a 2.0mm floor (open question: grow the plate "
    "DOWNWARD to 6mm for a 4mm floor)")
chk(C.WALL_BOTTOM_CHAMFER == 0.5, "wall bottom chamfer 0.5 lead-in")
chk(abs(2 * C.GROOVE_END_CLEARANCE - 0.30) < 1e-9,
    "groove length = wall length + 0.30 (ends register the wall in X)")
minx = min(kx - C.BODY_WIDTH_X / 2 for r in C.GEO for kx in r["keys_x"])
maxx = max(kx + C.BODY_WIDTH_X / 2 for r in C.GEO for kx in r["keys_x"])
chk(C.PLATE_X_MIN <= minx and maxx <= C.PLATE_X_MAX,
    "plate X %.1f..%.1f contains all bodies (%.2f..%.2f)"
    % (C.PLATE_X_MIN, C.PLATE_X_MAX, minx, maxx))
miny = min(r["body_front_y"] for r in C.GEO)
maxy = max(max(r["body_back_y"], r["boss_back_y"]) for r in C.GEO)
chk(C.PLATE_Y_MIN <= miny and maxy <= C.PLATE_Y_MAX,
    "plate Y %.1f..%.1f contains all bodies + bosses (%.2f..%.2f)"
    % (C.PLATE_Y_MIN, C.PLATE_Y_MAX, miny, maxy))
for r in C.GEO:
    for kx in r["keys_x"]:
        chk(C.WALL_X_MIN < kx < C.WALL_X_MAX,
            "%s wall spans key x=%.2f" % (r["name"], kx))
        chk(kx - C.PLUNGER_HOLE_DIA / 2 > C.PLATE_X_MIN and
            kx + C.PLUNGER_HOLE_DIA / 2 < C.PLATE_X_MAX,
            "%s O10 hole at x=%.2f fully inside the plate" % (r["name"], kx))

head(8, "KEY POSITIONS vs Full_84Key_Hole_Coordinates.csv")
rows = list(csv.DictReader(
    open(os.path.join(REPO, "Full_84Key_Hole_Coordinates.csv"))))
byname = {r["key"]: (float(r["x_mm"]), float(r["y_mm"])) for r in rows}
for k, (ex, ey) in {"S": (0.0, 0.0), "D": (19.05, 0.0),
                    "W": (-4.76, 19.05), "E": (14.29, 19.05)}.items():
    ax, ay = byname[k]
    chk(abs(ax - ex) < 1e-9 and abs(ay - ey) < 1e-9,
        "key %s CSV (%.2f, %.2f) == coupon (%.2f, %.2f)" % (k, ax, ay, ex, ey))
chk(abs((byname["W"][0] - byname["S"][0]) + C.STAGGER) < 1e-9,
    "coupon reproduces the real %.2fmm row stagger (back row LEFT)"
    % C.STAGGER)
chk(abs(byname["D"][0] - byname["S"][0] - C.PITCH_X) < 1e-9,
    "coupon reproduces the %.2fmm key pitch" % C.PITCH_X)

head(9, "CROSS-CHECK vs AS-BUILT  Air75_84Key_Plate_Left.stl")
try:
    import numpy as np
    import trimesh
    m = trimesh.load(os.path.join(REPO, "Air75_84Key_Plate_Left.stl"))
    lo, hi = m.bounds
    print("  STL bounds  x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f"
          % (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    chk(abs(hi[2] - 32.0) < 0.05,
        "as-built wall top = Z%.2f (coupon grows this to Z%.0f for the deck)"
        % (hi[2], C.WALL_TOP_Z))
    chk(hi[2] < C.BODY_TOP_Z,
        "as-built walls (Z%.0f) stop %.0fmm BELOW the body tops (Z%.0f) - "
        "consistent with reading A" % (hi[2], C.BODY_TOP_Z - hi[2],
                                       C.BODY_TOP_Z))

    n, tri = m.face_normals, m.triangles
    ymask = np.abs(np.abs(n[:, 1]) - 1.0) < 1e-4
    zc = tri[:, :, 2].mean(axis=1)
    band = ymask & (zc > 6) & (zc < 30)
    tot = {}
    for y, a in zip(np.round(tri[band][:, :, 1].mean(axis=1), 3),
                    m.area_faces[band]):
        tot[y] = tot.get(y, 0.0) + a
    big = sorted([y for y, a in tot.items() if a > 50.0])
    print("  wall-band planar Y faces (area>50mm2): %s"
          % ", ".join("%.3f" % y for y in big))
    for ry in sorted({float(r["y_mm"]) for r in rows if r["half"] == "L"}):
        datum = ry + C.WALL_OFFSET
        chk(any(abs(y - datum) < 0.02 for y in big),
            "as-built wall face at hole_y+8 = %.2f (row y=%.2f)"
            % (datum, ry))
        chk(any(abs(y - (datum + C.WALL_THICKNESS)) < 0.02 for y in big),
            "as-built back face at %.2f -> thickness %.2f"
            % (datum + C.WALL_THICKNESS, C.WALL_THICKNESS))
        chk(any(abs(y - (datum + C.COUNTERBORE_FLOOR_FROM_DATUM)) < 0.02
                for y in big),
            "as-built COUNTERBORE FLOOR at %.2f = datum + %.1f"
            % (datum + C.COUNTERBORE_FLOOR_FROM_DATUM,
               C.COUNTERBORE_FLOOR_FROM_DATUM))
    for target in (C.TAB_HOLE_Z_LOWER, C.TAB_HOLE_Z_UPPER):
        cnt = int((np.abs(m.vertices[:, 2] - target) < 1.70).sum())
        chk(cnt > 100,
            "as-built has a tab-hole ring at Z%.0f (%d verts)"
            % (target, cnt))
    chk(abs(lo[2] - (-33.50)) < 0.05,
        "as-built Z min = %.2f = the back leg contact, not the plate bottom"
        % lo[2])
    zmask = np.abs(np.abs(n[:, 2]) - 1.0) < 1e-4
    zf = {}
    for zz, a in zip(np.round(tri[zmask][:, :, 2].mean(axis=1), 3),
                     m.area_faces[zmask]):
        zf[zz] = zf.get(zz, 0.0) + a
    plate_z = sorted([z for z, a in zf.items() if a > 500.0])
    chk(any(abs(z - 0.0) < 0.02 for z in plate_z) and
        any(abs(z - C.PLATE_THICKNESS) < 0.02 for z in plate_z),
        "as-built plate slab spans Z0..Z%.0f (large flat faces at %s)"
        % (C.PLATE_THICKNESS, ", ".join("%.2f" % z for z in plate_z[:4])))
except ImportError:
    print("  SKIP trimesh/numpy not installed "
          "(pip install trimesh numpy --break-system-packages)")
    warns.append("STL cross-check skipped")

head(10, "PART SIZES + HARDWARE  (slicer and order)")
g = C.GEO[0]
print("  Coupon_Plate  %.1f x %.1f x %.1f mm"
      % (C.PLATE_X_MAX - C.PLATE_X_MIN, C.PLATE_Y_MAX - C.PLATE_Y_MIN,
         C.PLATE_THICKNESS))
print("  Wall (each)   %.1f long x %.0f tall; %.2f thin / %.2f flared"
      % (C.WALL_X_MAX - C.WALL_X_MIN, wall_h, C.WALL_THICKNESS,
         g["flare_thickness"]))
print("  Coupon_Deck   %.1f x %.1f x %.1f mm"
      % (C.PLATE_X_MAX - C.PLATE_X_MIN, C.PLATE_Y_MAX - C.PLATE_Y_MIN,
         C.DECK_THICKNESS))
print("  plate groove %.2f wide x %.1f deep | deck groove %.2f wide x %.1f deep"
      % (g["groove_back_y"] - g["groove_front_y"], C.GROOVE_DEPTH_PLATE,
         g["deck_groove_back_y"] - g["deck_groove_front_y"],
         C.GROOVE_DEPTH_DECK))
print("  hardware: 4x M3x3 flat head (tab screws) - already owned")
print("            2x M3 heat-set insert + 2x M3x8 pan head (deck)")
print("            2x solenoid - mount one per wall to test flare clearance")
print("  real build: M3 male-female standoffs, %.0fmm BODY length" % standoff)

print("\n" + "=" * 74)
print("RESULT: %d failure(s), %d warning(s)" % (len(fails), len(warns)))
for f in fails:
    print("  FAIL " + f)
for w in warns:
    print("  WARN " + w)
print("=" * 74)
sys.exit(1 if fails else 0)

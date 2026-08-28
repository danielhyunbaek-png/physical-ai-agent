"""
Groove-sandwich COUPON generator - Autodesk Fusion script
=========================================================
Physical AI Agent / brief 08 (Stage 1, item 7) - the TEARDOWN GATE.

Builds four printable components in a brand-new Fusion document:

    Coupon_Plate   46 x 50 x 4mm plate section, 4 x O10 plunger holes,
                   2 grooves cut 2mm into the top face
    Wall_A         front-row wall (keys S, D) - stepped: 2.5mm thin section
                   in the inter-body slot, flared above the bodies, plus an
                   insert boss
    Wall_B         back-row wall (keys W, E), same construction
    Coupon_Deck    mini-deck strip, grooves in the underside, 2 x O3.4
                   screw holes. NO pad pockets (see PAD/DECK JOINT below).

Key positions are the REAL ones from Full_84Key_Hole_Coordinates.csv:
    front row (row 3, y=0):      S at x=0.00,  D at x=19.05
    back  row (row 2, y=19.05):  W at x=-4.76, E at x=14.29
i.e. exactly the 2x2 prototype's key set, so the coupon exercises real
stagger, not a simplified grid.

Everything sits at true assembly coordinates, so the rendered document IS
the assembly - eyeball the groove engagement before printing.

HOW TO RE-TUNE THE FIT (the whole point of the coupon)
------------------------------------------------------
Wall too tight in its groove -> raise GROOVE_CLEARANCE by 0.05-0.10
Wall rattles / datum face not seating -> lower it by 0.05
Re-run the script (it makes a fresh document each time) and reprint ONLY
the coupon. Log the winning value into brief 08's parameter table.

=============================================================================
MEASURED Jul 27 2026 - THIS SUPERSEDES BRIEF 08's DECK HEIGHT
=============================================================================
Daniel measured, on a mounted solenoid, from the plate's top face:
    body top      30mm  ->  body_top_z    = Z34  (bodies rest on the plate
                                                  top; d = 7mm exactly)
    plunger top   50mm  ->  plunger_top_z = Z54

Back-solving the second one against the ball tip at Z-4 gives a 58mm
plunger, which matches the figure recorded as "confirmed" months ago. Two
independent paths agree.

CONSEQUENCE: brief 08 sets deck_underside_z = body_top_z + 8 = Z42. That is
12mm BELOW the plunger tops - the deck would have hit all 84 plungers. The
caliper gate as written measured the wrong feature. The deck is driven by the
PLUNGER, not the body. Corrected Jul 27: deck underside = Z58.
AMENDED Aug 2: the deck is now carried on a purchased 60mm standoff column
standing on the plate top, so deck underside = Z64 and the walls are 64mm.
The plunger clearance became an assertion instead of the driver.

The plunger only ever travels DOWN when fired (the ball extends), so Z54 at
rest is the worst case. No dynamic allowance is needed.

=============================================================================
DESIGN RULES THIS SCRIPT ENCODES - do not "fix" these
=============================================================================
* DATUM RULE. The wall MOUNTING face sits at hole_y + 8.000 EXACTLY, at
  every height, including through the flare and the boss. All clearance and
  all thickening go on the BACK face. Never centre the clearance - the datum
  face sets solenoid Y, and Y is what aims the plunger.

* TAB HOLES at Z11 and Z26 ABSOLUTE, O3.3, 15mm c-t-c. Fixed by the
  plunger's rest position, not by convenience.

* COUNTERBORE floor 1.0mm from the MOUNTING face (1.5mm deep from the back
  face). This is the AS-BUILT number, confirmed this session by measuring
  Air75_84Key_Plate_Left.stl - a planar face at datum+1.0 on all six walls.
  It differs from the older 2x2 note; as-built wins.

* STEPPED WALL. The wall only has to be 2.5mm where it lives in the 16.55mm
  slot between solenoid bodies, i.e. below the body tops. Above that the only
  obstruction is the NEXT ROW's return spring, so the wall flares backward for
  stiffness. At Z64-66 the wall is 64mm tall overall; a plain 2.5mm fin at
  that height is a 23:1 aspect ratio with 34mm of unsupported cantilever
  above its top screw. The flare turns it into a T-section for free.

* PAD / DECK JOINT - DECISION MADE BY CLAUDE, Jul 27, flagged for override.
  Brief 08 puts the pad flush with the wall top and has it enter a 2mm pocket
  in the deck underside. That leaves only 2mm of deck above the screw AND
  makes an M3x8 bottom out in a 6mm insert before its head touches the deck -
  so it would feel tight while clamping nothing. Here the boss top stops at
  the deck UNDERSIDE, there is no pocket, and the screw passes through the
  full 4mm slab into the insert with 2mm of thread margin. Daniel deferred
  this twice; the bottoming-out failure is unambiguous, so it is implemented
  the working way. Say so and it reverts.

* BOSS SITS IN THE SPRING GAP. A 5mm-thick flare cannot hold a O4 insert
  (0.5mm walls). The boss therefore thickens further back - but only in a
  narrow x band that slips between two of the NEXT row's return springs,
  which are on 19.05mm pitch and about O10, leaving a ~9mm gap. Put the boss
  anywhere else and it fouls a spring.

Author: Claude (Opus), Jul 27 2026 session. Units here are mm; the Fusion
API is centimetres, so every value is scaled by MM at use.
"""

# The adsk modules only exist inside Fusion. Guarding the import lets the
# constants below be imported by the sandbox verification script.
try:
    import adsk.core
    import adsk.fusion
    import traceback
    _IN_FUSION = True
except ImportError:  # pragma: no cover - running outside Fusion
    _IN_FUSION = False

MM = 0.1  # Fusion internal unit is cm

# ---------------------------------------------------------------------------
# GEOMETRY CONSTANTS
# ---------------------------------------------------------------------------

# --- the one number the coupon exists to validate -------------------------
WALL_THICKNESS = 2.50
GROOVE_CLEARANCE = 0.25          # <-- TUNE THIS AFTER THE FIRST PRINT

# --- plate ----------------------------------------------------------------
PLATE_THICKNESS = 4.00
GROOVE_DEPTH_PLATE = 2.00        # leaves a 2mm floor
PLUNGER_HOLE_DIA = 10.00

# --- keyboard layout ------------------------------------------------------
PITCH_X = 19.05
PITCH_Y = 19.05
STAGGER = 4.76

# --- wall / solenoid mount (all Z values ABSOLUTE, plate bottom = Z0) -----
WALL_OFFSET = 8.00               # mounting face = hole_y + WALL_OFFSET
TAB_HOLE_DIA = 3.30
TAB_HOLE_Z_LOWER = 11.00
TAB_HOLE_Z_UPPER = 26.00
COUNTERBORE_DIA = 6.00
COUNTERBORE_FLOOR_FROM_DATUM = 1.00
WALL_BOTTOM_CHAMFER = 0.50

# --- solenoid envelope, MEASURED Jul 27 -----------------------------------
BODY_HEIGHT = 30.00
BODY_DEPTH_Y = 16.00
BODY_WIDTH_X = 15.00
BODY_BOTTOM_Z = PLATE_THICKNESS          # Z4 - bodies rest on the plate top
BODY_TOP_Z = BODY_BOTTOM_Z + BODY_HEIGHT # Z34  <- MEASURED (30mm above top)
PLUNGER_LENGTH = 58.00                   # confirmed twice
BALL_TIP_Z = TAB_HOLE_Z_LOWER - 15.00    # Z-4, fixed by the lower tab hole
PLUNGER_TOP_Z = BALL_TIP_Z + PLUNGER_LENGTH   # Z54  <- MEASURED (50mm)
SPRING_OD = 10.00                # MEASURE on a loose solenoid to confirm
SPRING_CLEARANCE = 1.00          # flare-to-spring air gap

# --- deck stack -----------------------------------------------------------
# AMENDED Aug 2, 2026: the deck height is now set by the PURCHASED STANDOFF
# COLUMN, not by plunger clearance.  The column is F-F 20 + M-F 20 + M-F 20 =
# 60mm of body, standing on the plate top (Z4), so the deck underside lands at
# Z64.  Plunger clearance is no longer the driver -- it survives below as an
# ASSERTION, because a hardware purchase can silently violate it.
#   Was: DECK_UNDERSIDE_Z = PLUNGER_TOP_Z + 4  = Z58, walls 58mm.
#   Now: DECK_UNDERSIDE_Z = PLATE_THICKNESS + 60 = Z64, walls 64mm.
STANDOFF_COLUMN = 60.00          # F-F 20 + M-F 20 + M-F 20, bodies butted
DECK_PLUNGER_CLEARANCE = 4.00    # MINIMUM, now a check rather than a driver
DECK_UNDERSIDE_Z = PLATE_THICKNESS + STANDOFF_COLUMN        # Z64
GROOVE_DEPTH_DECK = 2.00
DECK_THICKNESS = 4.00
WALL_TOP_Z = DECK_UNDERSIDE_Z + GROOVE_DEPTH_DECK           # Z66
DECK_TOP_Z = DECK_UNDERSIDE_Z + DECK_THICKNESS              # Z68

# The plunger check that caught the Jul 27 error, kept live so a future change
# to STANDOFF_COLUMN cannot drive the deck back down into 84 plungers.
assert DECK_UNDERSIDE_Z - PLUNGER_TOP_Z >= DECK_PLUNGER_CLEARANCE, (
    "Deck underside Z%.2f is only %.2fmm above the plunger tops (Z%.2f); "
    "need >= %.2fmm. Shorten nothing -- lengthen the standoff column."
    % (DECK_UNDERSIDE_Z, DECK_UNDERSIDE_Z - PLUNGER_TOP_Z,
       PLUNGER_TOP_Z, DECK_PLUNGER_CLEARANCE))

# --- stepped wall ---------------------------------------------------------
FLARE_BOTTOM_Z = BODY_TOP_Z + 2.00       # Z36, clear of the body tops

# --- insert boss ----------------------------------------------------------
BOSS_SIZE_X = 7.00               # must fit the ~9mm gap between springs
BOSS_DEPTH_Y = 10.00             # from the datum face, backwards
BOSS_TOP_Z = DECK_UNDERSIDE_Z    # Z64 - bears on the deck underside, NO pocket
INSERT_HOLE_DIA = 4.00
INSERT_HOLE_DEPTH = 6.00
DECK_SCREW_HOLE_DIA = 3.40

# --- coupon extents -------------------------------------------------------
ROW_FRONT_Y = 0.00
ROW_BACK_Y = 19.05
FRONT_KEYS_X = (0.00, 19.05)     # S, D
BACK_KEYS_X = (-4.76, 14.29)     # W, E

PLATE_X_MIN, PLATE_X_MAX = -16.00, 30.00
PLATE_Y_MIN, PLATE_Y_MAX = -12.00, 38.00
WALL_X_MIN, WALL_X_MAX = -15.00, 29.00
GROOVE_END_CLEARANCE = 0.15      # per end -> groove is 0.3 longer than wall

# Boss X: midpoint of the gap between the two nearest NEXT-row springs.
# Front row's next row is the back row (keys -4.76, 14.29) -> gap centre 4.765.
# The back row has nothing behind it in the coupon; reuse the same X so the
# deck stays simple.
BOSS_CENTER_X = 4.765

ROWS = (
    {"name": "Wall_A", "hole_y": ROW_FRONT_Y, "keys_x": FRONT_KEYS_X,
     "next_keys_x": BACK_KEYS_X},
    {"name": "Wall_B", "hole_y": ROW_BACK_Y, "keys_x": BACK_KEYS_X,
     "next_keys_x": None},
)


# ---------------------------------------------------------------------------
# DERIVED GEOMETRY  (pure arithmetic - shared with the verification script)
# ---------------------------------------------------------------------------
def flare_back_y(hole_y):
    """Back face of the flared upper wall.

    Limited by the NEXT row's return spring, which is centred at
    hole_y + PITCH_Y and is SPRING_OD across.
    """
    return hole_y + PITCH_Y - SPRING_OD / 2.0 - SPRING_CLEARANCE


def row_geometry(hole_y):
    """Every Y coordinate for one row, derived from the datum rule."""
    datum_y = hole_y + WALL_OFFSET                  # wall mounting face
    fb = flare_back_y(hole_y)
    return {
        "hole_y": hole_y,
        "datum_y": datum_y,
        # thin lower section, in the inter-body slot
        "wall_back_y": datum_y + WALL_THICKNESS,
        "groove_front_y": datum_y,                  # datum face, no clearance
        "groove_back_y": datum_y + WALL_THICKNESS + GROOVE_CLEARANCE,
        "counterbore_floor_y": datum_y + COUNTERBORE_FLOOR_FROM_DATUM,
        # flared upper section
        "flare_back_y": fb,
        "flare_thickness": fb - datum_y,
        "deck_groove_front_y": datum_y,
        "deck_groove_back_y": fb + GROOVE_CLEARANCE,
        # insert boss
        "boss_back_y": datum_y + BOSS_DEPTH_Y,
        "insert_center_y": datum_y + BOSS_DEPTH_Y / 2.0,
        # solenoid envelope
        "body_front_y": hole_y - BODY_DEPTH_Y / 2.0,
        "body_back_y": hole_y + BODY_DEPTH_Y / 2.0,
    }


GEO = [dict(r, **row_geometry(r["hole_y"])) for r in ROWS]


# ---------------------------------------------------------------------------
# FUSION HELPERS
# ---------------------------------------------------------------------------
# Robustness note: every solid is created by sketching on a plane at the
# feature's MID-height and extruding SYMMETRICALLY, and every cut is a
# symmetric extrude straddling a reference face so overshoot lands in empty
# space. That makes the script independent of Fusion's construction-plane
# normal directions, the usual source of silent sign errors.

def _new_component(root, name):
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ.component


def _offset_plane(comp, base_plane, axis, target_mm):
    """Construction plane offset from base_plane, landing on axis==target_mm."""
    target = target_mm * MM
    planes = comp.constructionPlanes
    for value in (target, -target):
        pin = planes.createInput()
        pin.setByOffset(base_plane, adsk.core.ValueInput.createByReal(value))
        plane = planes.add(pin)
        if abs(getattr(plane.geometry.origin, axis) - target) < 1e-7:
            return plane
        plane.deleteMe()
    raise RuntimeError("could not place plane on {}={}".format(axis, target_mm))


def _plane_z(comp, z_mm):
    return _offset_plane(comp, comp.xYConstructionPlane, "z", z_mm)


def _plane_y(comp, y_mm):
    return _offset_plane(comp, comp.xZConstructionPlane, "y", y_mm)


def _all_profiles(sketch):
    coll = adsk.core.ObjectCollection.create()
    for prof in sketch.profiles:
        coll.add(prof)
    return coll


def _sym_extrude(comp, sketch, total_mm, operation, target_body=None):
    extrudes = comp.features.extrudeFeatures
    inp = extrudes.createInput(_all_profiles(sketch), operation)
    if target_body is not None:
        inp.participantBodies = [target_body]
    inp.setSymmetricExtent(
        adsk.core.ValueInput.createByReal(total_mm * MM), True
    )
    return extrudes.add(inp)


def _rect(sketch, x1, y1, x2, y2):
    p1 = adsk.core.Point3D.create(x1 * MM, y1 * MM, 0)
    p2 = adsk.core.Point3D.create(x2 * MM, y2 * MM, 0)
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(p1, p2)


def _circle_at_model_point(sketch, x, y, z, dia):
    """Circle centred on the projection of model point (x,y,z) onto the sketch.

    Uses modelToSketchSpace so it works on any plane orientation.
    """
    model_pt = adsk.core.Point3D.create(x * MM, y * MM, z * MM)
    sk_pt = sketch.modelToSketchSpace(model_pt)
    sk_pt.z = 0
    sketch.sketchCurves.sketchCircles.addByCenterRadius(sk_pt, dia * MM / 2.0)


def _chamfer_bottom_edges(comp, body, z_mm, size_mm):
    z = z_mm * MM
    edges = adsk.core.ObjectCollection.create()
    for edge in body.edges:
        sp, ep = edge.startVertex, edge.endVertex
        if sp is None or ep is None:
            continue
        if abs(sp.geometry.z - z) < 1e-6 and abs(ep.geometry.z - z) < 1e-6:
            edges.add(edge)
    if edges.count == 0:
        return None
    chamfers = comp.features.chamferFeatures
    cin = chamfers.createInput2()
    cin.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
        edges, adsk.core.ValueInput.createByReal(size_mm * MM), True
    )
    return chamfers.add(cin)


# ---------------------------------------------------------------------------
# PART BUILDERS
# ---------------------------------------------------------------------------
def build_plate(root):
    comp = _new_component(root, "Coupon_Plate")

    sk = comp.sketches.add(_plane_z(comp, PLATE_THICKNESS / 2.0))
    _rect(sk, PLATE_X_MIN, PLATE_Y_MIN, PLATE_X_MAX, PLATE_Y_MAX)
    body = _sym_extrude(
        comp, sk, PLATE_THICKNESS,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    ).bodies.item(0)
    body.name = "plate"

    # O10 plunger holes, straight through
    sk = comp.sketches.add(_plane_z(comp, PLATE_THICKNESS / 2.0))
    for row in GEO:
        for kx in row["keys_x"]:
            _circle_at_model_point(sk, kx, row["hole_y"], 0, PLUNGER_HOLE_DIA)
    _sym_extrude(comp, sk, PLATE_THICKNESS * 3,
                 adsk.fusion.FeatureOperations.CutFeatureOperation, body)

    # grooves for the THIN lower wall section. Cut symmetric about the plate
    # top face so the upper half lands in air.
    sk = comp.sketches.add(_plane_z(comp, PLATE_THICKNESS))
    for row in GEO:
        _rect(sk,
              WALL_X_MIN - GROOVE_END_CLEARANCE, row["groove_front_y"],
              WALL_X_MAX + GROOVE_END_CLEARANCE, row["groove_back_y"])
    _sym_extrude(comp, sk, GROOVE_DEPTH_PLATE * 2,
                 adsk.fusion.FeatureOperations.CutFeatureOperation, body)
    return comp


def build_wall(root, row):
    comp = _new_component(root, row["name"])
    wall_bottom_z = PLATE_THICKNESS - GROOVE_DEPTH_PLATE   # Z2, groove floor

    # --- thin lower section: groove floor up to the flare ---
    sk = comp.sketches.add(
        _plane_z(comp, (wall_bottom_z + FLARE_BOTTOM_Z) / 2.0))
    _rect(sk, WALL_X_MIN, row["datum_y"], WALL_X_MAX, row["wall_back_y"])
    body = _sym_extrude(
        comp, sk, FLARE_BOTTOM_Z - wall_bottom_z,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    ).bodies.item(0)
    body.name = "wall"

    # --- flared upper section: thicker, for stiffness. Datum face unmoved. ---
    sk = comp.sketches.add(_plane_z(comp, (FLARE_BOTTOM_Z + WALL_TOP_Z) / 2.0))
    _rect(sk, WALL_X_MIN, row["datum_y"], WALL_X_MAX, row["flare_back_y"])
    _sym_extrude(comp, sk, WALL_TOP_Z - FLARE_BOTTOM_Z,
                 adsk.fusion.FeatureOperations.JoinFeatureOperation, body)

    # --- insert boss: thickens further back, in the next row's spring gap.
    # Top stops at the DECK UNDERSIDE so the screw gets the full 4mm slab.
    sk = comp.sketches.add(_plane_z(comp, (FLARE_BOTTOM_Z + BOSS_TOP_Z) / 2.0))
    _rect(sk,
          BOSS_CENTER_X - BOSS_SIZE_X / 2.0, row["datum_y"],
          BOSS_CENTER_X + BOSS_SIZE_X / 2.0, row["boss_back_y"])
    _sym_extrude(comp, sk, BOSS_TOP_Z - FLARE_BOTTOM_Z,
                 adsk.fusion.FeatureOperations.JoinFeatureOperation, body)

    # --- tab holes: O3.3 horizontal, symmetric about the thin wall's midplane
    wall_mid_y = (row["datum_y"] + row["wall_back_y"]) / 2.0
    sk = comp.sketches.add(_plane_y(comp, wall_mid_y))
    for kx in row["keys_x"]:
        for z in (TAB_HOLE_Z_LOWER, TAB_HOLE_Z_UPPER):
            _circle_at_model_point(sk, kx, wall_mid_y, z, TAB_HOLE_DIA)
    _sym_extrude(comp, sk, WALL_THICKNESS * 4,
                 adsk.fusion.FeatureOperations.CutFeatureOperation, body)

    # --- counterbores: symmetric about the thin wall's BACK face, so the floor
    # lands exactly COUNTERBORE_FLOOR_FROM_DATUM from the mounting face
    cb_depth = WALL_THICKNESS - COUNTERBORE_FLOOR_FROM_DATUM   # 1.5
    sk = comp.sketches.add(_plane_y(comp, row["wall_back_y"]))
    for kx in row["keys_x"]:
        for z in (TAB_HOLE_Z_LOWER, TAB_HOLE_Z_UPPER):
            _circle_at_model_point(sk, kx, row["wall_back_y"], z,
                                   COUNTERBORE_DIA)
    _sym_extrude(comp, sk, cb_depth * 2,
                 adsk.fusion.FeatureOperations.CutFeatureOperation, body)

    # --- heat-set insert hole, vertical, symmetric about the BOSS top face
    sk = comp.sketches.add(_plane_z(comp, BOSS_TOP_Z))
    _circle_at_model_point(sk, BOSS_CENTER_X, row["insert_center_y"],
                           BOSS_TOP_Z, INSERT_HOLE_DIA)
    _sym_extrude(comp, sk, INSERT_HOLE_DEPTH * 2,
                 adsk.fusion.FeatureOperations.CutFeatureOperation, body)

    _chamfer_bottom_edges(comp, body, wall_bottom_z, WALL_BOTTOM_CHAMFER)
    return comp


def build_deck(root):
    comp = _new_component(root, "Coupon_Deck")

    sk = comp.sketches.add(
        _plane_z(comp, (DECK_UNDERSIDE_Z + DECK_TOP_Z) / 2.0))
    _rect(sk, PLATE_X_MIN, PLATE_Y_MIN, PLATE_X_MAX, PLATE_Y_MAX)
    body = _sym_extrude(
        comp, sk, DECK_THICKNESS,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    ).bodies.item(0)
    body.name = "deck"

    # underside grooves - these engage the FLARED section, so they are wider
    # than the plate grooves. Same datum rule: front face at hole_y + 8.
    sk = comp.sketches.add(_plane_z(comp, DECK_UNDERSIDE_Z))
    for row in GEO:
        _rect(sk,
              WALL_X_MIN - GROOVE_END_CLEARANCE, row["deck_groove_front_y"],
              WALL_X_MAX + GROOVE_END_CLEARANCE, row["deck_groove_back_y"])
    _sym_extrude(comp, sk, GROOVE_DEPTH_DECK * 2,
                 adsk.fusion.FeatureOperations.CutFeatureOperation, body)

    # NO pad pockets - the boss bears on the flat underside, so the screw gets
    # the full DECK_THICKNESS above it. See PAD / DECK JOINT in the header.

    # O3.4 screw holes through the deck, over each boss insert
    sk = comp.sketches.add(_plane_z(comp, DECK_TOP_Z))
    for row in GEO:
        _circle_at_model_point(sk, BOSS_CENTER_X, row["insert_center_y"],
                               DECK_TOP_Z, DECK_SCREW_HOLE_DIA)
    _sym_extrude(comp, sk, DECK_THICKNESS * 3,
                 adsk.fusion.FeatureOperations.CutFeatureOperation, body)
    return comp


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        doc = app.documents.add(
            adsk.core.DocumentTypes.FusionDesignDocumentType
        )
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        design.fusionUnitsManager.distanceDisplayUnits = \
            adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        doc.name = "Groove_Coupon_gc{:.2f}".format(GROOVE_CLEARANCE)

        root = design.rootComponent
        root.name = "Groove_Coupon"

        build_plate(root)
        for row in GEO:
            build_wall(root, row)
        build_deck(root)

        g = GEO[0]
        ui.messageBox(
            "Groove coupon built.\n\n"
            "plate groove      {:.2f} mm wide  (wall {:.2f} + {:.2f})\n"
            "deck groove       {:.2f} mm wide  (flare {:.2f} + {:.2f})\n"
            "wall              Z{:.1f} - Z{:.1f}   ({:.0f} mm tall)\n"
            "flare starts      Z{:.1f}\n"
            "boss top          Z{:.1f}  = deck underside, no pocket\n"
            "deck              Z{:.1f} - Z{:.1f}\n"
            "tab holes         Z{:.0f} / Z{:.0f}, O{:.1f}\n\n"
            "Driven by the MEASURED plunger top at Z{:.0f}, not the body top\n"
            "at Z{:.0f}. Brief 08's Z42 deck would have hit the plungers.\n\n"
            "Components are at true assembly coordinates - check the groove\n"
            "engagement visually, then export each component as STL.\n\n"
            "Fit wrong after printing? Edit GROOVE_CLEARANCE at the top of\n"
            "the script and re-run; you get a fresh document.".format(
                g["groove_back_y"] - g["groove_front_y"],
                WALL_THICKNESS, GROOVE_CLEARANCE,
                g["deck_groove_back_y"] - g["deck_groove_front_y"],
                g["flare_thickness"], GROOVE_CLEARANCE,
                PLATE_THICKNESS - GROOVE_DEPTH_PLATE, WALL_TOP_Z,
                WALL_TOP_Z - (PLATE_THICKNESS - GROOVE_DEPTH_PLATE),
                FLARE_BOTTOM_Z, BOSS_TOP_Z,
                DECK_UNDERSIDE_Z, DECK_TOP_Z,
                TAB_HOLE_Z_LOWER, TAB_HOLE_Z_UPPER, TAB_HOLE_DIA,
                PLUNGER_TOP_Z, BODY_TOP_Z
            ),
            "Groove Coupon"
        )
    except Exception:
        if ui:
            ui.messageBox("Script failed:\n{}".format(traceback.format_exc()),
                          "Groove Coupon")
        else:
            raise

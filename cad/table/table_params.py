# Overhead table — parameters (mm, desk frame: X right, Y back, Z up from desk)
import math, csv
T = math.radians(4.0)          # plate tilt (as-built, Jul 15 audit)
TOP_Z = 90.0                   # tabletop underside above desk
TOP_T = 5.0                    # tabletop thickness
GAP = 15.0                     # wiring layer (post height)
TX0, TX1, TY0, TY1 = -160.0, 282.0, -77.0, 97.0
SPLIT = 90.5
KEYS=[]
names=[]
_raw = """Esc F1 F2 F3 F4 F5 F6 F7 F8 F9 F10 F11 F12 PrtSc Cust1 Cust2
` 1 2 3 4 5 6 7 8 9 0 - = Bksp Home
Tab Q W E R T Y U I O P [ ] \\ PgUp
Caps A S D F G H J K L ; ' Enter PgDn
LShf Z X C V B N M , . / RShf Up End
LCtl LOpt LCmd Space RCmd Fn RCtl Left Down Right""".split('\n')
for row in _raw: names += row.split()
for r in csv.DictReader(open('keys.csv')): KEYS.append((float(r['x_mm']), float(r['y_mm'])))
assert len(names)==84==len(KEYS)
def plate_to_desk(y, z):
    """plate frame (y along plate, z along plate normal; plate bottom z=0; front leg contact y=-58.5,z=-23.9) -> (Y, H)"""
    Y = y*math.cos(T) - z*math.sin(T)
    H = (z+23.9)*math.cos(T) + (y+58.5)*math.sin(T)
    return Y, H
def z_at_height(y, H):
    return (H - (y+58.5)*math.sin(T))/math.cos(T) - 23.9
def lead_hole(kx, ky):
    # lead exits left face of body (x = kx-7.5) into the 4 mm gap; rises to the table
    zt = z_at_height(ky, TOP_Z)
    Y_perp,_ = plate_to_desk(ky, zt)       # if it follows the solenoid axis
    Y_exit,_ = plate_to_desk(ky, 20.0)     # if it goes truly vertical from the exit
    return kx-9.5, 0.5*(Y_perp+Y_exit)
HOLE_W, HOLE_L = 5.0, 10.0
# boards: 120 x 66, holes 4 in from corners (112 x 58), Ø3.2
BOARD_W, BOARD_D = 120.0, 66.0
BOARD_Y0 = -17.0
BOARDS = {'A': -96.5, 'B': 26.5, 'C': 150.5}
# strips (listing: 124.5 x 22 x 15); cradle interior with tolerance
STRIP_L, STRIP_W = 124.5, 22.0
POCKET_L, POCKET_W, LIP = 129.0, 23.0, 1.6
STRIPS = [(-56.0, -24.0, 0), (-56.0, 176.0, 0), (80.0, -29.0, -12), (80.0, 148.0, -12)]   # (Y centre, X centre, middle-rib x offset)
# Mega (101.6 x 53.34), long axis along Y, USB edge facing back
MEGA_X0, MEGA_YTOP = -155.0, 60.8
MEGA_HOLES_LOCAL = [(15.24,50.8),(66.04,7.62),(90.17,50.8),(96.52,2.54)]   # Arduino Mega hole pattern (mm from USB-edge/lower-left)
MEGA_POST_H = 5.0
PIN_D, PIN_H, POST_D = 2.9, 3.5, 6.5
# legs (separate prints) — 10x10, peg Ø6 into socket
LEG_S, PEG_D, PEG_H, SOCKET_D, SOCKET_H = 10.0, 6.0, 3.5, 6.4, 4.0
# (x, y) leg centres; near-seam legs dodge the base's seam screw blocks (x 88-93)
LEGS = [(-152,-72),(-40,-72),(78,-72),(101,-72),(190,-72),(274,-72),
        (-152,92),(-40,92),(74,92),(101,92),(190,92),(274,92)]
SEAM_BLOCK_X = (88.0, 93.0)

# stepped split: x=81 for Y>=STEP_Y (rows 0-1 + back strips), x=90.5 below (rows 2-5 + front strips)
SPLIT_BACK, SPLIT_FRONT, STEP_Y = 81.0, 90.5, 25.0
MEGA_TRAY_WALL, MEGA_PAD_H, MEGA_W, MEGA_L = 2.0, 4.0, 53.34, 101.6
TEXT_H, TEXT_DEPTH = 3.2, 0.6

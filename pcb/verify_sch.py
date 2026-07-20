#!/usr/bin/env python3
"""Full netlist verification of solenoid_driver.kicad_sch against brief 06/06a.

Rebuilds connectivity from geometry exactly like KiCad: pin connection points,
wire endpoints, coincident-point merging, labels naming nets, power symbols
naming nets via their Value. Mid-wire pin landings require a junction.
Exits nonzero on any failure.
"""
import math, re, sys
from collections import defaultdict

def parse_sexp(s):
    tokens = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', s)
    def walk(i):
        node = []
        while i < len(tokens):
            t = tokens[i]
            if t == '(':
                sub, i = walk(i+1); node.append(sub)
            elif t == ')':
                return node, i+1
            else:
                node.append(t[1:-1].replace('\\"', '"') if t.startswith('"') else t)
                i += 1
        return node, i
    return walk(0)[0]

def find_all(node, key):
    res = []
    if isinstance(node, list):
        if node and node[0] == key: res.append(node)
        for c in node: res += find_all(c, key)
    return res

def get(node, key):
    for c in node:
        if isinstance(c, list) and c and c[0] == key: return c
    return None

def props(sym):
    return {p[1]: p[2] for p in find_all(sym, 'property')}

fn = sys.argv[1] if len(sys.argv) > 1 else 'solenoid_driver.kicad_sch'
root = get(parse_sexp(open(fn).read()), 'kicad_sch')

# ---- lib pin geometry: libname -> {pinnum: (x, y)} (connection point, symbol coords)
libpins = {}
for sym in [c for c in (get(root, 'lib_symbols') or []) if isinstance(c, list) and c and c[0] == 'symbol']:
    pins = {}
    for p in find_all(sym, 'pin'):
        at = get(p, 'at'); num = get(p, 'number')
        pins[num[1]] = (float(at[1]), float(at[2]))
    libpins[sym[1]] = pins

# ---- placed items
def P(x, y): return (round(x, 3), round(y, 3))

pinpts = []   # (ref, pinnum, point)
powpts = []   # (netname, point)  from power symbols (Value = net)
refval = {}
for s in [c for c in root if isinstance(c, list) and c and c[0] == 'symbol']:
    lid = get(s, 'lib_id')[1]
    at = get(s, 'at')
    x, y, rot = float(at[1]), float(at[2]), float(at[3])
    pr = props(s)
    ref, val = pr['Reference'], pr['Value']
    refval[ref] = val
    th = math.radians(rot)
    for num, (px, py) in libpins[lid].items():
        rx = px*math.cos(th) - py*math.sin(th)
        ry = px*math.sin(th) + py*math.cos(th)
        pt = P(x + rx, y - ry)
        if lid.startswith('power:') and lid != 'power:PWR_FLAG':
            powpts.append((val, pt))
        pinpts.append((ref, num, pt))

wires = []
for w in find_all(root, 'wire'):
    pts = find_all(w, 'xy')
    wires.append((P(float(pts[0][1]), float(pts[0][2])), P(float(pts[1][1]), float(pts[1][2]))))

labels = [(l[1], P(float(get(l, 'at')[1]), float(get(l, 'at')[2]))) for l in find_all(root, 'label')]
junctions = {P(float(get(j, 'at')[1]), float(get(j, 'at')[2])) for j in find_all(root, 'junction')}

# ---- union-find over points
parent = {}
def find(a):
    parent.setdefault(a, a)
    while parent[a] != a:
        parent[a] = parent[parent[a]]; a = parent[a]
    return a
def union(a, b): parent[find(b)] = find(a)

def on_seg(pt, a, b):
    (x, y), (x1, y1), (x2, y2) = pt, a, b
    if abs((x2-x1)*(y-y1) - (y2-y1)*(x-x1)) > 1e-6: return False
    return min(x1, x2)-1e-6 <= x <= max(x1, x2)+1e-6 and min(y1, y2)-1e-6 <= y <= max(y1, y2)+1e-6

for a, b in wires:
    union(a, b)
# attach pins/labels: endpoint-coincident always; mid-wire only with junction
attach_pts = [pt for _, _, pt in pinpts] + [pt for _, pt in labels]
warn = []
for pt in attach_pts:
    for a, b in wires:
        if pt == a or pt == b:
            union(pt, a)
        elif on_seg(pt, a, b):
            if pt in junctions:
                union(pt, a)
            else:
                warn.append(f'mid-wire attach WITHOUT junction at {pt}')
# wire endpoint landing mid-other-wire needs junction too
for a, b in wires:
    for c, d in wires:
        if (a, b) == (c, d): continue
        for e in (a, b):
            if e not in (c, d) and on_seg(e, c, d) and e not in junctions:
                warn.append(f'wire-end on wire without junction at {e}')

# ---- net naming
netname = {}   # root -> set of names
for name, pt in labels + powpts:
    netname.setdefault(find(pt), set()).add(name)

def net_of(ref, pin):
    for r, n, pt in pinpts:
        if r == ref and n == str(pin):
            names = netname.get(find(pt), set())
            return frozenset(names), find(pt)
    raise KeyError((ref, pin))

fails = []
def expect(ref, pin, name):
    names, _ = net_of(ref, pin)
    if names != {name}:
        fails.append(f'{ref}.{pin}: expected net {{{name}}}, got {set(names) or "{unnamed}"}')

def expect_same(ref1, pin1, ref2, pin2):
    _, r1 = net_of(ref1, pin1)
    _, r2 = net_of(ref2, pin2)
    if r1 != r2:
        fails.append(f'{ref1}.{pin1} NOT connected to {ref2}.{pin2}')

def expect_isolated(ref1, pin1, ref2, pin2):
    _, r1 = net_of(ref1, pin1)
    _, r2 = net_of(ref2, pin2)
    if r1 == r2:
        fails.append(f'SHORT: {ref1}.{pin1} connected to {ref2}.{pin2}')

# ---- per-cell checks
Q595 = ['15', '1', '2', '3', '4', '5', '6', '7']          # QA..QH
OUT_ULN = ['18', '17', '16', '15', '14', '13', '12', '11']  # O1..O8
for n in range(1, 7):
    u1, u2 = f'U{n}1', f'U{n}2'
    for k in range(8):                                    # canonical Q->IN
        expect_same(u1, Q595[k], u2, str(k+1))
        if k: expect_isolated(u1, Q595[k], u1, Q595[k-1])  # adjacent isolation
    expect(u1, 16, '+5V'); expect(u1, 10, '+5V')
    expect(u1, 8, 'GND')
    expect(u1, 11, 'SCLK'); expect(u1, 12, 'RCLK'); expect(u1, 13, '~{OE}')
    expect(u1, 14, 'DATA_IN' if n == 1 else f'CASC{n-1}')
    expect(u1, 9, f'CASC{n}' if n < 6 else 'DATA_OUT')
    expect(u2, 9, 'GND'); expect(u2, 10, '+12V')          # COM flyback
    for k in range(8):                                    # O1..O8 -> J terminals
        expect_same(u2, OUT_ULN[k], f'J{n}{k//2+1}', str(k % 2 + 1))
        if k: expect_isolated(u2, OUT_ULN[k], u2, OUT_ULN[k-1])
    expect(f'C{n}1', 1, '+5V'); expect(f'C{n}1', 2, 'GND')

# ---- board-level
for j, dnet in (('J71', 'DATA_IN'), ('J72', 'DATA_OUT')):
    expect(j, 1, '+5V'); expect(j, 2, 'GND'); expect(j, 3, dnet)
    expect(j, 4, 'SCLK'); expect(j, 5, 'RCLK'); expect(j, 6, '~{OE}')
expect('J70', 1, '+12V'); expect('J70', 2, 'GND')
expect('R1', 1, '+5V'); expect('R1', 2, '~{OE}')
expect('CB1', 1, '+12V'); expect('CB1', 2, 'GND')          # pin1 = + (polarity!)
expect('CB2', 1, '+12V'); expect('CB2', 2, 'GND')
expect('CB3', 1, '+5V'); expect('CB3', 2, 'GND')

# ---- rail isolation (the +5/+12/GND meter-open test, on paper)
expect_isolated('U11', 16, 'U12', 10)   # +5V vs +12V
expect_isolated('U11', 16, 'U11', 8)    # +5V vs GND
expect_isolated('U12', 10, 'U12', 9)    # +12V vs GND

# ---- PWR_FLAG presence on the 3 rails (name-aware: power nets merge globally by name)
flag_names = set()
for r, n, pt in pinpts:
    if r.startswith('#FLG'):
        flag_names |= netname.get(find(pt), set())
for nm in ('+5V', '+12V', 'GND'):
    if nm not in flag_names:
        fails.append(f'no PWR_FLAG on {nm} net')

# ---- net name uniqueness (no accidental merges)
for rt, names in netname.items():
    if len(names) > 1:
        fails.append(f'net has conflicting names: {names}')

# ---- footprint sanity
fp_expect = {'U11': 'DIP-16', 'U12': 'DIP-18', 'J11': 'TB007-508', 'J70': 'TB007-508',
             'J71': 'PinHeader_1x06', 'R1': 'Axial', 'C11': 'C_Disc', 'CB1': 'CP_Radial', 'CB2': 'C_Disc'}
for s in [c for c in root if isinstance(c, list) and c and c[0] == 'symbol']:
    pr = props(s)
    if pr['Reference'] in fp_expect and fp_expect[pr['Reference']] not in pr.get('Footprint', ''):
        fails.append(f"{pr['Reference']}: footprint {pr.get('Footprint')!r} missing {fp_expect[pr['Reference']]!r}")

n_syms = len(refval)
print(f'{n_syms} symbols, {len(wires)} wires, {len(labels)} labels, {len(junctions)} junctions')
for w in sorted(set(warn)): print('WARN:', w)
if fails:
    print(f'\n{len(fails)} FAILURES:')
    for f in fails: print(' FAIL:', f)
    sys.exit(1)
print('\nALL CHECKS PASS — netlist matches brief 06/06a')

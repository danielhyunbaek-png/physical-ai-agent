#!/usr/bin/env python3
"""Generate solenoid_driver.kicad_sch — 6-cell 595+ULN driver per brief 06/06a.

Reuses lib_symbols defs (74HC595, ULN2803A, +5V, GND) from the existing file;
adds +12V (clone of +5V), PWR_FLAG, R, C, C_Polarized, Screw_Terminal_01x02,
Conn_01x06 hand-written in the same KiCad-10 grammar. All coords on 2.54 grid.
Footprints embedded per brief 06a so the assign step is already done.
"""
import re, uuid

BASE = 'base.kicad_sch'
OUT  = 'solenoid_driver.kicad_sch'
ROOT_UUID = '18b689b8-b344-482b-a80d-6c06a54d75f2'   # keep: instances path + pcb link

def u(): return str(uuid.uuid4())

# ---------- extract raw lib symbol defs from base ----------
base = open(BASE).read()
def extract(name):
    i = base.index(f'(symbol "{name}"')
    d = 0; j = i
    while True:
        c = base[j]
        if c == '(': d += 1
        elif c == ')':
            d -= 1
            if d == 0: break
        j += 1
    return base[i:j+1]

lib_595 = extract('74xx:74HC595')
lib_uln = extract('Transistor_Array:ULN2803A')
lib_5v  = extract('power:+5V')
lib_gnd = extract('power:GND')
lib_12v = lib_5v.replace('+5V', '+12V')

def mini_prop(name, val, hide=True, at='0 0 0'):
    h = '\n\t\t\t\t(hide yes)' if hide else ''
    return f'''\t\t\t(property "{name}" "{val}"
\t\t\t\t(at {at})
\t\t\t\t(show_name no)
\t\t\t\t(do_not_autoplace no){h}
\t\t\t\t(effects
\t\t\t\t\t(font
\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)'''

def lib_pin(ptype, x, y, rot, length, name, number):
    return f'''\t\t\t\t(pin {ptype} line
\t\t\t\t\t(at {x} {y} {rot})
\t\t\t\t\t(length {length})
\t\t\t\t\t(name "{name}"
\t\t\t\t\t\t(effects
\t\t\t\t\t\t\t(font
\t\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t\t)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t\t(number "{number}"
\t\t\t\t\t\t(effects
\t\t\t\t\t\t\t(font
\t\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t\t)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)'''

def rect(x1, y1, x2, y2):
    return f'''\t\t\t\t(rectangle
\t\t\t\t\t(start {x1} {y1})
\t\t\t\t\t(end {x2} {y2})
\t\t\t\t\t(stroke
\t\t\t\t\t\t(width 0.254)
\t\t\t\t\t\t(type default)
\t\t\t\t\t)
\t\t\t\t\t(fill
\t\t\t\t\t\t(type background)
\t\t\t\t\t)
\t\t\t\t)'''

def poly(pts):
    p = ' '.join(f'(xy {a} {b})' for a, b in pts)
    return f'''\t\t\t\t(polyline
\t\t\t\t\t(pts
\t\t\t\t\t\t{p}
\t\t\t\t\t)
\t\t\t\t\t(stroke
\t\t\t\t\t\t(width 0.254)
\t\t\t\t\t\t(type default)
\t\t\t\t\t)
\t\t\t\t\t(fill
\t\t\t\t\t\t(type none)
\t\t\t\t\t)
\t\t\t\t)'''

def libsym(name, ref, val, desc, graphics, pins, power=False, hide_pin_text=False):
    short = name.split(':')[1]
    pw = '\n\t\t\t(power global)' if power else ''
    hp = '''
\t\t\t(pin_numbers
\t\t\t\t(hide yes)
\t\t\t)
\t\t\t(pin_names
\t\t\t\t(offset 0)
\t\t\t\t(hide yes)
\t\t\t)''' if hide_pin_text else '''
\t\t\t(pin_names
\t\t\t\t(offset 1.016)
\t\t\t)'''
    g = '\n'.join(graphics)
    p = '\n'.join(pins)
    gblock = f'''\t\t\t(symbol "{short}_0_1"
{g}
\t\t\t)\n''' if graphics else ''
    return f'''\t\t(symbol "{name}"{pw}{hp}
\t\t\t(exclude_from_sim no)
\t\t\t(in_bom yes)
\t\t\t(on_board yes)
\t\t\t(in_pos_files yes)
\t\t\t(duplicate_pin_numbers_are_jumpers no)
{mini_prop("Reference", ref, hide=power, at='0 -3.81 0')}
{mini_prop("Value", val, hide=False, at='0 3.81 0')}
{mini_prop("Footprint", "")}
{mini_prop("Datasheet", "")}
{mini_prop("Description", desc)}
{gblock}\t\t\t(symbol "{short}_1_1"
{p}
\t\t\t)
\t\t\t(embedded_fonts no)
\t\t)'''

lib_flag = libsym('power:PWR_FLAG', '#FLG', 'PWR_FLAG', 'Special symbol for telling ERC where power comes from',
    [poly([(0, 0), (0, 1.27), (-1.016, 1.905), (0, 2.54), (1.016, 1.905), (0, 1.27)])],
    [lib_pin('power_out', 0, 0, 90, 0, '', '1')], power=True, hide_pin_text=True)

lib_r = libsym('Device:R', 'R', 'R', 'Resistor',
    [rect(-1.016, -2.54, 1.016, 2.54)],
    [lib_pin('passive', 0, 5.08, 270, 2.54, '~', '1'),
     lib_pin('passive', 0, -5.08, 90, 2.54, '~', '2')])

cap_plates = [poly([(-2.032, 0.762), (2.032, 0.762)]), poly([(-2.032, -0.762), (2.032, -0.762)])]
lib_c = libsym('Device:C', 'C', 'C', 'Unpolarized capacitor',
    cap_plates,
    [lib_pin('passive', 0, 5.08, 270, 4.318, '~', '1'),
     lib_pin('passive', 0, -5.08, 90, 4.318, '~', '2')])

lib_cp = libsym('Device:C_Polarized', 'C', 'C_Polarized', 'Polarized capacitor, pin 1 = +',
    cap_plates + [poly([(-3.302, 1.778), (-1.778, 1.778)]), poly([(-2.54, 1.016), (-2.54, 2.54)])],
    [lib_pin('passive', 0, 5.08, 270, 4.318, '+', '1'),
     lib_pin('passive', 0, -5.08, 90, 4.318, '-', '2')])

def circ(x, y, r):
    return f'''\t\t\t\t(circle
\t\t\t\t\t(center {x} {y})
\t\t\t\t\t(radius {r})
\t\t\t\t\t(stroke
\t\t\t\t\t\t(width 0.254)
\t\t\t\t\t\t(type default)
\t\t\t\t\t)
\t\t\t\t\t(fill
\t\t\t\t\t\t(type none)
\t\t\t\t\t)
\t\t\t\t)'''

lib_t2 = libsym('Connector:Screw_Terminal_01x02', 'J', 'Screw_Terminal_01x02', 'Screw terminal 2 pos',
    [rect(-1.27, 2.54, 2.54, -5.08), circ(0.635, 0, 0.635), circ(0.635, -2.54, 0.635)],
    [lib_pin('passive', -5.08, 0, 0, 3.81, 'Pin_1', '1'),
     lib_pin('passive', -5.08, -2.54, 0, 3.81, 'Pin_2', '2')])

lib_c6 = libsym('Connector_Generic:Conn_01x06', 'J', 'Conn_01x06', 'Generic 6-pin connector',
    [rect(-1.27, 2.54, 2.54, -15.24)] + [circ(0.635, -2.54*k, 0.635) for k in range(6)],
    [lib_pin('passive', -5.08, -2.54*k, 0, 3.81, f'Pin_{k+1}', str(k+1)) for k in range(6)])

# ---------- placed-item emitters ----------
body = []

def prop(name, val, x, y, hide=False):
    h = '\n\t\t\t(hide yes)' if hide else ''
    return f'''\t\t(property "{name}" "{val}"
\t\t\t(at {x} {y} 0){h}
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)'''

def sym(lib_id, ref, val, x, y, rot, npins, footprint='', hide_ref=False, hide_val=False):
    pins = '\n'.join(f'\t\t(pin "{k}"\n\t\t\t(uuid "{u()}")\n\t\t)' for k in range(1, npins+1))
    body.append(f'''\t(symbol
\t\t(lib_id "{lib_id}")
\t\t(at {x} {y} {rot})
\t\t(unit 1)
\t\t(body_style 1)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(dnp no)
\t\t(fields_autoplaced yes)
\t\t(uuid "{u()}")
{prop("Reference", ref, x, y-2.54, hide=hide_ref)}
{prop("Value", val, x, y+2.54, hide=hide_val)}
{prop("Footprint", footprint, x, y, hide=True)}
{prop("Datasheet", "", x, y, hide=True)}
{prop("Description", "", x, y, hide=True)}
{pins}
\t\t(instances
\t\t\t(project "solenoid_driver"
\t\t\t\t(path "/{ROOT_UUID}"
\t\t\t\t\t(reference "{ref}")
\t\t\t\t\t(unit 1)
\t\t\t\t)
\t\t\t)
\t\t)
\t)''')

def wire(x1, y1, x2, y2):
    body.append(f'''\t(wire
\t\t(pts
\t\t\t(xy {x1} {y1}) (xy {x2} {y2})
\t\t)
\t\t(stroke
\t\t\t(width 0)
\t\t\t(type default)
\t\t)
\t\t(uuid "{u()}")
\t)''')

def label(text, x, y):
    body.append(f'''\t(label "{text}"
\t\t(at {x} {y} 0)
\t\t(fields_autoplaced yes)
\t\t(effects
\t\t\t(font
\t\t\t\t(size 1.27 1.27)
\t\t\t)
\t\t\t(justify left bottom)
\t\t)
\t\t(uuid "{u()}")
\t)''')

def junction(x, y):
    body.append(f'''\t(junction
\t\t(at {x} {y})
\t\t(diameter 0)
\t\t(color 0 0 0 0)
\t\t(uuid "{u()}")
\t)''')

pwr_n = [0]; flg_n = [0]
def power(net, x, y, rot=0):
    pwr_n[0] += 1
    sym(f'power:{net}', f'#PWR0{pwr_n[0]:02d}', net, x, y, rot, 1, hide_ref=True)
def flag(x, y, rot=0):
    flg_n[0] += 1
    sym('power:PWR_FLAG', f'#FLG0{flg_n[0]:02d}', 'PWR_FLAG', x, y, rot, 1, hide_ref=True)

FP_DIP16 = 'Package_DIP:DIP-16_W7.62mm'
FP_DIP18 = 'Package_DIP:DIP-18_W7.62mm'
FP_TERM  = 'TerminalBlock_CUI:TerminalBlock_CUI_TB007-508-02_1x02_P5.08mm_Horizontal'
FP_HDR6  = 'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical'
FP_R     = 'Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal'
FP_C     = 'Capacitor_THT:C_Disc_D8.0mm_W5.0mm_P5.00mm'
FP_CP    = 'Capacitor_THT:CP_Radial_D18.0mm_P7.50mm'

# ---------- cells ----------
Q_OFFS = [10.16, 7.62, 5.08, 2.54, 0, -2.54, -5.08, -7.62]  # QA..QH abs y = sy-off

for n in range(1, 7):
    col, row = (n-1) % 3, (n-1)//3
    sx = 60.96 + 129.54*col
    sy = 81.28 + 119.38*row
    ux, uy = sx + 35.56, sy - 5.08
    sym('74xx:74HC595', f'U{n}1', '74HC595', sx, sy, 0, 16, FP_DIP16)
    sym('Transistor_Array:ULN2803A', f'U{n}2', 'ULN2803A', ux, uy, 0, 18, FP_DIP18)
    # Q -> IN (canonical, collinear horizontal wires)
    for off in Q_OFFS:
        wire(sx+10.16, sy-off, sx+25.4, sy-off)
    # 595 power + control
    power('+5V', sx, sy-15.24)                          # pin16 VCC
    power('GND', sx, sy+17.78)                          # pin8
    wire(sx-10.16, sy-2.54, sx-17.78, sy-2.54)          # pin10 ~SRCLR -> +5V
    power('+5V', sx-17.78, sy-2.54)
    wire(sx-10.16, sy-10.16, sx-25.4, sy-10.16)         # pin14 SER
    label('DATA_IN' if n == 1 else f'CASC{n-1}', sx-25.4, sy-10.16)
    wire(sx-10.16, sy-5.08, sx-25.4, sy-5.08)           # pin11 SRCLK
    label('SCLK', sx-25.4, sy-5.08)
    wire(sx-10.16, sy+2.54, sx-25.4, sy+2.54)           # pin12 RCLK
    label('RCLK', sx-25.4, sy+2.54)
    wire(sx-10.16, sy+5.08, sx-25.4, sy+5.08)           # pin13 ~OE
    label('~{OE}', sx-25.4, sy+5.08)
    wire(sx+10.16, sy+12.7, sx+17.78, sy+12.7)          # pin9 QH'
    label(f'CASC{n}' if n < 6 else 'DATA_OUT', sx+17.78, sy+12.7)
    # ULN power
    power('GND', ux, uy+17.78)                          # pin9
    power('+12V', ux+10.16, uy-7.62)                    # pin10 COM (flyback)
    # OUT wires + terminals: O1..O8 top->bottom, y = sy-10.16 + 2.54k
    for k in range(8):
        wire(ux+10.16, sy-10.16+2.54*k, sx+55.88, sy-10.16+2.54*k)
    for m in range(4):
        sym('Connector:Screw_Terminal_01x02', f'J{n}{m+1}', f'OUT{2*m+1}/{2*m+2}',
            sx+60.96, sy-10.16+5.08*m, 0, 2, FP_TERM)
    # decoupling cap
    cx, cy = sx-40.64, sy+2.54
    sym('Device:C', f'C{n}1', '100nF', cx, cy, 0, 2, FP_C)
    power('+5V', cx, cy-5.08)
    power('GND', cx, cy+5.08)

# ---------- board-level ----------
bx = 469.9
# J71 cascade IN at (bx, 60.96)
sym('Connector_Generic:Conn_01x06', 'J71', 'CASC-IN', bx, 60.96, 0, 6, FP_HDR6)
wire(bx-5.08, 60.96, 452.12, 60.96); power('+5V', 452.12, 60.96)
flag(457.2, 60.96); junction(457.2, 60.96)
wire(bx-5.08, 63.5, 441.96, 63.5); power('GND', 441.96, 63.5)
for k, name in ((2, 'DATA_IN'), (3, 'SCLK'), (4, 'RCLK'), (5, '~{OE}')):
    wire(bx-5.08, 60.96+2.54*k, 452.12, 60.96+2.54*k)
    label(name, 452.12, 60.96+2.54*k)
# J72 cascade OUT at (bx, 111.76)
sym('Connector_Generic:Conn_01x06', 'J72', 'CASC-OUT', bx, 111.76, 0, 6, FP_HDR6)
wire(bx-5.08, 111.76, 452.12, 111.76); power('+5V', 452.12, 111.76)
wire(bx-5.08, 114.3, 441.96, 114.3); power('GND', 441.96, 114.3)
for k, name in ((2, 'DATA_OUT'), (3, 'SCLK'), (4, 'RCLK'), (5, '~{OE}')):
    wire(bx-5.08, 111.76+2.54*k, 452.12, 111.76+2.54*k)
    label(name, 452.12, 111.76+2.54*k)
# J70 12V input at (bx, 160.02)
sym('Connector:Screw_Terminal_01x02', 'J70', '12V-IN', bx, 160.02, 0, 2, FP_TERM)
wire(bx-5.08, 160.02, 441.96, 160.02); power('+12V', 441.96, 160.02)
flag(449.58, 160.02); junction(449.58, 160.02)
wire(bx-5.08, 162.56, 452.12, 162.56); power('GND', 452.12, 162.56)
flag(457.2, 162.56, rot=180); junction(457.2, 162.56)
# R1 10k OE pullup at (419.1, 60.96)
sym('Device:R', 'R1', '10k', 419.1, 60.96, 0, 2, FP_R)
power('+5V', 419.1, 55.88)
wire(419.1, 66.04, 419.1, 68.58); wire(419.1, 68.58, 426.72, 68.58)
label('~{OE}', 426.72, 68.58)
# CB3 100nF on 5V near J71
sym('Device:C', 'CB3', '100nF', 434.34, 60.96, 0, 2, FP_C)
power('+5V', 434.34, 55.88); power('GND', 434.34, 66.04)
# CB1 4700uF + CB2 100nF on 12V near J70
sym('Device:C_Polarized', 'CB1', '4700uF 25V', 419.1, 160.02, 0, 2, FP_CP)
power('+12V', 419.1, 154.94); power('GND', 419.1, 165.1)
sym('Device:C', 'CB2', '100nF', 434.34, 160.02, 0, 2, FP_C)
power('+12V', 434.34, 154.94); power('GND', 434.34, 165.1)

# ---------- assemble ----------
libs = '\n'.join([lib_595, lib_uln, lib_5v, lib_12v, lib_gnd, lib_flag,
                  lib_r, lib_c, lib_cp, lib_t2, lib_c6])
out = f'''(kicad_sch
\t(version 20260306)
\t(generator "eeschema")
\t(generator_version "10.0")
\t(uuid "{ROOT_UUID}")
\t(paper "A2")
\t(title_block
\t\t(title "84-key solenoid driver — 6-cell 595+ULN board")
\t\t(date "2026-07-20")
\t\t(rev "A")
\t\t(comment 1 "Physical AI Agent — brief 06/06a. Board A = cells 1-6, Board B = same PCB, slot 6 empty.")
\t)
\t(lib_symbols
{libs}
\t)
{chr(10).join(body)}
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
\t(embedded_fonts no)
)
'''
open(OUT, 'w').write(out)
print('wrote', OUT, len(out), 'bytes;', len(body), 'items;',
      pwr_n[0], 'power syms;', flg_n[0], 'flags')

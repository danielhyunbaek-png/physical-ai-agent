# Finger-twist knob with PH1 Phillips tip, for M3x3 flat-heads in the 16.55 mm wall slot.
# Axis = Z. Knob z 0..KNOB_T, shaft, tip pointing +Z. Print knob flat (back face on bed), tip up.
import numpy as np, manifold3d as m3, trimesh
KNOB_T = 6.0
SHAFT_D, SHAFT_L = 4.5, 3.0          # enters the Ø6 x 1.5 counterbore
TIP_L, R_BASE, R_POINT, BLADE_T = 2.4, 1.65, 0.55, 0.85
CORE_BASE, CORE_POINT = 1.0, 0.35

def hull(pts): return m3.Manifold.hull_points([tuple(map(float,p)) for p in pts])
def rect_pts(hx, hy, z): return [(sx*hx, sy*hy, z) for sx in (-1,1) for sy in (-1,1)]

def knurl(d, ridges):
    ro, ri = d/2, d/2 - 0.8
    pts=[]
    for k in range(ridges*2):
        a = np.pi*k/ridges; r = ro if k%2==0 else ri
        pts.append((r*np.cos(a), r*np.sin(a)))
    return m3.Manifold.extrude(m3.CrossSection([pts]), KNOB_T)

def tool(d, scale, dots):
    knob = knurl(d, 16 if d<15 else 24)
    # ID dots on the back face (the face your fingertip pushes): 1/2/3 = 90/100/110 %
    for k in range(dots):
        x = (k-(dots-1)/2)*2.2
        knob = knob - m3.Manifold.cylinder(1.0, 0.6, 0.6, 16).translate((x, 0 if d<15 else -5, -0.01))
    # fingertip dimple on back face for the big knob
    if d >= 15:
        knob = knob - m3.Manifold.sphere(9, 48).translate((0,0,-8.2))
    z0 = KNOB_T + SHAFT_L; z1 = z0 + TIP_L
    shaft = m3.Manifold.cylinder(SHAFT_L+0.2, SHAFT_D/2, SHAFT_D/2, 48).translate((0,0,KNOB_T-0.1))
    s=scale; t=BLADE_T*s/2
    b1 = hull(rect_pts(R_BASE*s,t,z0)+rect_pts(R_POINT*s,t,z1))
    b2 = hull(rect_pts(t,R_BASE*s,z0)+rect_pts(t,R_POINT*s,z1))
    core = m3.Manifold.cylinder(TIP_L, CORE_BASE*s, CORE_POINT*s, 32).translate((0,0,z0))
    return knob + shaft + b1 + b2 + core

def save(man, fn):
    mesh = man.to_mesh(); tm = trimesh.Trimesh(mesh.vert_properties[:,:3], mesh.tri_verts); tm.export(fn); return tm

plate=None
for row,d in enumerate((12.0, 20.0)):
    for i,(s,n) in enumerate(((0.90,1),(1.00,2),(1.10,3))):
        t = tool(d,s,n); tm = save(t, f"Knob_D{int(d)}_PH1_{int(s*100)}.stl")
        print(f"D{int(d)} {int(s*100)}%", tm.is_watertight, np.round(tm.extents,2).tolist())
        tt = t.translate((i*26.0, row*26.0, 0)); plate = tt if plate is None else plate+tt
tm = save(plate, "Knob_Drivers_x6.stl"); print("plate", tm.is_watertight, np.round(tm.extents,1).tolist())

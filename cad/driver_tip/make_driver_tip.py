# Stubby Phillips (PH1) paddle driver for M3x3 flat-heads in the 16.55 mm wall slot.
# Axis = Z. Paddle z 0..PADDLE_T, shaft, then tip pointing +Z. Print paddle flat, tip up.
import numpy as np, manifold3d as m3, trimesh
PADDLE_T, PADDLE_W, PADDLE_L = 5.0, 12.0, 40.0   # paddle: 5 thick (along axis), 12 wide, 40 above axis
HUB_R = 6.0              # below-axis rounding: lower screw is 7 mm above plate top -> 1 mm clearance
SHAFT_D, SHAFT_L = 4.5, 3.0   # enters the Ø6 x 1.5 counterbore
TIP_L = 2.4              # PH1 cross length
R_BASE, R_POINT = 1.65, 0.55  # cross half-span at base / point (PH1 ~Ø3.3)
BLADE_T = 0.85           # wing thickness
CORE_BASE, CORE_POINT = 1.0, 0.35

def hull(pts): return m3.Manifold.hull_points([tuple(map(float,p)) for p in pts])
def rect_pts(hx, hy, z): return [(sx*hx, sy*hy, z) for sx in (-1,1) for sy in (-1,1)]

def tool(scale, notches):
    z0 = PADDLE_T + SHAFT_L; z1 = z0 + TIP_L
    # paddle = hull of circle (hub) + rectangle top
    circ = [(HUB_R*np.cos(a), HUB_R*np.sin(a), z) for a in np.linspace(0,2*np.pi,48,endpoint=False) for z in (0,PADDLE_T)]
    top = [(sx*PADDLE_W/2, PADDLE_L, z) for sx in (-1,1) for z in (0,PADDLE_T)]
    paddle = hull(circ+top)
    for k in range(notches):   # ID notches on the top edge
        x = (k-(notches-1)/2)*3.5
        paddle = paddle - m3.Manifold.cube((1.6,4,PADDLE_T+2)).translate((x-0.8,PADDLE_L-2.5,-1))
    shaft = m3.Manifold.cylinder(SHAFT_L+0.2, SHAFT_D/2, SHAFT_D/2, 48).translate((0,0,PADDLE_T-0.1))
    s = scale; t = BLADE_T*s/2
    b1 = hull(rect_pts(R_BASE*s, t, z0) + rect_pts(R_POINT*s, t, z1))
    b2 = hull(rect_pts(t, R_BASE*s, z0) + rect_pts(t, R_POINT*s, z1))
    core = m3.Manifold.cylinder(TIP_L, CORE_BASE*s, CORE_POINT*s, 32).translate((0,0,z0))
    return paddle + shaft + b1 + b2 + core

def save(man, fn):
    mesh = man.to_mesh(); tm = trimesh.Trimesh(mesh.vert_properties[:,:3], mesh.tri_verts)
    tm.export(fn); return tm

variants = [(0.90,1,"PH1_90"),(1.00,2,"PH1_100"),(1.10,3,"PH1_110")]
allm = None
for i,(s,n,name) in enumerate(variants):
    t = tool(s,n); tm = save(t, f"Driver_{name}.stl")
    print(name, "watertight", tm.is_watertight, "bbox", np.round(tm.bounds,2).tolist(), "vol", round(tm.volume,1))
    tt = t.translate((i*18.0,0,0)); allm = tt if allm is None else allm + tt
tm = save(allm, "Driver_Tips_x3.stl"); print("plate watertight", tm.is_watertight, np.round(tm.extents,1))

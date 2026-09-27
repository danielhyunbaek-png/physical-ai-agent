"""Overhead table for the Physical AI Agent — generates Table_Left.stl, Table_Right.stl, Table_Leg.stl.
Desk frame: X right, Y toward keyboard back, Z up from desk. Print tabletops UNDERSIDE DOWN (posts up, no supports)."""
import numpy as np, trimesh
from manifold3d import Manifold, CrossSection, FillRule
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from table_params import *
Z0 = TOP_Z; Z1 = TOP_Z + TOP_T           # tabletop underside / top face
def box(x0,x1,y0,y1,z0,z1): return Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0])
def cyl(x,y,z0,h,d,seg=48): return Manifold.cylinder(h,d/2,d/2,seg).translate([x,y,z0])
def union(ms):
    out=None
    for m in ms: out = m if out is None else out+m
    return out
def text_solid(s, x, y, h, depth, z_top):
    tp = TextPath((0,0), s, size=h, prop=FontProperties(family='DejaVu Sans', weight='bold'))
    polys=[p for p in tp.to_polygons() if len(p)>=3]
    if not polys: return None
    allp=np.vstack(polys); cx=(allp[:,0].min()+allp[:,0].max())/2; cy=(allp[:,1].min()+allp[:,1].max())/2
    cs = CrossSection([ [(float(px-cx+x),float(py-cy+y)) for px,py in p] for p in polys], FillRule.EvenOdd)
    return cs.extrude(depth+0.2).translate([0,0,z_top-depth])
def text_width(s,h):
    tp=TextPath((0,0),s,size=h,prop=FontProperties(family='DejaVu Sans',weight='bold')); v=tp.vertices
    return v[:,0].max()-v[:,0].min() if len(v) else 0

# ---- tabletop slab
slab = box(TX0,TX1,TY0,TY1,Z0,Z1)
adds=[]; subs=[]; keepout=[]   # keepout rects (for label placement)
# lead holes
holes=[lead_hole(*k) for k in KEYS]
for hx,hy in holes:
    subs.append(Manifold.cylinder(TOP_T+2, 1.0, 1.0, 48).scale([HOLE_W/2, HOLE_L/2, 1]).translate([hx,hy,Z0-1]))
# board pin posts
for n,x0 in BOARDS.items():
    for px in (x0+4,x0+116):
        for py in (BOARD_Y0+4,BOARD_Y0+BOARD_D-4):
            adds.append(cyl(px,py,Z1-0.01,GAP+0.01,POST_D)); adds.append(cyl(px,py,Z1+GAP,PIN_H,PIN_D,32))
            keepout.append((px-POST_D/2,px+POST_D/2,py-POST_D/2,py+POST_D/2))
# strip cradles: two U-shaped end blocks (8 long) + middle rib; strip rests at Z1+GAP, lips 3 mm up
for (yc,xc,rd) in STRIPS:
    yw=POCKET_W/2+LIP; xa=xc-POCKET_L/2-LIP; xb=xc+POCKET_L/2+LIP
    for (e0,e1,endwall) in ((xa,xa+8+LIP,(xa,xa+LIP)), (xb-8-LIP,xb,(xb-LIP,xb))):
        adds.append(box(e0,e1,yc-yw,yc+yw,Z1-0.01,Z1+GAP))
        adds.append(box(endwall[0],endwall[1],yc-yw,yc+yw,Z1+GAP-0.01,Z1+GAP+3))            # end lip
        adds.append(box(e0,e1,yc-yw,yc-yw+LIP,Z1+GAP-0.01,Z1+GAP+3))                        # side lips
        adds.append(box(e0,e1,yc+yw-LIP,yc+yw,Z1+GAP-0.01,Z1+GAP+3))
        keepout.append((e0,e1,yc-yw,yc+yw))
    adds.append(box(xc+rd-1.5,xc+rd+1.5,yc-yw,yc+yw,Z1-0.01,Z1+GAP))
    keepout.append((xc+rd-1.5,xc+rd+1.5,yc-yw,yc+yw))
# Mega tray: 4 pads + 3-sided wall (USB/back edge open)
MX0, MX1, MY0, MY1 = MEGA_X0, MEGA_X0+MEGA_W, MEGA_YTOP-MEGA_L, MEGA_YTOP
for lx,ly in MEGA_HOLES_LOCAL:
    adds.append(cyl(MX0+ly, MEGA_YTOP-lx, Z1-0.01, MEGA_PAD_H+0.01, 6.0))
c=0.6; w=MEGA_TRAY_WALL; hwall=MEGA_PAD_H+1.6+2.5
adds.append(box(MX0-c-w,MX0-c,MY0-c-w,MY1-10,Z1-0.01,Z1+hwall))
adds.append(box(MX1+c,MX1+c+w,MY0-c-w,MY1-10,Z1-0.01,Z1+hwall))
adds.append(box(MX0-c-w,MX1+c+w,MY0-c-w,MY0-c,Z1-0.01,Z1+hwall))
# leg sockets (from underside)
for lx,ly in LEGS: subs.append(cyl(lx,ly,Z0-1,SOCKET_H+1,SOCKET_D))
# engraved key labels, centred on the plunger x (between holes), at hole Y
labels_done=0
keepout += [(SPLIT_BACK-0.8,SPLIT_BACK+0.8,STEP_Y-0.8,TY1),(SPLIT_FRONT-0.8,SPLIT_FRONT+0.8,TY0,STEP_Y+0.8),(SPLIT_BACK-0.8,SPLIT_FRONT+0.8,STEP_Y-0.8,STEP_Y+0.8)]
def inside_keepout(x0,x1,y0,y1):
    return any(not(x1<a or x0>b or y1<c_ or y0>d) for a,b,c_,d in keepout)
for (hx,hy),nm in zip(holes,names):
    wtxt=text_width(nm,TEXT_H)
    if wtxt>13.5: print('too wide',nm,round(wtxt,1)); continue
    spot=None
    for cx,cy in ((hx+9.5,hy),(hx+wtxt/2+3.5,hy+HOLE_L/2+2.5),(hx+wtxt/2+3.5,hy-HOLE_L/2-2.5)):
        if not inside_keepout(cx-wtxt/2-0.5,cx+wtxt/2+0.5,cy-TEXT_H/2-0.5,cy+TEXT_H/2+0.5): spot=(cx,cy); break
    if spot is None: print('no spot',nm); continue
    keepout.append((spot[0]-wtxt/2,spot[0]+wtxt/2,spot[1]-TEXT_H/2,spot[1]+TEXT_H/2))
    t=text_solid(nm,spot[0],spot[1],TEXT_H,TEXT_DEPTH,Z1)
    if t: subs.append(t); labels_done+=1
    else: print('empty',nm)
# big engravings: board zones + FRONT arrow (on free areas)
for n,x0 in BOARDS.items():
    pass
for s_,x,y in [('FRONT',-128,-66),('A',-40,-3.0)]: pass
subs.append(text_solid('FRONT  v',-128,-68,6,TEXT_DEPTH,Z1))
table = slab + union(adds) - union(subs)
# ---- split (stepped): left = X<81 for Y>=25, X<90.5 for Y<25
BIG=1000
left_region = box(-BIG,SPLIT_BACK,STEP_Y,BIG,-BIG,BIG) + box(-BIG,SPLIT_FRONT,-BIG,STEP_Y,-BIG,BIG)
left = table ^ left_region
right = table - left_region
def save(m,fn):
    mesh=m.to_mesh(); t=trimesh.Trimesh(vertices=np.array(mesh.vert_properties)[:,:3], faces=np.array(mesh.tri_verts))
    t.export(fn); return t
L=save(left,'Table_Left.stl'); R=save(right,'Table_Right.stl')
# ---- leg (print standing): 10x10 x TOP_Z, peg on top
leg = box(-LEG_S/2,LEG_S/2,-LEG_S/2,LEG_S/2,0,TOP_Z) + cyl(0,0,TOP_Z-0.01,PEG_H+0.01,PEG_D)
G=save(leg,'Table_Leg.stl')
print('labels engraved:',labels_done,'/84')
for nm,t in [('Left',L),('Right',R),('Leg',G)]:
    print(nm,'watertight',t.is_watertight,'extents',np.round(t.extents,1),'bounds',np.round(t.bounds,1).tolist(),'vol cm3',round(t.volume/1000,1))

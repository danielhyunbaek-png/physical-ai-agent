from table_params import *
import itertools
holes=[lead_hole(*k) for k in KEYS]
def clear_rect(x0,x1,y0,y1):
    m=1e9
    for hx,hy in holes:
        dx=max(x0-(hx+HOLE_W/2), (hx-HOLE_W/2)-x1, 0); dy=max(y0-(hy+HOLE_L/2),(hy-HOLE_L/2)-y1,0)
        d=max(dx,dy) if (dx>0 or dy>0) else -1
        m=min(m,d)
    return m
def board_clear(x0,y0):
    return min(clear_rect(px-POST_D/2,px+POST_D/2,py-POST_D/2,py+POST_D/2) for px in (x0+4,x0+116) for py in (y0+4,y0+62))
# boards
best=None
for y0 in [v/2 for v in range(-44,-26)]:
    for dA in range(-1,9):
      cA=board_clear(-95.5+dA,y0)
      for dB in range(-12,13):
        xB=30.5+dB
        if not (xB+10<81 and xB+110>90.5): continue
        if xB < -95.5+dA+123: continue
        cB=board_clear(xB,y0)
        for dC in range(-6,13):
            xC=156.5+dC
            if xC < xB+123: continue
            cC=board_clear(xC,y0)
            s=min(cA,cB,cC)
            if best is None or s>best[0]: best=(s,y0,-95.5+dA,xB,xC)
print('boards best min clearance',best)

def strip_clear(xc,yc,rib_dx=0):
    yw=POCKET_W/2+LIP; x0=xc-POCKET_L/2-LIP; x1=xc+POCKET_L/2+LIP
    rects=[(x0,x0+8+LIP),(x1-8-LIP,x1),(xc+rib_dx-1.5,xc+rib_dx+1.5)]
    return min(clear_rect(a,b,yc-yw,yc+yw) for a,b in rects), x0, x1
HALF=POCKET_L/2+LIP
res={}
for side,(ylo,yhi,seam) in {'back':(70,80,81.0),'front':(-56,-46,90.5)}.items():
    bestL=bestR=None
    for yc in [v/2 for v in range(int(ylo*2),int(yhi*2)+1)]:
        for xc in [v/2 for v in range(-2*95+int(2*HALF), int(2*(seam-1-HALF))+1)]:
            for rd in (-12,-6,0,6,12):
                c,x0,x1=strip_clear(xc,yc,rd)
                if bestL is None or c>bestL[0]: bestL=(c,xc,yc,rd)
        for xc in [v/2 for v in range(int(2*(seam+1+HALF)), int(2*(276-HALF))+1)]:
            for rd in (-12,-6,0,6,12):
                c,x0,x1=strip_clear(xc,yc,rd)
                if bestR is None or c>bestR[0]: bestR=(c,xc,yc,rd)
    print(side,'L',bestL,'R',bestR)

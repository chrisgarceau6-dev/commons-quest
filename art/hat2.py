import math
OUT='#464a58'; W_='#ffffff'; L='#e4e8f0'; M='#bcc2d0'; D='#8e94a6'
def fitted_hat(c, cx, top, hw, bh=5, curve=2.0, crown_h=11, shadow=None):
    """Chef hat sized to the head: band wraps the head (edges dip), puffy crown overhangs the band."""
    P={}
    # band: top edge follows the head's curve, so the sides sit lower than the middle
    for x in range(-hw, hw+1):
        t=x/hw; y0=top+round(curve*t*t)
        for y in range(y0, y0+bh):
            sh = 0.85 - 0.55*((x+hw)/(2*hw))           # lit from the left
            col = W_ if sh>0.62 else L if sh>0.42 else M
            if y==y0+bh-1: col = M if x%2 else D        # stitched lower edge
            P[(cx+x,y)]=col
    # crown: three overlapping lobes, a little wider than the band
    lobes=[(-hw*0.48, crown_h*0.55, hw*0.62), (0, crown_h*0.78, hw*0.66), (hw*0.48, crown_h*0.55, hw*0.6)]
    base=top+1
    for (lx, ly, r) in lobes:
        ry=r*0.82
        for y in range(int(base-ly-ry)-1, base+1):
            for x in range(int(cx+lx-r)-1, int(cx+lx+r)+2):
                dx=(x-(cx+lx))/r; dy=(y-(base-ly))/ry
                if dx*dx+dy*dy<=1 or (y>=base-ly and abs(x-cx)<=hw+1 and y<=base):
                    if (x,y) in P and y>=top: continue
                    nz=math.sqrt(max(0,1-min(1,dx*dx+dy*dy)))
                    sh=0.45+0.55*(-0.6*dx-0.5*dy+0.6*nz)
                    P[(x,y)] = W_ if sh>0.7 else L if sh>0.5 else M
    # overhang shadow where the crown meets the band
    for x in range(-hw+1, hw):
        t=x/hw; y=top+round(curve*t*t)
        if (cx+x,y) in P: P[(cx+x,y)] = L if x< -hw*0.3 else M
    # soft fold lines from the gaps between lobes toward the band
    for fx in (-hw*0.25, hw*0.25):
        for k in range(int(crown_h*0.55)):
            x=round(cx+fx*(1-k/(crown_h*0.9))); y=top-1-k
            if (x,y) in P and P[(x,y)]!=OUT: P[(x,y)] = L if P[(x,y)]==W_ else M
    # dips between the lobes: notch the top edge and run a soft crease down from it
    for fx in (-hw*0.24, hw*0.24):
        x=round(cx+fx)
        col_ys=[y for (xx,y) in P if xx==x]
        if not col_ys: continue
        ytop=min(col_ys)
        del P[(x,ytop)]
        P.pop((x,ytop+1),None)
        for k in range(2,6):
            if (x,ytop+k) in P: P[(x,ytop+k)] = M if k<3 else L
        for xx in (x-1,x+1):
            ys=[y for (x2,y) in P if x2==xx]
            if ys: P[(xx,min(ys))]=L
    # outline: any empty neighbour of the hat gets the outline colour; head pixels just under the band get a shadow
    keys=set(P)
    for (x,y) in list(keys):
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            n=(x+dx,y+dy)
            if n in keys or not (0<=n[0]<c.w and 0<=n[1]<c.h): continue
            if c.g[n[1]][n[0]] is None and n not in c.fixed: P[n]=OUT
            elif dy==1 and shadow: P[n]=shadow
    for (x,y),col in P.items():
        if 0<=x<c.w and 0<=y<c.h: c.fix(x,y,col)

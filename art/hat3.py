import math
O='#2c2f3c'; W_='#ffffff'; L='#e2e6ef'; M='#b6bccb'; D='#878ea2'
def _finish(c,P,shadow):
    keys=set(P)
    for (x,y) in list(keys):
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            n=(x+dx,y+dy)
            if n in keys or not (0<=n[0]<c.w and 0<=n[1]<c.h): continue
            if c.g[n[1]][n[0]] is None and n not in c.fixed: P[n]=O
            elif dy==1 and shadow: P[n]=shadow
    for (x,y),col in P.items():
        if 0<=x<c.w and 0<=y<c.h: c.fix(x,y,col)

def toque_tall(c,cx,top,hw,shadow=None,tilt=0.0,scale=1.0):
    """A: classic tall pleated toque - band, flaring pleated crown, soft domed top."""
    P={}; bw=round(hw*scale); H=round(14*scale)
    for x in range(-bw,bw+1):
        for y in range(top,top+4):
            sh=0.85-0.5*((x+bw)/(2*bw)); P[(x,y)]=W_ if sh>0.6 else L if sh>0.45 else M
    for x in range(-bw,bw+1): P[(x,top)]=D                       # seam between crown and band
    for k in range(1,H):
        y=top-k; half=bw+1+round(k*0.18)
        for x in range(-half,half+1):
            sh=0.9-0.55*((x+half)/(2*half)); col=W_ if sh>0.62 else L if sh>0.46 else M
            if x%4==0 and k<H-2: col=L if col==W_ else M          # vertical pleats
            P[(x,y)]=col
    tophalf=bw+1+round(H*0.18)
    for x in range(-tophalf,tophalf+1):                           # three soft bumps on top
        bump=round(1.6*abs(math.cos((x+tophalf)/(2*tophalf)*math.pi*3)))
        for y in range(top-H-bump,top-H+1): P[(x,y)]=W_ if x<0 else L
    Q={}
    for (x,y),col in P.items(): Q[(cx+x+round((top-y)*tilt),y)]=col
    _finish(c,Q,shadow)

def toque_puffy(c,cx,top,hw,shadow=None):
    """B: short puffy cap like the reference - two big lobes with a deep dip, short band."""
    P={}
    for x in range(-hw,hw+1):
        for y in range(top,top+4):
            sh=0.85-0.5*((x+hw)/(2*hw)); P[(x,y)]=W_ if sh>0.6 else L if sh>0.45 else M
        P[(x,top+3)]=D if x%2 else M
    for (lx,r) in ((-hw*0.45,hw*0.62),(hw*0.42,hw*0.66)):
        ry=r*0.8
        for y in range(round(top-2*ry)-1,top+1):
            for x in range(round(lx-r)-1,round(lx+r)+2):
                dx=(x-lx)/r; dy=(y-(top-ry))/ry
                if dx*dx+dy*dy<=1 and (x,y) not in P or (dx*dx+dy*dy<=1 and y<top):
                    nz=math.sqrt(max(0,1-dx*dx-dy*dy)); sh=0.45+0.55*(-0.6*dx-0.5*dy+0.6*nz)
                    P[(x,y)]=W_ if sh>0.72 else L if sh>0.52 else M
    for x in range(-hw-1,hw+2): P[(x,top)]=M                       # overhang shadow line
    # deep dip between the lobes + crease
    xd=round(hw*-0.02)
    ys=sorted(y for (x,y) in P if x==xd)
    for y in ys[:3]: P.pop((xd,y),None)
    for k in range(3,7):
        if (xd,ys[0]+k) in P: P[(xd,ys[0]+k)]=M
    Q={(cx+x,y):col for (x,y),col in P.items()}
    _finish(c,Q,shadow)

import math
from PIL import Image
PAD=12
O=(44,47,60,255); Wc=(255,255,255,255); Lc=(228,232,240,255); Mc=(186,192,206,255); Dc=(140,146,164,255)
def hexrgba(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))+(255,)
def pad(img):
    out=Image.new('RGBA',(img.width,img.height+PAD)); out.paste(img,(0,PAD)); return out
def apply_hat(img,cx,top,hw,shadow,back=0.1,ch=1.35,lr=0.88):
    """Chef hat that sits ON the head: perspective band wrapping the forehead, big puffy crown leaning back."""
    out=pad(img); top+=PAD; W,H=out.size
    P={}; bh=4; curv=3.0
    band_top={}
    for x in range(-hw,hw+1):
        t=x/hw; yt=top+round(curv*0.55*(1-t*t)); yb=top+bh+round(curv*(1-t*t))
        band_top[cx+x]=yt
        for y in range(yt,yb+1):
            s=0.85-0.55*((x+hw)/(2*hw))
            col=Wc if s>0.62 else Lc if s>0.45 else Mc
            if y==yt: col=Mc if s>0.45 else Dc                     # shadow under the crown's overhang
            if y==yb: col=Dc if x%2 else Mc                          # stitched front edge
            P[(cx+x,y)]=col
    # crown: overlapping puffy lobes, leaning back (to the right, away from the face)
    Hc=round(hw*ch); off=round(hw*back)
    lobes=[(-0.55*lr,0.38,0.46*lr),(0.55*lr,0.40,0.46*lr),(-0.2*lr,0.66,0.5*lr),(0.25*lr,0.68,0.5*lr),(0.0,0.30,0.7*lr)]
    drawn=set()
    for (fx,fy,fr) in lobes:
        lx=cx+off+fx*hw; ly=top-fy*Hc; r=fr*hw; ry=r*0.86
        mine=set()
        for y in range(int(ly-ry)-1,int(ly+ry)+2):
            for x in range(int(lx-r)-1,int(lx+r)+2):
                dx=(x-lx)/r; dy=(y-ly)/ry; d2=dx*dx+dy*dy
                if d2>1: continue
                if y>=band_top.get(x,top): continue                   # crown stays above the band
                nz=math.sqrt(max(0,1-d2)); s=0.42+0.58*(-0.55*dx-0.55*dy+0.62*nz)
                col=Wc if s>0.74 else Lc if s>0.56 else Mc
                if d2>0.8 and (x,y) in drawn: col=Mc                 # crease where this lobe overlaps another
                P[(x,y)]=col; mine.add((x,y))
        drawn|=mine
    # outline + soft shadow on the head right under the band
    shadow=hexrgba(shadow) if isinstance(shadow,str) else shadow
    keys=set(P)
    for (x,y) in list(keys):
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            n=(x+dx,y+dy)
            if n in keys or not(0<=n[0]<W and 0<=n[1]<H): continue
            if out.getpixel(n)[3]==0: P[n]=O
            elif dy==1: P[n]=shadow
    for (x,y),col in P.items():
        if 0<=x<W and 0<=y<H: out.putpixel((x,y),col)
    return out

# tall chef toque, cloth-like shading: rounded puffs lit from top-left, soft cylinder body with gathered folds, smooth band
import math
from PIL import Image
O=(44,46,62,255); W=(255,255,255,255); L=(229,233,243,255); M=(192,199,216,255); D=(150,158,182,255)
STRIPE=[(150,24,40,255),(196,40,58,255),(226,72,84,255)]
LX,LY,LZ=-0.5,-0.55,0.67
def hexrgba(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))+(255,)
def tone(s): return W if s>0.62 else L if s>0.3 else M if s>0.0 else D
def build(bw=22,bh=7,body=9,puff=12,flare=2,ov=2):
    cw=bw+2*flare+2*ov; cx=cw/2; C={}; by1=puff+body
    # gathered lower poof: bulges wider than the band, tucks into it; pleats radiate down into the band
    for y in range(puff-3,by1):
        t=(y-(puff-3))/(by1-(puff-3))                     # 0 top .. 1 at band
        half=bw/2+1+(cw/2-bw/2-1)*math.sqrt(max(0,1-t*t))
        for x in range(cw):
            u=(x+0.5-cx)/half
            if abs(u)>1: continue
            nz=math.sqrt(max(0,1-u*u)); s=LX*u+LZ*nz+0.15-0.35*t
            C[(x,y)]=tone(s)
    for k in (-2,-1,0,1,2):                              # gathered pleats fanning up out of the band
        x0=cx+k*bw/5.2; ang=k*0.45
        for i in range(0,5):
            x=round(x0+ang*i-0.5); y=by1-1-i
            if (x,y) in C: C[(x,y)]=D if i<3 else M
            if i<2 and (x+1,y) in C and k<=0: C[(x+1,y)]=M
    # puff: middle lobe (behind) then side lobes (in front)
    lobes=[(cx,puff-5.6,cw*0.25),(cx-cw*0.27,puff-4.2,cw*0.215),(cx+cw*0.27,puff-4.2,cw*0.215)]
    for k,(bx,byy,r) in enumerate(lobes):
        ry=r*0.85
        for y in range(0,puff+1):
            for x in range(cw):
                dx=(x+0.5-bx)/r; dy=(y+0.5-byy)/ry
                inside=dx*dx+dy*dy<=1 or (dy>0 and abs(dx)<=1 and y<=puff-1)
                if not inside: continue
                d2=min(1,dx*dx+dy*dy); nz=math.sqrt(1-d2)
                s=LX*dx+LY*dy+LZ*nz
                if dy>0.2: s-=0.25*(dy-0.2)                       # underside rolls into shadow
                col=tone(s)
                if k>0 and (x,y) in C and d2>0.78 and y<puff-1: col=M   # crease where a front lobe meets the one behind
                C[(x,y)]=col
    for x in range(cw):                                           # shadow cast by the puff onto the body
        for y in (puff,puff+1):
            if (x,y) in C: C[(x,y)]=M if y==puff else (L if C[(x,y)]==W else C[(x,y)])
    # band: crisp separation, coloured stripe with a shine, then the white band with a curved bottom
    for y in range(by1,by1+bh+3):
        for x in range(cw):
            u=(x+0.5-cx)/(bw/2)
            if abs(u)>1: continue
            if y>by1+bh-1+round(2.2*(1-u*u)): continue
            nz=math.sqrt(max(0,1-u*u)); s=LX*u+LZ*nz+0.1
            if y==by1: C[(x,y)]=O; continue
            if y in (by1+1,by1+2):
                C[(x,y)]=STRIPE[2] if s>0.55 else STRIPE[1] if s>0.15 else STRIPE[0]
                if y==by1+1 and -0.55<u<-0.35: C[(x,y)]=(255,236,236,255)
                continue
            if y==by1+3: s-=0.35
            C[(x,y)]=tone(s)
    for (x,y) in list(C):
        if y>by1+3 and (x,y+1) not in C: C[(x,y)]=tone(-0.05) if C[(x,y)]!=W else L
    return C,cw,by1+bh-1+2
def apply(img,cx,band_bottom,shadow,pad=30,stripe=None,**kw):
    global STRIPE
    if stripe: STRIPE=stripe
    C,cw,bot=build(**kw)
    out=Image.new('RGBA',(img.width,img.height+pad)); out.paste(img,(0,pad))
    ox=round(cx-cw/2); oy=band_bottom+pad-bot
    keys={(x+ox,y+oy) for (x,y) in C}
    for (x,y),col in C.items(): out.putpixel((x+ox,y+oy),col)
    sh=hexrgba(shadow)
    for (x,y) in list(keys):
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            n=(x+dx,y+dy)
            if n in keys or not(0<=n[0]<out.width and 0<=n[1]<out.height): continue
            if dy==1 and out.getpixel(n)[3]: out.putpixel(n,sh)
            else: out.putpixel(n,O)
    return out

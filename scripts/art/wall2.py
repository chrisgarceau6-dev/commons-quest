# The Blue Wall v2: a chibi brick golem barista. Round, volume-shaded body parts with a brick texture laid over the shading.
import math, json
from pixart2 import Canvas, RAMPS, CONTRAST, sheet
from PIL import Image
RAMPS.update({
 'brick':['#071030','#1c3a86','#2d5cc4','#4a7ee6','#7aa6f8'],
 'stone':['#0b0618','#2a2c3c','#40445a','#5a6078','#7c84a0'],
 'apr':  ['#140c06','#3a2414','#56361e','#704a2a','#8e623a'],
 'cup':  ['#3a3a4a','#c9ccd8','#f2f3f8','#ffffff','#ffffff'],
 'sleeve':['#2a1606','#6e4420','#9a6232','#b97e48','#d8a066'],
 'lid':  ['#0b0618','#22222e','#363644','#4c4c5c','#64647a'],
})
CONTRAST.update({'brick':0.85,'stone':0.7,'apr':0.6,'cup':0.6})
W=H=84; GY=82
def hsh(i,j): return (i*73856093 ^ j*19349663) & 0xffff
def mix(a,b,t): return tuple(round(a[k]+(b[k]-a[k])*t) for k in range(3))+(255,)
class BC(Canvas):
    """brick texture: each part gets its own course grid, so bricks move with the part they belong to"""
    def __init__(s,w,h): super().__init__(w,h); s.grid={}
    def bricky(s,name,x0,y0,bw=8,bh=4): s.grid[name]=(x0,y0,bw,bh)
    def render(s,**k):
        im=super().render(**k)
        for y in range(s.h):
            for x in range(s.w):
                if s.g[y][x]!='brick' or (x,y) in s.fixed: continue
                p=s.pid[y][x]
                if p not in s.grid: continue
                x0,y0,bw,bh=s.grid[p]
                r=(y-y0)//bh; ry=(y-y0)%bh
                off=bw//2 if r%2 else 0
                cx=(x-x0+off)//bw; rx=(x-x0+off)%bw
                col=im.getpixel((x,y))
                if col[3]==0: continue
                # leave the outline alone
                # keep a clean 1px rim of plain shading inside the outline, and don't let mortar cross into other parts
                n=[s.pid[y+dy][x+dx] if 0<=x+dx<s.w and 0<=y+dy<s.h else None for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(2,0),(-2,0),(0,2),(0,-2))]
                if any(q!=p for q in n[:4]): continue
                if any(q!=p for q in n[4:]) and (ry==bh-1 or rx==bw-1): continue
                if ry==bh-1 or rx==bw-1: im.putpixel((x,y),mix(col,(10,20,60),0.55)); continue
                v=(hsh(cx+x0,r+y0)%3-1)*0.07
                if ry==0: col=mix(col,(255,255,255),0.18+v)
                elif v>0: col=mix(col,(255,255,255),v)
                else: col=mix(col,(0,0,30),-v)
                im.putpixel((x,y),col)
        return im
def rrect(c,x0,y0,x1,y1,r,m):
    """rounded block with volume shading: flat front face, edges rolling away from the light"""
    k=c._new()
    for y in range(int(y0),int(y1)+1):
        for x in range(int(x0),int(x1)+1):
            dx=max(x0+r-x,0,x-(x1-r)); dy=max(y0+r-y,0,y-(y1-r))
            if dx*dx+dy*dy>r*r+0.3: continue
            ex=min(x-x0,x1-x); ey=min(y-y0,y1-y); band=r+1.5
            nx=0 if ex>=band else (-1 if x-x0<x1-x else 1)*(1-ex/band)
            ny=0 if ey>=band else (-1 if y-y0<y1-y else 1)*(1-ey/band)
            nz=math.sqrt(max(0.05,1-nx*nx-ny*ny))
            c._put(x,y,m,k,c._lit(nx*0.9,ny*0.9,nz))
    return k
FONT={'B':["11.","1.1","11.","1.1","11."],'L':["1..","1..","1..","1..","111"],'U':["1.1","1.1","1.1","1.1","111"],
      'E':["111","1..","11.","1..","111"],'W':["1...1","1...1","1.1.1","11.11","1...1"],'A':[".1.","1.1","111","1.1","1.1"]}
def text(c,x,y,s,col,sh=None):
    pts=[]
    for ch in s:
        if ch==' ': x+=2; continue
        for j,row in enumerate(FONT[ch]):
            for i,v in enumerate(row):
                if v=='1': pts.append((x+i,y+j))
        x+=len(FONT[ch][0])+1
    if sh:
        for (a,b) in pts: c.fix(a+1,b+1,sh)
    for (a,b) in pts: c.fix(a,b,col)
def cup(c,x,y,steam=0):
    with c.group('cup'):
        for k in range(11):
            w=4.2-k*0.1; c.rect(round(x-w),y-k,round(x+w),y-k,'cup')
    with c.group('sleeve'): c.rect(x-4,y-7,x+4,y-3,'sleeve')
    with c.group('lid'):
        c.rect(x-5,y-13,x+5,y-11,'lid'); c.rect(x-3,y-14,x+3,y-14,'lid')
    for xx in (x-2,x-1,x,x+1): c.fix(xx,y-5,'#f0d8b0')
    c.fix(x-3,y-9,'#ffffff'); c.fix(x-3,y-8,'#ffffff')
    if steam is not None:
        for i,(dx,dy) in enumerate([(0,0),(1,-1),(1,-2),(0,-3),(-1,-4),(-1,-5),(0,-6)]):
            c.fix(x-1+dx+(1 if (i+steam)%4<2 else 0),y-16+dy,'#e6ecfa' if i%2 else '#cdd7f0')
def wall(nod=0,lean=0,face='stern',sit=0,hold=True,cupup=0,steam=0,crack=0,headtilt=0):
    c=BC(W,H); o=lean; b=sit
    # stubby stone feet + brick legs
    for x0 in (33,51):
        with c.group('leg%d'%x0): c.ell(x0+o,72,6,6,'brick')
        c.bricky('leg%d'%x0,x0-6,66,6,3)
        with c.group('foot%d'%x0): c.ell(x0+o,78.5,7,3.4,'stone')
    snap=c.snap()
    # round body
    with c.group('body'): rrect(c,26+o,46+b,58+o,70+b,5,'brick')
    c.bricky('body',26+o,46+b,8,4)
    for y in range(68,H):
        for x in range(36+o,49+o):
            if c.g[y][x]=='brick' and c.pid[y][x]=='body': c.restore(x,y,snap)
    # barista apron with BLUE WALL stitched across it
    with c.group('apr'):
        c.rect(31+o,48+b,53+o,52+b,'apr')
        for y in range(53,68):
            half=11+min(3,(y-53)*0.35); c.rect(round(42-half)+o,y+b,round(42+half)+o,y+b,'apr')
    c.line(32+o,48+b,29+o,42+b,'apr',2); c.line(52+o,48+b,55+o,42+b,'apr',2)                 # neck straps
    for x in range(27+o,58+o): c.fix(x,54+b,'#c8a66a') if c.g[54+b][x]=='apr' else None     # waist tie
    for x in range(30+o,55+o,2): c.fix(x,49+b,'#8e623a')                                       # running stitch
    # near arm: hand on hip
    with c.group('narm'):
        c.ell(24+o,49+b,5.5,5.5,'brick'); c.line(23+o,51+b,17+o,57+b,'brick',7); c.line(17+o,57+b,24+o,61+b,'brick',6.5)
    c.bricky('narm',14+o,44+b,6,3)
    with c.group('nfist'): c.ell(24+o,61+b,4.2,3.8,'stone')
    # far arm holding the coffee
    if hold:
        hx_,hy_=66+o,48+b-cupup
        with c.group('farm'):
            c.ell(60+o,49+b,5.5,5.5,'brick'); c.line(61+o,51+b,hx_,hy_+4,'brick',7)
        c.bricky('farm',54+o,44+b,6,3)
        cup(c,hx_+1,hy_-1,steam=steam)
        with c.group('ffist'): c.ell(hx_+1,hy_,4.4,3.6,'stone')                        # fist wraps the base of the cup
        for k in (-2,0,2): c.fix(hx_+1+k,hy_-1,'#5a6078')
    else:
        with c.group('farm'):
            c.ell(60+o,49+b,5.5,5.5,'brick'); c.line(61+o,51+b,65+o,60+b,'brick',7)
        c.bricky('farm',54+o,44+b,6,3)
        with c.group('ffist'): c.ell(65+o,62+b,4.2,3.8,'stone')
    # head: big rounded block, stone cap course on top
    hx,hy=41+o+headtilt,29+b+nod
    with c.group('head'): rrect(c,hx-18,hy-15,hx+18,hy+13,5,'brick')
    c.bricky('head',hx-18,hy-15,9,5)
    # a sprig of ivy growing out of the top course
    IVY=[(0,0,'#2f7a3a'),(0,-1,'#2f7a3a'),(1,-2,'#2f7a3a'),(1,-3,'#2f7a3a'),(2,-4,'#2f7a3a'),
         (-1,-2,'#5cbf5a'),(-2,-2,'#5cbf5a'),(-2,-3,'#8be07a'),(-3,-3,'#5cbf5a'),(-2,-1,'#2f7a3a'),
         (2,-5,'#5cbf5a'),(3,-5,'#8be07a'),(3,-6,'#5cbf5a'),(4,-5,'#5cbf5a'),(3,-4,'#2f7a3a')]
    for x,y,col in IVY: c.fix(hx+5+x,hy-16+y,col)

    if crack:
        pts=[(hx+8,hy-10),(hx+7,hy-9),(hx+7,hy-8),(hx+8,hy-7),(hx+9,hy-6)]
        if crack>1: pts+=[(hx+9,hy-5),(hx+10,hy-4),(hx-13,hy+6),(hx-12,hy+7),(hx-12,hy+8),(hx-11,hy+9)]
        for p in pts: c.fix(*p,'#071030')
    F=lambda x,y,col='#0b0618': c.fix(hx+x,hy+y,col)
    # heavy stone brows (a protruding course) — angled down toward the middle for the stern look
    if face!='dizzy':
        with c.group('brow'):
            c.line(hx-13,hy-5,hx-4,hy-3,'stone',3); c.line(hx+4,hy-3,hx+13,hy-5,'stone',3)
    if face=='stern':
        EYE=["..www.",".wwwww","wwppww","wwpgww",".wwww."]
        for ex,flip in ((-10,False),(4,True)):
            for j,row in enumerate(EYE):
                for i,ch in enumerate(row[::-1] if flip else row):
                    if ch=='.': continue
                    F(ex+i,j-2,{'w':'#f4f6ff','p':'#0b0618','g':'#ffd84a'}[ch])
            for i in range(6): F(ex+i,-2,'#071030'); F(ex+i,-1,'#071030') if (i<3)!=flip else None   # heavy lids, angled in
        for x in range(-5,5): F(x,9,'#0b0618')                     # smirk, one corner up
        F(5,8,'#0b0618'); F(6,7,'#0b0618')
        F(-2,10,'#e8ecf6'); F(-1,10,'#e8ecf6'); F(2,10,'#e8ecf6')   # chipped tooth gap
        F(-2,11,'#0b0618'); F(-1,11,'#0b0618'); F(2,11,'#0b0618'); F(0,10,'#0b0618'); F(1,10,'#0b0618')
    elif face=='hurt':
        for x,y in [(0,-2),(1,-1),(2,0),(3,1),(1,1),(0,2),(2,-1)]: F(-9+x,y)
        for x,y in [(4,-2),(3,-1),(2,0),(1,1),(3,1),(4,2),(2,-1)]: F(4+x,y)
        for x in range(-4,5): F(x,9)
        for x in range(-3,4): F(x,10,'#ff7a8a')
        F(20,-6,'#9cd8ff');F(20,-5,'#9cd8ff');F(21,-5,'#ffffff');F(20,-4,'#9cd8ff')
    elif face=='dizzy':
        SP=[(-2,-5),(-1,-5),(0,-5),(1,-5),(2,-4),(2,-3),(2,-2),(1,-1),(0,-1),(-1,-1),(-2,-2),(-2,-3),(-1,-3),(0,-3),(0,-2)]
        for cx in (-7,6):
            for x,y in SP: F(cx+x,y+3)
        for x,y in [(-5,9),(-4,8),(-3,9),(-2,8),(-1,9),(0,8),(1,9),(2,8),(3,9),(4,8)]: F(x,y)
    from nametag import stitch
    if c.g[60+b][42+o]=='apr':
        stitch(c,'BLUE',57+b,'apr',FONT,'#e8d8b0','#1a0e06',cx=42+o); stitch(c,'WALL',63+b,'apr',FONT,'#e8d8b0','#1a0e06',cx=42+o)
    return c.render(dither=False)
STAR=["..k..","..y..","kyyyk",".yky.","y...y"]
def stars(im,t,cx=41,cy=8,r=15):
    for k in range(3):
        a=t+k*2.09; x0=round(cx+r*math.cos(a))-2; y0=round(cy+3*math.sin(a))-2
        for j,row in enumerate(STAR):
            for i,ch in enumerate(row):
                if ch=='.': continue
                x,y=x0+i,y0+j
                if 0<=x<W and 0<=y<H: im.putpixel((x,y),(255,214,64,255) if ch=='y' else (122,74,0,255))
    return im
def spilled_cup(c,x=62,y=GY-1):
    for xx in range(x-12,x+2): c.fix(xx,y,'#6e4420')
    for xx in range(x-9,x): c.fix(xx,y-1,'#9a6232')
    with c.group('cup'): c.rect(x,y-7,x+10,y-1,'cup')
    with c.group('sleeve'): c.rect(x+3,y-7,x+6,y-1,'sleeve')
    with c.group('lid'): c.rect(x-2,y-8,x,y,'lid')
def rubble(t=0,settle=0,flying=False):
    c=BC(W,H)
    spilled_cup(c)
    rows=[(1,0,7),(5,1,6),(9,2,5),(13,3,4)]
    for (dy,r,n) in rows:
        for k in range(n):
            bx=12+r*4+k*8+((r*5+k*3)%3)-1; by=GY-1-dy+((k+r)%2)+(settle if r>1 else 0)
            name='rb%d_%d'%(r,k)
            with c.group(name): c.rect(bx,by-3,bx+6,by,'brick')
            c.bricky(name,bx,by-3,7,4)
    for (bx,by) in [(3,GY),(68,GY-9) if not flying else (70,30),(74,GY-1)]:
        with c.group('lb%d'%bx): c.rect(bx,by-3,bx+6,by,'brick')
        c.bricky('lb%d'%bx,bx,by-3,7,4)
    with c.group('fist1'): c.ell(10,GY-3,4.2,3.6,'stone')
    # the head rolled to the top of the pile, dazed
    hx,hy=42,GY-31+settle
    with c.group('head'): rrect(c,hx-17,hy-13,hx+17,hy+12,5,'brick')
    c.bricky('head',hx-17,hy-13,9,5)
    for x,y,col in [(0,0,'#2f7a3a'),(0,-1,'#2f7a3a'),(1,-2,'#2f7a3a'),(-1,-2,'#5cbf5a'),(-2,-2,'#8be07a'),(2,-3,'#5cbf5a'),(3,-3,'#8be07a')]:
        c.fix(hx+3+x,hy-14+y,col)
    F=lambda x,y,col='#0b0618': c.fix(hx+x,hy+y,col)
    SP=[(-2,-5),(-1,-5),(0,-5),(1,-5),(2,-4),(2,-3),(2,-2),(1,-1),(0,-1),(-1,-1),(-2,-2),(-2,-3),(-1,-3),(0,-3),(0,-2)]
    for cx in (-7,6):
        for x,y in SP: F(cx+x,y+3)
    for x,y in [(-5,9),(-4,8),(-3,9),(-2,8),(-1,9),(0,8),(1,9),(2,8),(3,9),(4,8)]: F(x,y)
    F(-1,10,'#ff8fae'); F(0,10,'#ff8fae'); F(0,11,'#ff8fae')
    for p in [(hx+8,hy-9),(hx+7,hy-8),(hx+7,hy-7),(hx+8,hy-6),(hx-11,hy+5),(hx-10,hy+6)]: c.fix(*p,'#071030')
    return stars(c.render(dither=False),t,cx=hx,cy=hy-19,r=13)
def crumbling():
    img=wall(face='dizzy',sit=6,hold=False,lean=2,crack=2,nod=2)
    c=BC(W,H); spilled_cup(c)
    for (bx,by) in [(14,20),(62,16),(36,8),(70,34),(6,40)]:
        with c.group('fly%d'%bx): c.rect(bx,by,bx+6,by+3,'brick')
        c.bricky('fly%d'%bx,bx,by,7,4)
    fl=c.render(dither=False)
    out=Image.alpha_composite(fl,img)
    for (bx,by) in [(14,20),(62,16),(36,8)]:
        out.alpha_composite(fl.crop((bx-1,by-1,bx+8,by+5)),(bx-1,by-1))
    return out
FR=[]
for i,(nd,st,cu) in enumerate([(0,0,0),(0,1,0),(1,2,1),(1,3,1),(0,0,0),(0,1,0)]):
    FR.append((f'idle{i+1}',wall(nod=nd,steam=st,cupup=cu)))
FR.append(('hurt1',wall(lean=2,face='hurt',crack=1,cupup=-1,steam=None,headtilt=1)))
FR.append(('hurt2',wall(lean=3,face='hurt',crack=2,nod=1,cupup=-2,steam=None,headtilt=2)))
FR.append(('hurt3',wall(lean=1,crack=1,steam=2)))
FR.append(('ko1',wall(lean=2,face='dizzy',crack=2,steam=None)))
FR.append(('ko2',wall(lean=-1,face='dizzy',crack=2,steam=None)))
FR.append(('ko3',wall(lean=3,face='dizzy',crack=2,nod=1,steam=None)))
FR.append(('ko4',crumbling()))
FR.append(('ko5',rubble(0.5,settle=-3)))
for k,t in enumerate((0,1.1,2.2)):
    FR.append((f'ko{6+k}',rubble(t)))
if __name__=='__main__':
    sheet([im for _,im in FR],'wall2.png'); json.dump([n for n,_ in FR],open('wall2_names.json','w'))


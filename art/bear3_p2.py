import math
from pixart2 import Canvas, RAMPS, sheet
from PIL import Image
W=H=72
FONT={'B':["11.","1.1","11.","1.1","11."],'E':["111","1..","11.","1..","111"],'R':["11.","1.1","11.","11.","1.1"],'K':["1.1","1.1","11.","1.1","1.1"]}
def text(c,x,y,s,col):
    for ch in s:
        for j,row in enumerate(FONT[ch]):
            for i,v in enumerate(row):
                if v=='1': c.fix(x+i,y+j,col)
        x+=4

HATP=[]
def bear(bob=0,breathe=0,lean=0,face='mean',hat=(0,0),hatoff=False,sit=0,spat=0,spatdrop=False,headtilt=0,bridge=True,nod=0):
    c=Canvas(W,H); o=lean; b=bob+sit
    # legs (stubby) + feet pads
    for x0 in (26,43):
        with c.group('legs'):
            c.ell(x0+o,65,5.5,4.5,'fur')
        for k in (-2,0,2): c.fix(x0+o+k-1,69,'#5a2a14')      # toe lines on the sole edge
    # belly (fills down to the legs so nothing hangs between them)
    snap=c.snap()
    with c.group('body'):
        c.ell(34+o,51+b,15,12+breathe*.5,'fur')
    for y in range(61,H):           # trim the belly's lowest point so nothing hangs between the legs
        for x in range(W):
            if c.g[y][x]!=snap[0][y][x]: c.restore(x,y,snap)
    with c.group('legs'):
        c.rect(26+o,56+b,43+o,60,"fur"); c.rect(26+o,61,31+o,62,"fur"); c.rect(38+o,61,43+o,62,"fur")
    # maroon chef apron: neck strap, bib, skirt curving over the belly, BERK stitched into the cloth
    c.line(29+o,38+b,31+o,42+b,'apronr',2); c.line(39+o,38+b,37+o,42+b,'apronr',2)   # neck straps
    c.part='apron'
    c.rect(27+o,42+b,41+o,47+b,'apronr')
    for y in range(48,59):
        half=min(11.5,8.5+(y-48)*.4)
        c.rect(round(34-half)+o,y+b,round(34+half)+o,y+b,'apronr')
    c.part=None
    for x in range(24,45): c.fix(x+o,48+b,'#f0e2b8')                      # cream waist tie
    c.fix(23+o,49+b,'#f0e2b8'); c.fix(45+o,49+b,'#f0e2b8')
    # letters follow the curve of the belly (outer letters sit 1px lower), stitched shadow underneath
    for (ch,x,dy) in (('B',27,1),('E',31,0),('R',35,0),('K',39,1)):
        text(c,x+1+o,52+b+dy,ch,'#4a0812')
        text(c,x+o,51+b+dy,ch,'#f6ead2')
    for x in range(26,43,2): c.fix(x+o,57+b,'#c03448')                    # running stitch along the hem
    # near arm (outside the apron, viewer's left)
    # near arm: shoulder -> bent elbow -> forearm resting forward, chunky paw with pad and claws
    with c.group('narm'):
        c.ell(21+o,45+b,4.5,4.5,'fur')
        c.line(21+o,45+b,16+o,51+b,'fur',7)
        c.line(16+o,51+b,22+o,53+b,'fur',6)
        c.ell(23+o,53+b,4.6,3.6,'fur')
    for x,y in [(26,52),(26,54)]: c.fix(x+o,y+b,'#7a3a1c')                  # finger creases
    # far arm raises the spatula beside the head (viewer's right)
    if not spatdrop:
        ax,ay=56+o,38+b-spat+nod
        with c.group('farm'):
            c.ell(47+o,45+b,4.5,4.5,'fur'); c.line(47+o,45+b,ax,ay,'fur',7); c.ell(ax,ay,4,4,'fur')
        c.rect(ax-1,ay-17,ax,ay-4,'shoe')
        c.rect(ax-5,ay-31,ax+4,ay-17,'metal')
        for y in range(ay-31,ay-17): c.fix(ax-5,y,'#f4f8fc')
        for sx in (ax-3,ax,ax+3):
            for y in range(ay-28,ay-19): c.fix(sx,y,'#55657c')
    else:
        c.ell(47+o,46+b,4.5,4.5,'fur'); c.line(47+o,46+b,53+o,56+b,'fur',7); c.ell(53+o,57+b,4,3.5,'fur')
        c.rect(52,62,66,63,'shoe'); c.rect(58,58,67,67,'metal')
    # head (big, chibi)
    hx,hy=33+o+headtilt,28+b+nod
    for ex in (-13,12):
        c.ell(hx+ex,hy-12,5,5,'fur'); c.ell(hx+ex,hy-12,2.5,2.5,'muz')
    c.ell(hx,hy,17,14,'fur')
    c.ell(hx-5,hy+6,8.5,6,'muz')
    c.ell(hx-8,hy+2,3.8,2.6,'nose'); c.fix(hx-9,hy+1,'#8a7aa0'); c.fix(hx-8,hy+1,'#6b5a80')
    F=lambda x,y,col='#1b1033': c.fix(hx+x,hy+y,col)
    if bridge:
        for y in range(4,8): F(-8,y)
    if face=='mean':
        for x in range(-11,-4): F(x,8)
        F(-12,9);F(-4,9)
        for cx in (-6,5):
            for x in (cx-1,cx,cx+1):
                for y in (-4,-3,-2): F(x,y)
            F(cx-1,-4,'#ffffff')
        for x,y in [(-10,-8),(-9,-8),(-8,-7),(-7,-7),(-6,-6),(-5,-6)]: F(x,y,'#3b1f0e')
        for x,y in [(9,-8),(8,-8),(7,-7),(6,-7),(5,-6),(4,-6)]: F(x,y,'#3b1f0e')
    elif face=='hurt':
        for cx,d in ((-6,1),(5,-1)):
            for x,y in [(-1,-5),(0,-4),(1,-3),(0,-2),(-1,-1)]: F(cx+x*d,y)
        for x in range(-11,-5): F(x,8)
        for x in range(-10,-6): F(x,9,'#ff6f8f')
        F(15,-8,'#9cd8ff');F(15,-7,'#9cd8ff');F(16,-7,'#ffffff');F(15,-6,'#9cd8ff')
    elif face=='dizzy':
        SP=[(-2,-5),(-1,-5),(0,-5),(1,-5),(2,-4),(2,-3),(2,-2),(1,-1),(0,-1),(-1,-1),(-2,-2),(-2,-3),(-1,-3),(0,-3),(0,-2)]
        for cx in (-6,5):
            for x,y in SP: F(cx+x,y)                      # 5x5 spiral eyes
        for x,y in [(-11,8),(-10,9),(-9,8),(-8,9),(-7,8),(-6,9)]: F(x,y)   # wavy mouth
    if face!='hurt':
        F(-14,-1,'#ff9fae');F(-13,-1,'#ff9fae');F(10,-1,'#ff9fae');F(11,-1,'#ff9fae')
    # chef hat
    if not hatoff:
        tx,ty=hat
        HATP[:]=[hx+tx,hy+ty-19]
    img=c.render(dither=False)
    if not hatoff and HATP:
        from hat4 import apply_hat
        return apply_hat(img,HATP[0],HATP[1],14,'#7a3a1c')
    from hat4 import pad
    return pad(img)

def stars(img,t):
    im=img.copy()
    for k in range(3):
        a=t+k*2.09; x=round(32+17*math.cos(a)); y=round(9+3*math.sin(a))
        for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
            col=(255,243,168,255) if (dx or dy) else (255,255,255,255)
            if 0<=x+dx<W and 0<=y+dy<H: im.putpixel((x+dx,y+dy),col)
    return im
F=[]
for i,(nd,br) in enumerate([(0,0),(0,1),(1,1),(1,1),(1,0),(0,0)]):
    F.append((f'idle{i+1}',bear(breathe=br,nod=nd)))
F.append(('hurt1',bear(lean=2,face='hurt',headtilt=1,spat=2)))
F.append(('hurt2',bear(lean=3,face='hurt',headtilt=2,hat=(1,-1),bob=1,spat=3)))
F.append(('hurt3',bear(lean=1)))
F.append(('ko1',bear(lean=2,face='dizzy')))
F.append(('ko2',bear(lean=-1,face='dizzy')))
F.append(('ko3',bear(lean=3,face='dizzy',bob=1)))
F.append(('ko4',bear(lean=4,face='dizzy',sit=3)))
F.append(('ko5',bear(lean=4,face='dizzy',sit=6)))
# flat on his back: the same bear, rotated a clean 90 degrees and laid on the ground
def lying(t,dust=False):
    up=bear(face='dizzy',sit=4,bridge=False)
    sq=Image.new('RGBA',(84,84)); sq.alpha_composite(up,(6,0)); r=sq.rotate(-90,resample=Image.NEAREST)
    sq=Image.new('RGBA',(84,84)); sq.alpha_composite(r if r.size==(84,84) else r,(0,0)) if False else None
    bb=r.getbbox(); out=Image.new('RGBA',(W,84))
    dx=(W-(bb[2]-bb[0]))//2-bb[0]; dy=83-bb[3]
    out.alpha_composite(r,(dx,dy))
    hx,hy=83-6-28+dx,33+6+dy                     # where the head ended up
    im=out
    STAR=["..o..",".oyo.","oyyyo",".oyo.","o.o.o"]
    STAR=["..o..","ooyoo",".oyo.","oy.yo","o...o"]
    STAR=["..k..","..y..","kyyyk",".yky.","y...y"]
    for k in range(3):
        a=t+k*2.09; x0=round(hx+2+12*math.cos(a))-2; y0=round(hy-15+3*math.sin(a))-2
        for j,row in enumerate(STAR):
            for i,ch in enumerate(row):
                if ch=='.': continue
                col=(255,214,64,255) if ch=='y' else (122,74,0,255)
                x,y=x0+i,y0+j
                if 0<=x<W and 0<=y<84: im.putpixel((x,y),col)
    if dust:
        for (dx,dy) in [(-30,-2),(-27,-3),(-24,-1),(26,-2),(29,-3),(31,-1)]:
            x,y=hx+dx-14,84-2+dy
            for (ex,ey) in ((0,0),(1,0),(0,1),(1,1)):
                if 0<=x+ex<W and 0<=y+ey<84: im.putpixel((x+ex,y+ey),(230,220,200,220))
    return im
for k,t in enumerate((0,1.1,2.2)):
    F.append((f'ko{6+k}',lying(t,dust=(k==0))))
sheet([im for _,im in F],'bear3_p2.png')
import json; json.dump([n for n,_ in F],open('bear3_names.json','w'))

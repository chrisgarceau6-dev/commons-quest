import math
from pixart import Canvas, RAMPS, sheet
from PIL import Image
RAMPS.update({
 'fur':  ['#2a1406','#7a3f17','#a8602b','#c98144','#e3a463'],
 'muz':  ['#6e4520','#d39a62','#f0c48e','#f8d9ae','#fff0d8'],
 'pad':  ['#2a1406','#5a3a2a','#7a5040','#9a6a58','#b8857a'],
 'tie':  ['#3d0612','#7a1022','#b51f33','#d23a52','#f0647a'],
})
W=H=72
FONT={'B':["11.","1.1","11.","1.1","11."],'E':["111","1..","11.","1..","111"],'R':["11.","1.1","11.","11.","1.1"],'K':["1.1","1.1","11.","1.1","1.1"]}
def text(c,x,y,s,col):
    for ch in s:
        for j,row in enumerate(FONT[ch]):
            for i,v in enumerate(row):
                if v=='1': c.fix(x+i,y+j,col)
        x+=4

def bear(bob=0,breathe=0,lean=0,face='mean',hat=(0,0),hatoff=False,sit=0,spat=0,spatdrop=False,headtilt=0):
    c=Canvas(W,H); o=lean; b=bob+sit
    # legs (stubby) + feet pads
    for x0 in (26,43):
        c.ell(x0+o,65,5.5,4.5,'fur')
        c.ell(x0+o-1,68,3.5,1.6,'pad')
    # belly (fills down to the legs so nothing hangs between them)
    snap=[row[:] for row in c.g]
    c.ell(34+o,51+b,15,12+breathe*.5,'fur')
    for y in range(61,H):           # trim the belly's lowest point so nothing hangs between the legs
        for x in range(W):
            if c.g[y][x]!=snap[y][x]: c.g[y][x]=snap[y][x]
    c.rect(26+o,56+b,43+o,60,"fur"); c.rect(26+o,61,31+o,62,"fur"); c.rect(38+o,61,43+o,62,"fur")
    # apron
    c.rect(26+o,41+b,42+o,47+b,'white')
    for y in range(48,59):
        half=min(11.5,8.5+(y-48)*.4)
        c.rect(round(34-half)+o,y+b,round(34+half)+o,y+b,'white')
    c.rect(24+o,47+b,44+o,48+b,'tie')
    text(c,27+o,51+b,'BERK','#b51f33')
    for x in range(28,41): c.fix(x+o,58+b,'#c9cde0')
    # near arm (outside the apron, viewer's left)
    c.ell(21+o,45+b,4.5,4.5,'fur'); c.line(21+o,45+b,16+o,54+b,'fur',7); c.ell(16+o,55+b,4,3.5,'fur')
    for k in (-2,0,2): c.fix(13+o,55+b+k,'#fff3dc')
    # far arm raises the spatula beside the head (viewer's right)
    if not spatdrop:
        ax,ay=56+o,38+b-spat
        c.ell(47+o,45+b,4.5,4.5,'fur'); c.line(47+o,45+b,ax,ay,'fur',7); c.ell(ax,ay,4,4,'fur')
        c.rect(ax-1,ay-17,ax,ay-4,'shoe')
        c.rect(ax-5,ay-31,ax+4,ay-17,'metal')
        for sx in (ax-3,ax,ax+3):
            for y in range(ay-28,ay-19): c.fix(sx,y,'#55657c')
    else:
        c.ell(47+o,46+b,4.5,4.5,'fur'); c.line(47+o,46+b,53+o,56+b,'fur',7); c.ell(53+o,57+b,4,3.5,'fur')
        c.rect(52,62,66,63,'shoe'); c.rect(58,58,67,67,'metal')
    # head (big, chibi)
    hx,hy=33+o+headtilt,28+b
    for ex in (-13,12):
        c.ell(hx+ex,hy-12,5,5,'fur'); c.ell(hx+ex,hy-12,2.5,2.5,'muz')
    c.ell(hx,hy,17,14,'fur')
    c.ell(hx-8,hy+6,8.5,6,'muz')
    c.ell(hx-12,hy+2,3.6,2.6,'nose'); c.fix(hx-13,hy+1,'#8a7aa0'); c.fix(hx-12,hy+1,'#6b5a80')
    F=lambda x,y,col='#1b1033': c.fix(hx+x,hy+y,col)
    for y in range(4,8): F(-12,y)
    if face=='mean':
        for x in range(-11,-3): F(x,8)
        F(-10,9,'#ffffff');F(-5,9,'#ffffff');F(-10,8,'#ffffff');F(-5,8,'#ffffff')
        for cx in (-6,5):
            for x in (cx-1,cx,cx+1):
                for y in (-4,-3,-2): F(x,y)
            F(cx-1,-4,'#ffffff')
        for x,y in [(-10,-8),(-9,-8),(-8,-7),(-7,-7),(-6,-6),(-5,-6)]: F(x,y,'#3b1f0e')
        for x,y in [(9,-8),(8,-8),(7,-7),(6,-7),(5,-6),(4,-6)]: F(x,y,'#3b1f0e')
    elif face=='hurt':
        for cx,d in ((-6,1),(5,-1)):
            for x,y in [(-1,-5),(0,-4),(1,-3),(0,-2),(-1,-1)]: F(cx+x*d,y)
        for x in range(-11,-4): F(x,8)
        for x in range(-10,-5): F(x,9,'#ff6f8f')
        F(15,-8,'#9cd8ff');F(15,-7,'#9cd8ff');F(16,-7,'#ffffff');F(15,-6,'#9cd8ff')
    elif face=='dizzy':
        for cx in (-6,5):
            for x,y in [(-1,-4),(0,-4),(1,-4),(1,-3),(1,-2),(0,-2),(-1,-2),(-1,-3)]: F(cx+x,y)
            F(cx,-3,'#ffcf3d')
        for x in range(-10,-5): F(x,8)
        F(-9,9,'#ff6f8f');F(-8,9,'#ff6f8f')
    if face!='hurt':
        F(-14,-1,'#ff9fae');F(-13,-1,'#ff9fae');F(10,-1,'#ff9fae');F(11,-1,'#ff9fae')
    # chef hat
    if not hatoff:
        tx,ty=hat
        c.rect(hx-9+tx,hy-17+ty,hx+9+tx,hy-13+ty,'white')
        for (x,y,r) in ((-7,-21,5),(0,-23,6),(7,-21,5)): c.ell(hx+x+tx,hy+y+ty,r,r,'white')
    return c.render(dither=False)

def stars(img,t):
    im=img.copy()
    for k in range(3):
        a=t+k*2.09; x=round(32+17*math.cos(a)); y=round(9+3*math.sin(a))
        for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
            col=(255,243,168,255) if (dx or dy) else (255,255,255,255)
            if 0<=x+dx<W and 0<=y+dy<H: im.putpixel((x+dx,y+dy),col)
    return im
F=[]
for i,(bb,br,sp) in enumerate([(0,0,0),(0,1,0),(1,2,1),(1,2,1),(1,1,0),(0,0,0)]):
    F.append((f'idle{i+1}',bear(bob=bb,breathe=br,spat=sp)))
F.append(('hurt1',bear(lean=2,face='hurt',headtilt=1)))
F.append(('hurt2',bear(lean=3,face='hurt',headtilt=2,hat=(1,0),bob=1)))
F.append(('hurt3',bear(lean=1)))
F.append(('ko1',bear(lean=2,face='dizzy')))
F.append(('ko2',bear(lean=-1,face='dizzy')))
F.append(('ko3',bear(lean=2,face='dizzy',hat=(0,-3))))
F.append(('ko4',bear(lean=1,face='dizzy',hat=(0,-1))))
F.append(('ko5',bear(face='dizzy',sit=3)))
for k,t in enumerate((0,1.1,2.2)):
    F.append((f'ko{6+k}',stars(bear(face='dizzy',sit=4),t)))
sheet([im for _,im in F],'bear3.png')
import json; json.dump([n for n,_ in F],open('bear3_names.json','w'))

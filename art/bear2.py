import math
from pixart import Canvas, RAMPS, sheet
from PIL import Image
RAMPS.update({
 'fur':  ['#2a1406','#6a3816','#94562a','#b8763f','#d4955a'],
 'furdk':['#2a1406','#4f2a10','#6a3816','#8a4d22','#a8663a'],
 'muz':  ['#6e4520','#c08a50','#e0ad78','#f2cc9c','#fbe4c4'],
 'tie':  ['#3d0612','#6e0d20','#a5162f','#d23a52','#f0647a'],
})
W=H=72
FONT={'B':["11.","1.1","11.","1.1","11."],'E':["111","1..","11.","1..","111"],'R':["11.","1.1","11.","1.1","1.1"],'K':["1.1","1.1","11.","1.1","1.1"]}
def text(c,x,y,s,col):
    for ch in s:
        for j,row in enumerate(FONT[ch]):
            for i,v in enumerate(row):
                if v=='1': c.fix(x+i,y+j,col)
        x+=4

def bear(bob=0, breathe=0, head=0, lean=0, arm=0, face='mean', hat=(0,0), hatoff=False, sit=0):
    c=Canvas(W,H)
    o=lean; b=bob
    by=b+sit
    # far arm (behind body)
    c.line(50+o,36+by,55+o,52+by,'furdk',7); c.ell(55+o,54+by,3.5,3,'furdk')
    # legs
    if not sit:
        for x0 in (27,43):
            c.rect(x0+o,56,x0+9+o,66,'fur'); c.ell(x0+3+o,67,6,2.6,'fur')
    else:
        c.ell(25+o,64,8,4,'fur'); c.ell(48+o,65,7,3.5,'furdk')
    # body: hump + big pear belly
    c.ell(44+o,32+by,13,9,'fur')
    c.ell(37+o,46+by,18,15+breathe*.6,'fur')
    # apron
    c.rect(27+o,36+by,43+o,42+by,'white')
    c.rect(29+o,35+by,41+o,35+by,'white')
    for y in range(43,58):
        if y+by>=66: break
        half=min(12,8+(y-43)*.5)-(1 if y==57 else 0)
        c.rect(round(35-half)+o,y+by,round(35+half)+o,y+by,'white')
    c.rect(24+o,42+by,46+o,43+by,'tie')
    text(c,28+o,46+by,'BERK','#a5162f')
    for x in range(30,41): c.fix(x+o,53+by,'#b9bdd6')
    # near arm (shoulder pivot) + paw + spatula
    sx,sy=31+o,36+by
    px,py=21+o-arm,50+by
    c.ell(sx,sy,4,4,'fur'); c.line(sx,sy,px,py,'fur',7); c.ell(px,py+1,4,3.5,'fur')
    for k in (-2,0,2): c.fix(px-3,py+1+k,'#fff3dc')
    hx,hy=px-1,py-2
    ang=math.radians(-140+arm*6)
    ex,ey=hx+9*math.cos(ang),hy+9*math.sin(ang)
    c.line(hx,hy,ex,ey,'shoe',2)
    ca,sa=math.cos(ang),math.sin(ang); qx,qy=-sa,ca
    for t in range(0,8):
        for k in (-3,-2,-1,0,1,2,3):
            c.px(ex+t*ca+k*qx, ey+t*sa+k*qy,'metal')
    for t in (2,4,6):
        for k in (-1.5,1.5):
            c.fix(round(ex+t*ca+k*qx),round(ey+t*sa+k*qy),'#55657c')
    # head
    hx0,hy0=24+o,24+b+head+sit
    c.ell(hx0+7,hy0-9,3.6,3.6,'fur'); c.ell(hx0+7,hy0-9,1.6,1.6,'muz')
    c.ell(hx0-3,hy0-9,3.4,3.4,'fur'); c.ell(hx0-3,hy0-9,1.5,1.5,'muz')
    c.ell(hx0,hy0,11,10,'fur')
    c.ell(hx0-8,hy0+4,6.5,4.6,'muz')
    c.rect(hx0-15,hy0+1,hx0-11,hy0+3,'nose'); c.fix(hx0-14,hy0+1,'#6b5a80')
    F=lambda x,y,col='#1b1033': c.fix(hx0+x,hy0+y,col)
    if face=='mean':
        for x in (-5,-4,-3):
            for y in (-3,-2,-1): F(x,y)
        F(-5,-3,'#ffffff');F(-4,-3,'#ffcf3d')
        for x in (3,4):
            for y in (-3,-2,-1): F(x,y)
        F(3,-3,'#ffcf3d')
        for i,(x,y) in enumerate([(-6,-6),(-5,-5),(-4,-5),(-3,-4)]): F(x,y,'#2a1406')
        for x,y in [(5,-6),(4,-5),(3,-5),(2,-4)]: F(x,y,'#2a1406')
        for x in range(-13,-6): F(x,6)
        F(-12,7,'#ffffff');F(-8,7,'#ffffff')
    elif face=='hurt':
        for x,y in [(-5,-4),(-4,-3),(-5,-2),(4,-4),(3,-3),(4,-2)]: F(x,y)
        for x in range(-12,-7): F(x,6)
        for x in range(-11,-8): F(x,7,'#ff6f8f')
        F(-11,5);F(-8,5)
        F(9,-6,'#9cd8ff');F(9,-5,'#9cd8ff');F(10,-5,'#ffffff')
    elif face=='dizzy':
        for (cx,cy) in ((-4,-3),(4,-3)):
            for x,y in [(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0)]: F(cx+x,cy+y)
        for x in range(-12,-7): F(x,6)
        F(-10,7,'#ff6f8f')
    # chef hat
    if not hatoff:
        tx,ty=hat
        c.rect(hx0-6+tx,hy0-12+ty,hx0+9+tx,hy0-9+ty,'white')
        for (x,y,r) in ((-4,-15,4),(1,-17,4.6),(6,-15,4)): c.ell(hx0+x+tx,hy0+y+ty,r,r,'white')
    img=c.render()
    return img

def stars(img,t):
    im=img.copy()
    for k in range(3):
        a=t+k*2.09; x=round(24+12*math.cos(a)); y=round(20+3*math.sin(a))
        for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
            col=(255,243,168,255) if (dx or dy) else (255,255,255,255)
            if 0<=x+dx<W and 0<=y+dy<H: im.putpixel((x+dx,y+dy),col)
    return im

F=[]
for i,(bb,br,hd,arm) in enumerate([(0,0,0,0),(0,1,0,1),(1,1,1,2),(1,2,1,2),(1,1,1,1),(0,0,0,0)]):
    F.append((f'idle{i+1}',bear(bob=bb,breathe=br,head=hd,arm=arm)))
F.append(('hurt1',bear(lean=2,face='hurt',arm=-1)))
F.append(('hurt2',bear(lean=3,head=1,face='hurt',arm=-2,hat=(1,0))))
F.append(('hurt3',bear(lean=1,face='mean',arm=0)))
F.append(('ko1',bear(lean=2,face='dizzy')))
F.append(('ko2',bear(lean=-1,face='dizzy',head=1)))
F.append(('ko3',bear(lean=2,face='dizzy',hat=(2,-6))))
F.append(('ko4',bear(lean=1,face='dizzy',hat=(5,-14))))
F.append(('ko5',bear(face='dizzy',sit=6,hatoff=True)))
F.append(('ko6',stars(bear(face='dizzy',sit=8,head=3,lean=2,hatoff=True),0)))
F.append(('ko7',stars(bear(face='dizzy',sit=8,head=3,lean=2,hatoff=True),1.1)))
F.append(('ko8',stars(bear(face='dizzy',sit=8,head=3,lean=2,hatoff=True),2.2)))
sheet([im for _,im in F],'bear2.png')
import json; json.dump([n for n,_ in F],open('bear2_names.json','w'))
print(len(F))

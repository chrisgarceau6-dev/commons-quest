import math
from pixart import Canvas, RAMPS, sheet
from PIL import Image
RAMPS.update({
 'drg':  ['#0d2a14','#2a7a36','#3fa84a','#62c766','#97e08f'],
 'drgdk':['#0d2a14','#1f5a28','#2a7a36','#3a9446','#56b05e'],
 'wing': ['#0d2a14','#5a2a6e','#7a3d94','#9a5ab4','#bd86d4'],
 'bellyc':['#5a4a1e','#d8c27a','#f0dc98','#f8ecbc','#fff8dc'],
 'horn': ['#3a2e1e','#b8a888','#e2d6b8','#f2ead4','#ffffff'],
 'bottle':['#1a0c04','#4a2008','#6e3010','#8e4a20','#b06a38'],
 'label':['#5a2a00','#d8761e','#f4a23a','#ffc46a','#ffe2a8'],
 'tie':  ['#3d0612','#7a1022','#b51f33','#d23a52','#f0647a'],
 'cap':  ['#0b0618','#1b1033','#2b1d3a','#4a3b5c','#6b5a80'],
})
W,H=82,72
FONT={'W':["1...1","1...1","1.1.1","11.11","1...1"],'O':["111","1.1","1.1","1.1","111"]}
def text(c,x,y,s,col):
    for ch in s:
        g=FONT[ch]
        for j,row in enumerate(g):
            for i,v in enumerate(row):
                if v=='1': c.fix(x+i,y+j,col)
        x+=len(g[0])+1

def wyrm(bob=0,breathe=0,lean=0,face='mean',wing=0,tail=0,smoke=0,sit=0,headtilt=0):
    c=Canvas(W,H); o=lean+10; b=bob+sit
    from PIL import ImageDraw
    # tail (behind): short, thick, curls up; cream underside + little ridge spikes
    pts=[(45,57),(53,59),(59,56),(61,50)]
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        c.line(x0+o,y0+b,x1+o,y1+b,'drg',6 if x0<55 else 5)
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):           # cream underside stripe
        c.line(x0+o,y0+b+2,x1+o+1,y1+b+1,'bellyc',2)
    tx,ty=61+o,49+b+tail
    for (dx,dy) in [(0,-1),(-1,-2),(1,-2),(-2,-3),(0,-3),(2,-3),(-1,-4),(0,-4),(1,-4),(0,-5)]: c.px(tx+dx,ty+dy,'drgdk')
    for (x,y) in [(50,56),(55,55),(59,52)]:             # ridge spikes on top
        c.px(x+o,y+b-1,'drgdk'); c.px(x+o,y+b-2,'drgdk'); c.px(x+o+1,y+b-1,'drgdk')
    # far wing (behind body): bone arm, three fingers, scalloped membrane
    sh=(47+o,35+b)
    wr=(57+o,20+b-wing)                                  # wrist
    tips=[(70+o,22+b-wing),(71+o,32+b-wing//2),(62+o,40+b)]
    scal=[(65+o,27+b-wing),(64+o,35+b-wing//2),(55+o,40+b)]
    poly=[sh,wr,tips[0],scal[0],tips[1],scal[1],tips[2],scal[2]]
    m=Image.new('L',(W,H),0); ImageDraw.Draw(m).polygon(poly,fill=1)
    for y in range(H):
        for x in range(W):
            if m.getpixel((x,y)) and c.g[y][x] is None: c.g[y][x]='wing'
    c.line(sh[0],sh[1],wr[0],wr[1],'drgdk',3)            # arm bone
    for t in tips: c.line(wr[0],wr[1],t[0],t[1],'drgdk',1)   # finger bones
    c.px(wr[0],wr[1]-1,'horn'); c.px(wr[0]-1,wr[1]-2,'horn') # wrist claw
    # legs
    for x0 in (27,43):
        c.ell(x0+o,65,5.5,4.5,'drg')
        for k in (-3,0,3): c.fix(x0+o+k-1,69,'#f4f5ff')
    # body with trimmed bottom
    snap=[row[:] for row in c.g]
    c.ell(35+o,51+b,14.5,12+breathe*.5,'drg')
    c.ell(32+o,53+b,9,9,'bellyc')
    for y in range(61,H):
        for x in range(W):
            if c.g[y][x]!=snap[y][x]: c.g[y][x]=snap[y][x]
    for y in (48,52,56):
        for x in range(26,39): 
            if c.g[y+b][x+o]=='bellyc': c.fix(x+o,y+b,'#c8b06a')
    # near arm: shoulder -> elbow -> forearm, outlined so it reads in front of the body
    shx,shy=22+o,45+b; elx,ely=19+o,54+b; hdx,hdy=6+o,56+b
    before=[row[:] for row in c.g]
    c.ell(shx,shy,4.5,4.5,'drg')
    c.line(shx,shy,elx,ely,'drg',5)
    c.line(elx,ely,hdx+2,hdy,'drg',5)
    c.ell(hdx+1,hdy,3.4,3.2,'drg')
    armpx={(x,y) for y in range(H) for x in range(W) if c.g[y][x]!=before[y][x]}
    for (x,y) in armpx:
        for dx,dy in ((1,0),(0,1),(1,1)):
            n=(x+dx,y+dy)
            if n not in armpx and 0<=n[0]<W and 0<=n[1]<H and c.g[n[1]][n[0]] is not None: c.fix(n[0],n[1],'#0d2a14')
    # whisk: wooden handle under the paw, thin separate wires above it (hand-pixeled)
    c.rect(hdx-1,hdy+2,hdx,hdy+10,'bottle'); c.rect(hdx-2,hdy+10,hdx+1,hdy+11,'bottle')
    wx0,wy0=hdx-0.5,hdy-10
    wires=set()
    for rxw in (1,3,5):
        for a in range(0,360,2):
            x=round(wx0+rxw*math.cos(math.radians(a))); y=round(wy0+8*math.sin(math.radians(a)))
            if y<=hdy-3: wires.add((x,y))
    for x in range(round(wx0)-5,round(wx0)+6):          # crisp silhouette outline around the balloon
        pass
    occupied=lambda x,y: 0<=x<W and 0<=y<H and c.g[y][x] is not None
    for (x,y) in wires:                                   # dark outline so wires read against the sky
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            n=(x+dx,y+dy)
            if n not in wires and not occupied(*n) and abs(n[0]-wx0)>4.4: c.fix(n[0],n[1],'#2d3746')
    for (x,y) in wires:
        col='#dfe7f1' if x<wx0 else '#8e9bb0'
        if y<wy0-6: col='#f4f8fc'
        c.fix(x,y,col)
    for (x,y) in [(hdx-1,hdy-3),(hdx,hdy-3),(hdx-1,hdy-2),(hdx,hdy-2),(hdx-2,hdy-3),(hdx+1,hdy-3)]: c.fix(x,y,'#7d8ca3')   # collar
    for k in (-2,0,2): c.fix(hdx-2,hdy+k,'#f2ead4')
    hx,hy=31+o+headtilt,26+b
    # back spikes
    for (x,y,h) in [(38,16,5),(43,19,5),(46,24,5),(47,30,4),(48,36,4)]:
        for k in range(h):
            w=(h-k)//2
            c.rect(x+o-w+k//2,y+b-k,x+o+w+k//2,y+b-k,'drgdk')
    # head
    hx,hy=31+o+headtilt,26+b
    c.ell(hx+3,hy+12,11,4.5,'drg')   # neck joins head to body
    c.ell(hx,hy,15,12,'drg')
    c.ell(hx-14,hy+4,8.5,6,'drg')
    c.ell(hx-13,hy+9.6,6.5,1.4,'bellyc')
    # horns
    c.line(hx-4,hy-10,hx-9,hy-19,'horn',3); c.line(hx-9,hy-19,hx-12,hy-21,'horn',2)
    c.line(hx+6,hy-10,hx+8,hy-20,'horn',3); c.line(hx+8,hy-20,hx+6,hy-23,'horn',2)
    # cheek fin
    for k in range(4): c.px(hx+13+k,hy+2-k,'drgdk'); c.px(hx+13+k,hy+3-k,'drgdk')
    # bandana: covers the chest exactly, following the body outline, tied under the jaw, V point at the bottom
    hxx,hyy,rx,ry=31+o+headtilt,26+b,15,12
    def hb(x):
        t=(x-hxx)/rx
        return None if abs(t)>=1 else hyy+ry*math.sqrt(1-t*t)
    bcx=35+o                                   # body centre line
    def vline(x): return 57+b-abs(x-bcx)*1.15
    solid={(x,y) for y in range(H) for x in range(W) if c.g[y][x] is not None and c.g[y][x]!='metal' and c.g[y][x]!='bottle'}
    P=set()
    for x in range(round(hxx-8),W):
        h=hb(x)
        top=(h+1) if h is not None else 40+b
        for y in range(int(top),int(vline(x))+1):
            if (x,y) in solid and c.g[y][x] in ('drg','bellyc','drgdk'): P.add((x,y))
    if P:
        def edge(x,y): return any((x+dx,y+dy) not in P for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)))
        for (x,y) in P:
            rel=x-bcx; col='#b51f33'
            if rel>3: col='#9a1a2c'
            if rel>8: col='#7a1022'
            if rel<-5: col='#c9283f'
            h=hb(x)
            if h is not None and y<=h+3: col='#a01b30' if rel>2 else '#c9283f'      # the band around the neck
            if h is not None and abs(y-(h+4))<0.5: col='#7a1022'                    # crease where band meets the point
            if (abs(x-(bcx-6+(y-47)*0.55))<0.5 or abs(x-(bcx+6-(y-47)*0.55))<0.5) and y>49: col='#8a1226'  # folds
            if edge(x,y): col='#3d0612'
            c.fix(x,y,col)
        for y in range(47+b,int(vline(bcx))-1):
            for x in (round(bcx-(57+b-y)/1.15)+1,round(bcx+(57+b-y)/1.15)-1):
                if (x,y) in P and not edge(x,y) and y%2==0: c.fix(x,y,'#f6d2d8')
        text(c,bcx-6,44+b,'WOO','#ffffff')
        # knot tucked at the back of the neck
        kx=round(hxx+11); ky=int(hb(kx) or 38+b)+1
        for (dx,dy,col) in [(0,0,'#3d0612'),(1,0,'#b51f33'),(2,0,'#3d0612'),(0,1,'#9a1a2c'),(1,1,'#7a1022'),(2,1,'#9a1a2c'),(1,2,'#3d0612'),(2,2,'#9a1a2c'),(3,3,'#7a1022'),(3,2,'#3d0612'),(4,4,'#3d0612')]:
            if c.g[ky+dy][kx+dx] is not None: c.fix(kx+dx,ky+dy,col)
    # eye sockets + brow ridges (part of the head shape, same every frame)
    for cx in (-6,5): c.ell(hx+cx,hy-2,3.6,3.4,'drgdk')
    F0=lambda x,y,col: c.fix(hx+x,hy+y,col)
    # forehead scales
    for (x,y) in [(-9,-9),(-4,-10),(1,-10),(6,-9),(-6,-12),(-1,-12),(4,-12),(10,-6),(12,-2),(9,4),(4,6)]:
        F0(x,y,'#36964a');F0(x+1,y,'#36964a');F0(x-1,y+1,'#36964a');F0(x+2,y+1,'#36964a')
    # snout ridge highlight + nostrils
    for x in range(-21,-11): F0(x,-2+((x+21)//5),'#97e08f')
    for (x,y) in [(-22,1),(-21,1),(-19,0),(-18,0)]: F0(x,y,'#0d2a14')
    F0(-22,0,'#62c766');F0(-19,-1,'#62c766')
    # jaw frills
    for k in range(3): c.px(hx+8+k*2,hy+11-k,'drgdk'); c.px(hx+8+k*2,hy+12-k,'drgdk')
    F=lambda x,y,col='#1b1033': c.fix(hx+x,hy+y,col)
    F(-20,1);F(-18,1)   # nostrils
    if face=='mean':
        for cx in (-6,5):
            for x in (cx-2,cx-1,cx,cx+1,cx+2):
                for y in (-4,-3,-2,-1,0): F(x,y,'#ffe24a')
            for x in (cx-2,cx+2): F(x,0,'#e0a800')
            for y in (-4,-3,-2,-1,0): F(cx,y)
            F(cx-2,-4,'#ffffff');F(cx-1,-4,'#ffffff')
        for x,y in [(-10,-8),(-9,-8),(-8,-7),(-7,-7),(-6,-6),(-5,-6),(-4,-6),(-3,-5)]: F(x,y,'#0d2a14');F(x,y-1,'#1f5a28')
        for x,y in [(9,-8),(8,-8),(7,-7),(6,-7),(5,-6),(4,-6),(3,-6),(2,-5)]: F(x,y,'#0d2a14');F(x,y-1,'#1f5a28')
        for x in range(-21,-6): F(x,8)
        for x in (-18,-14,-10): F(x,9,'#ffffff')
        F(-16,7,'#ffffff')
    elif face=='hurt':
        for cx,d in ((-6,1),(5,-1)):
            for x,y in [(-1,-5),(0,-4),(1,-3),(0,-2),(-1,-1)]: F(cx+x*d,y)
        for x in range(-19,-8): F(x,8)
        for x in range(-17,-11): F(x,9,'#ff6f8f')
        F(14,-8,'#9cd8ff');F(14,-7,'#9cd8ff');F(15,-7,'#ffffff');F(14,-6,'#9cd8ff')
    elif face=='dizzy':
        for cx in (-6,5):
            for x,y in [(-1,-4),(0,-4),(1,-4),(1,-3),(1,-2),(0,-2),(-1,-2),(-1,-3)]: F(cx+x,y)
            F(cx,-3,'#ffcf3d')
        for x in range(-18,-9): F(x,8)
        F(-14,9,'#ff6f8f');F(-13,9,'#ff6f8f')
    img=c.render(dither=False)
    if smoke:
        for i,(dx,dy,r) in enumerate([(-24,-2,1.5),(-27,-5,2),(-29,-9,2.5)][:smoke]):
            cx,cy=hx-0+dx+o*0,hy+dy
            for y in range(int(cy-r)-1,int(cy+r)+2):
                for x in range(int(cx-r)-1,int(cx+r)+2):
                    if (x-cx)**2+(y-cy)**2<=r*r and 0<=x<W and 0<=y<H and img.getpixel((x,y))[3]==0:
                        img.putpixel((x,y),(230,230,240,200))
    return img

def stars(img,t):
    im=img.copy()
    for k in range(3):
        a=t+k*2.09; x=round(40+16*math.cos(a)); y=round(6+3*math.sin(a))
        for dx,dy in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
            col=(255,243,168,255) if (dx or dy) else (255,255,255,255)
            if 0<=x+dx<W and 0<=y+dy<H: im.putpixel((x+dx,y+dy),col)
    return im
F=[]
for i,(bb,br,wg,tl,sm) in enumerate([(0,0,0,0,0),(0,1,2,1,0),(1,2,4,2,1),(1,2,4,2,2),(1,1,2,1,3),(0,0,0,0,0)]):
    F.append((f'idle{i+1}',wyrm(bob=bb,breathe=br,wing=wg,tail=tl,smoke=sm)))
F.append(('hurt1',wyrm(lean=2,face='hurt',headtilt=1,wing=2)))
F.append(('hurt2',wyrm(lean=3,face='hurt',headtilt=2,bob=1,wing=4,tail=2)))
F.append(('hurt3',wyrm(lean=1,wing=1)))
F.append(('ko1',wyrm(lean=2,face='dizzy')))
F.append(('ko2',wyrm(lean=-1,face='dizzy')))
F.append(('ko3',wyrm(lean=2,face='dizzy',wing=2)))
F.append(('ko4',wyrm(lean=1,face='dizzy')))
F.append(('ko5',wyrm(face='dizzy',sit=3)))
for k,t in enumerate((0,1.1,2.2)):
    F.append((f'ko{6+k}',stars(wyrm(face='dizzy',sit=4,headtilt=1),t)))
sheet([im for _,im in F],'wyrm.png')
import json; json.dump([n for n,_ in F],open('wyrm_names.json','w'))

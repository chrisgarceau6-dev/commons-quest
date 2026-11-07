import math
from pixart2 import Canvas, RAMPS, sheet
from PIL import Image
W,H=82,72
FONT={'W':["1...1","1...1","1.1.1","11.11","1...1"],'O':["111","1.1","1.1","1.1","111"]}
def text(c,x,y,s,col):
    for ch in s:
        g=FONT[ch]
        for j,row in enumerate(g):
            for i,v in enumerate(row):
                if v=='1': c.fix(x+i,y+j,col)
        x+=len(g[0])+1

def draw_whisk(c,hdx,hdy,tiltdeg):
    W,H=c.w,c.h
    tilt=math.radians(tiltdeg); ax_,ay_=-math.sin(tilt),-math.cos(tilt); px2,py2=math.cos(tilt),-math.sin(tilt)
    P=lambda u,v:(hdx+ax_*u+px2*v, hdy+ay_*u+py2*v)
    a0,a1=P(-8,0),P(4,0); c.line(a0[0],a0[1],a1[0],a1[1],'metal',2)
    e0,e1=P(-9,-1),P(-9,1); c.line(e0[0],e0[1],e1[0],e1[1],'shoe',2)     # handle end cap
    wires={}
    for k in range(0,401):
        t=k/400; u=5+18*t
        hw=0.8+3.4*math.sin(math.pi*min(t*1.05,1))**0.75 if t<0.999 else 0
        for f2 in (-1,-0.42,0.42,1):
            x,y=P(u,f2*hw); wires[(round(x),round(y))]=f2
    occupied=lambda x,y: 0<=x<W and 0<=y<H and c.g[y][x] is not None
    for (x,y),f2 in wires.items():
        if abs(f2)==1:
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                n=(x+dx,y+dy)
                if n not in wires and not occupied(*n):
                    # only outline on the outside of the balloon
                    cx,cy=P(14,0)
                    if (n[0]-cx)**2+(n[1]-cy)**2 > (x-cx)**2+(y-cy)**2: c.fix(n[0],n[1],'#2d3746')
    for (x,y),f2 in wires.items():
        c.fix(x,y,{-1:'#f4f8fc',-0.42:'#8e9bb0',0.42:'#7d8ca3',1:'#aebdd0'}[f2])
    for u in (3,4,5):
        for v in (-1.5,-0.5,0.5,1.5):
            x,y=P(u,v); c.fix(round(x),round(y),'#4a5468' if u==3 else '#7d8ca3')   # ferrule


def wyrm(bob=0,breathe=0,lean=0,face='mean',wing=0,tail=0,smoke=0,sit=0,headtilt=0,holdwhisk=True):
    c=Canvas(W,H); o=lean+10; b=bob+sit
    from PIL import ImageDraw
    # tail (behind): short, thick, curls up; cream underside + little ridge spikes
    pts=[(45,57),(53,59),(58,57),(60,52)]
    c.part='tail'
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        c.line(x0+o,y0+b,x1+o,y1+b,'drg',6 if x0<55 else 5)
    c.part=None
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):           # cream underside stripe
        c.line(x0+o,y0+b+2,x1+o+1,y1+b+1,'bellyc',2)
    tx,ty=60+o,51+b+tail
    for (dx,dy) in [(0,-1),(-1,-2),(1,-2),(-2,-3),(0,-3),(2,-3),(-1,-4),(0,-4),(1,-4),(0,-5)]: c.px(tx+dx,ty+dy,'drgdk')
    for (x,y) in [(50,56),(55,55),(59,52)]:             # ridge spikes on top
        c.px(x+o,y+b-1,'drgdk'); c.px(x+o,y+b-2,'drgdk'); c.px(x+o+1,y+b-1,'drgdk')
    # far wing (behind body): arched leading edge, three curved fingers, scalloped membrane
    def qb(p0,p1,p2,n=14):
        return [((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0],(1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]) for t in [k/n for k in range(n+1)]]
    sh=(47+o,39+b); wr=(58+o,22+b-wing)
    tips=[(68+o,23+b-wing),(67+o,32+b-wing//2),(60+o,39+b)]
    lead=qb(sh,(47+o,26+b-wing),wr)
    poly=list(lead)
    prev=wr
    for k,t in enumerate(tips):
        if k==0: poly+=qb(wr,(64+o,19+b-wing),t,8)[1:]
        else:
            mid=((prev[0]+t[0])/2,(prev[1]+t[1])/2); ctrl=(mid[0]+(wr[0]-mid[0])*0.45,mid[1]+(wr[1]-mid[1])*0.45)
            poly+=qb(prev,ctrl,t,8)[1:]
        prev=t
    end=(52+o,44+b); mid=((prev[0]+end[0])/2,(prev[1]+end[1])/2); ctrl=(mid[0]+(wr[0]-mid[0])*0.4,mid[1]+(wr[1]-mid[1])*0.4)
    poly+=qb(prev,ctrl,end,8)[1:]
    m=Image.new('L',(W,H),0); ImageDraw.Draw(m).polygon(poly,fill=1)
    for y in range(H):
        for x in range(W):
            if m.getpixel((x,y)) and c.g[y][x] is None:
                c.g[y][x]='wing'; c.pid[y][x]='wingm'
                d=math.hypot(x-wr[0],y-wr[1])/20.0
                c.sh[y][x]=max(0.12,0.95-0.8*d)
    with c.group('wingbone'):
        for (a,b2) in zip(lead,lead[1:]): c.line(a[0],a[1],b2[0],b2[1],'wingb',3)
    for k,t in enumerate(tips):
        bend=((wr[0]+t[0])/2+(t[1]-wr[1])*0.12,(wr[1]+t[1])/2-(t[0]-wr[0])*0.12)
        pts=qb(wr,bend,t,10)
        with c.group('finger%d'%k):
            for (a,b2) in zip(pts,pts[1:]): c.line(a[0],a[1],b2[0],b2[1],'wingb',2)
    # legs
    for x0 in (27,43):
        c.ell(x0+o,65,5.5,4.5,'drg')
        for k in (-3,0,3): c.fix(x0+o+k-1,69,'#f4f5ff')
    # body with trimmed bottom
    snap=c.snap()
    c.ell(35+o,51+b,14.5,12+breathe*.5,'drg')
    c.ell(32+o,53+b,9,9,'bellyc')
    for y in range(61,H):
        for x in range(W):
            if c.g[y][x]!=snap[0][y][x]: c.restore(x,y,snap)
    for y in (48,52,56):
        for x in range(26,39): 
            if c.g[y+b][x+o]=='bellyc': c.fix(x+o,y+b,'#c8b06a')
    with c.group('farpaw'):
        c.ell(47+o,53+b,3.4,3,'drg')
    for k in (-1,1): c.fix(45+o,53+b+k,'#f2ead4')
    # near arm: shoulder -> elbow -> forearm, outlined so it reads in front of the body
    shx,shy=22+o,45+b
    if holdwhisk: elx,ely,hdx,hdy=18+o,57+b,7+o,55+b
    else: elx,ely,hdx,hdy=17+o,52+b,17+o,59+b
    before=[row[:] for row in c.g]
    with c.group('narm'):
        c.ell(shx,shy,4.5,4.5,'drg')
        c.line(shx,shy,elx,ely,'drg',5)
        c.line(elx,ely,hdx+2,hdy,'drg',5)
        c.ell(hdx+1,hdy,3.4,3.2,'drg')
    armpx={(x,y) for y in range(H) for x in range(W) if c.g[y][x]!=before[y][x]}
    for (x,y) in armpx:
        for dx,dy in ((1,0),(0,1),(1,1)):
            n=(x+dx,y+dy)
            if n not in armpx and 0<=n[0]<W and 0<=n[1]<H and c.g[n[1]][n[0]] is not None: c.fix(n[0],n[1],'#0d2a14')
    if holdwhisk: draw_whisk(c,hdx,hdy,0)
    c.ell(hdx+1,hdy,3.4,3.2,'drg') if False else None
    for k in (-2,0,2): c.fix(hdx-2,hdy+k,'#f2ead4')
    hx,hy=31+o+headtilt,26+b
    # back spikes
    c.part='spikes'
    for (x,y,h) in [(38,16,5),(43,19,5),(46,24,5),(47,30,4),(48,36,4)]:
        for k in range(h):
            w=(h-k)//2
            c.rect(x+o-w+k//2,y+b-k,x+o+w+k//2,y+b-k,'drgdk')
    c.part=None
    # head
    hx,hy=31+o+headtilt,26+b
    c.part='head'
    c.ell(hx+3,hy+12,11,4.5,'drg')   # neck joins head to body
    c.ell(hx,hy,15,12,'drg')
    c.ell(hx-11,hy+4,7.5,5.5,'drg')
    c.part=None
    # horns
    with c.group('horn1'):
        c.line(hx-4,hy-10,hx-8,hy-16,'horn',4); c.line(hx-8,hy-16,hx-10,hy-19,'horn',2)
    with c.group('horn2'):
        c.line(hx+6,hy-10,hx+8,hy-16,'horn',4); c.line(hx+8,hy-16,hx+7,hy-19,'horn',2)
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
    F0=lambda x,y,col: c.fix(hx+x,hy+y,col)
    for x in range(-16,-9):
        yy=-1+((x+16)//4)
        if c.g[hy+yy][hx+x]=='drg' and c.g[hy+yy-1][hx+x]=='drg': F0(x,yy,'#a8de86')
    F=lambda x,y,col='#1b1033': c.fix(hx+x,hy+y,col)
    F(-17,1);F(-16,1);F(-14,0)   # nostrils
    if face=='mean':
        for cx,hw in ((-6,2),(5,1)):                      # near eye wide, far eye narrower (3/4 view)
            for x in range(cx-hw,cx+hw+1):
                for y in (-4,-3,-2,-1,0): F(x,y,'#ffe24a')
            for x in range(cx-hw,cx+hw+1): F(x,0,'#e0a800')
            for y in (-4,-3,-2,-1,0): F(cx,y)
            F(cx-hw,-4,'#ffffff')
        for x,y in [(-10,-8),(-9,-8),(-8,-7),(-7,-7),(-6,-6),(-5,-6),(-4,-6),(-3,-5)]: F(x,y,'#0d2a14');F(x,y-1,'#1f5a28')
        for x,y in [(9,-8),(8,-8),(7,-7),(6,-7),(5,-6),(4,-6),(3,-6),(2,-5)]: F(x,y,'#0d2a14');F(x,y-1,'#1f5a28')
        for x in range(-17,-5): F(x,8)
        F(-14,9,'#ffffff');F(-14,10,'#ffffff')            # one fang
    elif face=='hurt':
        for cx,d in ((-6,1),(5,-1)):
            for x,y in [(-2,-5),(-1,-5),(-1,-4),(0,-4),(0,-3),(1,-3),(0,-2),(-1,-2),(-1,-1),(-2,-1)]: F(cx+x*d,y)
        for x in range(-16,-7): F(x,8)
        for x in range(-14,-10): F(x,9,'#ff6f8f')
        F(14,-8,'#9cd8ff');F(14,-7,'#9cd8ff');F(15,-7,'#ffffff');F(14,-6,'#9cd8ff')
    elif face=='dizzy':
        SP=[(-2,-5),(-1,-5),(0,-5),(1,-5),(2,-4),(2,-3),(2,-2),(1,-1),(0,-1),(-1,-1),(-2,-2),(-2,-3),(-1,-3),(0,-3),(0,-2)]
        for cx in (-6,5):
            for x,y in [(cx+a,b2) for a in range(-2,3) for b2 in range(-5,0)]: F(x,y,'#ffe24a')
            for x,y in SP: F(cx+x,y)
        for x in range(-15,-8): F(x,8)
        F(-12,9,'#ff6f8f');F(-11,9,'#ff6f8f')
    img=c.render(dither=False)
    if smoke:
        for i,(dx,dy,r) in enumerate([(-24,-2,1.5),(-27,-5,2),(-29,-9,2.5)][:smoke]):
            cx,cy=hx-0+dx+o*0,hy+dy
            for y in range(int(cy-r)-1,int(cy+r)+2):
                for x in range(int(cx-r)-1,int(cx+r)+2):
                    if (x-cx)**2+(y-cy)**2<=r*r and 0<=x<W and 0<=y<H and img.getpixel((x,y))[3]==0:
                        img.putpixel((x,y),(255,255,255,255) if (x-cx)**2+(y-cy)**2<=(r-1)**2 else (196,206,222,255))
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
    F.append((f'idle{i+1}',wyrm(bob=0,breathe=br,wing=wg,tail=tl,smoke=sm)))
F.append(('hurt1',wyrm(lean=2,face='hurt',headtilt=1,wing=2)))
F.append(('hurt2',wyrm(lean=3,face='hurt',headtilt=2,bob=1,wing=4,tail=2)))
F.append(('hurt3',wyrm(lean=1,wing=1)))
F.append(('ko1',wyrm(lean=2,face='dizzy')))
F.append(('ko2',wyrm(lean=-1,face='dizzy')))
F.append(('ko3',wyrm(lean=3,face='dizzy',bob=1)))
_b=wyrm(lean=3,face='dizzy',sit=3,holdwhisk=False); _wc=Canvas(W,H); draw_whisk(_wc,12,H-12,-55)
F.append(('ko4',Image.alpha_composite(_b,_wc.render())))      # whisk tumbling out of his paw
def slumped(t,whisk_y_off=0):
    body=wyrm(face='dizzy',sit=7,lean=2,headtilt=1,holdwhisk=False,wing=-2)
    wc=Canvas(W,H); draw_whisk(wc,12,H-3+whisk_y_off,-90)
    out=Image.alpha_composite(body,wc.render())
    STAR=["..k..","..y..","kyyyk",".yky.","y...y"]
    for k in range(3):
        a=t+k*2.09; x0=round(43+16*math.cos(a))-2; y0=round(8+3*math.sin(a))-2
        for j,row in enumerate(STAR):
            for i,ch in enumerate(row):
                if ch=='.': continue
                x,y=x0+i,y0+j
                if 0<=x<W and 0<=y<H: out.putpixel((x,y),(255,214,64,255) if ch=='y' else (122,74,0,255))
    return out
F.append(('ko5',slumped(0,-3)))
for k,t in enumerate((0,1.1,2.2)):
    F.append((f'ko{6+k}',slumped(t)))
sheet([im for _,im in F],'wyrm_p2.png')
import json; json.dump([n for n,_ in F],open('wyrm_names.json','w'))

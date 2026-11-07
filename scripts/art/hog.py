import math, json
from pixart2 import Canvas, RAMPS, CONTRAST, sheet
from PIL import Image
RAMPS.update({
 'pig':  ['#5e1e30','#d9788f','#f4a0b2','#ffc2cf','#ffe2e9'],
 'pigdk':['#5e1e30','#c0607a','#dc8399','#ee9fb1','#f8b8c6'],
 'snout':['#5e1e30','#e47f98','#f9adbf','#ffcdd8','#ffe6ec'],
 'ovr':  ['#0c2618','#1d5534','#2c7a48','#43995e','#6cbd80'],
 'ovrdk':['#0c2618','#174a2c','#226a3e','#2f8250','#4a9e66'],
 'tee':  ['#4a4e6e','#c4c9e0','#eef0fa','#ffffff','#ffffff'],
 'iron': ['#08080e','#1e2029','#30333f','#474b5c','#666b80'],
 'hoof': ['#1a0c10','#3a2026','#553038','#6e4650','#8a6068'],
})
CONTRAST.update({'pig':0.7,'snout':0.6,'ovr':0.75,'tee':0.7,'iron':0.5})
W=H=84; GY=82
class HC(Canvas):
    """Detail pixels remember which part they were painted on; anything drawn over that part later hides them."""
    def __init__(s,w,h): super().__init__(w,h); s.det=[]
    def fix(s,x,y,color):
        x,y=int(round(x)),int(round(y))
        if 0<=x<s.w and 0<=y<s.h: s.det.append((x,y,color,s.pid[y][x]))
    def render(s,**k):
        s.fixed={}
        for x,y,col,p in s.det:
            if s.pid[y][x]==p: s.fixed[(x,y)]=col
        return super().render(**k)
FONT={'H':["1.1","1.1","111","1.1","1.1"],'A':[".1.","1.1","111","1.1","1.1"],
      'M':["1...1","11.11","1.1.1","1...1","1...1"],'P':["11.","1.1","11.","1..","1.."]}
def text(c,x,y,s,col):
    for ch in s:
        for j,row in enumerate(FONT[ch]):
            for i,v in enumerate(row):
                if v=='1': c.fix(x+i,y+j,col)
        x+=len(FONT[ch][0])+1
def poly(c,pts,m,shade=0.62):
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    for y in range(int(min(ys))-1,int(max(ys))+2):
        for x in range(int(min(xs))-1,int(max(xs))+2):
            px_,py_=x+0.5,y+0.5; ins=False; j=len(pts)-1
            for i in range(len(pts)):
                xi,yi=pts[i]; xj,yj=pts[j]
                if (yi>py_)!=(yj>py_) and px_<(xj-xi)*(py_-yi)/(yj-yi)+xi: ins=not ins
                j=i
            if ins: c.px(x,y,m,shade)
def pan(c,px,py,egg=True,tilt=0):
    """cast-iron skillet seen face-on, a fried egg in it; handle hangs down to the paw"""
    with c.group('panh'): c.line(px+tilt,py+9,px+tilt*2,py+19,'iron',3)
    with c.group('pan'):
        c.ell(px,py,10,8.5,'iron')
    for a in range(0,360,4):                       # inner rim ring
        x=round(px+8*math.cos(math.radians(a))); y=round(py+6.6*math.sin(math.radians(a)))
        c.fix(x,y,'#1a1c24')
    for x,y in [(px-6,py-5),(px-5,py-6),(px-4,py-6),(px-7,py-4)]: c.fix(x,y,'#8a90a8')   # rim glint
    if egg:
        for y in range(py-4,py+5):
            for x in range(px-6,px+7):
                if ((x-px+0.5)/6.2)**2+((y-py-0.3)/4.6)**2+0.12*math.sin(x*1.7+y)<=1: c.fix(x,y,'#fbfbf4')
        for x in range(px-5,px+6):
            if ((x-px+0.5)/6.2)**2+((py+4-py-0.3)/4.6)**2<=1.1: c.fix(x,py+4,'#d8dbe6')
        for y in range(py-2,py+2):
            for x in range(px-2,px+3):
                if ((x-px-0.3)/2.4)**2+((y-py+0.2)/2.0)**2<=1: c.fix(x,y,'#ffb21e')
        c.fix(px-1,py-1,'#ffe18a'); c.fix(px,py-1,'#ffe18a'); c.fix(px+2,py+1,'#e08a00'); c.fix(px+1,py+1,'#e89a10')
def hog(breathe=0,nod=0,lean=0,face='smug',sit=0,panup=0,hold=True,headtilt=0,tail=0,ears=0,snort=0,flinch=0):
    c=HC(W,H); o=lean; b=sit
    # tail: little corkscrew on the far hip, drawn first so the body overlaps its root
    tx,ty=59+o,60+b
    CURL=["..oooo.",".o1111o","o1o..o1o","o1o.o11o","o11o1oo.",".oo1o...","...o1o..","....o..."]
    for j,row in enumerate(CURL):
        for i,ch in enumerate(row):
            if ch=='o': c.fix(tx+i+tail*(j<4),ty+j,'#7a2a40')
            elif ch=='1': c.fix(tx+i+tail*(j<4),ty+j,'#f4a0b2' if j<3 else '#d9788f')
    # legs: overall cuffs + hooves
    for x0 in (34,50):
        with c.group('legs'):
            c.rect(x0-5+o,69,x0+5+o,77,'ovr')
        with c.group('hoof%d'%x0):
            c.ell(x0+o,79,5.5,3.2,'hoof')
        c.fix(x0+o,79,'#1a0c10'); c.fix(x0+o,80,'#1a0c10'); c.fix(x0+o,81,'#1a0c10')     # cloven split
        for x in range(x0-5,x0+6): c.fix(x+o,72,'#43995e' if x%2 else '#2c7a48')        # rolled cuff edge
    snap=c.snap()
    # body: pink barrel; the overalls cover the bottom
    with c.group('body'):
        c.ell(42+o,58+b,18,14+breathe*.5,'pig')
    with c.group('tee'):
        c.ell(42+o,52+b,15,8,'tee')
    with c.group('ovr'):
        for y in range(56,71):
            half=min(17.5,13+(y-56)*.6) if y<66 else 17.5-(y-66)*0.4
            c.rect(round(42-half)+o,y+b if y<66 else y,round(42+half)+o,y+b if y<66 else y,'ovr')
        c.rect(31+o,44+b,53+o,57+b,'ovr')                                           # bib
    for y in range(64,H):                                                           # body never shows below the overalls
        for x in range(W):
            if c.g[y][x]=='pig' and snap[0][y][x]!='pig' and y>=69: c.restore(x,y,snap)
    for y in range(64+b,H):                                                         # nothing hangs between the legs
        for x in range(39+o,46+o):
            if y>=68 and c.g[y][x] in ('ovr','pig'): c.restore(x,y,snap)
    for y in range(69,74): c.fix(41+o,y,'#0c2618'); c.fix(42+o,y,'#0c2618')            # inseam
    # straps + brass buttons
    with c.group('strap'):
        c.line(33+o,44+b,30+o,38+b,'ovr',3); c.line(51+o,44+b,54+o,38+b,'ovr',3)
    for bx in (33,51):
        c.fix(bx+o,45+b,'#7a5a10'); c.fix(bx+1+o,45+b,'#f2c84a'); c.fix(bx+o,46+b,'#c99a28'); c.fix(bx+1+o,46+b,'#a07818')
    # bib pocket with HAMP stitched in cream thread
    for x in range(32,53): c.fix(x+o,48+b,'#1d5534')
    for x in range(33,52,2): c.fix(x+o,49+b,'#8fd6a0')          # running stitch along pocket top
    for y in range(58,66):                                       # side seam + pocket on the hip
        c.fix(26+o,y+b,'#1d5534')
    # near arm: fist on hip (smug)
    with c.group('narm'):
        c.ell(26+o,48+b,4.2,3.8,'tee')
        c.line(24+o,52+b,19+o,58+b,'pig',6)
        c.line(19+o,58+b,25+o,62+b,'pig',5.5)
    with c.group('nhand'): c.ell(26+o,61+b,3.6,3.2,'pigdk')
    c.fix(27+o,60+b,'#5e1e30'); c.fix(27+o,62+b,'#5e1e30')
    # far arm raising the skillet
    if hold:
        hx_,hy_=63+o,43+b-panup+nod
        with c.group('farm'):
            c.ell(57+o,48+b,4.2,3.8,'tee'); c.line(58+o,50+b,hx_,hy_,'pig',6)
        pan(c,hx_+2,hy_-26,egg=True)
        with c.group('fhand'): c.ell(hx_,hy_-1,3.6,3.4,'pigdk')
    else:
        with c.group('farm'):
            c.ell(57+o,48+b,4.2,3.8,'tee'); c.line(58+o,50+b,62+o,60+b,'pig',6)
        with c.group('fhand'): c.ell(62+o,61+b,3.6,3.2,'pigdk')
    # head: big round pig head
    hx,hy=41+o+headtilt,30+b+nod
    for sx in (-1,1):                                            # pointed ears, tips flopping forward
        with c.group('ear%d'%sx):
            poly(c,[(hx+sx*4,hy-12),(hx+sx*15,hy-8+ears),(hx+sx*18,hy-21-ears),(hx+sx*8,hy-17)],'pig',0.75 if sx<0 else 0.5)
        with c.group('earin%d'%sx):
            poly(c,[(hx+sx*8,hy-13),(hx+sx*14,hy-10+ears),(hx+sx*16,hy-18-ears)],'pigdk',0.45)
        with c.group('eartip%d'%sx):
            poly(c,[(hx+sx*13,hy-19-ears),(hx+sx*20,hy-20-ears),(hx+sx*19,hy-13)],'pig',0.4)
    with c.group('head'):
        c.ell(hx,hy,18,15,'pig')
        c.ell(hx,hy+7,15,8,'pig')                                # jowls
    # snout
    sxn,syn=hx-1,hy+4
    with c.group('snout'):
        c.ell(sxn,syn,8.5-snort*0.5,5.8,'snout')
    for a_ in range(0,360,3):                                    # crisp rim so the snout pops off the face
        x=round(sxn+(8.9-snort*0.5)*math.cos(math.radians(a_))); y=round(syn+6.2*math.sin(math.radians(a_)))
        c.fix(x,y,'#b8506c' if y<syn else '#8a3050')
    for nx in (-4,2):                                            # nostrils
        pts=[(0,0),(1,0),(0,1),(1,1),(0,2),(1,2)] + ([(-1,1),(2,1)] if snort else [])
        for dx,dy in pts: c.fix(sxn+nx+dx,syn-1+dy,'#6a1e36')
        c.fix(sxn+nx,syn-1,'#4a1024')
    c.fix(sxn-5,syn-4,'#ffffff'); c.fix(sxn-4,syn-4,'#ffffff'); c.fix(sxn-6,syn-3,'#ffe6ec')   # snout shine
    F=lambda x,y,col='#1b1033': c.fix(hx+x,hy+y,col)
    if face=='smug':
        for cx in (-8,7):                                         # half-lidded, looking down at you
            for x in (cx-1,cx,cx+1):
                F(x,-3); F(x,-2)
            F(cx+1,-3,'#ffffff')
            for x in (cx-2,cx-1,cx,cx+1,cx+2): F(x,-4,'#5e1e30')     # heavy upper lid
        for x,y in [(-11,-8),(-10,-8),(-9,-7),(-8,-7),(-7,-7)]: F(x,y,'#7a2a40')   # one cocky brow up
        for x,y in [(5,-6),(6,-6),(7,-6),(8,-6),(9,-6)]: F(x,y,'#7a2a40')
        for x,y in [(-5,12),(-4,13),(-3,13),(-2,13),(-1,13),(0,13),(1,13),(2,13),(3,12),(4,11)]: F(x,y,'#5e1e30')   # lopsided smirk
        # straw of wheat in the smirk
        for i in range(10): F(5+i,11-i*0.55,'#e8c050' if i%2 else '#b8881e')
        F(14,5,'#f4d878');F(15,4,'#f4d878');F(15,5,'#e8c050');F(16,4,'#c99a28');F(14,4,'#e8c050');F(16,3,'#f4d878')
    elif face=='hurt':
        for cx,d in ((-8,1),(7,-1)):
            for x,y in [(-1,-5),(0,-4),(1,-3),(0,-2),(-1,-1)]: F(cx+x*d,y)
        for x in range(-4,3): F(x,11)
        for x in range(-3,2): F(x,12,'#ff6f8f')
        F(17,-9,'#9cd8ff');F(17,-8,'#9cd8ff');F(18,-8,'#ffffff');F(17,-7,'#9cd8ff')
    elif face=='dizzy':
        SP=[(-2,-5),(-1,-5),(0,-5),(1,-5),(2,-4),(2,-3),(2,-2),(1,-1),(0,-1),(-1,-1),(-2,-2),(-2,-3),(-1,-3),(0,-3),(0,-2)]
        for cx in (-8,7):
            for x,y in SP: F(cx+x,y)
        for x,y in [(-4,11),(-3,12),(-2,11),(-1,12),(0,11),(1,12),(2,11)]: F(x,y)
        F(-1,13,'#ff8fae'); F(0,13,'#ff8fae'); F(0,14,'#ff8fae')    # tongue out
    if face!='hurt':
        for x in (-14,-13,11,12): F(x,1,'#ff7a96')
    from nametag import stitch
    stitch(c,'HAMP',51+b,'ovr',FONT,'#f6ecd2','#123a22')
    return c.render(dither=False)
STAR=["..k..","..y..","kyyyk",".yky.","y...y"]
def stars(im,t,cx=41,cy=6):
    for k in range(3):
        a=t+k*2.09; x0=round(cx+16*math.cos(a))-2; y0=round(cy+3*math.sin(a))-2
        for j,row in enumerate(STAR):
            for i,ch in enumerate(row):
                if ch=='.': continue
                x,y=x0+i,y0+j
                if 0<=x<W and 0<=y<H: im.putpixel((x,y),(255,214,64,255) if ch=='y' else (122,74,0,255))
    return im
def ground_pan(body,x=12,y=GY-1,air=0,splat=True):
    lc=HC(W,H)
    if air:                                       # tumbling down: skillet on its edge
        with lc.group('panh'): lc.line(x+6,y-air+2,x+14,y-air+7,'iron',2.5)
        with lc.group('pan'): lc.ell(x,y-air,7.5,4.2,'iron')
        for xx in range(x-5,x+6): lc.fix(xx,y-air-1,'#1a1c24')
        lc.fix(x-4,y-air-3,'#8a90a8'); lc.fix(x-3,y-air-3,'#8a90a8')
    else:
        with lc.group('pan'): lc.ell(x,y-2,9,3.2,'iron')        # lying flat, face up
        with lc.group('panh'): lc.line(x+8,y-1,x+15,y,'iron',3)
    img=lc.render()
    if not air:
        for xx in range(x-6,x+7): img.putpixel((xx,y-3),(26,28,36,255))
    if splat:                                     # the egg is still in the pan, a little squished
        for ex in range(-5,6):
            img.putpixel((x+ex,y-3),(251,251,244,255))
            if abs(ex)<4: img.putpixel((x+ex,y-4),(251,251,244,255))
        for ex in (-1,0,1): img.putpixel((x+ex,y-4),(255,178,30,255))
        img.putpixel((x,y-5),(255,178,30,255)); img.putpixel((x-1,y-5),(255,225,138,255))
    return Image.alpha_composite(img,body)
FR=[]
for i,(br,nd,sn,tl) in enumerate([(0,0,0,0),(1,0,0,1),(1,1,1,1),(1,1,1,0),(0,1,0,0),(0,0,0,-1)]):
    FR.append((f'idle{i+1}',hog(breathe=br,nod=nd,snort=sn,tail=tl,panup=nd)))
FR.append(('hurt1',hog(lean=2,face='hurt',headtilt=1,ears=2,panup=-2)))
FR.append(('hurt2',hog(lean=3,face='hurt',headtilt=2,nod=1,ears=3,panup=-3,tail=1)))
FR.append(('hurt3',hog(lean=1,ears=1)))
FR.append(('ko1',hog(lean=2,face='dizzy',ears=2)))
FR.append(('ko2',hog(lean=-1,face='dizzy',ears=1)))
FR.append(('ko3',hog(lean=3,face='dizzy',nod=1,ears=3)))
FR.append(('ko4',ground_pan(hog(lean=3,face='dizzy',sit=3,hold=False,ears=3),air=10,splat=False)))
FR.append(('ko5',ground_pan(hog(lean=2,face='dizzy',sit=6,hold=False,headtilt=1,nod=1,ears=4))))
for k,t in enumerate((0,1.1,2.2)):
    FR.append((f'ko{6+k}',stars(ground_pan(hog(lean=2,face='dizzy',sit=7,hold=False,headtilt=1,nod=2,ears=4,tail=k%2)),t)))
if __name__=='__main__':
    sheet([im for _,im in FR],'hog.png'); json.dump([n for n,_ in FR],open('hog_names.json','w'))

    S=5; im=hog()
    bg=Image.new('RGBA',(W*S,H*S),(143,211,255,255)); bg.alpha_composite(im.resize((W*S,H*S),Image.NEAREST)); bg.save('preview__hog.png')

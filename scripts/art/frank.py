import math, json
from pixart2 import Canvas, RAMPS, sheet
from PIL import Image
RAMPS.update({
 'fskin':['#2a3a26','#7c9a72','#a3c294','#c2dcb2','#e0f0d0'],
 'fhair':['#05060a','#151821','#232838','#323a50','#465070'],
 'coat': ['#12141c','#2c303e','#424859','#5c6478','#7e8798'],
 'pants':['#16223a','#2e4670','#3f5f94','#5a7cb4','#86a4d6'],
 'soup': ['#6e2a08','#c8601a','#ec8a2a','#ffad4a','#ffd08a'],
 'boot': ['#0c0806','#24170f','#3a2618','#553824','#744e32'],
})
import pixart2; pixart2.CONTRAST['fskin']=0.55; pixart2.CONTRAST['coat']=0.8
W,H0=76,72
H=H0+12
HATP=[]; CX=[]
FONT={'F':["111","1..","11.","1..","1.."],'R':["11.","1.1","11.","11.","1.1"],'A':[".1.","1.1","111","1.1","1.1"],
      'N':["1..1","11.1","1.11","1..1","1..1"],'K':["1.1","1.1","11.","1.1","1.1"]}
def text(c,x,y,s,col):
    for ch in s:
        g=FONT[ch]
        for j,row in enumerate(g):
            for i,v in enumerate(row):
                if v=='1': c.fix(x+i,y+j,col)
        x+=len(g[0])+1

def ladle(c,hx,hy,tiltdeg=0,ground=False):
    t=math.radians(tiltdeg); ax,ay=math.sin(t),-math.cos(t); px,py=math.cos(t),math.sin(t)
    P=lambda u,v:(hx+ax*u+px*v, hy+ay*u+py*v)
    a,b=P(-6,0),P(20,0)
    c.line(a[0],a[1],b[0],b[1],'metal',2)                       # long handle
    h1,h2=P(20,0),P(22,-2); c.line(h1[0],h1[1],h2[0],h2[1],'metal',2)   # hook at the top
    bx,by=P(-10,0)
    with c.group('bowl'):
        c.ell(bx,by,7,5,'metal')
    # soup in the bowl (top surface)
    for u in (-6.4,-7.4):
        for k in range(-5,6):
            x,y=P(u,k); c.fix(round(x),round(y),'#ec8a2a' if u<-7 else '#c8601a')
    for k in (-3,0,3):
        x,y=P(-7.4,k); c.fix(round(x),round(y),'#ffd08a')

def ladle2(c,x,y,steam=True):
    # handle through the fist, hook curling at the top
    with c.group('handle'):
        c.line(x+1,y-22,x,y+6,'metal',2)
        c.line(x+1,y-22,x-1,y-25,'metal',2); c.line(x-1,y-25,x-3,y-24,'metal',2); c.line(x-3,y-24,x-3,y-22,'metal',2)
    # deep cup: lower half of an ellipse, rim on top
    cx,cy=x-5,y+8
    with c.group('cup'):
        for yy in range(int(cy),int(cy+7)+1):
            for xx in range(int(cx-8),int(cx+9)):
                if ((xx-cx)/8.2)**2+((yy-cy)/7)**2<=1: c.px(xx,yy,'metal',shade=0.75-0.5*((xx-cx+8)/16)-0.2*((yy-cy)/7))
    for xx in range(int(cx-7),int(cx+8)):                       # soup filling the cup
        c.fix(xx,cy,'#ec8a2a'); c.fix(xx,cy+1,'#c8601a')
    for xx in (cx-5,cx-1,cx+3): c.fix(round(xx),cy,'#ffc46a')
    for xx in range(int(cx-8),int(cx+9)): c.fix(xx,cy-1,'#2a3240')   # rim outline
    c.fix(round(cx-6),cy+3,'#ffffff'); c.fix(round(cx-6),cy+4,'#eef4fa')  # shine
    if steam:
        for (dx,dy) in [(-4,-3),(-5,-4),(-4,-5),(-3,-6),(1,-3),(2,-4),(1,-5),(2,-6),(1,-7)]:
            c.fix(round(cx+dx),cy+dy,'#ffffff')
def ladle_up(c,x,y):
    with c.group('handle'):
        c.line(x,y-6,x,y+12,'metal',2)
    c.line(x,y+12,x+2,y+15,'metal',2)                 # single curved hook at the bottom
    with c.group('bowl'):
        c.ell(x,y-11,6.5,4.6,'metal')
    for xx in range(-5,6):                               # soup surface filling the bowl
        for yy in (-14,-13):
            if abs(xx)<=5-(1 if yy==-14 else 0): c.fix(x+xx,y+yy,'#ec8a2a' if yy==-13 else '#ffad4a')
    for xx in (-3,1,3): c.fix(x+xx,y-14,'#ffe0a8')
    c.fix(x-4,y-10,'#ffffff'); c.fix(x-4,y-9,'#eef4fa')  # bowl shine
def ladle_flat(c,x,y,spill=True):
    # the same ladle lying on its side: bowl on the left, handle to the right, soup spilled in front
    with c.group('handle'):
        c.line(x+5,y,x+23,y,'metal',2)
    c.line(x+23,y,x+26,y-2,'metal',2)
    with c.group('bowl'):
        c.ell(x,y-2,4.6,6,'metal')
    c.fix(x-2,y-5,'#ffffff'); c.fix(x-2,y-4,'#eef4fa')
    if spill:
        for (dx,dy) in [(-9,2),(-8,2),(-7,2),(-6,2),(-5,3),(-4,3),(-8,1),(-7,1),(-10,3),(-9,3),(-6,3),(-3,3)]:
            c.fix(x+dx,y+dy,'#ec8a2a')
        for (dx,dy) in [(-8,1),(-6,2)]: c.fix(x+dx,y+dy,'#ffad4a')
def frank(nod=0,breathe=0,lean=0,face='mean',sit=0,headtilt=0,hold=True,flinch=0):
    c=Canvas(W,H0); o=lean+4; b=sit
    hb=b+nod                                     # head / upper parts
    # boots + short legs
    for x0 in (26,42):
        with c.group('legs'):
            c.rect(x0-4+o,54,x0+3+o,63,'pants')
        c.ell(x0+o-1,66,6.5,3.6,'boot')
        c.fix(x0+o-5,65,'#744e32'); c.fix(x0+o-4,64,'#744e32')
    # far arm (behind the coat), hanging
    with c.group('farm'):
        c.line(50+o,44+b,53+o,56+b,'coat',6)
        c.ell(53.5+o,58.5+b,3.2,3,'fskin')
    # coat: broad shoulders, boxy body
    with c.group('coat'):
        c.ell(34+o,45+b,17,7,'coat')
        c.rect(18+o,44+b,50+o,56+b,'coat')
        c.ell(34+o,53+b,16+breathe*.5,6,'coat')
    for x in range(19,50):                       # hem line
        if 56+b<H and c.g[56+b][x+o]=='coat': c.fix(x+o,56+b,'#2c303e')
    # chef collar
    with c.group('collar'):
        c.rect(25+o,38+hb,43+o,41+b,'coat')
    # name tag + buttons
    # FRANK embroidered across the chest in cream thread, with a stitched shadow
    for x in range(24,46,2): c.fix(x+o,50+b,'#6a7288')                          # running stitch underline
    for y in (51,54):
        for x in (28,40):
            c.fix(x+o,y+b,'#e9ecf8'); c.fix(x+o+1,y+b,'#b9c0dc'); c.fix(x+o,y+b+1,'#2c303e'); c.fix(x+o+1,y+b+1,'#2c303e')
    for y in range(50+b,56+b): c.fix(34+o,y,'#2c303e')            # jacket overlap seam (below the tag)
    # near arm: shoulder -> elbow -> fist around the ladle
    shx,shy=19+o,45+b
    if hold:
        hdx,hdy=11+o,42+b+nod
        ladle2(c,hdx,hdy)
        with c.group('narm'):
            c.ell(shx,shy,4.6,4.6,'coat'); c.line(shx,shy,13+o,52+b,'coat',6); c.line(13+o,52+b,hdx+1,hdy+1,'coat',5)
        c.ell(hdx,hdy,3.2,3,'fskin')
        for k in (-1,1): c.fix(hdx-2,hdy+k,'#7c9a72')
    else:
        with c.group('narm'):
            c.ell(shx,shy,4.6,4.6,'coat'); c.line(shx,shy,15+o,53+b,'coat',6)
        c.ell(15+o,56+b,3.2,3,'fskin')
    # head: wide, boxy jaw, flat top under the hair
    hx,hy=34+o+headtilt,24+hb
    with c.group('head'):
        c.ell(hx,hy+2,17,12.5,'fskin')
        c.rect(hx-16,hy-5,hx+16,hy+8,'fskin')
        c.ell(hx,hy+9,15,5.5,'fskin')
    c.ell(hx+15,hy+2,2.2,3,'fskin')              # ear (far side)
    # tufts of black hair peeking out under the hat
    pass
    # big chef's hat, centred: band + three puffs
    HATP[:]=[hx,hy-8]
    # neck bolts
    for sx in (-1,1):
        x0=hx-19 if sx<0 else hx+16
        with c.group('bolt%d'%sx):
            c.rect(x0,hy+7,x0+3,hy+8,'metal')                       # shaft out of the side of the jaw
        hx2=x0-1 if sx<0 else x0+4
        with c.group('bolthead%d'%sx):
            c.rect(hx2-(1 if sx<0 else 0),hy+5,hx2+(0 if sx<0 else 1),hy+10,'metal')   # hex head
    F=lambda x,y,col='#151821': c.fix(hx+x,hy+y,col)
    # forehead stitches
    for x in range(-6,7): F(x,-3,'#3a5034')
    for x in (-5,-2,1,4): F(x,-4,'#3a5034'); F(x,-2,'#3a5034')
    # heavy brow: thick, dipping toward the nose (grumpy)
    for x in range(-13,5):
        F(x,0 if x not in (-13,4) else -1,'#232838')
        if -9<=x<=0: F(x,1,'#232838')
    for (x,y) in [(-14,6),(-13,6),(5,6),(6,6)]: F(x,y,'#d39a9a')
    # nose: a squared bump with a shadow underneath
    for (x,y,col) in [(-6,4,'#c2dcb2'),(-5,4,'#a3c294'),(-6,5,'#a3c294'),(-5,5,'#a3c294'),(-4,5,'#7c9a72'),(-6,6,'#5c7a54'),(-5,6,'#5c7a54')]: F(x,y,col)
    if face=='mean':
        # near eye 4x3, far eye 3x3 (3/4 view), pupils looking toward the hero
        # near eye 5x3 (wider), far eye 3x3; heavy lids, pupils looking at the hero
        for cx in (-10,1):
            for x in range(cx-1,cx+2):
                for y in (2,3,4): F(x,y,'#151821')
            F(cx-1,2,'#ffffff')
            F(cx-2,3,'#e8f0dc'); F(cx+2,3,'#e8f0dc')
            for x in range(cx-1,cx+2): F(x,5,'#7c9a72')
        # flat grin with stitches and one tooth
        for x in range(-11,4): F(x,9)
        for x in (-8,-4,0): F(x,8);F(x,10)
        F(-6,9,'#f4f8e8')
    elif face=='hurt':
        for x,y in [(-12,2),(-11,2),(-10,3),(-9,3),(-10,4),(-11,4),(-12,4)]: F(x,y)
        for x,y in [(2,2),(1,2),(0,3),(-1,3),(0,4),(1,4),(2,4)]: F(x,y)
        for x in range(-10,3): F(x,8); F(x,11)
        for x in range(-9,2): F(x,9,'#f4f8e8'); F(x,10,'#f4f8e8')
        for x in (-7,-4,-1): F(x,9); F(x,10)
        F(-10,9);F(-10,10);F(2,9);F(2,10)
        for x,y,col in [(18,-4,'#ffffff'),(18,-3,'#9cd8ff'),(17,-3,'#9cd8ff'),(18,-2,'#5ab0f0'),(17,-2,'#5ab0f0')]: F(x,y,col)
    elif face=='dizzy':
        SP=[(-2,-2),(-1,-2),(0,-2),(1,-2),(2,-1),(2,0),(2,1),(1,2),(0,2),(-1,2),(-2,1),(-2,0),(-1,0),(0,0),(0,1)]
        for cx,cy in ((-10,3),(1,3)):
            for x,y in SP: F(cx+x,cy+y)
        for x,y in [(-11,9),(-10,10),(-9,9),(-8,10),(-7,9),(-6,10),(-5,9)]: F(x,y)
        F(-8,11,'#ff7a90')
    import hat7
    from nametag import stitch
    CX.append((stitch(c,'FRANK',44+b,'coat',FONT,'#f0e2b8','#1a1c24',cx=None),34+o))
    return hat7.apply(c.render(),HATP[0],HATP[1]+6,'#5c7a54',pad=12,bw=30,puff=12,body=8,stripe=[(40,44,58,255),(62,68,86,255),(92,100,122,255)])

STAR=["..k..","..y..","kyyyk",".yky.","y...y"]
def stars(im,t,cx=38,cy=4):
    for k in range(3):
        a=t+k*2.09; x0=round(cx+17*math.cos(a))-2; y0=round(cy+3*math.sin(a))-2
        for j,row in enumerate(STAR):
            for i,ch in enumerate(row):
                if ch=='.': continue
                x,y=x0+i,y0+j
                if 0<=x<W and 0<=y<H: im.putpixel((x,y),(255,214,64,255) if ch=='y' else (122,74,0,255))
    return im
def with_ladle_on_ground(body,x=13,y=H-3,spill=True):
    lc=Canvas(W,H)
    if spill:                                            # soup puddle around the upturned cup
        for xx in range(x-11,x+10):
            lc.fix(xx,y,'#ec8a2a'); 
            if x-8<=xx<=x+7: lc.fix(xx,y-1,'#ec8a2a')
        for xx in (x-9,x-4,x+5): lc.fix(xx,y-1,'#ffc46a')
    with lc.group('cupdown'):                           # cup landed upside-down: a dome
        for yy in range(y-7,y):
            for xx in range(x-8,x+9):
                if ((xx-x)/8.2)**2+((yy-(y-1))/6.5)**2<=1:
                    lc.px(xx,yy,'metal',shade=0.95-0.6*((xx-x+8)/16)-0.15*((yy-y+7)/7))
    with lc.group('handle'):                            # handle sticking out to the right, hook at the end
        lc.line(x+7,y-5,x+30,y-8,'metal',2)
        lc.line(x+30,y-8,x+33,y-10,'metal',2); lc.line(x+33,y-10,x+33,y-12,'metal',2)
    lc.fix(x-4,y-5,'#ffffff'); lc.fix(x-3,y-6,'#ffffff')
    return Image.alpha_composite(lc.render(),body)

FR=[]
for i,(nd,br) in enumerate([(0,0),(0,1),(1,1),(1,1),(1,0),(0,0)]):
    FR.append((f'idle{i+1}',frank(nod=nd,breathe=br)))
FR.append(('hurt1',frank(lean=2,face='hurt',headtilt=1)))
FR.append(('hurt2',frank(lean=3,face='hurt',headtilt=2,nod=1)))
FR.append(('hurt3',frank(lean=1)))
FR.append(('ko1',frank(lean=2,face='dizzy')))
FR.append(('ko2',frank(lean=-1,face='dizzy')))
FR.append(('ko3',frank(lean=3,face='dizzy',nod=1)))
FR.append(('ko4',with_ladle_on_ground(frank(lean=3,face='dizzy',sit=3,hold=False),y=H-13,spill=False)))   # ladle falling
FR.append(('ko5',with_ladle_on_ground(frank(lean=2,face='dizzy',sit=6,hold=False,headtilt=1,nod=1),y=H-6)))
for k,t in enumerate((0,1.1,2.2)):
    FR.append((f'ko{6+k}',stars(with_ladle_on_ground(frank(lean=2,face='dizzy',sit=7,hold=False,headtilt=1,nod=2)),t,cy=4)))
sheet([im for _,im in FR],'frank.png')
json.dump([n for n,_ in FR],open('frank_names.json','w'))
print(len(FR))

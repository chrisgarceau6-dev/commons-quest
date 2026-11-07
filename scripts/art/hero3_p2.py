import math
from pixart2 import Canvas, RAMPS, sheet
from PIL import Image
W,H,X0=68,48,4
def leg(c,hip_x,foot_x,lift=0,mat='sw'):
    hip_x+=X0; foot_x+=X0
    c.line(hip_x,34,foot_x,41-lift,mat,5)
    c.rect(foot_x-2,41-lift,foot_x+2,42-lift,'swdk')
    c.rect(foot_x-2,43-lift,foot_x+4,44-lift,'kick')
    c.rect(foot_x-2,45-lift,foot_x+4,45-lift,'sole')

def fork_along(c,hx,hy,ang):
    ca,sa=math.cos(ang),math.sin(ang); px_,py_=-sa,ca
    ex,ey=hx+16.5*ca,hy+16.5*sa
    c.line(hx-2*ca,hy-2*sa,ex,ey,'metal')            # shaft runs through the fist
    c.line(ex-2.4*px_,ey-2.4*py_,ex+2.4*px_,ey+2.4*py_,'metal')
    for k in (-2.4,0,2.4):
        sx,sy=ex+k*px_,ey+k*py_
        c.line(sx,sy,sx+4.5*ca,sy+4.5*sa,'metal')
    c.ell(hx,hy,1.9,1.9,'skin')                       # fist drawn over the shaft
    return ex+4.5*ca,ey+4.5*sa

def hero(f):
    c=Canvas(W,H)
    b=f.get('bob',0); o=f.get('lean',0)+X0; face=f.get('face','normal')
    legs=f.get('legs',[(21,20,0),(27,28,0)])
    ang=f.get('ang')  # None = resting pose holding fork upright
    behind = ang is not None and ang < -1.35
    sx,sy=29+o,24+b
    def swing_arm():
        a=ang; hx,hy=sx+8*math.cos(a),sy+8*math.sin(a)
        c.line(sx,sy,hx,hy,'qz',4); c.ell(hx,hy,1.8,1.8,'skin')
        return fork_along(c,hx,hy,a)
    # back arm
    ba=f.get('back',0)
    tip=None
    if behind: tip=swing_arm()
    for i,(hx,fx,lift) in enumerate(legs): leg(c,hx,fx,lift,'swdk' if i==0 else 'sw')
    # torso
    with c.group('torso'):
        c.ell(24+o,29+b,8.5,6,'qz'); c.rect(16+o,25+b,32+o,33,'qz')
    c.rect(16+o,32,32+o,33,'qzdk')
    # near-side arm, drawn in front of the shirt with its own outline
    before=[row[:] for row in c.g]
    with c.group('barm'):
        c.ell(17+o,26+b,2.4,2.4,'qzdk')
        c.line(17+o,26+b,16+o-ba,31+b,'qzdk',4)
    c.ell(16+o-ba,33+b,1.8,1.6,'skin')
    armpx={(x,y) for y in range(H) for x in range(W) if c.g[y][x]!=before[y][x]}
    for (x,y) in armpx:
        for dx,dy in ((1,0),(0,-1),(0,1),(-1,0)):
            n=(x+dx,y+dy)
            if n not in armpx and 0<=n[0]<W and 0<=n[1]<H and c.g[n[1]][n[0]] is not None:
                c.fix(n[0],n[1],'#0b1a4a')
    # head
    c.ell(24+o,13+b,10,9.5,'skin')
    with c.group('hair'):
        c.rect(13+o,8+b,18+o,17+b,'hair'); c.ell(23+o,7.5+b,11,6,'hair')
        for x,y in [(29,9),(30,9),(31,10),(32,10),(33,11),(28,10),(24,9),(25,10),(20,9)]: c.px(x+o,y+b,'hair')
        # jagged fringe tips + a tuft on top
        for x,y in [(20,14),(21,14),(21,15),(23,14),(24,14),(24,15),(25,14),(19,14)]: c.px(x+o,y+b,'hair')
        for x,y in [(22,1),(23,1),(23,0),(24,1),(25,2)]: c.px(x+o,y+b,'hair')
    for (x,y,col) in [(19,12,'#f2b48c'),(18,13,'#c9714e'),(17,14,'#c9714e'),(17,15,'#c9714e'),(18,16,'#c9714e'),(18,14,'#f2b48c'),(18,15,'#e8a07a'),(19,13,'#f2b48c'),(19,14,'#f2b48c'),(19,15,'#f2b48c')]:
        c.fix(x+o,y+b,col)
    # hair shine streaks (same every frame)
    for x,y in [(17,4),(18,3),(19,3),(20,3),(21,3),(26,3),(27,3),(28,4)]: c.fix(x+o,y+b,'#a8703c')
    for x,y in [(18,4),(19,4),(27,4)]: c.fix(x+o,y+b,'#8a5a30')
    # nose shadow
    c.fix(34+o,16+b,'#d98a66'); c.fix(33+o,17+b,'#e7a07a')
    # quarter-zip collar (drawn over the chin line)
    F=lambda x,y,col: c.fix(x+o,y+b,col)
    PAL={'o':'#0b1a4a','L':'#7ab0ff','M':'#3f86f0','D':'#2160c4','t':'#f4f5ff','z':'#d7dde8'}
    COL=["oLLLLotttoLLo","oMMMMMotoMMMo","oDDDDDDoDDDDo","oooooooozoooo"]
    for j,row in enumerate(COL):
        for i,ch in enumerate(row): F(19+i,21+j,PAL[ch])
    for y in (25,26): F(26,y,'#0b1a4a'); F(27,y,'#d7dde8' if y%2 else '#7d8ca3')
    F(26,27,'#0b1a4a');F(27,27,'#0b1a4a')
    F(28,26,'#0b1a4a');F(28,27,'#eef4fa');F(28,28,'#c2cfdd');F(28,29,'#0b1a4a');F(29,27,'#0b1a4a');F(29,28,'#0b1a4a')
    # face
    def fx(x,y,col='#1b1033'): F(x,y,col)
    if face=='blink':
        for x,y in [(26,15),(27,16),(28,16),(29,16),(30,15),(32,16),(33,16)]: fx(x,y)
    elif face=='happy':
        for x,y in [(25,16),(26,15),(27,14),(28,15),(29,16),(26,16),(28,16),(31,15),(32,14),(31,16)]: fx(x,y)
    elif face=='hurt':
        for x,y in [(25,13),(26,14),(27,14),(25,15),(32,13),(31,14),(32,15)]: fx(x,y)       # >  <
        for x,y,col in [(11,5,'#ffffff'),(11,6,'#9cd8ff'),(10,6,'#9cd8ff'),(11,7,'#5ab0f0'),(10,7,'#5ab0f0')]: fx(x,y,col)   # sweat drop
    else:
        D,Wt,I,L='#1b1033','#ffffff','#4a3a86','#8f7fd0'
        for x in (25,26,27,28): fx(x,12,D)                 # upper lash, flicks out at the corner
        fx(24,11,D)
        I='#2c3f86'
        near=[[Wt,Wt,D],[Wt,D,D],[D,D,I]]
        for j,row in enumerate(near):
            for i,col in enumerate(row): fx(26+i,13+j,col)
        fx(31,12,D);fx(32,12,D)
        far=[[Wt,D],[D,D],[D,I]]
        for j,row in enumerate(far):
            for i,col in enumerate(row): fx(31+i,13+j,col)
    if face in('normal','blink'):
        for x,y in [(28,19),(29,20),(30,20),(31,19)]: fx(x,y,'#8a3a32')
    elif face=='happy':
        for (x,y,col) in [(28,17,'#3a1414'),(29,17,'#ffffff'),(30,17,'#ffffff'),(31,17,'#ffffff'),(32,17,'#3a1414'),
                          (28,18,'#3a1414'),(29,18,'#7a2030'),(30,18,'#ff7a90'),(31,18,'#ff7a90'),(32,18,'#3a1414'),
                          (29,19,'#3a1414'),(30,19,'#3a1414'),(31,19,'#3a1414')]: fx(x,y,col)
    elif face=='hurt':
        for x in (28,29,30): fx(x,19,'#6a2a2a')
    else:
        for (x,y,col) in [(28,18,'#3a1414'),(29,18,'#ffffff'),(30,18,'#ffffff'),(31,18,'#3a1414'),
                          (29,19,'#3a1414'),(30,19,'#3a1414')]: fx(x,y,col)          # gritted teeth, nothing red
        for x,y in [(25,10),(26,10),(27,11),(28,11),(29,12),(33,10),(32,11)]: fx(x,y,'#2a140a')
    if face!='hurt': fx(25,17,'#ff9fae');fx(26,17,'#ff9fae');fx(25,18,'#ffb8c4');fx(34,17,'#ff9fae')
    # front arm
    if ang is None:
        c.line(29+o,24+b,35+o,31+b,'qz',4); c.rect(34+o,31+b,36+o,32+b,'qzdk')
        c.line(37+o,38+b,37+o,15+b,'metal'); c.rect(35+o,12+b,39+o,14+b,'metal')
        for x in (35,37,39): c.line(x+o,8+b,x+o,11+b,'metal')
        c.ell(36.5+o,33.5+b,2,1.9,'skin')
        c.fix(37+o,33+b,'#e0956e'); c.fix(37+o,34+b,'#e0956e')
    elif not behind: tip=swing_arm()
    img=c.render()
    trail=f.get('trail')
    if trail:  # motion smear between previous and current swing angle
        a0,a1=trail
        for i in range(30):
            a=a0+(a1-a0)*i/29
            for r,al in ((18,255),(17,255),(19,190),(16,160)):
                x=round(sx+r*math.cos(a)); y=round(sy+r*math.sin(a))
                if 0<=x<W and 0<=y<H and img.getpixel((x,y))[3]==0: img.putpixel((x,y),(255,255,255,int(al*(0.35+0.65*i/29))))
    return img

def walk(p,n=8):
    t=2*math.pi*p/n; s=math.sin(t); cc=math.cos(t)
    front=(27,round(28+4*s),round(max(0,2*cc)))
    back=(21,round(20-4*s),round(max(0,-2*cc)))
    return dict(legs=[back,front],bob=-1 if abs(s)<0.5 else 0,back=round(2*s))

D=math.radians
FR=[]
def add(name,**k): FR.append((name,k))
for i,bb in enumerate([0,0,1,1]): add(f'idle{i+1}',bob=bb)
add('blink',face='blink')
for p in range(8): add(f'walk{p+1}',**walk(p))
add('atk1 crouch',bob=1,lean=-1,legs=[(21,19,0),(27,29,0)])
add('atk2 wind',bob=1,lean=-2,ang=D(-150),face='fierce',legs=[(21,18,0),(27,29,0)])
add('atk3 wind+',bob=0,lean=-2,ang=D(-165),face='fierce',legs=[(21,18,0),(27,30,0)])
add('atk4 swing',bob=-1,lean=0,ang=D(-40),face='fierce',trail=(D(-150),D(-40)),legs=[(21,18,0),(27,31,0)])
add('atk5 swing',bob=-1,lean=1,ang=D(-18),face='fierce',trail=(D(-100),D(-18)),legs=[(21,17,0),(27,32,0)])
add('atk6 hit',bob=0,lean=1,ang=D(0),face='fierce',trail=(D(-70),D(0)),legs=[(21,17,0),(27,32,0)])
add('atk7 follow',bob=0,lean=1,ang=D(25),face='fierce',legs=[(21,17,0),(27,32,0)])
add('atk8 recover',bob=0,lean=0,ang=D(55),legs=[(21,19,0),(27,30,0)])
add('hurt1',lean=-1,face='hurt',legs=[(21,19,0),(27,27,0)])
add('hurt2',lean=-3,face='hurt',bob=1,legs=[(21,18,0),(27,26,0)])
add('win1',bob=1,face='happy',ang=D(-25),legs=[(21,19,0),(27,29,0)])
add('win2',bob=-2,face='happy',ang=D(-45),legs=[(21,20,2),(27,28,2)])
add('win3',bob=-3,face='happy',ang=D(-48),legs=[(21,20,3),(27,28,3)])
add('win4',bob=0,face='happy',ang=D(-52),legs=[(21,19,0),(27,29,0)])
imgs=[hero(k) for _,k in FR]
sheet(imgs,'hero3_p2.png')
import json; json.dump([n for n,_ in FR],open('hero3_names.json','w'))
print(len(FR))

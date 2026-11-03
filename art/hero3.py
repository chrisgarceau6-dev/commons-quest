import math
from pixart import Canvas, RAMPS, sheet
from PIL import Image
RAMPS.update({
 'qz':   ['#0b1a4a','#1d4fa8','#2f74e0','#5a9bff','#9cc4ff'],
 'qzdk': ['#0b1a4a','#163f8f','#2160c4','#3f86f0','#7ab0ff'],
 'sw':   ['#2a2b36','#7c7f8c','#a3a6b3','#c4c7d2','#e3e5ec'],
 'swdk': ['#2a2b36','#5f6272','#7c7f8c','#a3a6b3','#c4c7d2'],
 'kick': ['#2a2b36','#c9cde0','#f4f5ff','#ffffff','#ffffff'],
 'sole': ['#2a2b36','#9aa0b4','#c9cde0','#e6e8f2','#ffffff'],
})
W,H,X0=56,48,4
def leg(c,hip_x,foot_x,lift=0):
    hip_x+=X0; foot_x+=X0
    c.line(hip_x,34,foot_x,41-lift,'sw',5)
    c.rect(foot_x-2,41-lift,foot_x+2,42-lift,'swdk')
    c.rect(foot_x-2,43-lift,foot_x+4,44-lift,'kick')
    c.rect(foot_x-2,45-lift,foot_x+4,45-lift,'sole')

def fork_along(c,hx,hy,ang):
    ca,sa=math.cos(ang),math.sin(ang); px_,py_=-sa,ca
    ex,ey=hx+6*ca,hy+6*sa
    c.line(hx+ca,hy+sa,ex,ey,'metal',2)
    c.line(ex-2.4*px_,ey-2.4*py_,ex+2.4*px_,ey+2.4*py_,'metal')
    for k in (-2.4,0,2.4):
        sx,sy=ex+k*px_,ey+k*py_
        c.line(sx,sy,sx+3.5*ca,sy+3.5*sa,'metal')
    return ex+3.5*ca,ey+3.5*sa

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
    for hx,fx,lift in legs: leg(c,hx,fx,lift)
    # torso
    c.ell(24+o,29+b,8.5,6,'qz'); c.rect(16+o,25+b,32+o,33,'qz'); c.rect(16+o,32,32+o,33,'qzdk')
    # near-side arm, drawn in front of the shirt with its own outline
    before=[row[:] for row in c.g]
    c.ell(17+o,26+b,2.4,2.4,'qzdk')                      # shoulder stays put
    c.line(17+o,26+b,16+o-ba,31+b,'qzdk',4)              # arm pivots from it
    c.ell(16+o-ba,33+b,1.8,1.6,'skin')
    armpx={(x,y) for y in range(H) for x in range(W) if c.g[y][x]!=before[y][x]}
    for (x,y) in armpx:
        for dx,dy in ((1,0),(0,-1),(0,1),(-1,0)):
            n=(x+dx,y+dy)
            if n not in armpx and 0<=n[0]<W and 0<=n[1]<H and c.g[n[1]][n[0]] is not None:
                c.fix(n[0],n[1],'#0b1a4a')
    # head
    c.ell(24+o,13+b,10,9.5,'skin')
    c.ell(23+o,7.5+b,11,6,'hair'); c.rect(13+o,6+b,18+o,17+b,'hair')
    for x,y in [(29,9),(30,9),(31,10),(32,10),(33,11),(28,10),(24,9),(25,10),(20,9)]: c.px(x+o,y+b,'hair')
    c.ell(18.5+o,14+b,1.6,2.2,'skin')
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
        for x in (27,28,29,32,33): fx(x,15)
    elif face=='happy':
        for x,y in [(27,15),(28,14),(29,15),(32,15),(33,14)]: fx(x,y)
    elif face=='hurt':
        for x,y in [(27,13),(28,14),(29,15),(28,16),(27,17),(33,13),(32,14),(33,15)]: fx(x,y)
    else:
        for x in (27,28,29):
            for y in (13,14,15,16): fx(x,y)
        for x in (32,33):
            for y in (13,14,15,16): fx(x,y)
        fx(27,13,'#ffffff');fx(28,13,'#ffffff');fx(27,14,'#ffffff');fx(32,13,'#ffffff')
    if face in('normal','blink'):
        for x in (26,27,28,32,33): fx(x,11,'#3b1f0e')
        for x,y in [(29,18),(30,19),(31,19),(32,18)]: fx(x,y)
    elif face=='happy':
        for x in range(29,33):
            for y in (17,18,19): fx(x,y)
        for x in range(29,33): fx(x,17,'#ffffff')
        fx(30,19,'#ff6f8f');fx(31,19,'#ff6f8f')
    elif face=='hurt':
        for x,y in [(29,19),(30,18),(31,19),(32,18)]: fx(x,y)
    else:
        for x in range(29,33):
            for y in (18,19): fx(x,y)
        fx(30,18,'#ffffff');fx(31,18,'#ffffff')
        for x,y in [(26,11),(27,12),(28,12),(33,11),(32,12)]: fx(x,y,'#3b1f0e')
    if face!='hurt': fx(25,17,'#ff9fae');fx(26,17,'#ff9fae');fx(34,17,'#ff9fae')
    # front arm
    if ang is None:
        c.line(29+o,24+b,35+o,31+b,'qz',4); c.rect(34+o,31+b,36+o,32+b,'qzdk'); c.ell(36+o,33+b,1.8,1.8,'skin')
        c.line(38+o,38+b,38+o,15+b,'metal'); c.rect(36+o,12+b,40+o,14+b,'metal')
        for x in (36,38,40): c.line(x+o,8+b,x+o,11+b,'metal')
    elif not behind: tip=swing_arm()
    img=c.render()
    trail=f.get('trail')
    if trail:  # motion smear between previous and current swing angle
        a0,a1=trail
        for i in range(30):
            a=a0+(a1-a0)*i/29
            for r,al in ((17,210),(16,160),(18,120),(15,90)):
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
add('atk4 swing',bob=-1,lean=0,ang=D(-95),face='fierce',trail=(D(-165),D(-95)),legs=[(21,18,0),(27,31,0)])
add('atk5 swing',bob=-1,lean=1,ang=D(-28),face='fierce',trail=(D(-110),D(-28)),legs=[(21,17,0),(27,32,0)])
add('atk6 hit',bob=0,lean=1,ang=D(0),face='fierce',trail=(D(-70),D(0)),legs=[(21,17,0),(27,32,0)])
add('atk7 follow',bob=0,lean=1,ang=D(25),face='fierce',legs=[(21,17,0),(27,32,0)])
add('atk8 recover',bob=0,lean=0,ang=D(55),legs=[(21,19,0),(27,30,0)])
add('hurt1',lean=-1,face='hurt',legs=[(21,19,0),(27,27,0)])
add('hurt2',lean=-3,face='hurt',bob=1,legs=[(21,18,0),(27,26,0)])
add('win1',bob=1,face='happy',ang=D(40),legs=[(21,19,0),(27,29,0)])
add('win2',bob=-2,face='happy',ang=D(-10),legs=[(21,20,2),(27,28,2)])
add('win3',bob=-3,face='happy',ang=D(-22),legs=[(21,20,3),(27,28,3)])
add('win4',bob=0,face='happy',ang=D(-22),legs=[(21,19,0),(27,29,0)])
imgs=[hero(k) for _,k in FR]
sheet(imgs,'hero3.png')
import json; json.dump([n for n,_ in FR],open('hero3_names.json','w'))
print(len(FR))

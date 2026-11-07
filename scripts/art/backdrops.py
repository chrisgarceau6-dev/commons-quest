"""Fight backdrops, one per dining hall. 200x105 pixel art shown at 2x; ground line at y=78 (characters stand there)."""
import random, math
from PIL import Image
W,H,GY=200,105,78
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def mix(a,b,t): return tuple(round(a[i]+(b[i]-a[i])*t) for i in range(3))
class P:
    def __init__(s): s.im=Image.new('RGB',(W,H)); s.p=s.im.load()
    def px(s,x,y,c):
        x,y=int(x),int(y)
        if 0<=x<W and 0<=y<H: s.p[x,y]=c if isinstance(c,tuple) else hx(c)
    def rect(s,x0,y0,x1,y1,c):
        for y in range(int(y0),int(y1)+1):
            for x in range(int(x0),int(x1)+1): s.px(x,y,c)
    def ell(s,cx,cy,rx,ry,c):
        for y in range(int(cy-ry)-1,int(cy+ry)+2):
            for x in range(int(cx-rx)-1,int(cx+rx)+2):
                if ((x-cx)/rx)**2+((y-cy)/ry)**2<=1: s.px(x,y,c)
    def sky(s,stops,y1=GY):
        # banded gradient with 2-pixel dither between bands (classic pixel sky)
        n=len(stops)-1
        for y in range(y1):
            t=y/(y1-1)*n; i=min(n-1,int(t)); f=t-i
            a,b=hx(stops[i]),hx(stops[i+1])
            for x in range(W):
                c=a if f<0.5 else b
                if 0.35<f<0.65 and (x+y)%2: c=b if c==a else a
                s.p[x,y]=c
    def ground(s,top,mid,dark,edge,pattern='grass'):
        for y in range(GY,H):
            for x in range(W):
                c=hx(mid)
                if y==GY: c=hx(edge)
                elif y==GY+1: c=hx(top)
                elif pattern=='grass' and (x*7+y*3)%11==0: c=hx(dark)
                elif pattern=='tile' and ((x//10+(y-GY)//5)%2==0): c=mix(hx(mid),hx(dark),0.35)
                elif pattern=='tile' and ((y-GY)%5==0 or x%10==0): c=hx(dark)
                elif pattern=='boards' and ((y-GY)%4==0 or (x+((y-GY)//4)*7)%23==0): c=hx(dark)
                elif pattern=='dirt' and (x*5+y*9)%13==0: c=hx(dark)
                s.p[x,y]=c
    def stars(s,n,seed,y1=50):
        r=random.Random(seed)
        for _ in range(n):
            x,y=r.randrange(W),r.randrange(y1); s.px(x,y,'#ffffff' if r.random()<.4 else '#c8c8f0')
    def outline_shape(s,pts,fill,ol='#1b1530'):
        """filled polygon with a 1px dark outline"""
        from PIL import ImageDraw
        m=Image.new('L',(W,H),0); ImageDraw.Draw(m).polygon(pts,fill=255); mp=m.load()
        for y in range(H):
            for x in range(W):
                if mp[x,y]:
                    edge=any(not(0<=x+dx<W and 0<=y+dy<H) or not mp[x+dx,y+dy] for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)))
                    s.px(x,y,ol if edge else fill)
def pine(s,x,base,h,c1,c2,snow=False):
    for k in range(h):
        w=max(0,round((k/h)*h*0.42)); y=base-h+k
        for dx in range(-w,w+1): s.px(x+dx,y,c1 if dx<1 else c2)
    s.rect(x,base,x,base+2,'#4a2c18')
def tree(s,x,base,r,c1,c2,c3):
    s.rect(x-1,base-r,x,base,'#5a3820')
    s.ell(x,base-r-r*0.6,r,r*0.9,c2); s.ell(x-r*0.3,base-r-r*0.9,r*0.6,r*0.55,c1); s.ell(x+r*0.4,base-r*0.6-r*0.5,r*0.5,r*0.4,c3)
def window(s,x,y,lit,c_off='#2b2a48',c_on='#ffd86a',w=3,h=3):
    s.rect(x,y,x+w-1,y+h-1,c_on if lit else c_off)
# ---------------- Berkshire: lodge kitchen at golden hour in the woods ----------------
def berk():
    s=P(); s.sky(['#ffb46b','#ff8e6b','#c96a8e','#6a4a8e'][::-1]+[][:0])
    s.sky(['#5b3f8a','#b05e8e','#f08a6a','#ffc27a'])
    s.ell(150,40,13,13,'#fff2b8'); s.ell(150,40,11,11,'#ffe48a')
    for x in range(0,W,9): pine(s,x+(x*7)%5,GY-6,26+(x*13)%14,'#4a3a6a','#3a2c58')       # far ridge of pines
    for x in range(4,W,15): pine(s,x,GY,34+(x*7)%12,'#2e5a3e','#1f4430')
    # log lodge
    s.rect(40,46,118,GY,'#8e5428')
    for y in range(47,GY,4): s.rect(40,y,118,y,'#6a3a1c')
    s.outline_shape([(34,48),(79,22),(124,48)],'#7a1022')
    for y in range(26,48,3):
        for x in range(36,123):
            pass
    s.rect(58,58,70,GY,'#3a2210'); s.rect(59,59,69,GY,'#5a3418'); s.px(67,68,'#f4d35e')       # door
    for wx in (46,84,100): s.rect(wx,54,wx+9,62,'#3a2210'); window(s,wx+1,55,True,w=8,h=7); s.rect(wx+5,55,wx+5,62,'#3a2210')
    s.rect(100,26,107,40,'#6e6a78'); s.rect(99,25,108,26,'#3a3848')                           # chimney
    for i,(dx,dy) in enumerate([(1,-3),(3,-7),(1,-11),(4,-15),(2,-19)]): s.ell(103+dx,24+dy,2+i*0.4,1.6+i*0.3,'#e8e0f0')
    # BERK sign on the gable
    s.rect(70,33,88,40,'#f0e2b8'); s.rect(70,33,88,33,'#3a2210'); s.rect(70,40,88,40,'#3a2210')
    F={'B':["11.","1.1","11.","1.1","11."],'E':["111","1..","11.","1..","111"],'R':["11.","1.1","11.","11.","1.1"],'K':["1.1","1.1","11.","1.1","1.1"]}
    x=72
    for ch in 'BERK':
        for j,row in enumerate(F[ch]):
            for i,v in enumerate(row):
                if v=='1': s.px(x+i,35+j,'#7a1022')
        x+=4
    s.ground('#8fd060','#6cae44','#4e8a34','#2e4a24')
    for x in (10,20,150,175,190): s.ell(x,GY+6,2,1,'#e8d06a')
    return s.im
# ---------------- Worcester: dragon's terrace at dusk, lanterns ----------------
def wor():
    s=P(); s.sky(['#1d1640','#3a2a6e','#7a3a8e','#e06a7a'])
    s.stars(40,3,40)
    s.ell(40,24,7,7,'#fff6d8'); s.ell(43,22,6,6,'#3a2a6e')                                        # crescent moon
    # far castle-like hall silhouette
    s.rect(20,40,180,GY,'#2a1f4e')
    for x in range(20,181,8): s.rect(x,36,x+4,40,'#2a1f4e')
    s.rect(90,22,110,GY,'#2a1f4e'); 
    for x in range(90,111,5): s.rect(x,18,x+2,22,'#2a1f4e')
    for (x,y) in [(30,50),(46,50),(62,50),(130,50),(146,50),(162,50),(96,30),(104,30),(96,44),(104,44)]: window(s,x,y,True,w=3,h=4)
    # stone terrace wall with hanging lanterns
    s.rect(0,62,W-1,GY,'#5a5470')
    for y in range(62,GY,4):
        for x in range(0,W):
            if y%8==2 and x%12==0 or y%8==6 and (x+6)%12==0: s.rect(x,y,x,y+3,'#3e3a52')
        s.rect(0,y,W-1,y,'#3e3a52')
    s.rect(0,61,W-1,61,'#8a84a0')
    for lx in (14,52,148,186):
        s.rect(lx,52,lx,61,'#2a1f4e'); s.rect(lx-2,53,lx+2,58,'#ff8a3a'); s.rect(lx-1,54,lx+1,57,'#ffd86a')
        for dy in range(-3,4):
            for dx in range(-5,6):
                if dx*dx+dy*dy<20: 
                    c=s.p[min(W-1,max(0,lx+dx)),55+dy]; s.px(lx+dx,55+dy,mix(c,(255,180,90),0.25))
    s.ground('#6a6488','#4e4a66','#3a3650','#1b1530','tile')
    return s.im
# ---------------- Franklin: mad-science lab on a stormy night ----------------
def frank():
    s=P(); s.sky(['#0e1226','#1e2a44','#2e3e5a','#3e4e6a'])
    for (cx,cy,rx,ry) in [(30,14,26,7),(90,10,34,8),(160,16,30,7),(120,26,24,5)]: s.ell(cx,cy,rx,ry,'#283650'); s.ell(cx,cy-2,rx-4,ry-2,'#34445e')
    # lightning bolt
    pts=[(130,18),(126,28),(131,28),(124,42),(129,42),(121,56)]
    for (a,b) in zip(pts,pts[1:]):
        n=max(abs(b[0]-a[0]),abs(b[1]-a[1]))
        for i in range(n+1): s.px(a[0]+(b[0]-a[0])*i/n,a[1]+(b[1]-a[1])*i/n,'#fff6a0'); s.px(a[0]+(b[0]-a[0])*i/n+1,a[1]+(b[1]-a[1])*i/n,'#c8f0ff')
    # lab wall: brick, with a big window and gauges
    s.rect(0,30,W-1,GY,'#3a4052')
    for y in range(30,GY,4):
        s.rect(0,y,W-1,y,'#2c3142')
        for x in range((y//4)%2*6,W,12): s.rect(x,y,x,y+3,'#2c3142')
    s.rect(70,36,130,60,'#1b1530'); s.rect(72,38,128,58,'#2a3a5a')                              # window showing the storm
    s.rect(100,38,100,58,'#1b1530'); s.rect(72,48,128,48,'#1b1530')
    for i in range(10): s.px(110-i,40+i*2,'#fff6a0')
    # tesla coils with sparks
    for cx in (28,172):
        s.rect(cx-2,48,cx+2,GY,'#8a6a3a'); 
        for y in range(48,GY,3): s.rect(cx-3,y,cx+3,y,'#c99a48')
        s.ell(cx,44,6,4,'#aebdd0'); s.ell(cx-1,43,4,2,'#ffffff')
        for k in range(5): 
            a=k*1.2; s.px(cx+round(9*math.cos(a)),40+round(5*math.sin(a)),'#8af0ff')
    # bubbling beakers on a bench
    s.rect(140,62,195,64,'#5a4028'); s.rect(142,65,144,GY,'#3a2818'); s.rect(190,65,192,GY,'#3a2818')
    for bx,col in ((150,'#5be36b'),(162,'#ff5ec8'),(176,'#3ec7ff')):
        s.rect(bx,54,bx+6,61,'#d8eef8'); s.rect(bx+1,57,bx+5,61,col); s.px(bx+2,52,col); s.px(bx+4,50,col)
    s.ground('#5e6680','#464c62','#33384a','#1b1530','tile')
    return s.im
# ---------------- Hampshire: sunny farm, barn and garden ----------------
def hamp():
    s=P(); s.sky(['#5ab8f5','#7fcaf7','#a6dcfa','#d4f0ff'])
    s.ell(30,18,9,9,'#fff6b0'); s.ell(30,18,7,7,'#ffe46a')
    for (cx,cy) in [(80,14),(150,22)]: s.ell(cx,cy,12,4,'#ffffff'); s.ell(cx+6,cy-2,8,4,'#ffffff')
    # rolling hills
    for x in range(W):
        y=round(52+6*math.sin(x/22)+3*math.sin(x/9)); s.rect(x,y,x,GY,'#7fcf63')
        y2=round(60+4*math.sin(x/15+1)); s.rect(x,y2,x,GY,'#5fb43f')
    # red barn
    s.rect(120,44,176,GY,'#c2273a')
    for x in range(120,177,4): s.rect(x,44,x,GY,'#a01b30')
    s.outline_shape([(116,46),(148,26),(180,46)],'#8a1626','#3a0610')
    s.rect(140,56,156,GY,'#f4ead2'); s.rect(142,58,154,GY,'#8a1626')
    for i in range(12): s.px(142+i,58+i*20//12,'#f4ead2'); s.px(154-i,58+i*20//12,'#f4ead2')
    s.rect(144,34,152,40,'#f4ead2'); s.rect(145,35,151,39,'#3a2a20')                                # hayloft
    # fence + garden rows + sunflowers
    for x in range(0,110,6): s.rect(x,66,x+1,GY-2,'#e8d8b0')
    s.rect(0,68,110,68,'#e8d8b0'); s.rect(0,72,110,72,'#e8d8b0')
    for fx in (12,26,40,96): 
        s.rect(fx,50,fx,66,'#3f8f3a'); s.ell(fx,48,4,4,'#ffc83d'); s.ell(fx,48,2,2,'#6a3a10')
    s.ground('#b88a5a','#9a6e44','#7a5232','#3a2818','dirt')
    for x in range(4,W,10):
        for k in range(3): s.px(x+k,GY+5,'#4fa34a'); s.px(x+1,GY+4,'#7fcf63')
    return s.im
# ---------------- Campus Center: brick plaza under the library tower ----------------
def cc():
    s=P(); s.sky(['#3a7ad8','#5a9ae8','#8abdf2','#c4e0fa'])
    for (cx,cy) in [(40,16),(120,10),(176,24)]: s.ell(cx,cy,11,3,'#ffffff'); s.ell(cx+5,cy-2,6,3,'#ffffff')
    # Du Bois-style tower in the back
    s.rect(84,6,116,GY,'#a8603a')
    for y in range(9,GY,4):
        for x in range(87,114,4): window(s,x,y,(x*y)%5==0,'#3c4d7a','#a8d4ff',w=2,h=2)
    s.rect(84,6,116,7,'#7a3a2e'); s.rect(84,6,84,GY,'#7a3a2e')
    # low campus buildings
    s.rect(0,40,70,GY,'#c9b48a'); s.rect(130,44,W-1,GY,'#b8b4ac')
    for x in range(4,68,8): window(s,x,46,x%16==4,'#3c4d7a','#a8d4ff',w=4,h=5); window(s,x,58,False,'#3c4d7a','#a8d4ff',w=4,h=5)
    for x in range(134,W,8): window(s,x,50,x%16==6,'#3c4d7a','#a8d4ff',w=4,h=5); window(s,x,62,False,'#3c4d7a','#a8d4ff',w=4,h=5)
    s.rect(0,39,70,40,'#8a7a5a'); s.rect(130,43,W-1,44,'#7a7880')
    # trees in planters
    for tx in (20,60,140,184): tree(s,tx,GY-2,6,'#7ccf5c','#2e8b3a','#45a84a'); s.rect(tx-4,GY-3,tx+4,GY,'#8a7a5a')
    s.ground('#d8a07a','#c4805a','#a8603a','#5a2a18','tile')
    return s.im
for name,fn in [('berk',berk),('wor',wor),('frank',frank),('hamp',hamp),('cc',cc)]:
    fn().save(f'bg_{name}.png')
S=3; out=Image.new('RGB',(W*S*2+10,H*S*3+20),(255,255,255))
for i,n in enumerate(['berk','wor','frank','hamp','cc']):
    im=Image.open(f'bg_{n}.png').resize((W*S,H*S),Image.NEAREST); out.paste(im,((i%2)*(W*S+10),(i//2)*(H*S+10)))
out.save('_all.png')

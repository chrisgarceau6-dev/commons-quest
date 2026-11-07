"""Commons Quest campus map v2: same geometry as the official UMass map, drawn as a 3/4-view pixel town. Day + night."""
import pymupdf as fitz, random, math, json
from PIL import Image, ImageDraw, ImageFilter, ImageChops
doc=fitz.open('campus.pdf'); p=doc[0]; dr=p.get_drawings()
X0,Y0,X1,Y1=140,222,474,656
W=368; K=W/(X1-X0); H=round((Y1-Y0)*K)
def T(pt): return ((pt.x-X0)*K,(pt.y-Y0)*K)
def r2(c): return tuple(round(x,2) for x in c) if c else None
def polys(d,steps=6):
    out=[];cur=[]
    for it in d['items']:
        op=it[0]
        if op=='l':
            a,b=T(it[1]),T(it[2])
            if cur and math.dist(cur[-1],a)>0.01: out.append(cur);cur=[]
            if not cur: cur=[a]
            cur.append(b)
        elif op=='c':
            P=[it[1],it[2],it[3],it[4]];a=T(P[0])
            if cur and math.dist(cur[-1],a)>0.01: out.append(cur);cur=[]
            if not cur: cur=[a]
            for i in range(1,steps+1):
                t=i/steps;u=1-t
                x=u**3*P[0].x+3*u*u*t*P[1].x+3*u*t*t*P[2].x+t**3*P[3].x
                y=u**3*P[0].y+3*u*u*t*P[1].y+3*u*t*t*P[2].y+t**3*P[3].y
                cur.append(T(fitz.Point(x,y)))
        elif op=='re':
            if cur: out.append(cur);cur=[]
            r=it[1];out.append([T(r.tl),T(r.tr),T(r.br),T(r.bl),T(r.tl)])
        elif op=='qu':
            if cur: out.append(cur);cur=[]
            q=it[1];out.append([T(q.ul),T(q.ur),T(q.lr),T(q.ll),T(q.ul)])
    if cur: out.append(cur)
    return out
groups={}
for d in dr: groups.setdefault((r2(d.get('fill')),r2(d.get('color')),round(d.get('width') or 0,1),d['type']),[]).append(d)
def isgrid(pl):
    if len(pl)!=2: return False
    (a,b),(c,e)=pl
    return (abs(a-c)<0.3 or abs(b-e)<0.3) and math.dist(pl[0],pl[1])>60
def mask(): return Image.new('L',(W,H),0)
rnd=random.Random(11)
# ---------- masks ----------
edges=mask(); ge=ImageDraw.Draw(edges)
for d in groups.get((None,(1.0,1.0,1.0),0.5,'s'),[]):
    for pl in polys(d):
        if not isgrid(pl) and len(pl)>=2: ge.line(pl,fill=255,width=1)
# close the gap between paired road edges -> road surface
roads=edges.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
roads=ImageChops.lighter(roads,edges)
wide=roads.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))     # broad avenues
fields=mask(); gf=ImageDraw.Draw(fields)
for d in groups.get((None,(0.77,0.72,0.57),0.5,'s'),[]):
    for pl in polys(d):
        if len(pl)>=4: gf.polygon(pl,fill=255)
plaza=mask(); gp=ImageDraw.Draw(plaza)
for k in [((0.73,0.7,0.64),None,0,'f'),((0.73,0.7,0.64),(0.83,0.81,0.77),0.5,'fs')]:
    for d in groups.get(k,[]):
        for pl in polys(d):
            if len(pl)>=3: gp.polygon(pl,fill=255)
water=mask(); gw=ImageDraw.Draw(water)
for d in groups.get(((0.56,0.79,0.85),(0.56,0.79,0.85),0.5,'fs'),[]):
    for pl in polys(d):
        if len(pl)>=3: gw.polygon(pl,fill=255)
blds=[]
for k in [((1.0,1.0,1.0),(0.83,0.81,0.77),0.5,'fs'),((1.0,1.0,1.0),None,0,'f'),((1.0,1.0,1.0),(0.8,0.78,0.73),0.3,'fs'),((1.0,1.0,1.0),(0.83,0.81,0.77),1.0,'fs')]:
    for d in groups.get(k,[]):
        r=d['rect']
        if r.x1<X0 or r.x0>X1 or r.y1<Y0 or r.y0>Y1 or r.width>200 or r.height>200: continue
        for pl in polys(d):
            if len(pl)>=3:
                m=mask(); ImageDraw.Draw(m).polygon(pl,fill=255); bb=m.getbbox()
                if not bb: continue
                area=sum(1 for v in m.crop(bb).getdata() if v)
                if area<4: continue
                cx=sum(x for x,_ in pl)/len(pl); cy=sum(y for _,y in pl)/len(pl)
                blds.append(dict(pl=pl,bb=bb,area=area,c=(cx,cy)))
bm=mask(); gb=ImageDraw.Draw(bm)
for b in blds: gb.polygon(b['pl'],fill=255)
# ---------- landmarks / dining halls ----------
def nearest(x,y,maxd=26):
    best=None
    for b in blds:
        d=math.dist(b['c'],(x,y))
        if d<maxd and (best is None or d<best[0]): best=(d,b)
    return best[1] if best else None
SPECIAL={  # name: (label point, roof, wall, height)
 'dubois':((160,165),None,None,26),'lederle':((158,40),None,None,15),'cc':((155,116),'#3a5fd0','#26408e',11),
 'chapel':((157,212),'#9c3b2e','#6e2a22',7),
 'wor':((229,82),'#3fa34a','#23704a',6),'frank':((280,201),'#8fa3b8','#55657c',6),
 'hamp':((79,382),'#e98aa6','#a8506e',6),'berk':((90,447),'#8e2a3a','#5a1622',6),'hampden':((95,414),None,None,5),
}
special={}
for k,(pt,roof,wall,h) in SPECIAL.items():
    b=nearest(*pt)
    if b: b.update(sp=k,h=h,roof=roof,wall=wall); special[k]=b
ROOFS=[('#7d8aa8','#4f5a78'),('#b85c4a','#7a3a2e'),('#c9774f','#86482e'),('#d8c39a','#a08c62'),('#a7a9b4','#6e7080'),('#6fae9c','#3e7266'),('#b7a07c','#7c6a4e')]
WALLS=['#c96f52','#d9c6a4','#b8b4ac','#a85a44','#cdbb98']
for b in blds:
    if 'h' not in b: b['h']=max(2,min(8,round(2+math.sqrt(b['area'])/7)))
    if not b.get('roof'):
        r=rnd.choice(ROOFS); b['roof']=r[0]; b['roofd']=r[1]
    else: b['roofd']=b['wall']
    if not b.get('wall') or 'sp' not in b: b['wallc']=rnd.choice(WALLS)
    else: b['wallc']=b['wall']
    b['seed']=rnd.random()
# ---------- palette ----------
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def sh(c,f): return tuple(max(0,min(255,round(v*f))) for v in c)
def mix(a,b,t): return tuple(round(a[i]+(b[i]-a[i])*t) for i in range(3))
def render(night=False):
    im=Image.new('RGB',(W,H)); px=im.load()
    G1,G2,G3=hx('#6cc24a'),hx('#5fb43f'),hx('#7fd05a')
    rm,wm,fm,pm,bmm,wdm=roads.load(),water.load(),fields.load(),plaza.load(),bm.load(),wide.load()
    for y in range(H):
        for x in range(W):
            n=(math.sin(x*0.21+y*0.07)+math.sin(y*0.17-x*0.05)+math.sin((x+y)*0.11))   # soft lawn patches
            c=G1 if n>-0.6 else G2
            if n>1.6: c=G3
            if (x*7+y*13)%23==0: c=G2 if c!=G2 else G1
            if fm[x,y]: c=hx('#86d462') if (y//3)%2 else hx('#7acb57')               # mown stripes
            if pm[x,y]: c=hx('#e3cfa0') if (x+y)%4 else hx('#d6c08e')
            if rm[x,y]:
                if wdm[x,y]: c=hx('#7d8193')
                else: c=hx('#e2cf9e') if (x*3+y)%11 else hx('#d6c08e')
            if wm[x,y]: c=hx('#3fb6e8')
            px[x,y]=c
    # road edges / curbs, avenue centre dashes
    for y in range(1,H-1):
        for x in range(1,W-1):
            if rm[x,y] and not wm[x,y]:
                nb=[rm[x+1,y],rm[x-1,y],rm[x,y+1],rm[x,y-1]]
                if not all(nb): px[x,y]=hx('#5a5e6e') if wdm[x,y] else hx('#b39a68')
    # fields: white boundary lines
    for y in range(1,H-1):
        for x in range(1,W-1):
            if fm[x,y] and not all([fm[x+1,y],fm[x-1,y],fm[x,y+1],fm[x,y-1]]): px[x,y]=hx('#eef8e2')
    # pond: shoreline, depth, ripples, lily pads, ducks
    for y in range(1,H-1):
        for x in range(1,W-1):
            if wm[x,y]:
                e=min(sum(1 for dx in range(-k,k+1) for dy in range(-k,k+1) if not wm[x+dx,y+dy])==0 and k for k in (1,2,3)) if False else None
                inner=all(wm[x+dx,y+dy] for dx in (-2,0,2) for dy in (-2,0,2))
                px[x,y]=hx('#2c95d0') if inner else hx('#58c8f0')
                if inner and (x*5+y*3)%17==0: px[x,y]=hx('#bdeeff')
            elif any(wm[x+dx,y+dy] for dx in (-1,0,1) for dy in (-1,0,1)): px[x,y]=hx('#e8d8a0')
    wb=water.getbbox()
    if wb:
        pads=[(wb[0]+6,wb[1]+30),(wb[0]+9,wb[1]+52),(wb[2]-6,wb[3]-25)]
        for (x,y) in pads:
            for dx,dy in ((0,0),(1,0),(0,1),(1,1),(-1,0)): 
                if wm[x+dx,y+dy]: px[x+dx,y+dy]=hx('#4fa34a')
        for (x,y) in [(wb[0]+13,wb[1]+20),(wb[0]+16,wb[1]+22),(wb[0]+11,wb[1]+70)]:
            if wm[x,y]: px[x,y]=(255,255,255); px[x+1,y]=(255,255,255); px[x+2,y-1]=(255,255,255); px[x+3,y-1]=hx('#f4a52a')
    # trees: shadows first, then canopies (back to front)
    occ=lambda x,y: not(0<=x<W and 0<=y<H) or rm[x,y] or wm[x,y] or bmm[x,y] or fm[x,y] or pm[x,y]
    trees=[]
    tr=random.Random(5)
    for _ in range(5200):
        x,y=tr.randrange(6,W-6),tr.randrange(7,H-6)
        r=tr.choice((2,2,3,3,4))
        if any(occ(x+dx,y+dy) for dx in range(-r-1,r+2) for dy in range(-r-1,r+3)): continue
        if any(math.dist((x,y),(a,b))<r+rr-0.5 for a,b,rr in trees[-60:]): continue
        trees.append((x,y,r))
    trees.sort(key=lambda t:t[1])
    for (x,y,r) in trees:
        for dy in range(-r,r+1):
            for dx in range(-r,r+2):
                if (dx/(r+1))**2+(dy/r)**2<=1:
                    xx,yy=x+dx+2,y+dy+2
                    if 0<=xx<W and 0<=yy<H and not rm[xx,yy] and not wm[xx,yy]: px[xx,yy]=sh(px[xx,yy],0.72)
    TC=[hx('#1d6b2c'),hx('#2e8b3a'),hx('#45a84a'),hx('#7ccf5c')]
    for (x,y,r) in trees:
        px[x,y+r]=hx('#6e4828')
        for dy in range(-r,r+1):
            for dx in range(-r,r+1):
                d=(dx*dx+dy*dy)/(r*r+0.3)
                if d<=1:
                    l=(-dx-dy)/(r*1.4)+0.15*((dx*3+dy*5)%3-1)
                    c=TC[3] if l>0.55 and d<0.6 else TC[2] if l>0.0 else TC[1] if l>-0.6 else TC[0]
                    if d>0.8 and dx+dy>0: c=TC[0]
                    px[x+dx,y+dy-1]=c
    # buildings, back to front: drop shadow, extruded walls with windows, roof with rim light
    order=sorted(blds,key=lambda b:b['bb'][3])
    for b in order:
        sm=mask(); ImageDraw.Draw(sm).polygon([(x+2,y+1) for x,y in b['pl']],fill=255)
        for (x,y) in [(x,y) for y in range(max(0,b['bb'][1]),min(H,b['bb'][3]+3)) for x in range(max(0,b['bb'][0]),min(W,b['bb'][2]+4)) if sm.getpixel((x,y))]:
            px[x,y]=sh(px[x,y],0.62)
    lit_r=random.Random(9)
    for b in order:
        h=b['h']; pl=b['pl']
        fm_=mask(); ImageDraw.Draw(fm_).polygon(pl,fill=255)
        rf=mask(); ImageDraw.Draw(rf).polygon([(x,y-h) for x,y in pl],fill=255)
        x0,y0,x1,y1=b['bb']; wc=hx(b['wallc']); rc=hx(b['roof']); rd=hx(b['roofd'])
        tall=b.get('sp') in ('dubois','lederle')
        # walls: the footprint swept up to the roof
        for y in range(max(0,y0-h),min(H,y1+1)):
            for x in range(max(0,x0),min(W,x1+1)):
                inside=any(fm_.getpixel((x,y+k)) for k in range(0,h+1) if y+k<H)
                if not inside or rf.getpixel((x,y)): continue
                depth=next(k for k in range(0,h+1) if y+k<H and fm_.getpixel((x,y+k)))        # 0 = ground level
                c=sh(wc,0.82 if (x*0.6)%9<5 else 0.78)
                c=sh(c,0.9) if x>(x0+x1)/2 else c
                win=(depth>=1 and depth<h and (h-depth)%3==1 and x%3!=0) if not tall else (depth>=1 and (depth%3)!=0 and x%2==0)
                if win:
                    if night: c=hx('#ffd86a') if lit_r.random()<0.62 else hx('#20203a')
                    else: c=hx('#3c4d7a') if (x+depth)%4 else hx('#a8d4ff')
                if depth==0: c=sh(c,0.75)
                px[x,y]=c
        # roof
        for y in range(max(0,y0-h),min(H,y1-h+1)):
            for x in range(max(0,x0),min(W,x1+1)):
                if not rf.getpixel((x,y)): continue
                edge=not(rf.getpixel((min(W-1,x+1),y)) and rf.getpixel((max(0,x-1),y)) and rf.getpixel((x,min(H-1,y+1))) and rf.getpixel((x,max(0,y-1))))
                c=rc
                if edge:
                    c=mix(rc,(255,255,255),0.35) if (not rf.getpixel((x,max(0,y-1))) or not rf.getpixel((max(0,x-1),y))) else rd
                elif (x+y)%9==0: c=mix(rc,rd,0.22)
                px[x,y]=c
        # rooftop detail: a vent box on big flat roofs
        if b['area']>140 and not b.get('sp'):
            cx,cy=round(b['c'][0]),round(b['c'][1])-h
            if rf.getpixel((cx,cy)) and rf.getpixel((cx+2,cy+1)):
                for dx,dy in ((0,0),(1,0),(0,1),(1,1)): px[cx+dx,cy+dy]=sh(rc,0.7)
                px[cx,cy-1]=mix(rc,(255,255,255),0.4); px[cx+1,cy-1]=mix(rc,(255,255,255),0.4)
        # outline
        sil=ImageChops.lighter(rf, ImageChops.lighter(fm_, mask()))
        for k in range(1,h): ImageDraw.Draw(sil).polygon([(x,y-k) for x,y in pl],fill=255)
        sp=sil.load()
        for y in range(max(1,y0-h-1),min(H-1,y1+2)):
            for x in range(max(1,x0-1),min(W-1,x1+2)):
                if not sp[x,y] and (sp[x+1,y] or sp[x-1,y] or sp[x,y+1] or sp[x,y-1]):
                    px[x,y]=hx('#2a2236')
    # Du Bois: crown + a flag; chapel: little bell tower
    if 'dubois' in special:
        b=special['dubois']; cx=round((b['bb'][0]+b['bb'][2])/2); top=b['bb'][1]-b['h']
        for x in range(b['bb'][0]+1,b['bb'][2]): px[x,top+1]=hx('#e8e0d0')
    if 'chapel' in special:
        b=special['chapel']; cx=round(b['c'][0]); top=b['bb'][1]-b['h']
        for y in range(top-7,top+1):
            for x in range(cx-2,cx+2): px[x,y]=hx('#9c3b2e') if x<cx+1 else hx('#6e2a22')
        for x in range(cx-3,cx+3): px[x,top-8]=hx('#2a2236')
        px[cx-1,top-9]=hx('#2a2236'); px[cx-1,top-5]=hx('#f4d35e') if night else hx('#2a2236')
    if night:
        out=Image.new('RGB',(W,H)); op=out.load()
        for y in range(H):
            for x in range(W):
                c=px[x,y]
                if c in (hx('#ffd86a'),hx('#f4d35e')): op[x,y]=c; continue
                l=(c[0]*0.3+c[1]*0.59+c[2]*0.11)/255
                op[x,y]=(round(c[0]*0.28+10),round(c[1]*0.32+14),round(c[2]*0.5+40))
        # street lamps: soft pools of light along the paths
        lr=random.Random(3)
        for _ in range(140):
            x,y=lr.randrange(3,W-3),lr.randrange(3,H-3)
            if not rm[x,y] or wdm[x,y]: continue
            for dy in range(-4,5):
                for dx in range(-5,6):
                    d=(dx*dx)/30+(dy*dy)/20
                    if d<1 and 0<=x+dx<W and 0<=y+dy<H:
                        c=op[x+dx,y+dy]; op[x+dx,y+dy]=mix(c,(255,214,120),0.35*(1-d))
            op[x,y]=(255,240,190)
        # moon on the pond
        if wb:
            mx,my=(wb[0]+wb[2])//2,(wb[1]+wb[3])//2
            for dy in range(-6,7):
                if wm[mx,my+dy]: op[mx,my+dy]=(220,230,255) if dy%2==0 else op[mx,my+dy]
        return out
    return im
day=render(False); day.save('map_day.png')
def snowify(img,night=False):
    out=img.copy(); p=out.load()
    GR={hx('#6cc24a'),hx('#5fb43f'),hx('#7fd05a'),hx('#86d462'),hx('#7acb57')}
    TL={hx('#7ccf5c'),hx('#45a84a')}
    for y in range(H):
        for x in range(W):
            c=p[x,y]
            if c in GR: p[x,y]=(236,242,250) if (x*7+y*3)%13 else (214,224,240)
            elif c in TL: p[x,y]=(246,250,255) if c==hx('#7ccf5c') else (196,214,214)
            elif c in (hx('#3fb6e8'),hx('#2c95d0'),hx('#58c8f0'),hx('#bdeeff')): p[x,y]=(176,214,236) if (x+y)%5 else (220,240,252)
            elif c in (hx('#e2cf9e'),hx('#d6c08e')): p[x,y]=(206,206,214)
            elif c[1]>c[0]+20 and c[1]>c[2]+20 and c[1]<200: p[x,y]=mix(c,(225,232,244),0.75)   # shaded lawn
    return out
snowday=snowify(day); snowday.save('map_snow_day.png')
night=render(True); night.save('map_night.png')
sn=snowify(day).load(); nn=night.copy(); np_=nn.load(); dp=day.load()
for y in range(H):
    for x in range(W):
        if sn[x,y]!=dp[x,y]:
            c=sn[x,y]; np_[x,y]=(round(c[0]*0.36+12),round(c[1]*0.4+16),round(c[2]*0.55+42))
nn.save('map_snow_night.png')
json.dump({k:[round(v['c'][0]),round(v['c'][1])] for k,v in special.items()},open('map2_meta.json','w'))
print(W,H,len(blds),{k:(round(v['c'][0]),round(v['c'][1]),v['h']) for k,v in special.items()})

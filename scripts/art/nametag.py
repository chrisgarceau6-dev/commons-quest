"""Stitch a name centred on the visible chest: measured after every part is drawn, painted only onto the cloth itself."""
def width(word,font,gap=1,space=2):
    w=0
    for ch in word: w+=space if ch==' ' else len(font[ch][0])+gap
    return w-gap
def stitch(c,word,y,mats,font,col,shadow=None,cx=None,lines=None):
    mats=set(mats) if not isinstance(mats,str) else {mats}
    rows=[y+j for j in range(5)]
    if cx is None:
        cs=[]
        for yy in rows:
            xs=[x for x in range(c.w) if c.g[yy][x] in mats]
            if xs:
                # the cloth's run that contains the most pixels (ignores a stray strap or a far-side sliver)
                runs=[]; st=xs[0]; pv=xs[0]
                for x in xs[1:]+[None]:
                    if x is None or x!=pv+1: runs.append((st,pv)); st=x
                    if x is not None: pv=x
                a,b=max(runs,key=lambda r:r[1]-r[0])
                cs.append((a+b)/2)
        cx=sorted(cs)[len(cs)//2]
    w=width(word,font); x=round(cx-(w-1)/2)
    pts=[]
    for ch in word:
        if ch==' ': x+=2; continue
        for j,row in enumerate(font[ch]):
            for i,v in enumerate(row):
                if v=='1': pts.append((x+i,y+j))
        x+=len(font[ch][0])+1
    ok=lambda p: 0<=p[0]<c.w and 0<=p[1]<c.h and c.g[p[1]][p[0]] in mats
    if shadow:
        for (a,b) in pts:
            if ok((a+1,b+1)) and (a+1,b+1) not in pts: c.fix(a+1,b+1,shadow)
    for p in pts:
        if ok(p): c.fix(*p,col)
    return cx

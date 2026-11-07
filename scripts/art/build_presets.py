import json, importlib
from PIL import Image
import hero_presets as HP
from pixart2 import sheet
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
SK0=['#8a3e26','#e0956e','#f2b48c','#ffcfa3','#ffe6c4']
SKX={'#c9714e':0.7,'#e8a07a':1.45,'#d98a66':0.9,'#e7a07a':1.45}
HR0=['#1a0b08','#3a1c14','#5c3220','#7d4a2a','#9c6436']
HRX={'#a8703c':4.3,'#8a5a30':3.5}
SKIN={
 'light': SK0,
 'fair':  ['#7a3a2a','#e6a488','#f6c4a8','#ffdcc4','#fff0e2'],
 'golden':['#6e3e20','#cf9466','#e8b484','#f6cfa2','#ffe8c8'],
 'tan':   ['#5e2c16','#b8754a','#d39468','#e8b080','#f5cc9e'],
 'brown': ['#3e1c0e','#8a4e2c','#a8653a','#c27e50','#d89a6a'],
 'deep':  ['#200e08','#4e2814','#6a3a20','#84502e','#9e6a44'],
}
HAIR={
 'brown': HR0,
 'black': ['#050407','#120e16','#221c2a','#352c40','#4c4260'],
 'blonde':['#5a3a10','#b8862e','#dcae4a','#f0cc6e','#fde49a'],
 'auburn':['#3a0c06','#7a2412','#a3391c','#c4552a','#de7a3e'],
 'dkbrown':['#120806','#2a140c','#3e2014','#56301e','#704228'],
}
def lerp_ramp(r,level):
    level=max(0,min(4,level)); i=int(level); t=level-i
    a=hx(r[i]); b=hx(r[min(4,i+1)]); return tuple(round(a[k]+(b[k]-a[k])*t) for k in range(3))
def palette(skin,hair):
    m={}
    for i,cn in enumerate(SK0): m[hx(cn)]=hx(SKIN[skin][i])
    for cn,l in SKX.items(): m[hx(cn)]=lerp_ramp(SKIN[skin],l)
    for i,cn in enumerate(HR0): m[hx(cn)]=hx(HAIR[hair][i])
    for cn,l in HRX.items(): m[hx(cn)]=lerp_ramp(HAIR[hair],l)
    return m
def swap(im,m):
    im=im.copy(); px=im.load()
    for y in range(im.height):
        for x in range(im.width):
            p=px[x,y]
            if p[3] and p[:3] in m: px[x,y]=m[p[:3]]+(p[3],)
    return im
PRESETS=[
 ('og',    'Chris',  'short','light','brown',False),
 ('p2',    'Marcus', 'fade', 'deep', 'black',False),
 ('p3',    'Diego',  'short','tan',  'black',False),
 ('p4',    'Kenji',  'short','golden','black',False),
 ('p5',    'Jamal',  'curly','brown','black',False),
 ('g1',    'Emma',   'pony', 'fair', 'blonde',True),
 ('g2',    'Aaliyah','puff', 'deep', 'black',True),
 ('g3',    'Sofia',  'long', 'tan',  'dkbrown',True),
 ('g4',    'Mei',    'bun',  'golden','black',True),
 ('g5',    'Priya',  'braids','brown','black',True),
 ('g6',    'Riley',  'long', 'light','auburn',True),
]
if __name__=='__main__':
    out={}
    for pid,name,hair,skin,hc,lash in PRESETS:
        HP.STYLE.clear(); HP.STYLE.update(hair=hair,lash=lash)
        imgs=[swap(HP.hero(k),palette(skin,hc)) for _,k in HP.FR]
        sheet(imgs,f'presets/hero_{pid}.png'); out[pid]=name
    json.dump(out,open('presets/presets.json','w'))
    # lineup
    S=5; L=Image.new('RGBA',(68*S*len(PRESETS),48*S),(143,211,255,255))
    for k,(pid,*_ ) in enumerate(PRESETS):
        f=Image.open(f'presets/hero_{pid}.png').crop((0,0,68,48)).resize((68*S,48*S),Image.NEAREST)
        L.alpha_composite(f,(k*68*S,0))
    L.save('preview__presets.png')

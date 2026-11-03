from pixart import Canvas, RAMPS, sheet
from PIL import Image
RAMPS.update({
 'qz':   ['#0b1a4a','#1d4fa8','#2f74e0','#5a9bff','#9cc4ff'],
 'qzdk': ['#0b1a4a','#123a80','#1d4fa8','#2f74e0','#5a9bff'],
 'sw':   ['#2a2b36','#7c7f8c','#a3a6b3','#c4c7d2','#e3e5ec'],
 'swdk': ['#2a2b36','#5f6272','#7c7f8c','#a3a6b3','#c4c7d2'],
 'kick': ['#2a2b36','#c9cde0','#f4f5ff','#ffffff','#ffffff'],
 'sole': ['#2a2b36','#9aa0b4','#c9cde0','#e6e8f2','#ffffff'],
})
W=H=48
def leg(c,hip_x,foot_x,lift=0):
    # baggy sweatpant leg from hip to ankle, bunched cuff, sneaker
    c.line(hip_x,34,foot_x,41-lift,'sw',5)
    c.rect(foot_x-2,41-lift,foot_x+2,42-lift,'swdk')
    c.rect(foot_x-2,43-lift,foot_x+4,44-lift,'kick')
    c.rect(foot_x-2,45-lift,foot_x+4,45-lift,'sole')

def hero(f):
    c=Canvas(W,H)
    b=f.get('bob',0); o=f.get('lean',0); arm=f.get('arm','down'); face=f.get('face','normal')
    legs=f.get('legs',[(21,20,0),(27,28,0)])
    # back arm (behind torso)
    if arm=='windup':
        c.line(22+o,24+b,13+o,13+b,'qz',4); c.ell(12+o,12+b,1.8,1.8,'skin')
        c.line(11+o,11+b,5+o,4+b,'metal',2); c.rect(1+o,0,6+o,3,'metal')
        for x in (1,3,5): c.px(x+o,0,'metal')
    c.ell(16+o,28+b,2.6,5,'qzdk'); c.ell(16+o,33+b,1.8,1.6,'skin')
    for hx,fx,lift in legs: leg(c,hx,fx,lift)
    # torso: quarter-zip
    c.ell(24+o,29+b,8.5,6,'qz'); c.rect(16+o,25+b,32+o,33,'qz')
    c.rect(16+o,32,32+o,33,'qzdk')
    c.rect(21+o,21+b,29+o,23+b,'qzdk')           # collar stand
    for y in range(22,28): c.fix(27+o,y+b,'#dfe6f2')  # zipper
    c.fix(27+o,28+b,'#ffffff'); c.fix(28+o,28+b,'#9aa3b5')
    # head
    c.ell(24+o,13+b,10,9.5,'skin')
    c.ell(23+o,7.5+b,11,6,'hair'); c.rect(13+o,6+b,18+o,17+b,'hair')
    for x,y in [(29,9),(30,9),(31,10),(32,10),(33,11),(28,10),(24,9),(25,10),(20,9)]: c.px(x+o,y+b,'hair')
    c.ell(18.5+o,14+b,1.6,2.2,'skin')
    # face
    if face=='blink':
        for x in (27,28,29): c.fix(x+o,15+b,'#1b1033')
        c.fix(32+o,15+b,'#1b1033'); c.fix(33+o,15+b,'#1b1033')
    elif face=='happy':
        for x,y in [(27,15),(28,14),(29,15),(32,15),(33,14)]: c.fix(x+o,y+b,'#1b1033')
    elif face=='hurt':
        for x,y in [(27,13),(28,14),(29,15),(28,16),(27,17),(33,13),(32,14),(33,15)]: c.fix(x+o,y+b,'#1b1033')
    else:
        c.rect(27+o,13+b,29+o,16+b,'dark'); c.fix(27+o,13+b,'#ffffff'); c.fix(28+o,13+b,'#ffffff'); c.fix(27+o,14+b,'#ffffff')
        c.rect(32+o,13+b,33+o,16+b,'dark'); c.fix(32+o,13+b,'#ffffff')
    if face in('normal','blink'):
        for x in (26,27,28): c.fix(x+o,11+b,'#3b1f0e')
        c.fix(32+o,11+b,'#3b1f0e'); c.fix(33+o,11+b,'#3b1f0e')
        c.fix(29+o,19+b,'#1b1033'); c.fix(30+o,20+b,'#1b1033'); c.fix(31+o,20+b,'#1b1033'); c.fix(32+o,19+b,'#1b1033')
    elif face=='happy':
        c.rect(29+o,18+b,32+o,20+b,'dark'); c.fix(30+o,20+b,'#ff6f8f'); c.fix(31+o,20+b,'#ff6f8f')
        for x in (29,30,31,32): c.fix(x+o,18+b,'#ffffff')
    elif face=='hurt':
        for x,y in [(29,20),(30,19),(31,20),(32,19)]: c.fix(x+o,y+b,'#1b1033')
    else: # fierce (attack)
        c.rect(29+o,19+b,32+o,20+b,'dark'); c.fix(30+o,19+b,'#ffffff'); c.fix(31+o,19+b,'#ffffff')
    if face!='hurt':
        c.fix(25+o,17+b,'#ff9fae'); c.fix(26+o,17+b,'#ff9fae'); c.fix(34+o,17+b,'#ff9fae')
    if face=='fierce':
        c.fix(26+o,11+b,'#3b1f0e');c.fix(27+o,12+b,'#3b1f0e');c.fix(28+o,12+b,'#3b1f0e');c.fix(33+o,11+b,'#3b1f0e');c.fix(32+o,12+b,'#3b1f0e')
    # front arm + fork
    if arm=='down':
        c.line(29+o,24+b,35+o,31+b,'qz',4); c.rect(34+o,31+b,36+o,32+b,'qzdk'); c.ell(36+o,33+b,1.8,1.8,'skin')
        c.line(38+o,38+b,38+o,15+b,'metal'); c.rect(36+o,12+b,40+o,14+b,'metal')
        for x in (36,38,40): c.line(x+o,8+b,x+o,11+b,'metal')
    elif arm=='windup':
        pass
    elif arm=='strike':
        c.line(29+o,24+b,37+o,24+b,'qz',4); c.rect(37+o,23+b,38+o,26+b,'qzdk'); c.ell(39+o,24+b,1.8,1.8,'skin')
        c.line(40+o,24+b,42,24+b,'metal',2); c.rect(42,21+b,43,27+b,'metal')
        for y in (21,24,27): c.line(44,y+b,47,y+b,'metal')
    elif arm=='victory':
        c.line(30+o,24+b,38+o,20+b,'qz',4); c.line(38+o,20+b,40+o,13+b,'qz',4); c.ell(40+o,11+b,1.8,1.8,'skin')
        c.line(40+o,10+b,40+o,5,'metal',2); c.rect(38+o,2,42+o,4,'metal')
        for x in (38,40,42): c.line(x+o,0,x+o,1,'metal')
    img=c.render()
    if arm=='strike':  # motion smear in front of the swing
        import math
        for t in range(40):
            a=-1.3+t*0.03; 
            for r,al in ((13,200),(12,150),(14,110)):
                x=round(33+r*math.cos(a)); y=round(24+r*math.sin(a))
                if 0<=x<48 and 0<=y<48 and img.getpixel((x,y))[3]==0: img.putpixel((x,y),(255,255,255,al))
    return img

L0=[(21,20,0),(27,28,0)]
frames=[
 ('Idle 1',dict()),
 ('Idle 2 (blink)',dict(bob=1,face='blink',legs=L0)),
 ('Walk 1',dict(legs=[(21,17,0),(27,31,0)])),
 ('Walk 2',dict(bob=-1,legs=[(21,22,2),(27,26,0)])),
 ('Walk 3',dict(legs=[(21,25,0),(27,23,0)])),
 ('Walk 4',dict(bob=-1,legs=[(21,20,0),(27,28,2)])),
 ('Wind-up',dict(lean=-2,arm='windup',face='fierce',legs=[(21,18,0),(27,29,0)])),
 ('Strike',dict(lean=2,arm='strike',face='fierce',legs=[(21,17,0),(27,32,0)])),
 ('Hurt',dict(lean=-2,face='hurt',legs=[(21,19,0),(27,27,0)])),
 ('Victory',dict(bob=-1,arm='victory',face='happy',legs=[(21,19,0),(27,29,0)])),
]
imgs=[hero(f) for _,f in frames]
sheet(imgs,'hero2.png')
import pickle; pickle.dump([n for n,_ in frames],open('hero2_names.pkl','wb'))
print('ok')

import math
from PIL import Image
from pixart import Canvas, RAMPS, hexc
RAMPS.update({
 'bowl':['#0d1a4a','#1f4fc2','#3a7bff','#6fa3ff','#a8c8ff'],
 'rim': ['#0d1a4a','#c9cde0','#f4f5ff','#ffffff','#ffffff'],
 'rice':['#6b6a80','#d9d6e6','#fbfaff','#ffffff','#ffffff'],
 'chick':['#5a2408','#b8561a','#e8842e','#ffad5a','#ffd08f'],
 'broc':['#0b3a12','#1f8a2e','#3fc24c','#7be37f','#b6f5b0'],
 'yolk':['#7a4a00','#e8a400','#ffcc3d','#ffe27a','#fff3b8'],
 'steam':['#7d7f99','#e6e8ff','#ffffff','#ffffff','#ffffff'],
})
N=36
c=Canvas(N,N)
# food mound
c.ell(18,18.5,11.5,5.5,'rice')
for x,y in [(11,17),(15,15),(21,16)]: c.ell(x,y,2.6,2.0,'chick')
c.ell(26,16.5,2.2,2.2,'broc'); c.ell(24,14.5,2,2,'broc'); c.rect(25,17,26,19,'broc')
c.ell(17.5,13.5,3.2,2.4,'rice'); c.ell(17.5,13.8,1.6,1.3,'yolk')
# bowl body (lower half of ellipse) + rim
for y in range(21,34):
    for x in range(N):
        if ((x-18)/13.5)**2+((y-20.5)/12.5)**2<=1: c.px(x,y,'bowl')
c.rect(15,33,21,34,'bowl')
c.ell(18,21,13.8,2.2,'rim')
# face
for ex in (11,23):
    c.rect(ex,25,ex+2,27,'dark'); c.fix(ex,25,'#ffffff'); c.fix(ex+1,25,'#ffffff')
for i in range(4): c.px(10+i,23+ (1 if i<2 else 0) - (0 if i<2 else 0),'dark')
c.line(10,23,13,24,'dark'); c.line(26,23,23,24,'dark')
c.rect(14,28,22,29,'dark'); c.rect(15,30,21,30,'dark'); c.rect(16,31,20,31,'dark')
c.fix(15,28,'#ffffff');c.fix(16,28,'#ffffff');c.fix(20,28,'#ffffff');c.fix(21,28,'#ffffff')
for x in (17,18,19): c.fix(x,30,'#ff6f8f')
for x,y in [(8,28),(9,28),(27,28),(28,28)]: c.fix(x,y,'#ff8fae')
# steam
for x0,top in ((12,3),(18,1),(24,3)):
    for i,y in enumerate(range(10,top,-1)):
        x=x0+round(math.sin(i*.75)*1.4)
        c.fix(x,y,'#ffffff'); c.fix(x+1,y,'#ffd6ea')
spr=c.render()
# background sunburst
bg=Image.new('RGBA',(N,N))
for y in range(N):
    for x in range(N):
        a=math.atan2(y-19,x-18); r=math.hypot(x-18,y-19)
        ray=int((a+math.pi)/(2*math.pi)*16)%2
        col=['#ff4fa3','#ff86c4'][ray]
        if r>21: col=['#d42c7f','#e85aa3'][ray]
        bg.putpixel((x,y),hexc(col))
# sparkles
for x,y in [(4,6),(31,5),(30,30),(5,31)]:
    for dx,dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]: bg.putpixel((x+dx,y+dy),hexc('#fff3a8' if (dx or dy) else '#ffffff'))
bg.alpha_composite(spr)
OUT='/tmp/claude-0/-home-claude/dde05494-8074-5f71-a563-8a539f6f5958/scratchpad/gq-app/'
bg.resize((180,180),Image.NEAREST).convert('RGB').save(OUT+'icon-180.png')
big=Image.new('RGB',(512,512),hexc('#d42c7f')[:3]); big.paste(bg.resize((504,504),Image.NEAREST).convert('RGB'),(4,4)); big.save(OUT+'icon-512.png')
print('ok')

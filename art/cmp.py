import sys
from PIL import Image
def frame(path,i,fw,fh): return Image.open(path).crop((i*fw,0,i*fw+fw,fh))
rows=[('hero3.png','hero3_p2.png',56,48),('bear3.png','bear3_p2.png',72,72),('wyrm.png','wyrm_p2.png',82,72)]
S=6
W=sum([2*fw*S+40 for _,_,fw,_ in rows[:1]]) 
out=[]
for a,b,fw,fh in rows:
    im=Image.new('RGBA',(2*fw*S+20,fh*S),(143,211,255,255))
    im.alpha_composite(frame(a,0,fw,fh).resize((fw*S,fh*S),Image.NEAREST),(0,0))
    im.alpha_composite(frame(b,0,fw,fh).resize((fw*S,fh*S),Image.NEAREST),(fw*S+20,0))
    out.append(im)
for k,im in enumerate(out): im.save(f'../audit/_cmp{k}.png')

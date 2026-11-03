from PIL import Image
# hand-placed chef's toque in the reference style (lit from the left to match our characters)
G = [
"......oooo....ooooo.......",
".....oWWWlo.ooWWWWWoo.....",
"....oWWWWWlomWWWWWWWlo....",
"...oWWWWWWWlWWWWWWWWWlo...",
"..oWWWWWWWWWlWWWWWWWWllo..",
"..oWWWWWWWWWWlWWWWWWWllmo.",
".oWWWWWWWWWWWlWWWWWWlllmo.",
".oWWWWWWlWWWWlWWWWWlllmmo.",
".olWWWWWWlWWWlWWWWlllmmmo.",
"..ollWWWWWlWWlWWWlllmmmo..",
"...oollllllmmmmmmmmmmoo...",
"....ooWWWWWWWlllllmmoo....",
"....oWWWWWWWWlllllmmmo....",
"....oWWWWWWWWlllllmmmo....",
"....omlmlmlmlmlmlmmmmo....",
"....oddddddddddddddddo....",
".....oooooooooooooooo.....",
]
PAL={'o':(70,74,88,255),'W':(255,255,255,255),'l':(226,230,238,255),'m':(184,190,204,255),'d':(140,146,162,255)}
def hat_img():
    w=max(len(r) for r in G); im=Image.new('RGBA',(w,len(G)),(0,0,0,0))
    for y,r in enumerate(G):
        for x,ch in enumerate(r):
            if ch in PAL: im.putpixel((x,y),PAL[ch])
    return im
def put_hat(c,cx,band_bottom_y):
    w=max(len(r) for r in G); x0=round(cx-w/2); y0=band_bottom_y-15
    for y,r in enumerate(G):
        for x,ch in enumerate(r):
            if ch in PAL: c.fix(x0+x,y0+y,'#%02x%02x%02x'%PAL[ch][:3])
if __name__=='__main__':
    h=hat_img(); h.resize((h.width*14,h.height*14),Image.NEAREST).save('../audit/_hat.png')

from pixart import Canvas, sheet
from PIL import Image

OUT = '/tmp/claude-0/-home-claude/dde05494-8074-5f71-a563-8a539f6f5958/scratchpad/art/'
from pixart import RAMPS
RAMPS['tie'] = ['#3d0612', '#6e0d20', '#a5162f', '#d23a52', '#f0647a']


def hero(bob=0, legs=0, arm='down', dx=0):
    c = Canvas(40, 34)
    b = bob
    o = dx
    # legs (walk phase: -1, 0, 1)
    lx = [(13, 15), (18, 20)]
    sh = [legs, -legs]
    for (x0, x1), s in zip(lx, sh):
        c.rect(x0 + o + s, 23, x1 + o + s, 29, 'jeans')
        c.rect(x0 + o + s - (1 if s < 0 else 0), 30, x1 + o + s + 1, 31, 'shoe')
    # back arm
    c.ell(11 + o, 19 + b, 2, 3.5, 'hood')
    c.ell(11 + o, 23 + b, 1.5, 1.5, 'skin')
    # torso hoodie
    c.ell(16.5 + o, 20 + b, 6, 5, 'hood')
    c.rect(11 + o, 19 + b, 22 + o, 24, 'hood')
    # UM letters
    # hoodie details: drawstrings + kangaroo pocket
    for x in (15, 18):
        c.fix(x + o, 17 + b, '#ffffff'); c.fix(x + o, 18 + b, '#f4f5ff'); c.fix(x + o, 19 + b, '#c9cde0')
    for x in range(13, 21): c.fix(x + o, 21 + b, '#6e0d20')
    c.fix(13 + o, 22 + b, '#6e0d20'); c.fix(20 + o, 22 + b, '#6e0d20')
    # head
    c.ell(17 + o, 9 + b, 6.5, 6, 'skin')
    c.px(23.5 + o, 10 + b, 'skin')
    # hair: top + back
    c.ell(16 + o, 5 + b, 7, 3.5, 'hair')
    c.rect(10 + o, 5 + b, 12 + o, 10 + b, 'hair')
    for x, y in [(20, 7), (21, 7), (22, 7), (23, 6), (19, 8)]:
        c.px(x + o, y + b, 'hair')
    # ear
    c.px(13 + o, 10 + b, 'skin')
    # eye + brow + mouth
    c.rect(19 + o, 9 + b, 20 + o, 11 + b, 'dark')
    c.fix(20 + o, 9 + b, '#ffffff')
    c.rect(18 + o, 7 + b, 21 + o, 7 + b, 'hair')
    c.rect(20 + o, 13 + b, 22 + o, 13 + b, 'dark')
    c.fix(21 + o, 13 + b, '#c2405a')
    # front arm + fork
    if arm == 'down':
        c.line(20 + o, 17 + b, 24 + o, 21 + b, 'hood', 3)
        c.ell(25 + o, 22 + b, 1.6, 1.6, 'skin')
        c.line(26 + o, 4 + b, 26 + o, 25 + b, 'metal')
        c.rect(24 + o, 1 + b, 28 + o, 4 + b, 'metal')
        for x in (24, 26, 28):
            c.px(x + o, 0 + b, 'metal')
        for x in (25, 27):
            c.g[1 + b][x + o] = None
    elif arm == 'up':
        c.line(20 + o, 17 + b, 18 + o, 12 + b, 'hood', 3)
        c.ell(17 + o, 11 + b, 1.6, 1.6, 'skin')
        c.line(17 + o, 11 + b, 6 + o, 2 + b, 'metal', 2)
        c.rect(3 + o, 0, 7 + o, 2, 'metal')
    else:  # strike
        c.line(20 + o, 18 + b, 27 + o, 18 + b, 'hood', 3)
        c.ell(28 + o, 18 + b, 1.6, 1.6, 'skin')
        c.line(28 + o, 18 + b, 36 + o, 18 + b, 'metal', 2)
        c.rect(36 + o, 16 + b, 39 + o, 20 + b, 'metal')
        for y in (17, 19):
            c.g[y + b][38 + o] = None
            c.g[y + b][39 + o] = None
    return c.render()


def bear(phase=0, mood='idle', drop=0):
    c = Canvas(56, 56)
    br = 1 if phase in (1, 2) else 0
    hy = drop + (1 if phase in (1, 2) else 0)
    by = drop
    # legs
    c.rect(17, 46 + by // 2, 23, 51, 'fur')
    c.rect(31, 46 + by // 2, 37, 51, 'fur')
    c.rect(16, 51, 24, 53, 'tan')
    c.rect(30, 51, 38, 53, 'tan')
    # body
    c.ell(27, 37 + by, 15, 12 - br * .5 - drop * .3, 'fur')
    c.ell(27, 39 + by, 9, 8, 'tan')
    # chef apron: neck straps, bib, flared skirt, maroon waist tie, pocket
    c.line(22, 30 + by, 24, 34 + by, 'tie'); c.line(32, 30 + by, 30, 34 + by, 'tie')
    c.rect(23, 34 + by, 31, 38 + by, 'white')
    for y in range(39, 49):
        half = min(9, 6 + (y - 39) * .6) - (1 if y == 48 else 0)
        c.rect(round(27 - half), y + by, round(27 + half), y + by, 'white')
    c.rect(20, 38 + by, 34, 39 + by, 'tie')
    c.px(19, 40 + by, 'tie'); c.px(35, 40 + by, 'tie')
    for x in range(24, 31): c.fix(x, 42 + by, '#b9bdd6')
    for y in range(42, 46): c.fix(24, y + by, '#b9bdd6'); c.fix(30, y + by, '#b9bdd6')
    c.fix(27, 36 + by, '#a5162f')
    # arms (swing with phase)
    sw = [0, 1, 0, -1][phase % 4]
    c.ell(11, 35 + by + sw, 4.5, 7.5, 'fur')
    c.ell(43, 35 + by - sw, 4.5, 7.5, 'fur')
    c.ell(10, 41 + by + sw, 3, 2.5, 'tan')
    c.ell(44, 41 + by - sw, 3, 2.5, 'tan')
    # spatula in left paw
    c.line(9, 41 + by + sw, 4, 26 + by + sw, 'metal', 2)
    c.rect(1, 20 + by + sw, 6, 26 + by + sw, 'metal')
    # head
    c.ell(16, 11 + hy, 4, 4, 'fur'); c.ell(16, 11 + hy, 2, 2, 'tan')
    c.ell(38, 11 + hy, 4, 4, 'fur'); c.ell(38, 11 + hy, 2, 2, 'tan')
    c.ell(27, 21 + hy, 13, 10.5, 'fur')
    c.ell(23, 26 + hy, 6, 4, 'tan')
    c.rect(19, 23 + hy, 22, 25 + hy, 'nose')
    c.fix(20, 23 + hy, '#6b5a80')
    if mood == 'hurt' or mood == 'ko':
        for x0 in (17, 29):
            for i in range(4):
                c.px(x0 + i, 17 + hy + i, 'dark'); c.px(x0 + 3 - i, 17 + hy + i, 'dark')
        c.rect(22, 29 + hy, 27, 29 + hy, 'dark')
    else:
        for x0 in (18, 30):
            c.rect(x0, 18 + hy, x0 + 2, 20 + hy, 'dark')
            c.fix(x0, 18 + hy, '#ffffff')
        c.line(16, 15 + hy, 21, 17 + hy, 'nose')
        c.line(28, 17 + hy, 33, 15 + hy, 'nose')
        c.rect(23, 29 + hy, 27, 29 + hy, 'dark')
        c.fix(24, 30 + hy, '#ffffff'); c.fix(26, 30 + hy, '#ffffff')
    # chef hat
    if mood != 'ko' or drop < 8:
        c.ell(21, 4 + hy, 5, 4, 'white')
        c.ell(27, 3 + hy, 5.5, 4.5, 'white')
        c.ell(33, 4 + hy, 5, 4, 'white')
        c.rect(19, 6 + hy, 35, 10 + hy, 'white')
    else:
        c.ell(45, 50, 5, 3, 'white')
    return c.render()


h = [hero(0, 0, 'down'), hero(1, 0, 'down'), hero(0, -1, 'down'), hero(0, 1, 'down'), hero(0, 0, 'up'), hero(0, 0, 'strike', 0)]
sheet(h, OUT + 'hero.png')
bf = [bear(0), bear(1), bear(2), bear(3), bear(0, 'hurt'), bear(0, 'ko', 4), bear(0, 'ko', 10)]
sheet(bf, OUT + 'bear.png')
prev = Image.new('RGBA', (40 * 6 * 4, 34 * 4 + 56 * 4 + 20), (36, 26, 77, 255))
prev.paste(sheet(h, OUT + '_h.png', 4), (0, 0))
prev.paste(sheet(bf, OUT + '_b.png', 4), (0, 34 * 4 + 20))
prev.save(OUT + 'preview.png')
print('ok')

from PIL import Image


PAD = 12

# Palette-matched trace of the supplied reference image.
COLORS = {
    'K': (44, 47, 60, 255),
    'D': (91, 99, 110, 255),
    'M': (140, 146, 164, 255),
    'L': (205, 210, 222, 255),
    'W': (255, 255, 255, 255),
}

# Exact 30x27 pixel-grid trace. The cuff is at the lower-right of the poof,
# matching the three-quarter angle of the supplied hat.
HAT = (
    '.....................M........',
    '.............DDDD..DDLWWWD....',
    '...........DDDDDDDDLWWWWWWD...',
    '.........DDMWWWWWWMWWWWWWWWD..',
    '........KWWWWWWWWKWWWWWWWWWWM.',
    '......DKWWWWWWWWWWWWWWWWWWWWW.',
    '....DDMMWWWWWWWWWWWWWWWWWWWWW.',
    '...DMLMWWWWWWWWWWWWWWWLMWWWWW.',
    '...MLLMWWWWWWWWWWWWWWWMWWWWWW.',
    '..KMLMMLWWWWWLWWWWWWWMDWWWWWWD',
    '..KLLLLLWWWWLMWWWWWWWMWWWWWWKD',
    '.KMLLLLLLWWWWWMWWWWWMDWWWWWL..',
    'DMMLLLLLLLWWWWWDWWWWMDLLLMLKK.',
    'DMMMLLLLLLLLWWWWDLLDDDMMDDKK..',
    'KMMMMLLLMLLLLWWWMDDWWWWWWWK...',
    'KMMMMMLLDDMLLLLDWWWDDDDDWWKK..',
    '.KMMMMMLLMDDMMDWDDWWWWWWWWKK..',
    '.KKMMMLLLLMDDMDDWWWWWWWWWWWKK.',
    '.LKKMMLLLLLKDDLLWWWWWWWWWWWKK.',
    '...KKMMMLLKKKMLLLLWWWKWWWWKKK.',
    '...LKKKKMKKKKLLLLWKKKKKKKKKKK.',
    '.......KKKKMMLLKKKDDMMMMMMDKK.',
    '.......LLLKMMLMKKMDMMMMMMMKK..',
    '...........KMMKDMMMMMMMMMKK...',
    '...........KMKDDMMMMMMKKK.....',
    '............KKDDMMKKKK........',
    '.............KKKKKLLL.........',
)


def _make_worn_hat():
    """Build the traced hat and level its cuff so it sits on the skull."""
    traced = Image.new('RGBA', (len(HAT[0]), len(HAT)))
    for y, row in enumerate(HAT):
        for x, value in enumerate(row):
            color = COLORS.get(value)
            if color is not None:
                traced.putpixel((x, y), color)

    worn = traced.rotate(-12, Image.Resampling.NEAREST, expand=True)
    return worn.crop(worn.getbbox())


WORN_HAT = _make_worn_hat()
CROWN_HAT = WORN_HAT.crop((0, 0, WORN_HAT.width, 22))


def _make_band(width):
    """Make a rounded chef-hat band that wraps a head instead of perching."""
    height = 9
    band = Image.new('RGBA', (width, height))
    shape = set()
    for y in range(height):
        inset = 2 if y in (0, height - 1) else 1 if y in (1, height - 2) else 0
        for x in range(inset, width - inset):
            shape.add((x, y))

    for x, y in shape:
        boundary = any((x + dx, y + dy) not in shape for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
        if boundary:
            color = COLORS['K']
        elif y >= height - 3:
            color = COLORS['M'] if x < width // 4 else COLORS['L']
        elif x < width // 5:
            color = COLORS['M'] if x < 3 else COLORS['L']
        elif x >= width - 4:
            color = COLORS['L']
        else:
            color = COLORS['W']
        band.putpixel((x, y), color)

    # Subtle vertical folds make the cylinder read as cloth, not a white block.
    for x in (width // 3, (2 * width) // 3):
        for y in range(2, 6):
            if band.getpixel((x, y))[3]:
                band.putpixel((x, y), COLORS['L'] if y < 5 else COLORS['M'])
    return band


def _restore_pixels(out, source, cx, cy, radius, colors=None):
    """Bring ears/hair back in front of the band at the sides."""
    r2 = radius * radius
    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 > r2:
                continue
            if 0 <= x < out.width and 0 <= y < out.height:
                pixel = source.getpixel((x, y))
                if pixel[3] and (colors is None or pixel[:3] in colors):
                    out.putpixel((x, y), pixel)


def pad(img):
    out = Image.new('RGBA', (img.width, img.height + PAD))
    out.paste(img, (0, PAD))
    return out


def apply_hat(img, cx, top, hw, shadow, back=0.0):
    """Place the traced reference hat at the character's approved head height."""
    out = pad(img)
    character = out.copy()
    top += PAD

    # The supplied poof remains intact. A head-width cylinder replaces its
    # side-view cuff so the lower edge actually wraps the forehead.
    band = _make_band(round(hw * 2 - 1))
    band_x = round(cx - band.width // 2 + hw * back)
    band_y = top + 13 - (band.height - 1)
    crown_x = round(cx - CROWN_HAT.width // 2 + hw * back)
    crown_y = band_y - CROWN_HAT.height + 3
    out.alpha_composite(CROWN_HAT, (crown_x, crown_y))
    out.alpha_composite(band, (band_x, band_y))

    if hw <= 14:
        # Berkshire's ears sit naturally outside and in front of the band.
        _restore_pixels(out, character, round(cx - 13), top + 7, 5)
        _restore_pixels(out, character, round(cx + 12), top + 7, 5)
    else:
        # Frank's black side tufts perform the same overlap cue as ears.
        hair = {
            (5, 6, 10),
            (21, 24, 33),
            (35, 40, 56),
            (50, 58, 80),
            (70, 80, 112),
        }
        _restore_pixels(out, character, round(cx - 15), top + 9, 4, hair)
        _restore_pixels(out, character, round(cx + 15), top + 9, 4, hair)
    return out

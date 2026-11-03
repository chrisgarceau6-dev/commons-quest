"""Tiny pixel-art rig: shapes painted as material ids, then auto shading + selective outlines."""
import math
from PIL import Image

RAMPS = {  # outline, shadow, base, light, highlight
    'skin':  ['#7a3e2a', '#d68f6a', '#f6c49a', '#ffdcb8', '#fff0e0'],
    'hair':  ['#1a0c04', '#3b1f0e', '#5a321a', '#7a4a28', '#9a6238'],
    'hood':  ['#3d0612', '#6e0d20', '#a5162f', '#d23a52', '#f0647a'],
    'white': ['#7d7f99', '#c9cde0', '#f4f5ff', '#ffffff', '#ffffff'],
    'jeans': ['#0c1230', '#23357a', '#3456b8', '#5b7fe0', '#8aa6ff'],
    'shoe':  ['#0b0618', '#2b1d3a', '#4a3b5c', '#6b5a80', '#8a7aa0'],
    'metal': ['#2d3746', '#7d8ca3', '#c2cfdd', '#eef4fa', '#ffffff'],
    'dark':  ['#0b0618', '#0b0618', '#1b1033', '#1b1033', '#1b1033'],
    'fur':   ['#2a1406', '#6e3a17', '#9a5a2c', '#bf7a42', '#d99a5e'],
    'tan':   ['#6e4520', '#c08a50', '#e3b07a', '#f5d3a5', '#fff0d6'],
    'apron': ['#4a0812', '#b51f33', '#ff5e5e', '#ff8f8f', '#ffc2c2'],
    'nose':  ['#0b0618', '#1b1033', '#2b1d3a', '#4a3b5c', '#6b5a80'],
    'pink':  ['#7a2840', '#d9607f', '#ff8fae', '#ffb8cc', '#ffe0ea'],
}
FLAT = {'dark', 'nose'}


class Canvas:
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.g = [[None] * w for _ in range(h)]
        s.fixed = {}

    def px(s, x, y, m):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < s.w and 0 <= y < s.h:
            s.g[y][x] = m

    def fix(s, x, y, color):  # exact color, painted after shading
        x, y = int(round(x)), int(round(y))
        if 0 <= x < s.w and 0 <= y < s.h:
            s.fixed[(x, y)] = color

    def rect(s, x0, y0, x1, y1, m):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                s.px(x, y, m)

    def ell(s, cx, cy, rx, ry, m):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x - cx) / max(rx, .5)) ** 2 + ((y - cy) / max(ry, .5)) ** 2 <= 1.0:
                    s.px(x, y, m)

    def line(s, x0, y0, x1, y1, m, w=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
        for i in range(n + 1):
            t = i / n
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            if w == 1:
                s.px(x, y, m)
            else:
                s.rect(round(x) - w // 2, round(y) - w // 2, round(x) - w // 2 + w - 1, round(y) - w // 2 + w - 1, m)

    def render(s, light=(-1, -1), dither=True):
        img = Image.new('RGBA', (s.w, s.h), (0, 0, 0, 0))
        G = s.g
        get = lambda x, y: G[y][x] if 0 <= x < s.w and 0 <= y < s.h else None
        for y in range(s.h):
            for x in range(s.w):
                m = G[y][x]
                if m is None:
                    continue
                r = RAMPS[m]
                if m in FLAT:
                    c = r[2]
                else:
                    up, lf = get(x, y - 1) != m, get(x - 1, y) != m
                    dn, rt = get(x, y + 1) != m, get(x + 1, y) != m
                    dn2 = get(x, y + 2) != m
                    if up and lf:
                        c = r[4]
                    elif up or lf:
                        c = r[3]
                    elif dn or rt:
                        c = r[1]
                    elif dither and dn2 and (x + y) % 2 == 0:
                        c = r[1]
                    else:
                        c = r[2]
                img.putpixel((x, y), hexc(c))
        # selective outline: empty pixels touching the silhouette take the neighbour's outline tone
        out = img.copy()
        for y in range(s.h):
            for x in range(s.w):
                if G[y][x] is not None:
                    continue
                for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                    n = get(x + dx, y + dy)
                    if n is not None:
                        out.putpixel((x, y), hexc(RAMPS[n][0]))
                        break
        # internal seams between different materials get the darker outline on the lower/right side
        for y in range(s.h):
            for x in range(s.w):
                m = G[y][x]
                if m is None or m in FLAT:
                    continue
                n = get(x, y - 1)
                if n is not None and n != m and n not in FLAT and m in ('skin', 'tan') and n in ('hair', 'white'):
                    out.putpixel((x, y), hexc(RAMPS[m][1]))
        for (x, y), c in s.fixed.items():
            out.putpixel((x, y), hexc(c))
        return out


def hexc(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def sheet(frames, path, scale=1):
    w, h = frames[0].size
    s = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        s.paste(f, (i * w, 0))
    if scale != 1:
        s = s.resize((s.width * scale, s.height * scale), Image.NEAREST)
    s.save(path)
    return s

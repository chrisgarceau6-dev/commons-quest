"""Pixel-art rig v2: volume shading from one light, hue-shifted ramps, selective outlines, part separation lines."""
import math
from PIL import Image

RAMPS = {  # outline, shadow, base, light, highlight  (shadows lean cool, highlights lean warm)
    'skin':  ['#8a3e26', '#e0956e', '#f2b48c', '#ffcfa3', '#ffe6c4'],
    'hair':  ['#1a0b08', '#3a1c14', '#5c3220', '#7d4a2a', '#9c6436'],
    'hood':  ['#3d0612', '#6e0d20', '#a5162f', '#d23a52', '#f0647a'],
    'white': ['#4a4e6e', '#b9c0dc', '#e9ecf8', '#ffffff', '#ffffff'],
    'jeans': ['#0c1230', '#23357a', '#3456b8', '#5b7fe0', '#8aa6ff'],
    'shoe':  ['#0b0618', '#241a33', '#3d3150', '#5a4d70', '#7a6c90'],
    'metal': ['#262d40', '#6f7d98', '#aebdd0', '#dce6f0', '#ffffff'],
    'dark':  ['#0b0618', '#0b0618', '#1b1033', '#1b1033', '#1b1033'],
    'fur':   ['#2b1208', '#7a3a1c', '#a8602b', '#cf8a48', '#efb978'],
    'furdk': ['#2b1208', '#5a2a14', '#7a3a1c', '#975026', '#b86c36'],
    'muz':   ['#5e3a1c', '#c98f5c', '#ecc08c', '#f8d9ae', '#fff0d8'],
    'pad':   ['#2b1208', '#4e3028', '#6e463a', '#8a5e50', '#a87a6a'],
    'tan':   ['#6e4520', '#c08a50', '#e3b07a', '#f5d3a5', '#fff0d6'],
    'apron': ['#4a0812', '#b51f33', '#ff5e5e', '#ff8f8f', '#ffc2c2'],
    'nose':  ['#0b0618', '#1b1033', '#2b1d3a', '#4a3b5c', '#6b5a80'],
    'pink':  ['#7a2840', '#d9607f', '#ff8fae', '#ffb8cc', '#ffe0ea'],
    'apronr':['#3a0610', '#7a1022', '#9e1a30', '#bd2e44', '#da5468'],
    'tie':   ['#3d0612', '#7a1022', '#b51f33', '#d23a52', '#f0647a'],
    'qz':    ['#0a1640', '#1c4296', '#2f6fd8', '#5b9cff', '#a6ccff'],
    'qzdk':  ['#0a1640', '#163a84', '#2160c4', '#3f86f0', '#7ab0ff'],
    'sw':    ['#24252f', '#727788', '#a0a5b4', '#c6cad6', '#e8eaf0'],
    'swdk':  ['#24252f', '#5a5e70', '#7a7f90', '#a0a5b4', '#c6cad6'],
    'kick':  ['#2a2b36', '#c3c8dc', '#f2f3fb', '#ffffff', '#ffffff'],
    'sole':  ['#2a2b36', '#8e95ac', '#c3c8dc', '#e3e6f0', '#ffffff'],
    'drg':   ['#0f2a1f', '#23704a', '#3fa34a', '#74c95a', '#b4e57a'],
    'drgdk': ['#0f2a1f', '#1a5238', '#23704a', '#33884a', '#4ea054'],
    'wingb': ['#12051c', '#24093a', '#33124f', '#45206a', '#5c3088'],
    'wing':  ['#24103a', '#4e2470', '#73399a', '#9a5cc0', '#c690e0'],
    'bellyc':['#5a4a1e', '#cdb070', '#ecd696', '#f8eab8', '#fff8dc'],
    'horn':  ['#3a2e1e', '#b0a084', '#ded2b4', '#f2ead4', '#ffffff'],
    'bottle':['#1f0e06', '#4a2410', '#6e3a18', '#8e5228', '#b0703a'],
    'label': ['#5a2a00', '#d8761e', '#f4a23a', '#ffc46a', '#ffe2a8'],
    'cap':   ['#0b0618', '#1b1033', '#2b1d3a', '#4a3b5c', '#6b5a80'],
}
FLAT = {'dark', 'nose'}
CONTRAST = {'skin': 0.45, 'white': 0.7, 'metal': 0.35, 'fur': 0.8}
NOSEL = {'horn', 'metal'}            # always get the dark outline   # soften form shading on faces and cloth
LIGHT = (-0.55, -0.65, 0.52)
_n = math.sqrt(sum(v * v for v in LIGHT)); LIGHT = tuple(v / _n for v in LIGHT)


def hexc(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


class Canvas:
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.g = [[None] * w for _ in range(h)]
        s.pid = [[None] * w for _ in range(h)]
        s.sh = [[None] * w for _ in range(h)]
        s.fixed = {}
        s.part = None; s._id = 0; s.order = {}

    def _new(s):
        if s.part is not None:
            if s.part not in s.order: s.order[s.part] = len(s.order)
            return s.part
        s._id += 1; k = ('p', s._id); s.order[k] = len(s.order); return k

    def _put(s, x, y, m, k, shade):
        if 0 <= x < s.w and 0 <= y < s.h:
            s.g[y][x] = m; s.pid[y][x] = k; s.sh[y][x] = shade

    @staticmethod
    def _lit(nx, ny, nz):
        d = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
        return max(0.0, min(1.0, 0.36 + 0.64 * d))

    def px(s, x, y, m, shade=0.55):
        k = s._new(); s._put(int(round(x)), int(round(y)), m, k, shade)

    def fix(s, x, y, color):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < s.w and 0 <= y < s.h: s.fixed[(x, y)] = color

    def rect(s, x0, y0, x1, y1, m):
        k = s._new(); cy = (y0 + y1) / 2; hh = max(1, (y1 - y0) / 2 + .5)
        for y in range(int(y0), int(y1) + 1):
            ny = (y - cy) / hh * 0.5
            for x in range(int(x0), int(x1) + 1):
                s._put(x, y, m, k, s._lit(0, ny, math.sqrt(max(0, 1 - ny * ny))))

    def ell(s, cx, cy, rx, ry, m):
        k = s._new(); rx = max(rx, .5); ry = max(ry, .5)
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                nx, ny = (x - cx) / rx, (y - cy) / ry
                r2 = nx * nx + ny * ny
                if r2 <= 1.0:
                    s._put(x, y, m, k, s._lit(nx, ny, math.sqrt(max(0, 1 - r2))))

    def line(s, x0, y0, x1, y1, m, w=1):
        k = s._new()
        if w <= 1:
            n = int(max(abs(x1 - x0), abs(y1 - y0)) * 2) + 1
            for i in range(n + 1):
                t = i / n; s._put(int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t)), m, k, 0.6)
            return
        r = w / 2; dx, dy = x1 - x0, y1 - y0; L2 = dx * dx + dy * dy or 1
        for y in range(int(min(y0, y1) - r) - 1, int(max(y0, y1) + r) + 2):
            for x in range(int(min(x0, x1) - r) - 1, int(max(x0, x1) + r) + 2):
                t = max(0, min(1, ((x - x0) * dx + (y - y0) * dy) / L2))
                px_, py_ = x - (x0 + t * dx), y - (y0 + t * dy)
                d2 = px_ * px_ + py_ * py_
                if d2 <= r * r:
                    nx, ny = px_ / r, py_ / r
                    s._put(x, y, m, k, s._lit(nx, ny, math.sqrt(max(0, 1 - nx * nx - ny * ny))))

    def render(s, dither=False, seams=True):
        W, H = s.w, s.h; G = s.g
        get = lambda x, y: G[y][x] if 0 <= x < W and 0 <= y < H else None
        # smooth shading inside each part so overlapping primitives blend
        sh = [[None] * W for _ in range(H)]
        for y in range(H):
            for x in range(W):
                if G[y][x] is None: continue
                k = s.pid[y][x]; acc = n = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        xx, yy = x + dx, y + dy
                        if 0 <= xx < W and 0 <= yy < H and s.pid[yy][xx] == k and s.sh[yy][xx] is not None:
                            acc += s.sh[yy][xx]; n += 1
                sh[y][x] = acc / n if n else 0.55
        img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        for y in range(H):
            for x in range(W):
                m = G[y][x]
                if m is None: continue
                r = RAMPS[m]
                if m in FLAT: c = r[2]
                else:
                    v = sh[y][x]
                    if m in CONTRAST: v = 0.6 + (v - 0.6) * CONTRAST[m]
                    c = r[1] if v < 0.34 else r[2] if v < 0.70 else r[3] if v < 0.90 else r[4]
                img.putpixel((x, y), hexc(c))
        out = img.copy()
        # selective outline: darkest tone on the shadow side, a step lighter on the lit (upper-left) side
        for y in range(H):
            for x in range(W):
                if G[y][x] is not None: continue
                for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                    m = get(x + dx, y + dy)
                    if m is not None:
                        lit_side = (dx == 1 or dy == 1)   # we sit above/left of the shape
                        col = RAMPS[m][0]
                        if lit_side and m not in FLAT and m not in NOSEL and sh[y + dy][x + dx] > 0.7:
                            col = RAMPS[m][1]
                        out.putpixel((x, y), hexc(col)); break
        # separation lines where a part sits in front of an earlier part
        if seams:
            for y in range(H):
                for x in range(W):
                    m = G[y][x]
                    if m is None or m in FLAT: continue
                    k = s.pid[y][x]; o = s.order.get(k, 0)
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        xx, yy = x + dx, y + dy
                        if not (0 <= xx < W and 0 <= yy < H): continue
                        k2 = s.pid[yy][xx]
                        if k2 is None or k2 == k or G[yy][xx] in FLAT or G[yy][xx] != m: continue
                        if s.order.get(k2, 0) > o:      # neighbour is in front -> line on our side
                            out.putpixel((x, y), hexc(RAMPS[m][0])); break
        for (x, y), c in s.fixed.items():
            out.putpixel((x, y), hexc(c))
        return out


def sheet(frames, path, scale=1):
    w, h = frames[0].size
    s = Image.new('RGBA', (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames): s.paste(f, (i * w, 0))
    if scale != 1: s = s.resize((s.width * scale, s.height * scale), Image.NEAREST)
    s.save(path); return s


def _snap(s):
    return ([r[:] for r in s.g], [r[:] for r in s.pid], [r[:] for r in s.sh])
def _restore(s, x, y, snap):
    s.g[y][x] = snap[0][y][x]; s.pid[y][x] = snap[1][y][x]; s.sh[y][x] = snap[2][y][x]
Canvas.snap = _snap; Canvas.restore = _restore

import contextlib
@contextlib.contextmanager
def _group(s, name):
    prev = s.part; s.part = name
    try: yield
    finally: s.part = prev
Canvas.group = _group

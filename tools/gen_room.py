# Usage: python tools/gen_room.py assets   (regenerates assets/room.svg)
"""A pixel-art isometric room for the GitHub profile README: a tiny game scene with an RPG HUD.
Pure SVG + SMIL (stepped animations for the pixel look). No JS, no external fonts: all text is drawn
from a 5x7 bitmap font made of rectangles."""
import os
import sys

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

BG, BG2, ACC, ACC2, INK, MUTED = "#120706", "#1c0c0a", "#e8604f", "#f6a38f", "#f4eadb", "#a89488"
WOOD, DARK = "#5a2d1f", "#2a100c"
BLUE, GREEN, YEL, PURPLE = "#6c9ed6", "#7fbf4d", "#f2c94c", "#5b4a9a"

TW, TH = 40, 20          # half tile width / height (2:1 isometric)
OX, OY = 600, 215        # screen position of the back corner on the floor
N = 8                    # room is N x N tiles
H = 200                  # wall height in px

# ---------------------------------------------------------------- helpers
def sh(c, f):
    r, g, b = (int(c[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)))


def P(i, j, z=0):
    return (OX + (i - j) * TW, OY + (i + j) * TH - z)


def pts(ps):
    return " ".join("%.1f,%.1f" % p for p in ps)


def poly(ps, fill, op=None):
    o = ' opacity="%s"' % op if op is not None else ""
    return '<polygon points="%s" fill="%s"%s/>' % (pts(ps), fill, o)


def rect(x, y, w, h, fill, extra=""):
    return '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"%s/>' % (x, y, w, h, fill, extra)


def box(i, j, w, d, z0, z1, c, top=None, fi=None, fj=None):
    top, fj, fi = top or sh(c, 1.18), fj or sh(c, .92), fi or sh(c, .66)
    return (
        poly([P(i + w, j, z0), P(i + w, j + d, z0), P(i + w, j + d, z1), P(i + w, j, z1)], fi)
        + poly([P(i, j + d, z0), P(i + w, j + d, z0), P(i + w, j + d, z1), P(i, j + d, z1)], fj)
        + poly([P(i, j, z1), P(i + w, j, z1), P(i + w, j + d, z1), P(i, j + d, z1)], top)
    )


def shadow(i, j, w, d, pad=.12):
    return poly([P(i - pad + .1, j - pad + .1), P(i + w + pad + .1, j - pad + .1), P(i + w + pad + .1, j + d + pad + .1), P(i - pad + .1, j + d + pad + .1)], "#000", .32)


def FJ(jf):  # plane j = jf, local x = 40*i, local y = z (up)
    return "matrix(1 .5 0 -1 %s %s)" % (OX - TW * jf, OY + TH * jf)


def FI(i0):  # plane i = i0, local x = 40*j, local y = z (up)
    return "matrix(-1 .5 0 -1 %s %s)" % (OX + TW * i0, OY + TH * i0)


FLOOR = "matrix(40 20 -40 20 %s %s)" % (OX, OY)  # local x = i, local y = j

# ---------------------------------------------------------------- 5x7 bitmap font
_F = """
A .###. #...# #...# ##### #...# #...# #...#
B ####. #...# #...# ####. #...# #...# ####.
C .#### #.... #.... #.... #.... #.... .####
D ####. #...# #...# #...# #...# #...# ####.
E ##### #.... #.... ####. #.... #.... #####
F ##### #.... #.... ####. #.... #.... #....
G .#### #.... #.... #..## #...# #...# .###.
H #...# #...# #...# ##### #...# #...# #...#
I ##### ..#.. ..#.. ..#.. ..#.. ..#.. #####
J ..### ...#. ...#. ...#. ...#. #..#. .##..
K #...# #..#. #.#.. ##... #.#.. #..#. #...#
L #.... #.... #.... #.... #.... #.... #####
M #...# ##.## #.#.# #.#.# #...# #...# #...#
N #...# ##..# #.#.# #..## #...# #...# #...#
O .###. #...# #...# #...# #...# #...# .###.
P ####. #...# #...# ####. #.... #.... #....
Q .###. #...# #...# #...# #.#.# #..#. .##.#
R ####. #...# #...# ####. #.#.. #..#. #...#
S .#### #.... #.... .###. ....# ....# ####.
T ##### ..#.. ..#.. ..#.. ..#.. ..#.. ..#..
U #...# #...# #...# #...# #...# #...# .###.
V #...# #...# #...# #...# #...# .#.#. ..#..
W #...# #...# #...# #.#.# #.#.# ##.## #...#
X #...# #...# .#.#. ..#.. .#.#. #...# #...#
Y #...# #...# .#.#. ..#.. ..#.. ..#.. ..#..
Z ##### ....# ...#. ..#.. .#... #.... #####
0 .###. #...# #..## #.#.# ##..# #...# .###.
1 ..#.. .##.. ..#.. ..#.. ..#.. ..#.. .###.
2 .###. #...# ....# ...#. ..#.. .#... #####
3 ####. ....# ....# .###. ....# ....# ####.
4 ...#. ..##. .#.#. #..#. ##### ...#. ...#.
5 ##### #.... ####. ....# ....# #...# .###.
6 .###. #.... #.... ####. #...# #...# .###.
7 ##### ....# ...#. ..#.. .#... .#... .#...
8 .###. #...# #...# .###. #...# #...# .###.
9 .###. #...# #...# .#### ....# ....# .###.
> #.... .#... ..#.. ...#. ..#.. .#... #....
- ..... ..... ..... ##### ..... ..... .....
: ..... ..#.. ..#.. ..... ..#.. ..#.. .....
. ..... ..... ..... ..... ..... .##.. .##..
! ..#.. ..#.. ..#.. ..#.. ..#.. ..... ..#..
' ..#.. ..#.. .#... ..... ..... ..... .....
+ ..... ..#.. ..#.. ##### ..#.. ..#.. .....
/ ....# ....# ...#. ..#.. .#... #.... #....
? .###. #...# ....# ...#. ..#.. ..... ..#..
"""
FONT = {" ": ["....."] * 7}
for _l in _F.strip().splitlines():
    _p = _l.split()
    FONT[_p[0]] = _p[1:]


def ptext(t, x, y, s, fill, flip=False, anchor="start", extra=""):
    w = len(t) * 6 * s - s
    if anchor == "middle":
        x -= w / 2
    out = []
    for ci, ch in enumerate(t):
        g = FONT.get(ch, FONT[" "])
        for r, row in enumerate(g):
            c = 0
            while c < 5:
                if row[c] == "#":
                    c2 = c
                    while c2 < 5 and row[c2] == "#":
                        c2 += 1
                    X = x + ci * 6 * s + c * s
                    Y = (y + (6 - r) * s) if flip else (y + r * s)
                    out.append('<rect x="%s" y="%s" width="%s" height="%s"/>' % (round(X, 3), round(Y, 3), round((c2 - c) * s, 3), round(s, 3)))
                    c = c2
                else:
                    c += 1
    return '<g fill="%s" %s>%s</g>' % (fill, extra, "".join(out))


def sprite(rows, pal, x, y, p, flip=False):
    n, out = len(rows), []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch == ".":
                c += 1
                continue
            c2 = c
            while c2 < len(row) and row[c2] == ch:
                c2 += 1
            yy = (y + (n - 1 - r) * p) if flip else (y + r * p)
            out.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (x + c * p, yy, (c2 - c) * p, p, pal[ch]))
            c = c2
    return "".join(out)


def step_anim(attr, values, dur, begin="0s", times=None, kind="animate", typ=None):
    n = len(values)
    kt = times or [k / n for k in range(n)]
    t = ' type="%s"' % typ if typ else ""
    tag = "animateTransform" if kind == "animateTransform" else "animate"
    name = "transform" if kind == "animateTransform" else attr
    return '<%s attributeName="%s"%s values="%s" keyTimes="%s" calcMode="discrete" dur="%ss" begin="%s" repeatCount="indefinite"/>' % (
        tag, name, t, ";".join(str(v) for v in values), ";".join("%.4f" % k for k in kt), dur, begin)


def blink(dur, begin, vals=(1, 0)):
    return step_anim("opacity", list(vals), dur, begin)


def jit(i, k=1):
    return (((i + 1) * 2654435761 * (k + 3)) % 1000) / 1000.0


# ---------------------------------------------------------------- room shell
FL_A, FL_B = "#552a1c", "#66321f"
WALL_L, WALL_R = "#4d2419", "#5f2d20"
shell = []
# floor slab thickness
shell.append(poly([P(0, N, 0), P(N, N, 0), P(N, N, -16), P(0, N, -16)], "#1a0806"))
shell.append(poly([P(N, 0, 0), P(N, N, 0), P(N, N, -16), P(N, 0, -16)], "#120504"))
for i in range(N):
    for j in range(N):
        shell.append(poly([P(i, j), P(i + 1, j), P(i + 1, j + 1), P(i, j + 1)], FL_A if (i + j) % 2 == 0 else FL_B))
# walls
shell.append(poly([P(0, 0, 0), P(0, N, 0), P(0, N, H), P(0, 0, H)], WALL_L))
shell.append(poly([P(0, 0, 0), P(N, 0, 0), P(N, 0, H), P(0, 0, H)], WALL_R))
# wallpaper stripes + baseboard + ambient-occlusion dither, drawn in each wall's own plane
dither = '<pattern id="dith" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="2" height="2" fill="#000" opacity=".35"/><rect x="2" y="2" width="2" height="2" fill="#000" opacity=".35"/></pattern>'
for mat, base in ((FI(0), WALL_L), (FJ(0), WALL_R)):
    g = ['<g transform="%s">' % mat]
    for k in range(0, N * TW, 32):
        g.append(rect(k, 0, 16, H, sh(base, 1.07)))
    g.append(rect(0, 0, N * TW, 10, sh(base, .6)))
    g.append(rect(0, 10, N * TW, 3, sh(base, 1.4)))
    g.append(rect(0, 13, N * TW, 26, "url(#dith)"))
    g.append(rect(0, H - 8, N * TW, 8, sh(base, .75)))
    g.append("</g>")
    shell.append("".join(g))
# wall caps (thickness) and cut ends
shell.append(poly([P(-.25, -.25, H), P(-.25, N, H), P(0, N, H), P(0, -.25, H)], "#7a3a2a"))
shell.append(poly([P(-.25, -.25, H), P(N, -.25, H), P(N, 0, H), P(-.25, 0, H)], "#8a4432"))
shell.append(poly([P(-.25, N, H), P(0, N, H), P(0, N, 0), P(-.25, N, 0)], "#251009"))
shell.append(poly([P(N, -.25, H), P(N, 0, H), P(N, 0, 0), P(N, -.25, 0)], "#1c0b07"))
shell.append(poly([P(-.25, -.25, H), P(-.25, -.25, 0), P(-.25, N, 0), P(-.25, N, H)], "#180806", 0))

# rug with the site name painted on it
rug = [
    '<g transform="%s">' % FLOOR,
    rect(2.7, 3.0, 4.0, 3.9, "#7c2e24"),
    rect(2.85, 3.15, 3.7, 3.6, "#2c120d"),
    rect(3.0, 3.3, 3.4, 3.3, "#4a1d16"),
]
for a in range(0, 14):
    rug.append(rect(3.05 + a * 0.24, 3.35, 0.12, 0.08, ACC, ' opacity=".55"'))
    rug.append(rect(3.05 + a * 0.24, 6.47, 0.12, 0.08, ACC, ' opacity=".55"'))
rug.append(ptext("MEKMITRA", 3.243, 3.75, 0.062, ACC2))
rug.append(ptext("GARAGE SOFTWARE", 3.187, 4.5, 0.034, INK, extra='opacity=".8"'))
rug.append("</g>")
rug = "".join(rug)

# ---------------------------------------------------------------- wall decorations
deco = []
# window on the left wall (plane i=0), u = 40*j
wu0, wu1, wz0, wz1 = 132, 244, 106, 184
w = ['<g transform="%s">' % FI(0)]
w.append(rect(wu0 - 8, wz0 - 8, wu1 - wu0 + 16, wz1 - wz0 + 16, "#7a3a2a"))
for k, c in enumerate(["#170a1c", "#25102a", "#3b1727", "#5a2020"]):
    w.append(rect(wu0, wz0 + k * 19.5, wu1 - wu0, 19.5, c))
for k in range(16):
    sx, sy = wu0 + 4 + int(jit(k, 2) * (wu1 - wu0 - 8)), wz0 + 34 + int(jit(k, 4) * 40)
    w.append('<rect x="%d" y="%d" width="2" height="2" fill="%s">%s</rect>' % (sx, sy, INK, blink(2 + k % 3, "-%ss" % (k % 4), (1, 0.15))))
moon = ["..MMMM..", ".MMMM...", "MMMM....", "MMMM....", "MMMM....", "MMMM....", ".MMMM...", "..MMMM.."]
w.append(sprite(moon, {"M": INK}, wu1 - 36, wz1 - 34, 3, True))
x = wu0
for k in range(11):
    bw, bh = 9 + int(jit(k, 5) * 6), 14 + int(jit(k, 6) * 30)
    w.append(rect(x, wz0, bw, bh, "#0d050a"))
    for q in range(3):
        if jit(k * 3 + q, 8) > .45:
            w.append('<rect x="%d" y="%d" width="2" height="2" fill="%s">%s</rect>' % (x + 2 + (q % 2) * 4, wz0 + 4 + q * 8, YEL, blink(3 + (k + q) % 4, "-%ss" % ((k * q) % 5), (1, 0, 1, 1))))
    x += bw
w.append(rect((wu0 + wu1) / 2 - 2, wz0, 4, wz1 - wz0, "#7a3a2a"))
w.append(rect(wu0, (wz0 + wz1) / 2 - 2, wu1 - wu0, 4, "#7a3a2a"))
w.append(rect(wu0 - 12, wz0 - 14, wu1 - wu0 + 24, 6, "#9a4a36"))
w.append("</g>")
deco.append("".join(w))

# pixel car poster on the left wall (a nod to MekMitra's garages)
car = ["....BBBBBB......", "...BWWBBWWB.....", "..BWWWBBWWWB....", "BBBBBBBBBBBBBBB.", "BBBBBBBBBBBBBBBB", "BBTTTBBBBBTTTBBB", "..TTHTT..TTHTT..", "...TTT....TTT..."]
deco.append(
    '<g transform="%s">' % FI(0)
    + rect(34, 112, 76, 62, "#7a3a2a") + rect(38, 116, 68, 54, "#1c0c0a") + rect(38, 116, 68, 54, "#3a1a14", ' opacity=".6"')
    + sprite(car, {"B": ACC, "W": "#9fd0f0", "T": "#0b0403", "H": "#a89488"}, 42, 124, 4, True)
    + rect(42, 118, 60, 3, ACC2, ' opacity=".7"')
    + "</g>"
)

# pixel clock on the left wall
clock = ['<g transform="%s">' % FI(0), rect(268, 134, 44, 44, "#7a3a2a"), rect(272, 138, 36, 36, "#1c0c0a")]
for k in range(12):
    import math as _m
    ang = k * 30 * _m.pi / 180
    clock.append(rect(round(290 + 14 * _m.sin(ang) - 1), round(156 + 14 * _m.cos(ang) - 1), 2, 2, MUTED))
clock.append('<g transform="translate(290,156)"><rect x="-1" y="0" width="2" height="11" fill="%s"><animateTransform attributeName="transform" type="rotate" values="%s" keyTimes="%s" calcMode="discrete" dur="12s" repeatCount="indefinite"/></rect></g>' % (INK, ";".join("%d" % (k * 30) for k in range(12)), ";".join("%.4f" % (k / 12) for k in range(12))))
clock.append('<g transform="translate(290,156)"><rect x="-1" y="0" width="2" height="7" fill="%s"><animateTransform attributeName="transform" type="rotate" values="%s" keyTimes="%s" calcMode="discrete" dur="144s" repeatCount="indefinite"/></rect></g>' % (ACC2, ";".join("%d" % (k * 30) for k in range(12)), ";".join("%.4f" % (k / 12) for k in range(12))))
clock.append(rect(289, 155, 3, 3, ACC))
clock.append("</g>")
deco.append("".join(clock))

# sprint board on the right wall (plane j=0), u = 40*i
kb = ['<g transform="%s">' % FJ(0)]
bu0, bu1, bz0, bz1 = 92, 268, 100, 184
kb.append(rect(bu0 - 6, bz0 - 6, bu1 - bu0 + 12, bz1 - bz0 + 12, "#7a3a2a"))
kb.append(rect(bu0, bz0, bu1 - bu0, bz1 - bz0, "#170a08"))
kb.append(ptext("SPRINT", bu0 + 6, bz1 - 18, 2, ACC2, True))
colw = (bu1 - bu0) / 3
for k, name in enumerate(["TODO", "WIP", "DONE"]):
    cx0 = bu0 + k * colw
    kb.append(ptext(name, cx0 + 6, bz1 - 38, 2, MUTED, True))
    if k:
        kb.append(rect(cx0 - 1, bz0 + 4, 2, bz1 - bz0 - 24, "#3a1a14"))


def card(x0, z0, col, lines=2):
    s = rect(x0, z0, 50, 16, "#1c0c0a") + rect(x0, z0, 50, 2, col) + rect(x0 + 4, z0 + 8, 30, 3, col, ' opacity=".7"')
    if lines > 1:
        s += rect(x0 + 4, z0 + 3, 18, 3, col, ' opacity=".4"')
    return s


kb.append(card(bu0 + 6, bz0 + 8, MUTED))
kb.append(card(bu0 + 6, bz0 + 28, MUTED))
kb.append(card(bu0 + colw + 6, bz0 + 8, BLUE))
kb.append(card(bu0 + 2 * colw + 6, bz0 + 8, GREEN))
kb.append(card(bu0 + 2 * colw + 6, bz0 + 28, GREEN))
mv = card(bu0 + 6, bz0 + 48, ACC)
kb.append('<g>' + step_anim("transform", ["0 0", "0 0", "%s -20" % colw, "%s -20" % colw, "%s -40" % (2 * colw), "%s -40" % (2 * colw)], 12, times=[0, .14, .3, .5, .7, .86], kind="animateTransform", typ="translate").replace('values=', 'values=', 1) + mv + "</g>")
kb.append("</g>")
deco.append("".join(kb))

# ---------------------------------------------------------------- furniture
pal_person = lambda hair, skin, shirt, pants: {"H": hair, "S": skin, "T": shirt, "t": sh(shirt, .75), "P": pants}
BODY = ["...HHHHHHHH...", "..HHHHHHHHHH..", "..HHHHHHHHHH..", "..HHHHHHHHHH..", "..SHHHHHHHHS..", "...HHHHHHHH...", "....SSSSSS....",
        "..TTTTTTTTTT..", "...TTTTTTTT...", "...TTTTTTTT...", "...TTTTTTTT...", "...tTTTTTTt...", "..TTTTTTTTTT..", "..PPPPPPPPPP..", "..PPPPPPPPPP.."]


def person(cx, by, hair, skin, shirt, pants, ph):
    p = 4
    x0, y0 = cx - 28, by - 60
    pal = pal_person(hair, skin, shirt, pants)
    body = sprite(BODY, pal, x0, y0, p)
    arms = ""
    for side, ax in (("L", x0 + 1 * p), ("R", x0 + 11 * p)):
        d = ph if side == "L" else ph + .3
        arms += (
            '<g>%s%s%s</g>' % (
                step_anim("transform", ["0 0", "0 -4", "0 0", "0 0"], .8, "-%ss" % d, kind="animateTransform", typ="translate"),
                rect(ax, y0 + 8 * p, 2 * p, 3 * p, sh(shirt, .8)),
                rect(ax, y0 + 11 * p, 2 * p, p, skin),
            )
        )
    return body + arms


def chair(ci, cj, back="j", col="#2a1a3a"):
    s = [shadow(ci, cj, .9, .9), box(ci + .15, cj + .15, .6, .6, 0, 3, "#150a08"), box(ci + .38, cj + .38, .14, .14, 3, 20, "#150a08"), box(ci, cj, .9, .9, 20, 26, col)]
    if back == "j":
        b = box(ci, cj + .8, .9, .1, 26, 46, col)
    else:
        b = box(ci + .8, cj, .1, .9, 26, 46, col)
    return "".join(s), b


def desk(i, j, w, d, col=WOOD):
    s = [shadow(i, j, w, d)]
    for (a, b) in [(i + .05, j + .05), (i + w - .17, j + .05), (i + .05, j + d - .17), (i + w - .17, j + d - .17)]:
        s.append(box(a, b, .12, .12, 0, 32, "#2a100c"))
    s.append(box(i, j, w, d, 32, 38, col))
    return "".join(s)


def screen(mat, u0, u1, z0, z1, seed, cid, tint=ACC2):
    n = 14
    cols = [tint, BLUE, GREEN, INK, YEL]
    lines = []
    for k in range(n):
        ind = ((k + seed) % 3) * 6
        wd = 12 + int(jit(k + seed * 7, 3) * (u1 - u0 - 26))
        lines.append(rect(u0 + 4 + ind, z0 + 3 + k * 5, max(6, wd), 3, cols[(k * 2 + seed) % 5]))
    body = "".join(lines)
    vals = ["0 %d" % (k * 5) for k in range(n)]
    anim = step_anim("transform", vals, .45 * n, kind="animateTransform", typ="translate")
    return (
        '<g transform="%s"><clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (mat, cid, u0, z0, u1 - u0, z1 - z0)
        + rect(u0, z0, u1 - u0, z1 - z0, "#0f0605")
        + '<g clip-path="url(#%s)"><g>%s%s<g transform="translate(0,%d)">%s</g></g></g>' % (cid, anim, body, -n * 5, body)
        + rect(u0, z1 - 2, u1 - u0, 2, tint, ' opacity=".25"')
        + "</g>"
    )


def mug(i, j, z):
    x, y = P(i, j, z)
    s = box(i, j, .14, .14, z, z + 10, ACC2)
    for k in range(3):
        s += '<rect x="%d" y="%d" width="2" height="2" fill="%s" opacity="0">%s%s</rect>' % (
            x - 1 + (k % 2) * 3, y - 14, INK,
            step_anim("y", [y - 14, y - 18, y - 22, y - 26], 1.6, "-%ss" % (k * .5)),
            step_anim("opacity", [0, .7, .5, 0], 1.6, "-%ss" % (k * .5)),
        )
    return s


# --- server rack (corner, right wall)
rack_i, rack_j = .8, .1
rack = [shadow(rack_i, rack_j, .75, .85), box(rack_i, rack_j, .75, .85, 0, 118, "#2a2236")]
rf = ['<g transform="%s">' % FJ(rack_j + .85)]
ru0 = TW * rack_i
for k in range(7):
    z0 = 8 + k * 15
    rf.append(rect(ru0 + 2, z0, 26, 12, "#150f1c") + rect(ru0 + 4, z0 + 2, 12, 2, "#3a3050") + rect(ru0 + 4, z0 + 6, 12, 2, "#3a3050"))
    for q in range(3):
        c = [GREEN, YEL, ACC][(k + q) % 3]
        rf.append('<rect x="%d" y="%d" width="3" height="3" fill="%s">%s</rect>' % (ru0 + 19 + q * 4, z0 + 4, c, blink(.6 + jit(k * 3 + q, 9) * 1.6, "-%ss" % (jit(k + q, 2) * 2), (1, .15, 1, .15, 1, 1))))
rf.append("</g>")
rack.append("".join(rf))
rack = "".join(rack)

# --- bookshelf (left wall)
bs_i, bs_j, bs_d = .1, 1.7, 1.5
shelf = [shadow(bs_i, bs_j, .65, bs_d), box(bs_i, bs_j, .65, bs_d, 0, 118, "#5a2d1f")]
sf = ['<g transform="%s">' % FI(bs_i + .65)]
su0 = TW * bs_j
bookcols = [ACC, BLUE, YEL, GREEN, ACC2, PURPLE, INK]
for lvl in range(4):
    z0 = 6 + lvl * 28
    sf.append(rect(su0 + 2, z0 - 3, TW * bs_d - 4, 3, "#3a1a14"))
    x = su0 + 4
    k = 0
    while x < su0 + TW * bs_d - 10:
        bw = 5 + int(jit(lvl * 20 + k, 11) * 4)
        bh = 17 + int(jit(lvl * 20 + k, 12) * 8)
        sf.append(rect(x, z0, bw, bh, bookcols[(lvl * 3 + k) % 7]))
        x += bw + 1
        k += 1
sf.append("</g>")
shelf.append("".join(sf))
shelf = "".join(shelf)

# --- desks and people
CH = []   # (seat+post, person, back) in draw order
d1 = desk(2.0, .1, 1.9, 1.2) + box(2.6, .35, .5, .1, 38, 46, "#1a0a07")
d1 += box(2.35, .3, 1.2, .16, 46, 82, "#1a0a07") + screen(FJ(.46), TW * 2.41, TW * 3.49, 49, 79, 1, "scr1")
d1 += box(2.45, .75, .9, .3, 38, 40, "#6b3a30") + mug(3.55, .85, 38)

d2 = desk(4.3, .1, 2.6, 1.3) + box(4.7, .35, .4, .1, 38, 46, "#1a0a07") + box(5.85, .35, .4, .1, 38, 46, "#1a0a07")
d2 += box(4.4, .3, 1.15, .16, 46, 82, "#1a0a07") + screen(FJ(.46), TW * 4.46, TW * 5.49, 49, 79, 2, "scr2")
d2 += box(5.65, .3, 1.15, .16, 46, 82, "#1a0a07") + screen(FJ(.46), TW * 5.71, TW * 6.74, 49, 79, 3, "scr3", GREEN)
d2 += box(5.0, .8, 1.0, .3, 38, 40, "#6b3a30") + mug(6.55, .95, 38)

d3 = desk(.1, 3.5, 1.2, 2.5)
d3 += box(.3, 4.4, .1, .5, 38, 46, "#1a0a07") + box(.3, 3.85, .16, 1.6, 46, 82, "#1a0a07") + screen(FI(.46), TW * 3.91, TW * 5.39, 49, 79, 4, "scr4", BLUE)
d3 += box(.75, 4.1, .3, 1.0, 38, 40, "#6b3a30") + mug(.9, 5.55, 38)

c1s, c1b = chair(2.45, 1.95, "j")
c2s, c2b = chair(4.85, 1.95, "j", "#3a1a14")
c3s, c3b = chair(1.8, 4.2, "i")


def seat_anchor(ci, cj):
    return P(ci + .45, cj + .45, 26)


a1, a2, a3 = seat_anchor(2.45, 1.95), seat_anchor(4.85, 1.95), seat_anchor(1.8, 4.2)
p1 = person(a1[0], a1[1], "#2b1a14", "#e0b08c", ACC, "#2a2f4a", 0)
p2 = person(a2[0], a2[1], "#120706", "#c98f6b", INK, "#3a1a14", .2)
p3 = person(a3[0], a3[1], "#1a0f0a", "#8d5a3c", BLUE, "#2a2f4a", .4)

# --- plant
pl_i, pl_j = 7.1, .35
pot = box(pl_i, pl_j, .55, .55, 0, 22, ACC)
px, py = P(pl_i + .27, pl_j + .27, 22)
leaf = {"a": "#8fd05a", "b": "#5f9a3a", "c": "#4f8a30"}
plant = (shadow(pl_i, pl_j, .55, .55) + pot
         + '<g><animateTransform attributeName="transform" type="translate" values="0 0;1 0;0 0;-1 0" keyTimes="0;.25;.5;.75" calcMode="discrete" dur="2.4s" repeatCount="indefinite"/>'
         + sprite(["...a...", "..aba..", ".abbba.", "aabbbaa", ".abcba.", "..bcb..", "...c..."], leaf, px - 28, py - 56, 8)
         + "</g>")

# --- cat sleeping on the rug
cx_, cy_ = P(6.0, 6.1, 0)
cat_rows = ["..OO...OO.....", "..OOOOOOOO....", ".OOOOOOOOOOOO.", "OOOOODOODOOOOO", "OOOOOOOOOOOOOO", ".OOOOOOOOOOOO."]
cat = (
    '<ellipse cx="%d" cy="%d" rx="30" ry="9" fill="#000" opacity=".3"/>' % (cx_, cy_ + 2)
    + sprite(cat_rows, {"O": "#e08a4c", "D": "#a85a2c"}, cx_ - 21, cy_ - 17, 3)
    + '<g>%s%s%s</g>' % (step_anim("transform", ["0 0", "0 -3", "0 0", "0 -3"], 2.4, kind="animateTransform", typ="translate") if False else "", rect(cx_ + 20, cy_ - 8, 12, 3, "#e08a4c"), rect(cx_ + 29, cy_ - 11 , 3, 3, "#e08a4c"))
)
for k in range(3):
    cat += '<g opacity="0">%s%s%s</g>' % (
        step_anim("opacity", [0, 1, 1, .6, 0], 4.5, "-%ss" % (k * 1.5)),
        step_anim("transform", ["0 0", "2 -6", "-1 -12", "2 -18", "0 -24"], 4.5, "-%ss" % (k * 1.5), kind="animateTransform", typ="translate"),
        ptext("Z", cx_ - 4 + k * 5, cy_ - 34 - k * 3, 2 + (k % 2), ACC2),
    )

# --- arcade cabinet
ar_i, ar_j = 6.95, 1.75
arc = [shadow(ar_i, ar_j, 1.0, .9), box(ar_i, ar_j, 1.0, .9, 0, 56, "#2a3f7a"), box(ar_i + .05, ar_j + .05, .9, .72, 56, 112, "#233466")]
arc.append(box(ar_i + .05, ar_j + .77, .9, .3, 56, 62, "#15203f"))
jx, jy = P(ar_i + .3, ar_j + .92, 62)
arc.append(rect(jx - 1, jy - 8, 3, 8, "#0b0403") + rect(jx - 3, jy - 11, 7, 4, ACC))
for q, c in enumerate([YEL, GREEN, BLUE]):
    bx, by_ = P(ar_i + .55 + q * .12, ar_j + .92, 62)
    arc.append(rect(bx - 1, by_ - 3, 4, 3, c))
af = ['<g transform="%s">' % FJ(ar_j + .77)]
au0, au1 = TW * (ar_i + .12), TW * (ar_i + .88)
af.append(rect(au0, 64, au1 - au0, 34, "#0b0b1a"))
inv_a = ["..#...#..", "...#.#...", "..#####..", ".##.#.##.", "#########", "#.#####.#", "#.#...#.#", "...##.##."]
inv_b = ["..#...#..", "#..#.#..#", "#.#####.#", "###.#.###", "#########", ".#######.", "..#...#..", ".#.....#."]
for gi, (g, off) in enumerate(((inv_a, 0), (inv_b, 0))):
    af.append('<g>%s%s</g>' % (
        '<animate attributeName="opacity" values="%s" keyTimes="0;.5" calcMode="discrete" dur=".9s" repeatCount="indefinite"/>' % ("1;0" if gi == 0 else "0;1"),
        sprite(["".join("G" if ch == "#" else "." for ch in r) for r in g], {"G": GREEN}, au0 + 4, 76, 2, True),
    ))
af.append(sprite(["...G...", "..GGG..", ".GGGGG."], {"G": ACC2}, au0 + 9, 66, 2, True))
af.append(rect(au0 + 10, 70, 2, 4, YEL) + "")
af[-1] = '<rect x="%d" y="72" width="2" height="4" fill="%s">%s</rect>' % (au0 + 12, YEL, step_anim("y", [72, 80, 88, 96], .8))
af.append(rect(au0, 100, au1 - au0, 8, "#0b0b1a"))
for q in range(6):
    af.append('<rect x="%d" y="102" width="4" height="4" fill="%s">%s</rect>' % (au0 + 2 + q * 5, [ACC, YEL, GREEN, BLUE, ACC2, INK][q], blink(.8, "-%ss" % (q * .13), (1, .2))))
af.append("</g>")
arc.append("".join(af))
arcade = "".join(arc)

# --- nameplates + coin popups
def tag(cx, by, text, col, hi=False):
    w = len(text) * 12 + 14
    y = by - 90
    return (
        '<g>%s%s%s%s%s</g>' % (
            step_anim("transform", ["0 0", "0 -3"], 1.2, kind="animateTransform", typ="translate"),
            rect(cx - w / 2, y, w, 22, "#120706"),
            rect(cx - w / 2 - 2, y + 2, w + 4, 18, ACC if hi else "#5a2d1f"),
            rect(cx - w / 2, y + 2, w, 18, "#120706"),
            ptext(text, cx, y + 5, 2, INK if hi else MUTED, anchor="middle"),
        )
        + poly([(cx - 4, y + 22), (cx + 4, y + 22), (cx, y + 28)], ACC if hi else "#5a2d1f")
    )


def coin(cx, by, delay):
    x, y = cx + 34, by - 62
    return (
        '<g opacity="0">%s%s%s%s%s%s</g>' % (
            step_anim("opacity", [0, 1, 1, 1, .5, 0], 5, "-%ss" % delay),
            step_anim("transform", ["0 0", "0 -4", "0 -8", "0 -12", "0 -16", "0 -20"], 5, "-%ss" % delay, kind="animateTransform", typ="translate"),
            rect(x, y, 10, 10, YEL), rect(x + 2, y + 2, 6, 6, "#fff1a8"),
            ptext("+1", x + 13, y + 1, 2, YEL),
            "",
        )
    )


labels = tag(a1[0] - 10, a1[1] - 26, "FRONTEND", MUTED) + tag(a2[0] + 36, a2[1], "ASHIM LEAD", ACC2, True) + tag(a3[0] - 34, a3[1] + 6, "BACKEND", MUTED)
coins = coin(a1[0], a1[1], 0) + coin(a2[0], a2[1], 1.7) + coin(a3[0], a3[1], 3.1)

# ---------------------------------------------------------------- HUD
def panel(x, y, w, h):
    return (rect(x, y, w, h, ACC) + rect(x + 3, y + 3, w - 6, h - 6, "#120706") + rect(x + 6, y + 6, w - 12, h - 12, "#1c0c0a")
            + rect(x, y, 6, 6, BG) + rect(x + w - 6, y, 6, 6, BG) + rect(x, y + h - 6, 6, 6, BG) + rect(x + w - 6, y + h - 6, 6, 6, BG))


heart = [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."]
hearts = "".join(
    '<g>%s%s</g>' % (step_anim("transform", ["0 0", "0 -2"], 1.0, "-%ss" % (k * .33), kind="animateTransform", typ="translate"), sprite(heart, {"#": ACC}, 36 + k * 36, 110, 4))
    for k in range(3)
)
left = panel(20, 20, 256, 120) + ptext("ASHIM'S LAB", 36, 36, 3, ACC2) + ptext("FULL STACK AI ENGINEER", 36, 74, 2, MUTED) + hearts
left = left.replace(ptext("FULL STACK AI ENGINEER", 36, 74, 2, MUTED), ptext("FULL STACK AI DEV", 36, 74, 2, MUTED))

XP = 216
xp_vals = [int(XP * k / 10) for k in range(11)] + [0]
xp_times = [k / 12 for k in range(11)] + [11.4 / 12]
xp = (
    panel(924, 20, 256, 120)
    + ptext("QUEST:", 940, 34, 2, MUTED)
    + ptext("SHIP MEKMITRA", 940, 54, 3, ACC2)
    + rect(940, 92, XP + 8, 20, INK)
    + rect(942, 94, XP + 4, 16, "#120706")
    + '<rect x="944" y="96" width="0" height="12" fill="%s">%s</rect>' % (ACC, step_anim("width", xp_vals, 12, times=xp_times))
    + ptext("JOB CARDS + VAT", 940, 120, 2, MUTED)
)

msgs = ["> GIT COMMIT: FEAT JOB CARDS", "> CODE REVIEW: LGTM. MERGING!", "> DEPLOY OK. MEKMITRA IS LIVE!"]
CYC = 15.0
DY = 120
dlg = [panel(170, 556 + DY, 860, 76), rect(190, 544 + DY, 120, 26, ACC), rect(193, 547 + DY, 114, 20, "#120706"), ptext("ASHIM", 250, 551 + DY, 2, ACC2, anchor="middle")]
for k, m in enumerate(msgs):
    t0 = k * 5.0
    for c, ch in enumerate(m):
        if ch == " ":
            continue
        ton = t0 + .15 + c * .1
        toff = t0 + 4.6
        kt = "0;%.4f;%.4f" % (ton / CYC, toff / CYC)
        dlg.append(
            '<g opacity="0"><animate attributeName="opacity" values="0;1;0" keyTimes="%s" calcMode="discrete" dur="%ss" repeatCount="indefinite"/>%s</g>'
            % (kt, CYC, ptext(ch, 196 + c * 18, 584 + DY, 3, INK))
        )
dlg.append('<g>%s%s</g>' % (blink(.8, "0s"), rect(990, 610 + DY, 12, 4, ACC) + rect(993, 614 + DY, 6, 4, ACC) + rect(995, 618 + DY, 2, 3, ACC)))
dlg = "".join(dlg)
clips = []

# ---------------------------------------------------------------- stars outside the window (night sky around the room)
sky = "".join(
    '<rect x="%d" y="%d" width="%d" height="%d" fill="%s" opacity=".5">%s</rect>'
    % (int(jit(k, 5) * 1200), int(jit(k, 7) * 760), 2 + k % 2, 2 + k % 2, INK, blink(2 + k % 4, "-%ss" % (k % 5), (1, .3)) if k % 3 == 0 else "")
    for k in range(70)
)

# ---------------------------------------------------------------- assemble
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 760" width="1200" height="760" shape-rendering="crispEdges" role="img" aria-label="A pixel-art isometric workshop: three developers typing at desks, a sprint board, a sleeping cat, an arcade cabinet, and an RPG dialogue box typing out commit messages">
<title>Ashim's pixel workshop</title>
<defs>{dither}{''.join(clips)}
<radialGradient id="glow"><stop offset="0" stop-color="{ACC}" stop-opacity=".30"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient>
<clipPath id="all"><rect width="1200" height="760" rx="18"/></clipPath></defs>
<g clip-path="url(#all)">
<rect width="1200" height="760" fill="#0b0403"/>
{sky}
<ellipse cx="600" cy="400" rx="520" ry="260" fill="url(#glow)"/>
<g transform="translate(-120,6) scale(1.2)">
{''.join(shell)}
{rug}
{''.join(deco)}
{rack}
{shelf}
{d1}
{c1s}{p1}{c1b}
{d3}
{d2}
{c3s}{p3}{c3b}
{c2s}{p2}{c2b}
{plant}
{cat}
{arcade}
{labels}
{coins}
</g>
{left}
{xp}
{dlg}
</g>
<rect x=".5" y=".5" width="1199" height="759" rx="18" fill="none" stroke="{ACC}" stroke-opacity=".35"/>
</svg>
"""
with open(os.path.join(OUT, "room.svg"), "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print("room ok", len(svg) // 1024, "kb")

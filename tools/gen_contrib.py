# Usage: python tools/gen_contrib.py <github-username> <out-dir>
#   Fetches the public contribution calendar and writes <out-dir>/contributions.svg
#   (an animated 3D skyline: one bar per day, rising in a wave). Re-run it any time to refresh.
import datetime as dt
import math
import os
import re
import sys
import urllib.request

USER, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

BG, BG2, ACC, ACC2, INK, MUTED = "#120706", "#1c0c0a", "#e8604f", "#f6a38f", "#f4eadb", "#a89488"
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "'Segoe UI', -apple-system, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Consolas, monospace"
LEVEL = {0: "#2a100c", 1: "#7a3027", 2: "#b8463a", 3: "#e8604f", 4: "#f6a38f"}


def shade(hex_, f):
    r, g, b = (int(hex_[i : i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))


# ------------------------------------------------------------ data
req = urllib.request.Request(f"https://github.com/users/{USER}/contributions", headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode()
cells = re.findall(r'<td[^>]*data-date="([\d-]+)"[^>]*id="(contribution-day-component-\d+-\d+)"[^>]*data-level="(\d)"', html)
tips = dict(re.findall(r'for="(contribution-day-component-\d+-\d+)"[^>]*>([^<]*)<', html))
days = []
for date, cid, lvl in cells:
    m = re.match(r"(\d+) contribution", tips.get(cid, ""))
    days.append((dt.date.fromisoformat(date), int(m.group(1)) if m else 0, int(lvl)))
days.sort()
first = days[0][0]
first_sunday = first - dt.timedelta(days=(first.weekday() + 1) % 7)

total = sum(c for _, c, _ in days)
best = max(days, key=lambda d: d[1])
streak = longest = 0
for _, c, _ in days:
    streak = streak + 1 if c else 0
    longest = max(longest, streak)
active = sum(1 for _, c, _ in days if c)

# ------------------------------------------------------------ geometry
W, DX, DY = 14, 6, -6  # bar width, depth vector (up and to the right)
PITCH = 19.5
X0, BASE = 62, 392
CYCLE = 14.0


def height(c):
    return 0 if c == 0 else min(8 + math.sqrt(c) * 24, 210)


def bar(x, y, h, lvl, ts, best_day):
    top, left, right = LEVEL[lvl], shade(LEVEL[lvl], 0.62), shade(LEVEL[lvl], 0.8)
    kt = "0;%.4f;%.4f;0.9;0.96;1" % (ts, ts + 0.05)
    return (
        f'<g transform="translate({x:.1f},{y:.1f})"><g>'
        f'<animateTransform attributeName="transform" type="scale" values="1 0;1 0;1 1;1 1;1 0;1 0" keyTimes="{kt}" dur="{CYCLE}s" repeatCount="indefinite" calcMode="spline" '
        f'keySplines="0 0 1 1;.2 .9 .3 1;0 0 1 1;.6 0 1 .6;0 0 1 1"/>'
        f'<rect x="0" y="{-h:.1f}" width="{W}" height="{h:.1f}" fill="{left}"/>'
        f'<polygon points="{W},0 {W},{-h:.1f} {W+DX},{-h+DY:.1f} {W+DX},{DY}" fill="{right}"/>'
        f'<polygon points="0,{-h:.1f} {W},{-h:.1f} {W+DX},{-h+DY:.1f} {DX},{-h+DY:.1f}" fill="{top}"/>'
        + (f'<polygon points="0,{-h:.1f} {W},{-h:.1f} {W+DX},{-h+DY:.1f} {DX},{-h+DY:.1f}" fill="{INK}" opacity="0"><animate attributeName="opacity" values="0;.9;0" dur="2.2s" repeatCount="indefinite"/></polygon>' if best_day else "")
        + "</g></g>"
    )


def tile(x, y):
    return f'<polygon points="{x:.1f},{y:.1f} {x+W:.1f},{y:.1f} {x+W+DX:.1f},{y+DY:.1f} {x+DX:.1f},{y+DY:.1f}" fill="{LEVEL[0]}" opacity=".55"/>'


# painter's order: back rows (Saturday) first, front row (Sunday) last
items = []
for d, c, lvl in days:
    col = (d - first_sunday).days // 7
    row = (d.weekday() + 1) % 7
    x = X0 + col * PITCH + row * DX
    y = BASE + row * DY
    items.append((row, col, d, c, lvl, x, y))
items.sort(key=lambda t: (-t[0], t[1]))

parts = []
ncols = max(i[1] for i in items) + 1
for row, col, d, c, lvl, x, y in items:
    if c == 0:
        parts.append(tile(x, y))
    else:
        ts = 0.04 + (col / ncols) * 0.5 + (6 - row) * 0.004
        parts.append(bar(x, y, height(c), lvl, ts, d == best[0]))

# month labels along the front edge
labels, seen = [], set()
for row, col, d, c, lvl, x, y in items:
    if row == 0 and d.day <= 7 and (d.year, d.month) not in seen:
        seen.add((d.year, d.month))
        labels.append(f'<text x="{x:.0f}" y="{BASE+30}" font-family="{MONO}" font-size="12" fill="{MUTED}" letter-spacing="1.5">{d.strftime("%b").upper()}</text>')

best_item = next(i for i in items if i[2] == best[0])
bx, by = best_item[5] + W / 2, best_item[6] - height(best[1]) - 26
best_label = (
    f'<g><animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.4;.5;.85;.92" dur="{CYCLE}s" repeatCount="indefinite"/>'
    f'<rect x="{bx-62:.0f}" y="{by-18:.0f}" width="124" height="24" rx="12" fill="{BG2}" stroke="{ACC}"/>'
    f'<text x="{bx:.0f}" y="{by-2:.0f}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{ACC2}">best day: {best[1]}</text></g>'
)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 460" width="1200" height="460" role="img" aria-label="{total} contributions in the last year, drawn as an animated 3D skyline">
<title>{total} contributions in the last year</title>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>
<linearGradient id="sweep" x1="0" x2="1"><stop offset="0" stop-color="{INK}" stop-opacity="0"/><stop offset=".5" stop-color="{INK}" stop-opacity=".16"/><stop offset="1" stop-color="{INK}" stop-opacity="0"/></linearGradient>
<radialGradient id="halo"><stop offset="0" stop-color="{ACC}" stop-opacity=".28"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient>
<clipPath id="c"><rect width="1200" height="460" rx="18"/></clipPath>
</defs>
<g clip-path="url(#c)">
<rect width="1200" height="460" fill="url(#bg)"/>
<ellipse cx="600" cy="400" rx="560" ry="90" fill="url(#halo)"/>
<text x="56" y="62" font-family="{MONO}" font-size="13" fill="{MUTED}" letter-spacing="3">CONTRIBUTIONS · LAST 12 MONTHS</text>
<text x="56" y="116" font-family="{SERIF}" font-size="52" font-weight="700" fill="{INK}">{total:,}</text>
<text x="{56 + 34*len(f'{total:,}')}" y="116" font-family="{SANS}" font-size="20" fill="{ACC2}">commits, PRs and reviews</text>
<g font-family="{MONO}" font-size="13" fill="{MUTED}"><text x="1144" y="62" text-anchor="end">longest streak <tspan fill="{ACC2}" font-weight="700">{longest} days</tspan></text>
<text x="1144" y="86" text-anchor="end">active days <tspan fill="{ACC2}" font-weight="700">{active}</tspan></text></g>
{''.join(parts)}
{''.join(labels)}
{best_label}
<rect y="0" width="140" height="460" fill="url(#sweep)"><animateTransform attributeName="transform" type="translate" values="-160 0;1240 0" dur="7s" repeatCount="indefinite"/></rect>
</g>
<rect x=".5" y=".5" width="1199" height="459" rx="18" fill="none" stroke="{ACC}" stroke-opacity=".3"/>
</svg>
"""
with open(os.path.join(OUT, "contributions.svg"), "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print("ok", total, "longest", longest, "active", active, "best", best[0], best[1], "kb", len(svg) // 1024)

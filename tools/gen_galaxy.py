# Usage: python tools/gen_galaxy.py <github-username> <out-dir>
#   Fetches the public contribution calendar and writes <out-dir>/galaxy.svg:
#   every day is a star on a spiral arm (today at the core, a year ago on the rim), streaks become
#   constellations, the busiest day is a supernova. Pure SVG + SMIL, no JS. Re-run to refresh.
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
STAR = {1: "#c9574a", 2: "#e8604f", 3: "#f6a38f", 4: "#fff1dd"}

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
N = len(days)
total = sum(c for _, c, _ in days)
active = sum(1 for _, c, _ in days if c)
best_i = max(range(N), key=lambda i: days[i][1])

# longest streak (as index range)
run_start, best_run = None, (0, -1)
for i, (_, c, _) in enumerate(days + [(None, 0, 0)]):
    if c and run_start is None:
        run_start = i
    elif not c and run_start is not None:
        if i - run_start > best_run[1] - best_run[0] + 1:
            best_run = (run_start, i - 1)
        run_start = None
longest = best_run[1] - best_run[0] + 1


def jit(i, k):
    return (((i + 1) * 2654435761 * (k + 3)) % 1000) / 1000.0 - 0.5


# ------------------------------------------------------------ spiral: newest at the core, oldest on the rim
TURNS, R0, R1 = 2.25, 18.0, 292.0


def pos(i):
    u = math.sqrt(1 - i / (N - 1))  # i = N-1 -> u = 0 (core); i = 0 -> u = 1 (rim). equal area per day
    th = TURNS * 2 * math.pi * u
    r = R0 + (R1 - R0) * u
    lateral = jit(i, 1) * (22 + 34 * u)
    return (r + lateral) * math.cos(th), (r + lateral) * math.sin(th)


pts = [pos(i) for i in range(N)]

stars, halos, dust = [], [], []
for i, (d, c, lvl) in enumerate(days):
    x, y = pts[i]
    if c == 0:
        dust.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r=".8" fill="#9a7468" opacity=".32"/>')
        continue
    r = 2.0 + math.sqrt(c) * 1.0
    col = STAR[lvl]
    tw = 2.2 + (i % 7) * 0.6
    stars.append(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}"><animate attributeName="opacity" values="1;.35;1" dur="{tw:.1f}s" begin="-{(i % 9) * .7:.1f}s" repeatCount="indefinite"/></circle>'
    )
    if lvl >= 3:
        halos.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r*4.5:.1f}" fill="url(#halo)" opacity=".8"/>')

# constellations: runs of >= 3 consecutive active days
lines = []
i = 0
while i < N:
    if days[i][1] > 0:
        j = i
        while j + 1 < N and days[j + 1][1] > 0:
            j += 1
        if j - i + 1 >= 3 and (i, j) != best_run:
            lines.append('<polyline points="%s" fill="none" stroke="%s" stroke-opacity=".38" stroke-width=".8"/>' % (" ".join("%.1f,%.1f" % pts[k] for k in range(i, j + 1)), ACC2))
        i = j + 1
    else:
        i += 1
hero = " ".join("%.1f,%.1f" % pts[k] for k in range(best_run[0], best_run[1] + 1))
hero_line = (
    f'<polyline points="{hero}" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linecap="round" stroke-dasharray="3 5" stroke-opacity=".95">'
    f'<animate attributeName="stroke-dashoffset" from="0" to="-32" dur="2.4s" repeatCount="indefinite"/></polyline>'
)

bx, by = pts[best_i]
supernova = "".join(
    f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="3" fill="none" stroke="{INK}" stroke-width="1.4" opacity="0">'
    f'<animate attributeName="r" values="3;34" dur="3.2s" begin="{k*1.06:.2f}s" repeatCount="indefinite"/>'
    f'<animate attributeName="opacity" values=".9;0" dur="3.2s" begin="{k*1.06:.2f}s" repeatCount="indefinite"/></circle>'
    for k in range(3)
) + f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="5" fill="{INK}"/><circle cx="{bx:.1f}" cy="{by:.1f}" r="22" fill="url(#halo)"/>'

arm = " ".join("%.1f,%.1f" % ((18 + 274 * k / 160) * math.cos(TURNS * 2 * math.pi * k / 160), (18 + 274 * k / 160) * math.sin(TURNS * 2 * math.pi * k / 160)) for k in range(161))
glow = (
    f'<polyline points="{arm}" fill="none" stroke="{ACC}" stroke-opacity=".05" stroke-width="86" stroke-linejoin="round" stroke-linecap="round"/>'
    f'<polyline points="{arm}" fill="none" stroke="{ACC}" stroke-opacity=".07" stroke-width="46" stroke-linejoin="round" stroke-linecap="round"/>'
    f'<polyline points="{arm}" fill="none" stroke="{ACC2}" stroke-opacity=".06" stroke-width="16" stroke-linejoin="round" stroke-linecap="round"/>'
)
haze = []
for k in range(900):
    u = math.sqrt((k + .5) / 900)
    th = TURNS * 2 * math.pi * u + jit(k, 2) * 0.5
    r = 18 + 274 * u + jit(k, 3) * (50 + 40 * u)
    haze.append('<circle cx="%.1f" cy="%.1f" r="%.2f" fill="%s" opacity="%.2f"/>' % (r * math.cos(th), r * math.sin(th), 0.5 + (k % 4) * 0.22, ACC2 if k % 5 == 0 else "#b07a6c", 0.12 + (k % 6) * 0.045))

# ------------------------------------------------------------ background sky
sky = "".join(
    '<circle cx="%d" cy="%d" r="%.1f" fill="%s" opacity="%.2f">%s</circle>'
    % (
        int((jit(k, 5) + .5) * 1200),
        int((jit(k, 7) + .5) * 520),
        0.6 + ((k * 7) % 5) * 0.25,
        INK,
        0.25 + ((k * 3) % 5) * 0.1,
        '<animate attributeName="opacity" values=".15;.9;.15" dur="%ds" begin="-%ds" repeatCount="indefinite"/>' % (3 + k % 5, k % 6) if k % 3 == 0 else "",
    )
    for k in range(130)
)

shoot = "".join(
    f'<g><animateTransform attributeName="transform" type="translate" values="{x0} {y0};{x0+340} {y0+170}" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/>'
    f'<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;.05;.16;1" dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/>'
    f'<line x1="-90" y1="-45" x2="0" y2="0" stroke="url(#tail)" stroke-width="2" stroke-linecap="round"/><circle r="2.2" fill="{INK}"/></g>'
    for x0, y0, dur, beg in [(80, 30, 9, 1), (620, 10, 13, 5), (360, 60, 11, 8)]
)

# ------------------------------------------------------------ assemble
best_day = days[best_i][0]
svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 560" width="1200" height="560" role="img" aria-label="{total} contributions in the last year drawn as a rotating spiral galaxy: one star per day, constellations for streaks, a supernova on the busiest day">
<title>{total} contributions in the last year, drawn as a galaxy</title>
<defs>
<radialGradient id="halo"><stop offset="0" stop-color="{ACC2}" stop-opacity=".55"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient>
<radialGradient id="core"><stop offset="0" stop-color="#fff4e0" stop-opacity="1"/><stop offset=".25" stop-color="{ACC2}" stop-opacity=".75"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient>
<radialGradient id="disc"><stop offset="0" stop-color="{ACC}" stop-opacity=".22"/><stop offset=".6" stop-color="{ACC}" stop-opacity=".07"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient>
<linearGradient id="tail" x1="0" x2="1"><stop offset="0" stop-color="{INK}" stop-opacity="0"/><stop offset="1" stop-color="{INK}" stop-opacity=".9"/></linearGradient>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0b0403"/><stop offset="1" stop-color="{BG}"/></linearGradient>
<clipPath id="c"><rect width="1200" height="560" rx="18"/></clipPath>
</defs>
<g clip-path="url(#c)">
<rect width="1200" height="560" fill="url(#bg)"/>
{sky}
{shoot}
<g transform="translate(600,300) scale(1.6,.62)">
<circle r="320" fill="url(#disc)"/>
<g><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="150s" repeatCount="indefinite"/>
{glow}{''.join(haze)}{''.join(dust)}
{''.join(halos)}
{''.join(lines)}
{hero_line}
{''.join(stars)}
{supernova}
</g>
<circle r="78" fill="url(#core)"><animate attributeName="r" values="70;88;70" dur="5s" repeatCount="indefinite"/></circle>
</g>
<text x="48" y="64" font-family="{MONO}" font-size="13" fill="{MUTED}" letter-spacing="3">CONTRIBUTION GALAXY · LAST 12 MONTHS</text>
<text x="48" y="122" font-family="{SERIF}" font-size="58" font-weight="700" fill="{INK}">{total:,}</text>
<text x="48" y="160" font-family="{SANS}" font-size="18" fill="{ACC2}">stars across {active} active days</text>
<g font-family="{MONO}" font-size="13" fill="{MUTED}">
<circle cx="878" cy="60" r="4" fill="{INK}"/><text x="898" y="64">supernova · {best_day.strftime('%b %d').replace(' 0', ' ')} · <tspan fill="{ACC2}" font-weight="700">{days[best_i][1]}</tspan></text>
<line x1="868" y1="86" x2="888" y2="86" stroke="{INK}" stroke-width="1.6" stroke-dasharray="3 5"/><text x="898" y="90">constellation · <tspan fill="{ACC2}" font-weight="700">{longest}-day</tspan> streak</text>
<circle cx="878" cy="112" r="6" fill="url(#core)"/><text x="898" y="116">core · today</text>
</g>
<text x="48" y="526" font-family="{MONO}" font-size="12" fill="{MUTED}" letter-spacing="1.5">NEWEST DAYS BURN AT THE CORE · A YEAR AGO DRIFTS ON THE RIM</text>
</g>
<rect x=".5" y=".5" width="1199" height="559" rx="18" fill="none" stroke="{ACC}" stroke-opacity=".3"/>
</svg>
"""
with open(os.path.join(OUT, "galaxy.svg"), "w", encoding="utf-8", newline="\n") as f:
    f.write(svg)
print("ok", total, "active", active, "streak", longest, "best", best_day, days[best_i][1], "kb", len(svg) // 1024)

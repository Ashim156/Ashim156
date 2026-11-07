# Usage: python tools/gen_assets.py assets   (regenerates every SVG in ./assets)
"""Generates the animated SVGs for the GitHub profile README. Pure SVG + CSS/SMIL: no JS, no external fonts."""
import math, os, sys

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

BG, BG2, ACC, ACC2, INK, MUTED = "#120706", "#1c0c0a", "#e8604f", "#f6a38f", "#f4eadb", "#a89488"
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "'Segoe UI', -apple-system, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Consolas, monospace"


def wave(width, amp, period, y, phase=0.0):
    pts = []
    for x in range(0, width + 1, 20):
        pts.append((x, y + amp * math.sin((x / period) * 2 * math.pi + phase)))
    d = "M0,%d " % 400 + " ".join("L%.1f,%.1f" % p for p in pts) + " L%d,400 Z" % width
    return d


def write(name, s):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


# ---------------------------------------------------------------- header
roles = ["Founder", "Full Stack Developer", "AI Engineer", "Team Lead"]
cycle = 3.0 * len(roles)
role_css, role_svg = [], []
for i, r in enumerate(roles):
    a = i * 100 / len(roles)
    role_css.append(
        ".r%d{opacity:0;animation:role%d %ss infinite}"
        "@keyframes role%d{%.2f%%{opacity:0;transform:translateY(14px)}%.2f%%{opacity:1;transform:translateY(0)}"
        "%.2f%%{opacity:1;transform:translateY(0)}%.2f%%{opacity:0;transform:translateY(-14px)}100%%{opacity:0}}"
        % (i, i, cycle, i, a + 0.01, a + 3, a + 100 / len(roles) - 3, a + 100 / len(roles))
    )
    # first role starts from 0%: shift keyframes so loop is clean
    role_svg.append('<text class="r%d" x="70" y="232" font-family="%s" font-size="34" fill="%s" font-weight="600">%s</text>' % (i, SANS, ACC2, r))

dots = "".join(
    '<circle cx="%d" cy="%d" r="1.6" fill="%s" opacity="%.2f"><animate attributeName="opacity" values="0.1;0.7;0.1" dur="%.1fs" begin="-%.1fs" repeatCount="indefinite"/></circle>'
    % (60 + (i * 97) % 1100, 30 + (i * 53) % 240, INK, 0.3, 3 + (i % 5), i % 7)
    for i in range(46)
)

header = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 400" width="1200" height="400" role="img" aria-label="Ashim Nakarmi, Full Stack AI Engineer from Nepal">
<title>Ashim Nakarmi, Full Stack AI Engineer from Nepal</title>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="{BG2}"/></linearGradient>
<radialGradient id="glow"><stop offset="0" stop-color="{ACC}" stop-opacity=".55"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient>
<linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="{INK}"/><stop offset="1" stop-color="{ACC2}"/></linearGradient>
<linearGradient id="w1" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{ACC}" stop-opacity=".30"/><stop offset="1" stop-color="{ACC}" stop-opacity=".04"/></linearGradient>
<linearGradient id="w2" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{ACC2}" stop-opacity=".20"/><stop offset="1" stop-color="{ACC2}" stop-opacity=".02"/></linearGradient>
<clipPath id="c"><rect width="1200" height="400" rx="18"/></clipPath>
</defs>
<style>
text{{font-kerning:normal}}
.name{{animation:rise 1.1s cubic-bezier(.2,.8,.2,1) both}}
.sub{{animation:rise 1.1s .25s cubic-bezier(.2,.8,.2,1) both}}
.tag{{animation:rise 1.1s .45s cubic-bezier(.2,.8,.2,1) both}}
@keyframes rise{{from{{opacity:0;transform:translateY(22px)}}to{{opacity:1;transform:translateY(0)}}}}
.caret{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
{''.join(role_css)}
.r0{{animation-delay:0s}}
</style>
<g clip-path="url(#c)">
<rect width="1200" height="400" fill="url(#bg)"/>
<circle r="260" fill="url(#glow)"><animateMotion dur="16s" repeatCount="indefinite" path="M980,90 C1100,200 860,260 980,90 S1040,40 980,90"/></circle>
<circle r="190" fill="url(#glow)" opacity=".5"><animateMotion dur="22s" repeatCount="indefinite" path="M200,330 C320,260 120,230 200,330 S260,380 200,330"/></circle>
{dots}
<g><animateTransform attributeName="transform" type="translate" from="0 0" to="-1200 0" dur="18s" repeatCount="indefinite"/>
<path d="{wave(2400, 16, 300, 318)}" fill="url(#w1)"/></g>
<g><animateTransform attributeName="transform" type="translate" from="-1200 0" to="0 0" dur="26s" repeatCount="indefinite"/>
<path d="{wave(2400, 12, 400, 338, 1.2)}" fill="url(#w2)"/></g>
<text class="name" x="68" y="140" font-family="{SERIF}" font-size="84" font-weight="700" fill="url(#name)">Ashim Nakarmi</text>
<g class="sub">{''.join(role_svg)}</g>
<text class="tag" x="70" y="290" font-family="{SANS}" font-size="20" fill="{MUTED}" letter-spacing=".4">Founder of Your Tech Mitra  ·  Maker of MekMitra  ·  Kathmandu, Nepal</text>
<rect x="68" y="168" width="64" height="4" rx="2" fill="{ACC}"><animate attributeName="width" values="0;64;220;64" keyTimes="0;.15;.5;1" dur="8s" repeatCount="indefinite"/></rect>
</g>
<rect x=".5" y=".5" width="1199" height="399" rx="18" fill="none" stroke="{ACC}" stroke-opacity=".25"/>
</svg>
"""
write("header.svg", header)

# ---------------------------------------------------------------- footer
footer = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 160" width="1200" height="160" role="img" aria-label="Thanks for visiting">
<title>Thanks for visiting</title>
<defs>
<linearGradient id="a" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{ACC}" stop-opacity=".35"/><stop offset="1" stop-color="{ACC}" stop-opacity=".05"/></linearGradient>
<linearGradient id="b" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{ACC2}" stop-opacity=".22"/><stop offset="1" stop-color="{ACC2}" stop-opacity=".02"/></linearGradient>
<clipPath id="c"><rect width="1200" height="160" rx="18"/></clipPath>
</defs>
<g clip-path="url(#c)">
<rect width="1200" height="160" fill="{BG}"/>
<g transform="translate(0,-250)"><g><animateTransform attributeName="transform" type="translate" from="0 0" to="-1200 0" dur="16s" repeatCount="indefinite"/><path d="{wave(2400, 14, 300, 340)}" fill="url(#a)"/></g>
<g><animateTransform attributeName="transform" type="translate" from="-1200 0" to="0 0" dur="24s" repeatCount="indefinite"/><path d="{wave(2400, 10, 400, 356, 1.4)}" fill="url(#b)"/></g></g>
<text x="600" y="82" text-anchor="middle" font-family="{SERIF}" font-size="30" fill="{INK}">Let's build something worth using.</text>
<text x="600" y="116" text-anchor="middle" font-family="{SANS}" font-size="16" fill="{MUTED}" letter-spacing="1">asimnakarmi156@gmail.com</text>
</g>
<rect x=".5" y=".5" width="1199" height="159" rx="18" fill="none" stroke="{ACC}" stroke-opacity=".25"/>
</svg>
"""
write("footer.svg", footer)

# ---------------------------------------------------------------- divider
divider = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 24" width="1200" height="24" role="presentation">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{ACC}" stop-opacity="0"/><stop offset=".5" stop-color="{ACC}"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></linearGradient></defs>
<rect y="11" width="1200" height="2" fill="url(#g)" opacity=".35"/>
<circle cy="12" r="5" fill="{ACC2}"><animate attributeName="cx" values="0;1200" dur="5s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;1;0" dur="5s" repeatCount="indefinite"/></circle>
<circle cy="12" r="11" fill="{ACC}" opacity=".18"><animate attributeName="cx" values="0;1200" dur="5s" repeatCount="indefinite"/></circle>
</svg>
"""
write("divider.svg", divider)

# ---------------------------------------------------------------- stack marquee
items = [
    ("React", "#61dafb"), ("Next.js", "#f4eadb"), ("TypeScript", "#4b9be8"), ("Tailwind CSS", "#38bdf8"),
    ("Ant Design", "#e8604f"), ("Three.js", "#f4eadb"), ("Django", "#3fb68b"), ("DRF", "#c0453a"),
    ("Python", "#f2c94c"), ("Node.js", "#7fbf4d"), ("Express", "#a89488"), ("PostgreSQL", "#6c9ed6"),
    ("MongoDB", "#52b46b"), ("MySQL", "#4f8fc0"), ("Docker", "#4aa3e0"), ("Linux", "#f2c94c"), ("Git", "#e8604f"),
]
H, GAP, PAD = 46, 14, 22
pill = []
x = 0
for name, col in items:
    w = int(len(name) * 9.6 + PAD * 2 + 16)
    pill.append(
        f'<g transform="translate({x},12)"><rect width="{w}" height="{H}" rx="{H//2}" fill="{BG2}" stroke="{col}" stroke-opacity=".55"/>'
        f'<circle cx="{PAD-4}" cy="{H//2}" r="4.5" fill="{col}"/>'
        f'<text x="{PAD+10}" y="{H//2+5}" font-family="{SANS}" font-size="16" fill="{INK}">{name}</text></g>'
    )
    x += w + GAP
total = x
row = "".join(pill)
marquee = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 70" width="1200" height="70" role="img" aria-label="Tech stack: React, Next.js, TypeScript, Django, Node.js, PostgreSQL, Docker and more">
<title>Tech stack</title>
<defs><linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".07" stop-color="#fff"/><stop offset=".93" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<mask id="m"><rect width="1200" height="70" fill="url(#fade)"/></mask></defs>
<g mask="url(#m)"><g><animateTransform attributeName="transform" type="translate" from="0 0" to="-{total} 0" dur="{int(total/55)}s" repeatCount="indefinite"/>
{row}<g transform="translate({total},0)">{row}</g></g></g>
</svg>
"""
write("stack.svg", marquee)

# ---------------------------------------------------------------- now card
def line(y, label, text, delay):
    return (
        f'<g style="animation:fade .8s {delay}s both"><circle cx="46" cy="{y-6}" r="5" fill="{ACC}"><animate attributeName="r" values="4;7;4" dur="2.4s" begin="{delay}s" repeatCount="indefinite"/>'
        f'<animate attributeName="opacity" values="1;.4;1" dur="2.4s" begin="{delay}s" repeatCount="indefinite"/></circle>'
        f'<text x="68" y="{y}" font-family="{MONO}" font-size="15" fill="{ACC2}" letter-spacing="1">{label}</text>'
        f'<text x="200" y="{y}" font-family="{SANS}" font-size="18" fill="{INK}">{text}</text></g>'
    )

now = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 230" width="1200" height="230" role="img" aria-label="What Ashim is working on now">
<title>Right now</title>
<style>@keyframes fade{{from{{opacity:0;transform:translateX(-14px)}}to{{opacity:1;transform:translateX(0)}}}}</style>
<rect width="1200" height="230" rx="18" fill="{BG}"/>
<rect x=".5" y=".5" width="1199" height="229" rx="18" fill="none" stroke="{ACC}" stroke-opacity=".3"/>
<text x="46" y="52" font-family="{MONO}" font-size="14" fill="{MUTED}" letter-spacing="3">~/ashim  $  now</text>
{line(100, "BUILDING", "MekMitra, a garage management SaaS for auto workshops in Nepal", .2)}
{line(140, "LEADING", "a dev team shipping ERP and CRM platforms at Codesc Nepal", .5)}
{line(180, "EXPLORING", "where AI genuinely makes software more useful", .8)}
<rect x="940" y="20" width="12" height="12" rx="6" fill="{ACC}"><animate attributeName="opacity" values="1;.2;1" dur="1.6s" repeatCount="indefinite"/></rect>
<text x="960" y="31" font-family="{MONO}" font-size="13" fill="{INK}">open to collaboration</text>
</svg>
"""
write("now.svg", now)
print("ok", total)

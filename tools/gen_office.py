# Usage: python tools/gen_office.py assets   (regenerates assets/office.svg)
"""Animated office scene for the GitHub profile README. Pure SVG + SMIL: no JS, no external fonts."""
import os
import sys

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

BG, BG2, ACC, ACC2, INK, MUTED = "#120706", "#1c0c0a", "#e8604f", "#f6a38f", "#f4eadb", "#a89488"
SANS = "'Segoe UI', -apple-system, Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Consolas, monospace"
WOOD, DARK = "#3a1a14", "#2a100c"
BLUE, GREEN, YEL = "#6c9ed6", "#7fbf4d", "#f2c94c"


def write(name, s):
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def code_lines(seed):
    cols = [ACC2, BLUE, GREEN, INK, YEL]
    out = []
    for i in range(16):
        indent = ((i + seed) % 3) * 9
        w = 22 + ((i * 37 + seed * 11) % 70)
        c = cols[(i * 2 + seed) % 5]
        op = 0.55 if c == INK else 0.9
        out.append('<rect x="%d" y="%d" width="%d" height="5" rx="2.5" fill="%s" opacity="%s"/>' % (4 + indent, i * 10 + 4, w, c, op))
    return "".join(out)


def bubble(msgs, delay):
    """Commit-message bubbles that cycle above a developer's head (desk-local coordinates)."""
    parts = []
    n = len(msgs)
    for k, m in enumerate(msgs):
        t0 = k / n
        kt = [0.0, t0 + 0.001, t0 + 0.04, t0 + 1 / n - 0.05, t0 + 1 / n - 0.01, 1.0]
        for j in range(1, len(kt)):
            if kt[j] <= kt[j - 1]:
                kt[j] = kt[j - 1] + 0.0005
        kt[-1] = 1.0
        kts = ";".join("%.4f" % v for v in kt)
        parts.append(
            f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{kts}" dur="{3*n}s" begin="{delay}s" repeatCount="indefinite"/>'
            f'<rect x="-120" y="197" width="150" height="26" rx="13" fill="{BG2}" stroke="{ACC}" stroke-opacity=".6"/>'
            f'<path d="M-62,223 l6,9 l6,-9 z" fill="{BG2}" stroke="{ACC}" stroke-opacity=".6"/>'
            f'<rect x="-63" y="221" width="14" height="3" fill="{BG2}"/>'
            f'<text x="-45" y="214" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{ACC2}">{m}</text></g>'
        )
    return "".join(parts)


def desk(i, cx, skin, hair, shirt, pants, tag, msgs, delay, lead=False):
    cid = "scr%d" % i
    speed = 7 + i
    stroke = ACC if lead else MUTED
    sop = ".9" if lead else ".4"
    return f"""
<g transform="translate({cx},0)">
  <ellipse cx="60" cy="270" rx="95" ry="70" fill="url(#mglow)"><animate attributeName="opacity" values=".55;.9;.55" dur="{3+i}s" repeatCount="indefinite"/></ellipse>
  <rect x="-102" y="318" width="9" height="66" rx="4" fill="{DARK}"/>
  <rect x="-98" y="374" width="56" height="10" rx="5" fill="{DARK}"/>
  <rect x="-74" y="384" width="6" height="40" fill="{DARK}"/>
  <rect x="-94" y="422" width="46" height="5" rx="2.5" fill="{DARK}"/>
  <rect x="-34" y="344" width="8" height="86" fill="{DARK}"/><rect x="136" y="344" width="8" height="86" fill="{DARK}"/>
  <rect x="-40" y="330" width="196" height="14" rx="4" fill="{WOOD}"/>
  <rect x="54" y="316" width="12" height="14" fill="#1a0a07"/><rect x="38" y="326" width="44" height="5" rx="2" fill="#1a0a07"/>
  <rect x="-10" y="226" width="140" height="92" rx="7" fill="#0b0403" stroke="{ACC}" stroke-opacity=".55" stroke-width="2"/>
  <clipPath id="{cid}"><rect x="-4" y="232" width="128" height="80" rx="3"/></clipPath>
  <g clip-path="url(#{cid})"><rect x="-4" y="232" width="128" height="80" fill="#0f0605"/>
    <g transform="translate(0,232)"><g><animateTransform attributeName="transform" type="translate" from="0 0" to="0 -160" dur="{speed}s" repeatCount="indefinite"/>{code_lines(i)}<g transform="translate(0,160)">{code_lines(i)}</g></g></g></g>
  <rect x="-22" y="324" width="62" height="6" rx="3" fill="#5a2a22"/>
  <rect x="112" y="314" width="15" height="16" rx="3" fill="{ACC2}"/><path d="M127,318 q8,2 0,9" fill="none" stroke="{ACC2}" stroke-width="2.5"/>
  <path d="M116,308 q-4,-6 0,-12 q4,-6 0,-12" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round" opacity="0"><animate attributeName="opacity" values="0;.55;0" dur="3s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="0 6;0 -6" dur="3s" repeatCount="indefinite"/></path>
  <path d="M123,308 q-4,-6 0,-12 q4,-6 0,-12" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round" opacity="0"><animate attributeName="opacity" values="0;.5;0" dur="3s" begin="-1.2s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="0 6;0 -6" dur="3s" begin="-1.2s" repeatCount="indefinite"/></path>
  <rect x="-80" y="364" width="64" height="15" rx="7.5" fill="{pants}"/>
  <rect x="-30" y="370" width="13" height="54" rx="6" fill="{pants}"/><rect x="-36" y="420" width="24" height="9" rx="4.5" fill="#0b0403"/>
  <rect x="-88" y="294" width="42" height="80" rx="17" fill="{shirt}"/>
  <path d="M-62,312 Q-40,338 -14,322" fill="none" stroke="{shirt}" stroke-width="13" stroke-linecap="round" opacity=".92"><animate attributeName="d" values="M-62,312 Q-40,338 -14,322;M-62,312 Q-40,334 -11,319;M-62,312 Q-40,339 -16,324;M-62,312 Q-40,338 -14,322" dur="0.7s" repeatCount="indefinite"/></path>
  <circle cx="-14" cy="322" r="6" fill="{skin}"><animate attributeName="cx" values="-14;-11;-16;-14" dur="0.7s" repeatCount="indefinite"/><animate attributeName="cy" values="322;319;324;322" dur="0.7s" repeatCount="indefinite"/></circle>
  <g><animateTransform attributeName="transform" type="translate" values="0 0;0 1.6;0 0" dur="2.6s" repeatCount="indefinite"/>
    <rect x="-72" y="282" width="16" height="16" fill="{skin}"/>
    <circle cx="-62" cy="272" r="20" fill="{skin}"/>
    <path d="M-82,273 A20,20 0 0 1 -42,272 Q-49,259 -62,259 Q-76,259 -82,273 Z" fill="{hair}"/>
    <circle cx="-50" cy="274" r="2.2" fill="#0b0403"/>
  </g>
  {bubble(msgs, delay)}
  <g transform="translate(40,0)"><rect x="-70" y="446" width="140" height="26" rx="13" fill="{BG2}" stroke="{stroke}" stroke-opacity="{sop}"/>
  <text x="0" y="463" text-anchor="middle" font-family="{SANS}" font-size="13" fill="{INK}">{tag}</text></g>
</g>"""


stars = "".join(
    '<circle cx="%d" cy="%d" r="1.5" fill="%s"><animate attributeName="opacity" values=".15;1;.15" dur="%ds" begin="-%ds" repeatCount="indefinite"/></circle>'
    % (74 + (k * 37) % 205, 52 + (k * 23) % 70, INK, 2 + k % 4, k % 5)
    for k in range(18)
)
towers = "".join(
    '<rect x="%d" y="%d" width="24" height="%d" fill="#10060a"/>' % (60 + k * 23, 194 - h, h)
    for k, h in enumerate([50, 78, 44, 96, 60, 70, 40, 88, 56, 66])
)
lights = "".join(
    '<rect x="%d" y="%d" width="4" height="5" fill="%s"><animate attributeName="opacity" values="1;1;0;1" keyTimes="0;.6;.65;1" dur="%ds" begin="-%ds" repeatCount="indefinite"/></rect>'
    % (66 + (k * 29) % 215, 130 + (k * 17) % 55, YEL, 4 + k % 6, k % 4)
    for k in range(20)
)
window = f"""
<clipPath id="win"><rect x="60" y="44" width="230" height="150" rx="6"/></clipPath>
<linearGradient id="sky" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#1a0d1f"/><stop offset="1" stop-color="#5a1f1a"/></linearGradient>
<g clip-path="url(#win)"><rect x="60" y="44" width="230" height="150" fill="url(#sky)"/>{stars}
<circle cx="238" cy="84" r="17" fill="{INK}" opacity=".92"/><circle cx="246" cy="79" r="15" fill="#241020"/>{towers}{lights}</g>
<rect x="60" y="44" width="230" height="150" rx="6" fill="none" stroke="{WOOD}" stroke-width="7"/>
<line x1="175" y1="44" x2="175" y2="194" stroke="{WOOD}" stroke-width="4"/><line x1="60" y1="118" x2="290" y2="118" stroke="{WOOD}" stroke-width="4"/>
"""


def card(x, y, col=MUTED, op=0.45):
    return (
        f'<g transform="translate({x},{y})"><rect width="104" height="24" rx="5" fill="{BG}" stroke="{col}" stroke-opacity="{op}"/>'
        f'<rect x="8" y="7" width="60" height="3.5" rx="1.75" fill="{col}" opacity=".7"/><rect x="8" y="14" width="38" height="3.5" rx="1.75" fill="{col}" opacity=".4"/></g>'
    )


cols = "".join(
    '<text x="%d" y="80" font-family="%s" font-size="11" fill="%s" letter-spacing="1.5">%s</text>' % (x, MONO, ACC2, t)
    for x, t in [(398, "TODO"), (528, "DOING"), (658, "DONE")]
)
board = f"""
<rect x="380" y="36" width="430" height="156" rx="10" fill="{BG2}" stroke="{ACC}" stroke-opacity=".4"/>
<text x="398" y="58" font-family="{MONO}" font-size="12" fill="{MUTED}" letter-spacing="2">SPRINT BOARD</text>
{cols}{card(398, 122)}{card(528, 92)}{card(658, 92, GREEN, .7)}
<g><animateTransform attributeName="transform" type="translate" values="0 0;0 0;130 0;130 0;260 30;260 30" keyTimes="0;.15;.35;.55;.75;1" dur="12s" repeatCount="indefinite"/>
<g><animate attributeName="opacity" values="1;1;1;0" keyTimes="0;.75;.92;1" dur="12s" repeatCount="indefinite"/>{card(398, 92, ACC, 1)}</g></g>
"""

ticks = "".join(
    '<line x1="0" y1="-29" x2="0" y2="-33" stroke="%s" stroke-width="2" transform="rotate(%d)"/>' % (MUTED, a) for a in range(0, 360, 30)
)
clock = f"""
<g transform="translate(940,112)"><circle r="40" fill="{BG2}" stroke="{ACC}" stroke-opacity=".6" stroke-width="3"/>{ticks}
<line y2="-20" stroke="{INK}" stroke-width="4" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="360s" repeatCount="indefinite"/></line>
<line y2="-29" stroke="{ACC2}" stroke-width="2.5" stroke-linecap="round"><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="30s" repeatCount="indefinite"/></line>
<circle r="3.5" fill="{ACC}"/></g>
"""

books = "".join(
    '<rect x="%d" y="%d" width="%d" height="%d" rx="1.5" fill="%s"/>' % (x, 150 - h, w, h, c)
    for x, w, h, c in [(1018, 12, 34, ACC), (1030, 10, 28, BLUE), (1040, 14, 38, ACC2), (1054, 10, 30, GREEN), (1064, 12, 36, YEL)]
)
shelf = f"""
<rect x="1010" y="150" width="140" height="6" rx="3" fill="{WOOD}"/>{books}
<g transform="translate(1124,150)"><path d="M-10,0 L-7,-14 L7,-14 L10,0 Z" fill="{ACC}"/>
<g><animateTransform attributeName="transform" type="rotate" values="-4 0 -14;4 0 -14;-4 0 -14" dur="5s" repeatCount="indefinite"/>
<path d="M0,-14 Q-14,-30 -8,-46 Q2,-32 0,-14 Z" fill="{GREEN}"/><path d="M0,-14 Q14,-28 10,-44 Q-2,-30 0,-14 Z" fill="#5f9a3a"/><path d="M0,-14 Q0,-34 0,-52 Q6,-34 0,-14 Z" fill="#8fd05a"/></g></g>
"""

plant = f"""
<g transform="translate(1160,430)"><path d="M-22,0 L-16,-50 L16,-50 L22,0 Z" fill="{ACC}"/>
<g><animateTransform attributeName="transform" type="rotate" values="-3 0 -50;3 0 -50;-3 0 -50" dur="6s" repeatCount="indefinite"/>
<path d="M0,-50 Q-48,-70 -40,-130 Q0,-100 0,-50 Z" fill="{GREEN}"/><path d="M0,-50 Q48,-66 44,-124 Q4,-96 0,-50 Z" fill="#5f9a3a"/>
<path d="M0,-50 Q-8,-110 4,-160 Q22,-110 0,-50 Z" fill="#8fd05a"/><path d="M0,-50 Q-30,-90 -14,-146 Q10,-100 0,-50 Z" fill="#4f8a30" opacity=".9"/></g></g>
"""

desks = (
    desk(0, 150, "#e0b08c", "#2b1a14", "#e8604f", "#2a2f4a", "Frontend", ["feat(ui): job card board", "fix: invoice table", "style: polish the nav"], 0)
    + desk(1, 540, "#c98f6b", "#120706", "#f4eadb", "#3a1a14", "Ashim · Team Lead", ["review: LGTM, merging", "feat: VAT report", "chore: tidy the sprint"], -3, True)
    + desk(2, 930, "#8d5a3c", "#1a0f0a", "#6c9ed6", "#2a2f4a", "Backend", ["feat(api): gate pass", "fix: stock sync", "test: all green"], -6)
)

office = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 500" width="1200" height="500" role="img" aria-label="An animated office: a small team coding at their desks, a sprint board moving a card to done, commit messages floating above each developer">
<title>The workspace</title>
<defs>
<linearGradient id="wall" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>
<linearGradient id="floor" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#1a0907"/><stop offset="1" stop-color="#0a0403"/></linearGradient>
<radialGradient id="mglow"><stop offset="0" stop-color="{ACC}" stop-opacity=".35"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient>
<clipPath id="all"><rect width="1200" height="500" rx="18"/></clipPath>
</defs>
<g clip-path="url(#all)">
<rect width="1200" height="500" fill="url(#wall)"/>
<rect y="430" width="1200" height="70" fill="url(#floor)"/><rect y="430" width="1200" height="2" fill="{ACC}" opacity=".25"/>
{window}{board}{clock}{shelf}{desks}{plant}
</g>
<rect x=".5" y=".5" width="1199" height="499" rx="18" fill="none" stroke="{ACC}" stroke-opacity=".3"/>
</svg>
"""
write("office.svg", office)
print("office ok")

#!/usr/bin/env python3
"""Render the ENTIRE GitHub profile as one continuous pixel/space SVG.

Animations are CSS @keyframes (GitHub renders CSS in <img> SVGs but ignores SMIL).
The contribution snake follows a nearest-neighbour tour over the *filled* cells,
so it weaves through real contributions and skips empty days.

Reads assets/data.json (scripts/fetch_data.sh) -> writes assets/profile.svg.
"""
import json, random, os, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "assets", "data.json")
OUTP = os.path.join(ROOT, "assets", "profile.svg")

AMBER, MAGENTA, CYAN, STAR, MUTED = "#f0a742", "#ff5c8a", "#4ad9e4", "#e8ecff", "#8a8ac0"
INK, EMPTY = "#c7c7ee", "#12122e"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"

FONT = {
    "F": ["11111","10000","11110","10000","10000","10000","10000"],
    "E": ["11111","10000","11110","10000","10000","10000","11111"],
    "L": ["10000","10000","10000","10000","10000","10000","11111"],
    "I": ["11111","00100","00100","00100","00100","00100","11111"],
    "P": ["11110","10001","10001","11110","10000","10000","10000"],
    "O": ["01110","10001","10001","10001","10001","10001","01110"],
    "V": ["10001","10001","10001","10001","10001","01010","00100"],
    "R": ["11110","10001","10001","11110","10100","10010","10001"],
    "A": ["01110","10001","10001","11111","10001","10001","10001"],
    " ": ["00000"]*7,
}
ROCKET = ["..a..",".aaa.",".aca.",".aaa.",".aaa.","b.a.b","f.f.f",".fff.","..f.."]
ROCKET_PAL = {"a": "#d8dcf0", "c": CYAN, "b": MAGENTA, "f": AMBER}

W = 820
Y_HERO, Y_STACK, Y_STATS, Y_NOW, Y_FOOT = 0, 258, 516, 792, 982
H = 1052

s = []
def add(x): s.append(x)
def esc(t): return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def load():
    d = json.load(open(DATA))["data"]["user"]
    cal = d["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [dd for w in weeks for dd in w["contributionDays"]]
    lon = c = 0
    for dd in days:
        if dd["contributionCount"] > 0: c += 1; lon = max(lon, c)
        else: c = 0
    return {"total": cal["totalContributions"], "repos": d["repositories"]["totalCount"],
            "followers": d["followers"]["totalCount"], "longest": lon, "weeks": weeks}

# ---- drawing helpers ----
def heading(x, y, prompt, label):
    add(f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="15" font-weight="700">'
        f'<tspan fill="{AMBER}">&gt; {esc(prompt)}</tspan><tspan fill="{CYAN}"> {esc(label)}</tspan></text>')
    add(f'<line x1="{x+(len(prompt)+len(label))*9+30}" y1="{y-5}" x2="{W-40}" y2="{y-5}" '
        f'stroke="{CYAN}" stroke-opacity="0.25" stroke-width="1" stroke-dasharray="4 4"/>')

def glyphs(text, p, x0, y0, face, shadow=None, hi=None):
    ox = x0
    for ch in text:
        g = FONT.get(ch, FONT[" "])
        for r in range(7):
            for c in range(5):
                if g[r][c] == "1":
                    px, py = ox + c*p, y0 + r*p
                    if shadow:
                        sh = round(p*0.34)
                        add(f'<rect x="{px+sh}" y="{py+sh}" width="{p}" height="{p}" fill="{shadow}"/>')
                    add(f'<rect x="{px}" y="{py}" width="{p}" height="{p}" fill="{face}"/>')
                    if hi:
                        add(f'<rect x="{px}" y="{py}" width="{max(1,round(p*0.4))}" height="{max(1,round(p*0.4))}" fill="{hi}"/>')
        ox += 6*p

def chip(x, y, text, bg, fg, star=False):
    label = text + ("  ★" if star else "")
    w = 18 + len(label)*7.3
    add(f'<rect x="{x+2}" y="{y+2}" width="{w:.0f}" height="23" rx="3" fill="#000" opacity="0.5"/>')
    add(f'<rect x="{x}" y="{y}" width="{w:.0f}" height="23" rx="3" fill="{bg}" stroke="#000" stroke-opacity="0.3" stroke-width="1.5"/>')
    add(f'<text x="{x+w/2:.0f}" y="{y+16}" text-anchor="middle" font-family="{MONO}" font-size="12" font-weight="700" fill="{fg}">{esc(label)}</text>')
    return x + w + 9

def tile(x, y, w, num, label, fire=False):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="72" rx="4" fill="#0e0e26" stroke="#2a2a55" stroke-width="1.5"/>')
    add(f'<text x="{x+w/2:.0f}" y="{y+38}" text-anchor="middle" font-family="{MONO}" font-size="26" font-weight="800" fill="{AMBER if fire else STAR}">{esc(str(num))}</text>')
    add(f'<text x="{x+w/2:.0f}" y="{y+58}" text-anchor="middle" font-family="{MONO}" font-size="10" letter-spacing="1" fill="{MUTED}">{esc(label)}</text>')

# ==== build ====
data = load()
DUR = 20.0  # snake loop seconds

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'role="img" aria-label="Felipe Oliveira — Backend Engineer profile">')

# ---- CSS (GitHub animates CSS keyframes in <img> SVGs; it ignores SMIL) ----
add('<style>'
    '@keyframes tw{0%,100%{opacity:.25}50%{opacity:.9}}'
    '@keyframes shoot{0%{opacity:0;transform:translate(0,0)}12%{opacity:.95}42%{opacity:0}100%{opacity:0;transform:translate(var(--dx),var(--dy))}}'
    '@keyframes bob{0%,100%{transform:translateY(0)}50%{transform:translateY(-9px)}}'
    '@keyframes flick{0%,100%{opacity:.3}50%{opacity:1}}'
    '@keyframes fuel{0%,100%{opacity:.5}50%{opacity:1}}'
    '@keyframes steam{0%{opacity:0;transform:translateY(0)}30%{opacity:.7}100%{opacity:0;transform:translateY(-9px)}}'
    '@media(prefers-reduced-motion:reduce){*{animation:none!important}}'
    '</style>')

add('<defs>'
    '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#0c0c24"/><stop offset="0.5" stop-color="#0a0a1a"/>'
    '<stop offset="1" stop-color="#060615"/></linearGradient>'
    f'<radialGradient id="neb" cx="14%" cy="3%" r="45%"><stop offset="0" stop-color="{AMBER}" stop-opacity="0.16"/><stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>'
    f'<radialGradient id="neb2" cx="90%" cy="52%" r="40%"><stop offset="0" stop-color="{CYAN}" stop-opacity="0.08"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>'
    '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity="0.15"/></pattern>'
    '</defs>')
add(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
add(f'<rect width="{W}" height="{H}" fill="url(#neb)"/><rect width="{W}" height="{H}" fill="url(#neb2)"/>')

# continuous twinkling starfield (CSS)
random.seed(42)
for _ in range(int(W*H/2600)):
    x, y = random.randint(0, W-2), random.randint(0, H-2)
    big = random.random() < 0.14
    sz = 2 if big else 1
    col = AMBER if (big and random.random() < 0.5) else STAR
    dur = round(random.uniform(1.8, 4.2), 2)
    delay = round(random.uniform(0, 4), 2)
    add(f'<rect x="{x}" y="{y}" width="{sz}" height="{sz}" fill="{col}" '
        f'style="animation:tw {dur}s ease-in-out infinite;animation-delay:-{delay}s"/>')

# shooting stars (CSS translate)
for sx, sy, dx, dy, dur, delay in [(150,40,120,52,7,0),(560,66,-150,68,9,3.2),(300,168,150,-52,8,5.6)]:
    add(f'<line x1="{sx}" y1="{sy}" x2="{sx-dx*0.22:.0f}" y2="{sy-dy*0.22:.0f}" stroke="{STAR}" stroke-width="1.5" '
        f'style="--dx:{dx}px;--dy:{dy}px;opacity:0;animation:shoot {dur}s linear infinite;animation-delay:-{delay}s"/>')

for yy in (Y_STACK, Y_STATS, Y_NOW, Y_FOOT):
    add(f'<line x1="0" y1="{yy}" x2="{W}" y2="{yy}" stroke="#1a1a3a" stroke-width="1"/>')

# ---------- HERO ----------
title = "FELIPE OLIVEIRA"
p = 8; tw = (len(title)*6-1)*p; x0 = (W-tw)//2
glyphs(title, p, x0, 74, AMBER, shadow=MAGENTA, hi="#ffe0a8")
rp, rx, ry = 7, 690, 20
add(f'<g transform="translate({rx},{ry})"><g style="animation:bob 3.4s ease-in-out infinite">')
for r, row in enumerate(ROCKET):
    for c, k in enumerate(row):
        if k in ROCKET_PAL:
            add(f'<rect x="{c*rp}" y="{r*rp}" width="{rp}" height="{rp}" fill="{ROCKET_PAL[k]}"/>')
add(f'<rect x="{2*rp}" y="{9*rp}" width="{rp}" height="{rp}" fill="{AMBER}" style="animation:flick .5s ease-in-out infinite"/>')
add('</g></g>')
sy = 74 + 7*p + 26
add(f'<rect x="{x0}" y="{sy-14}" width="{tw}" height="2" fill="{CYAN}" opacity="0.5"/>')
add(f'<text x="{W//2}" y="{sy+2}" text-anchor="middle" font-family="{MONO}" font-size="13" letter-spacing="4" fill="{CYAN}">B A C K E N D&#160;&#160;E N G I N E E R</text>')
add(f'<text x="{W//2}" y="{sy+22}" text-anchor="middle" font-family="{MONO}" font-size="10" letter-spacing="2" fill="{MUTED}">// payments &#183; billing &#183; distributed systems&#160;&#160;&#9749;</text>')

# ---------- STACK ----------
heading(40, Y_STACK+42, "const", "stack = [")
rows = [
    ("// languages", [("PHP","#777bb4","#fff",False),("TypeScript","#3178c6","#fff",False),("Python","#3776ab","#fff",False)]),
    ("// backend", [("Symfony","#0b0b0b","#fff",True),("Laravel","#ff2d20","#fff",False),("NestJS","#e0234e","#fff",False),("Express","#151515","#fff",False)]),
    ("// data & msg", [("PostgreSQL","#4169e1","#fff",False),("MySQL","#4479a1","#fff",False),("Redis","#dc382d","#fff",False),("RabbitMQ","#ff6600","#fff",False)]),
    ("// infra", [("Docker","#2496ed","#fff",False),("Kubernetes","#326ce5","#fff",False),("AWS","#ff9900","#0a0a14",False),("Grafana","#f46800","#fff",False)]),
]
yy = Y_STACK + 66
for cat, chips in rows:
    add(f'<text x="40" y="{yy+16}" font-family="{MONO}" font-size="11.5" fill="{CYAN}">{esc(cat)}</text>')
    xx = 178
    for txt, bg, fg, st in chips:
        xx = chip(xx, yy, txt, bg, fg, st)
    yy += 40
add(f'<text x="40" y="{yy+14}" font-family="{MONO}" font-size="15" font-weight="700" fill="{AMBER}">]</text>')

# ---------- STATS ----------
heading(40, Y_STATS+42, "git", "--stats")
tw2 = (W-80-3*16)/4; tx = 40
for num, lbl, fire in [(f"{data['total']:,}".replace(",", " "), "CONTRIBUTIONS", True),
                       (data["longest"], "LONGEST STREAK", True),
                       (data["repos"], "REPOSITORIES", False),
                       (data["followers"], "FOLLOWERS", False)]:
    tile(tx, Y_STATS+58, int(tw2), num, lbl, fire)
    tx += tw2 + 16

# --- contribution grid + smart snake ---
gx, gy = 40, Y_STATS + 150
cell, gap = 11, 3; step = cell + gap
NW = len(data["weeks"])
def level(n):
    if n == 0: return EMPTY
    if n <= 3: return "#4d3413"
    if n <= 9: return "#8a5a1e"
    if n <= 20: return "#cc8a34"
    return AMBER
def center(wi, di): return (gx + wi*step + cell/2, gy + di*step + cell/2)

filled = []   # (wi, di, color, cx, cy)
for wi, wk in enumerate(data["weeks"]):
    for di, dd in enumerate(wk["contributionDays"]):
        col = level(dd["contributionCount"])
        px, py = gx + wi*step, gy + di*step
        add(f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="2" fill="{EMPTY}"/>')
        if col != EMPTY:
            cx, cy = center(wi, di)
            filled.append((wi, di, col, cx, cy, px, py))

# nearest-neighbour tour over filled cells (snake weaves through real contributions)
n = len(filled)
cx0 = [f[3] for f in filled]; cy0 = [f[4] for f in filled]
used = [False]*n
cur = min(range(n), key=lambda j: cx0[j] + cy0[j])   # start top-left-most
tour = [cur]; used[cur] = True
for _ in range(n-1):
    bx, by = cx0[cur], cy0[cur]
    best, bd = -1, 1e18
    for j in range(n):
        if used[j]: continue
        d = (bx-cx0[j])**2 + (by-cy0[j])**2
        if d < bd: bd, best = d, j
    tour.append(best); used[best] = True; cur = best

# Snake + eat share ONE percentage timeline: the head visits tour cell k at
# (k/(n-1))% via a transform keyframe, and cell k vanishes at that same % —
# synced by construction, no arc-length/offset-path anchor guesswork. Only
# transform + opacity, which animate reliably on GitHub. Cell fades to reveal
# the empty backdrop and stays empty until the tour restarts.
N_SEG = 6
stepp = 100.0 / max(n-1, 1)
snake_stops, kf, cellrects = [], [], []
for order_pos, j in enumerate(tour):
    wi, di, col, cx, cy, px, py = filled[j]
    pct = round(order_pos * stepp, 3)
    snake_stops.append(f'{pct}%{{transform:translate({cx:.0f}px,{cy:.0f}px)}}')
    p1 = round(min(max(pct, 0.3), 99.7), 3)
    p2 = round(min(p1 + 0.15, 99.85), 3)
    kf.append(f'@keyframes e{order_pos}{{0%,{p1}%{{opacity:1}}{p2}%,100%{{opacity:0}}}}')
    cellrects.append(f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="2" fill="{col}" '
                     f'style="animation:e{order_pos} {DUR}s linear infinite"/>')
kf.append('@keyframes snake{' + ''.join(snake_stops) + '}')
add('<style>' + ''.join(kf) + '</style>')
for r in cellrects:
    add(r)

# snake segments (transform-driven). Head = delay 0 (the timing reference);
# body segments trail by one tour cell each. fill-mode backwards holds them at
# the start cell during their initial delay (no flash at the SVG origin).
seg_dt = DUR / max(n-1, 1)   # seconds per tour cell
for i in range(N_SEG):
    d = i * seg_dt
    anim = f'animation:snake {DUR}s linear infinite backwards;animation-delay:{d:.3f}s'
    if i == 0:
        add(f'<g style="{anim}">'
            f'<rect x="{-cell/2-2:.0f}" y="{-cell/2-2:.0f}" width="{cell+4}" height="{cell+4}" rx="4" fill="{AMBER}" opacity="0.35"/>'
            f'<rect x="{-cell/2:.0f}" y="{-cell/2:.0f}" width="{cell}" height="{cell}" rx="3" fill="#ffe0a8"/></g>')
    else:
        add(f'<g style="{anim}">'
            f'<rect x="{-cell/2:.0f}" y="{-cell/2:.0f}" width="{cell}" height="{cell}" rx="3" fill="{AMBER}" opacity="{round(1-i*0.13,2)}"/></g>')

# ---------- NOW ----------
heading(40, Y_NOW+42, "whoami", "--now")
lines = [
    ("\U0001F6F0", "Shipping billing & payments infra at Orange Labs — usebill"),
    ("\U0001F331", "Going deep on Kubernetes & distributed systems"),
    ("\U0001F30C", "After hours: tinkering with Go & systems programming"),
    ("\U0001F4E1", "Ping me: felipe.dev2148@gmail.com"),
]
yy = Y_NOW + 78
for ic, txt in lines:
    add(f'<text x="44" y="{yy}" font-size="16">{ic}</text>')
    add(f'<text x="76" y="{yy}" font-family="{MONO}" font-size="13.5" fill="{INK}">{esc(txt)}</text>')
    yy += 30

# ---------- FOOTER (animated fuel gauge) ----------
bx, by, bw = 250, Y_FOOT+34, 220
seg = bw/8; filledn = int(0.78*8)
for i in range(8):
    if i < filledn:
        add(f'<rect x="{bx+i*seg+1:.0f}" y="{by}" width="{seg-3:.0f}" height="12" fill="{AMBER}" '
            f'style="animation:fuel 1.8s ease-in-out infinite;animation-delay:-{i*0.18:.2f}s"/>')
    else:
        add(f'<rect x="{bx+i*seg+1:.0f}" y="{by}" width="{seg-3:.0f}" height="12" fill="#23233f"/>')
add(f'<text x="{bx}" y="{by-4}" font-family="{MONO}" font-size="10" letter-spacing="2" fill="{MUTED}">FUEL STATUS: COFFEE</text>')
add(f'<text x="{bx+bw+14}" y="{by+11}" font-family="{MONO}" font-size="11" fill="{AMBER}">78%</text>')
add(f'<text x="{bx+bw+52}" y="{by+11}" font-family="{MONO}" font-size="11" fill="{MUTED}">— safe for launch</text>')
# animated steam over a coffee cup
cup = bx + bw + 190
for k in range(3):
    add(f'<circle cx="{cup+k*5}" cy="{by-2}" r="1.6" fill="{STAR}" '
        f'style="opacity:0;animation:steam 2.2s ease-in-out infinite;animation-delay:-{k*0.5:.1f}s"/>')
add(f'<text x="{cup-4}" y="{by+12}" font-size="14">&#9749;</text>')

add(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
add(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="#2a2a55" stroke-width="2" rx="4"/>')
add('</svg>')

open(OUTP, "w").write("\n".join(s))
print(f"wrote {OUTP} ({len(chr(10).join(s))} bytes) — {n} filled cells, {data['total']} contributions")

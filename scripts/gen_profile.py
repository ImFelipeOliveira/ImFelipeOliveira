#!/usr/bin/env python3
"""Render the ENTIRE GitHub profile as one continuous pixel/space SVG.

Reads real data from assets/data.json (produced by scripts/fetch_data.sh)
and writes assets/profile.svg. Static output -> regenerate via the Action.
"""
import json, random, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "assets", "data.json")
OUTP = os.path.join(ROOT, "assets", "profile.svg")

AMBER, MAGENTA, CYAN, STAR, MUTED = "#f0a742", "#ff5c8a", "#4ad9e4", "#e8ecff", "#8a8ac0"
INK = "#c7c7ee"
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
Y_HERO, Y_STACK, Y_STATS, Y_NOW = 0, 258, 516, 792
Y_FOOT = 982
H = 1052

s = []
def add(x): s.append(x)
def esc(t): return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

# ---- data ----
def load():
    d = json.load(open(DATA))["data"]["user"]
    cal = d["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    days = [dd for w in weeks for dd in w["contributionDays"]]
    lon = c = 0
    for dd in days:
        if dd["contributionCount"] > 0: c += 1; lon = max(lon, c)
        else: c = 0
    return {
        "total": cal["totalContributions"],
        "repos": d["repositories"]["totalCount"],
        "followers": d["followers"]["totalCount"],
        "longest": lon,
        "weeks": weeks,
    }

# ---- shared drawing ----
def heading(x, y, prompt, label):
    add(f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="15" font-weight="700">'
        f'<tspan fill="{AMBER}">&gt; {esc(prompt)}</tspan><tspan fill="{CYAN}"> {esc(label)}</tspan></text>')
    add(f'<line x1="{x+ (len(prompt)+len(label))*9 + 30}" y1="{y-5}" x2="{W-40}" y2="{y-5}" '
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
    col = AMBER if fire else STAR
    add(f'<text x="{x+w/2:.0f}" y="{y+38}" text-anchor="middle" font-family="{MONO}" font-size="26" font-weight="800" fill="{col}">{esc(str(num))}</text>')
    add(f'<text x="{x+w/2:.0f}" y="{y+58}" text-anchor="middle" font-family="{MONO}" font-size="10" letter-spacing="1" fill="{MUTED}">{esc(label)}</text>')

# ==== build ====
data = load()

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'role="img" aria-label="Felipe Oliveira — Backend Engineer profile">')
add('<defs>'
    '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
    '<stop offset="0" stop-color="#0c0c24"/><stop offset="0.5" stop-color="#0a0a1a"/>'
    '<stop offset="1" stop-color="#060615"/></linearGradient>'
    f'<radialGradient id="neb" cx="14%" cy="3%" r="45%">'
    f'<stop offset="0" stop-color="{AMBER}" stop-opacity="0.16"/>'
    f'<stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>'
    f'<radialGradient id="neb2" cx="90%" cy="52%" r="40%">'
    f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0.08"/>'
    f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>'
    '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
    '<rect width="4" height="1" fill="#000" opacity="0.15"/></pattern>'
    '</defs>')
add(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
add(f'<rect width="{W}" height="{H}" fill="url(#neb)"/>')
add(f'<rect width="{W}" height="{H}" fill="url(#neb2)"/>')

# continuous starfield across whole canvas
random.seed(42)
for _ in range(int(W*H/2600)):
    x, y = random.randint(0, W-2), random.randint(0, H-2)
    big = random.random() < 0.14
    sz = 2 if big else 1
    col = AMBER if (big and random.random() < 0.5) else STAR
    base = round(random.uniform(0.18, 0.6), 2)
    dur = round(random.uniform(1.8, 4.2), 2)
    beg = round(random.uniform(0, 4), 2)
    add(f'<rect x="{x}" y="{y}" width="{sz}" height="{sz}" fill="{col}" opacity="{base}">'
        f'<animate attributeName="opacity" values="{base};{round(min(1,base+0.35),2)};{base}" '
        f'dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/></rect>')

# section dividers
for yy in (Y_STACK, Y_STATS, Y_NOW, Y_FOOT):
    add(f'<line x1="0" y1="{yy}" x2="{W}" y2="{yy}" stroke="#1a1a3a" stroke-width="1"/>')

# ---------- HERO ----------
title = "FELIPE OLIVEIRA"
p = 8
tw = (len(title)*6 - 1)*p
x0 = (W - tw)//2
glyphs(title, p, x0, 74, AMBER, shadow=MAGENTA, hi="#ffe0a8")
# rocket
rp, rx, ry = 7, 690, 20
add(f'<g><animateTransform attributeName="transform" type="translate" '
    f'values="{rx} {ry};{rx} {ry-9};{rx} {ry}" dur="3.4s" repeatCount="indefinite" '
    f'calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>')
for r, row in enumerate(ROCKET):
    for c, k in enumerate(row):
        if k in ROCKET_PAL:
            add(f'<rect x="{c*rp}" y="{r*rp}" width="{rp}" height="{rp}" fill="{ROCKET_PAL[k]}"/>')
add(f'<rect x="{2*rp}" y="{9*rp}" width="{rp}" height="{rp}" fill="{AMBER}">'
    f'<animate attributeName="opacity" values="0.2;0.9;0.2" dur="0.4s" repeatCount="indefinite"/>'
    f'<animate attributeName="height" values="{rp};{rp*2};{rp}" dur="0.4s" repeatCount="indefinite"/></rect>')
add('</g>')
sy = 74 + 7*p + 26
add(f'<rect x="{x0}" y="{sy-14}" width="{tw}" height="2" fill="{CYAN}" opacity="0.5"/>')
add(f'<text x="{W//2}" y="{sy+2}" text-anchor="middle" font-family="{MONO}" font-size="13" '
    f'letter-spacing="4" fill="{CYAN}">B A C K E N D&#160;&#160;E N G I N E E R</text>')
add(f'<text x="{W//2}" y="{sy+22}" text-anchor="middle" font-family="{MONO}" font-size="10" '
    f'letter-spacing="2" fill="{MUTED}">// payments &#183; billing &#183; distributed systems&#160;&#160;&#9749;</text>')

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
tw2 = (W - 80 - 3*16) / 4
tx = 40
for num, lbl, fire in [(f"{data['total']:,}".replace(",", " "), "CONTRIBUTIONS", True),
                       (data["longest"], "LONGEST STREAK", True),
                       (data["repos"], "REPOSITORIES", False),
                       (data["followers"], "FOLLOWERS", False)]:
    tile(tx, Y_STATS+58, int(tw2), num, lbl, fire)
    tx += tw2 + 16
# contribution grid (real data)
gx, gy = 40, Y_STATS + 150
cell, gap = 11, 3
def level(n):
    if n == 0: return None
    if n <= 3: return "#4d3413"
    if n <= 9: return "#8a5a1e"
    if n <= 20: return "#cc8a34"
    return AMBER
for wi, wk in enumerate(data["weeks"]):
    for di, dd in enumerate(wk["contributionDays"]):
        col = level(dd["contributionCount"])
        px, py = gx + wi*(cell+gap), gy + di*(cell+gap)
        if col is None:
            add(f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="2" fill="#12122e"/>')
        elif col == AMBER:
            add(f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="2" fill="{AMBER}">'
                f'<animate attributeName="opacity" values="0.6;1;0.6" dur="2.4s" '
                f'begin="{round((wi%7)*0.3,1)}s" repeatCount="indefinite"/></rect>')
        else:
            add(f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="2" fill="{col}"/>')

# ---------- NOW ----------
heading(40, Y_NOW+42, "whoami", "--now")
lines = [
    ("\U0001F6F0", "Shipping billing & payments infra at Orange Labs — usebill"),
    ("\U0001F331", "Going deep on Kubernetes & distributed systems"),
    ("\U0001F30C", "After hours: tinkering with Go & systems programming"),
    ("\U0001F4E1", "Ping me: flipeaz342@gmail.com"),
]
yy = Y_NOW + 78
for ic, txt in lines:
    add(f'<text x="44" y="{yy}" font-size="16">{ic}</text>')
    add(f'<text x="76" y="{yy}" font-family="{MONO}" font-size="13.5" fill="{INK}">{esc(txt)}</text>')
    yy += 30

# ---------- FOOTER ----------
bx, by, bw = 250, Y_FOOT+34, 220
seg = bw/8
for i in range(8):
    col = AMBER if i < int(0.78*8) else "#23233f"
    add(f'<rect x="{bx + i*seg + 1:.0f}" y="{by}" width="{seg-3:.0f}" height="12" fill="{col}"/>')
add(f'<text x="{bx}" y="{by-4}" font-family="{MONO}" font-size="10" letter-spacing="2" fill="{MUTED}">FUEL STATUS: COFFEE</text>')
add(f'<text x="{bx+bw+14}" y="{by+11}" font-family="{MONO}" font-size="11" fill="{AMBER}">78%</text>')
add(f'<text x="{bx+bw+52}" y="{by+11}" font-family="{MONO}" font-size="11" fill="{MUTED}">— safe for launch ☕</text>')

# overlay
add(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
add(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="#2a2a55" stroke-width="2" rx="4"/>')
add('</svg>')

open(OUTP, "w").write("\n".join(s))
print(f"wrote {OUTP} ({len('\n'.join(s))} bytes) — {data['total']} contributions, longest {data['longest']}")

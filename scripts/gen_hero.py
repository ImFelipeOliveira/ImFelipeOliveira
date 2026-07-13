#!/usr/bin/env python3
"""Generate an animated pixel/space hero SVG for the GitHub profile."""
import random, sys

random.seed(42)

W, H = 800, 250
AMBER, MAGENTA, CYAN, STAR = "#f0a742", "#ff5c8a", "#4ad9e4", "#e8ecff"

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
    " ": ["00000","00000","00000","00000","00000","00000","00000"],
}

ROCKET = [
    "..a..",
    ".aaa.",
    ".aca.",
    ".aaa.",
    ".aaa.",
    "b.a.b",
    "f.f.f",
    ".fff.",
    "..f..",
]
ROCKET_PAL = {"a": "#d8dcf0", "c": CYAN, "b": MAGENTA, "f": AMBER}

out = []
def add(s): out.append(s)

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Felipe Oliveira — Backend Engineer">')
add('<defs>')
add(f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="#0c0c24"/><stop offset="0.55" stop-color="#0a0a1a"/>'
    f'<stop offset="1" stop-color="#050510"/></linearGradient>')
add(f'<radialGradient id="neb" cx="14%" cy="6%" r="70%">'
    f'<stop offset="0" stop-color="{AMBER}" stop-opacity="0.16"/>'
    f'<stop offset="0.5" stop-color="{MAGENTA}" stop-opacity="0.05"/>'
    f'<stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>')
add(f'<radialGradient id="neb2" cx="92%" cy="90%" r="60%">'
    f'<stop offset="0" stop-color="{CYAN}" stop-opacity="0.10"/>'
    f'<stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>')
add('<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
    '<rect width="4" height="1" y="0" fill="#000" opacity="0.18"/></pattern>')
add('</defs>')

# background
add(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
add(f'<rect width="{W}" height="{H}" fill="url(#neb)"/>')
add(f'<rect width="{W}" height="{H}" fill="url(#neb2)"/>')

# starfield
for i in range(150):
    x = random.randint(0, W - 3)
    y = random.randint(0, H - 3)
    big = random.random() < 0.16
    s = 2 if big else 1
    col = AMBER if (big and random.random() < 0.5) else STAR
    base = round(random.uniform(0.25, 0.7), 2)
    peak = round(min(1.0, base + random.uniform(0.25, 0.4)), 2)
    dur = round(random.uniform(1.6, 4.2), 2)
    begin = round(random.uniform(0, 3), 2)
    add(f'<rect x="{x}" y="{y}" width="{s}" height="{s}" fill="{col}" opacity="{base}">'
        f'<animate attributeName="opacity" values="{base};{peak};{base}" '
        f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></rect>')

# a couple of shooting stars
for k, (sx, sy, dx, dy, delay) in enumerate([(120, 30, 90, 40, 2.0), (560, 60, -70, 35, 6.5)]):
    add(f'<line x1="{sx}" y1="{sy}" x2="{sx-dx*0.28:.0f}" y2="{sy-dy*0.28:.0f}" '
        f'stroke="{STAR}" stroke-width="1.5" opacity="0">'
        f'<animate attributeName="opacity" values="0;0.9;0" dur="1s" begin="{delay}s" '
        f'repeatCount="indefinite" keyTimes="0;0.3;1"/>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0 0;{dx} {dy}" dur="1s" begin="{delay}s" repeatCount="indefinite"/></line>')

def draw_glyphs(text, p, x0, y0, face, shadow=None, hi=None):
    ox = x0
    for ch in text:
        g = FONT.get(ch, FONT[" "])
        for r in range(7):
            for c in range(5):
                if g[r][c] == "1":
                    px, py = ox + c * p, y0 + r * p
                    if shadow:
                        sh = round(p * 0.34)
                        add(f'<rect x="{px+sh}" y="{py+sh}" width="{p}" height="{p}" fill="{shadow}"/>')
                    add(f'<rect x="{px}" y="{py}" width="{p}" height="{p}" fill="{face}"/>')
                    if hi:
                        add(f'<rect x="{px}" y="{py}" width="{max(1,round(p*0.4))}" height="{max(1,round(p*0.4))}" fill="{hi}"/>')
        ox += 6 * p

# title "FELIPE OLIVEIRA" centered
title = "FELIPE OLIVEIRA"
p = 8
tw = (len(title) * 6 - 1) * p
x0 = (W - tw) // 2
y0 = 92
# group with subtle load-in
add('<g>')
draw_glyphs(title, p, x0, y0, AMBER, shadow=MAGENTA, hi="#ffe0a8")
add(f'<animate attributeName="opacity" values="0;1" dur="0.6s" fill="freeze"/>')
add('</g>')

# rocket sprite, floating, top-right
rp = 7
rx, ry = 690, 26
add(f'<g transform="translate({rx},{ry})">')
add(f'<animateTransform attributeName="transform" type="translate" '
    f'values="{rx} {ry};{rx} {ry-9};{rx} {ry}" dur="3.4s" repeatCount="indefinite" '
    f'calcMode="spline" keyTimes="0;0.5;1" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"/>')
for r, row in enumerate(ROCKET):
    for c, k in enumerate(row):
        if k in ROCKET_PAL:
            add(f'<rect x="{c*rp}" y="{r*rp}" width="{rp}" height="{rp}" fill="{ROCKET_PAL[k]}"/>')
# animated flame flicker (last rows already amber; add a pulsing exhaust)
add(f'<rect x="{2*rp}" y="{9*rp}" width="{rp}" height="{rp}" fill="{AMBER}" opacity="0.9">'
    f'<animate attributeName="opacity" values="0.2;0.9;0.2" dur="0.4s" repeatCount="indefinite"/>'
    f'<animate attributeName="height" values="{rp};{rp*2};{rp}" dur="0.4s" repeatCount="indefinite"/></rect>')
add('</g>')

# subtitle strip under title
sy = y0 + 7 * p + 26
add(f'<rect x="{x0}" y="{sy-14}" width="{tw}" height="2" fill="{CYAN}" opacity="0.5"/>')
add(f'<text x="{W//2}" y="{sy+2}" text-anchor="middle" '
    f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
    f'font-size="13" letter-spacing="4" fill="{CYAN}">B A C K E N D &#160; E N G I N E E R</text>')
add(f'<text x="{W//2}" y="{sy+22}" text-anchor="middle" '
    f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" '
    f'font-size="10" letter-spacing="2" fill="#8a8ac0">// payments &#183; billing &#183; distributed systems &#160; &#9749;</text>')

# scanline overlay
add(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
# pixel border frame
add(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="#2a2a55" stroke-width="2"/>')

add('</svg>')

svg = "\n".join(out)
path = sys.argv[1] if len(sys.argv) > 1 else "hero.svg"
open(path, "w").write(svg)
print(f"wrote {path} ({len(svg)} bytes, {svg.count('<rect')} rects)")

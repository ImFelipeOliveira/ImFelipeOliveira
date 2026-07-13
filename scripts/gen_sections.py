#!/usr/bin/env python3
"""Generate pixel/space themed section SVGs (stack, now, footer) for the profile."""
import random, sys, os

AMBER, MAGENTA, CYAN, STAR, MUTED = "#f0a742", "#ff5c8a", "#4ad9e4", "#e8ecff", "#8a8ac0"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
OUT = sys.argv[1] if len(sys.argv) > 1 else "."

def head(W, H, seed, glow="14%,6%"):
    random.seed(seed)
    gx, gy = glow.split(",")
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    s.append('<defs>'
             '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#0b0b20"/><stop offset="1" stop-color="#070718"/></linearGradient>'
             f'<radialGradient id="g" cx="{gx}" cy="{gy}" r="80%">'
             f'<stop offset="0" stop-color="{AMBER}" stop-opacity="0.10"/>'
             f'<stop offset="1" stop-color="{AMBER}" stop-opacity="0"/></radialGradient>'
             '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
             '<rect width="4" height="1" fill="#000" opacity="0.14"/></pattern>'
             '</defs>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
    s.append(f'<rect width="{W}" height="{H}" fill="url(#g)"/>')
    # starfield
    for _ in range(int(W * H / 4200)):
        x, y = random.randint(0, W - 2), random.randint(0, H - 2)
        big = random.random() < 0.14
        sz = 2 if big else 1
        col = AMBER if (big and random.random() < 0.5) else STAR
        base = round(random.uniform(0.2, 0.6), 2)
        dur = round(random.uniform(1.8, 4.0), 2)
        beg = round(random.uniform(0, 3), 2)
        s.append(f'<rect x="{x}" y="{y}" width="{sz}" height="{sz}" fill="{col}" opacity="{base}">'
                 f'<animate attributeName="opacity" values="{base};{round(min(1,base+0.35),2)};{base}" '
                 f'dur="{dur}s" begin="{beg}s" repeatCount="indefinite"/></rect>')
    return s

def foot(s, W, H):
    s.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/>')
    s.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="#2a2a55" stroke-width="2"/>')
    s.append('</svg>')
    return "\n".join(s)

def heading(s, x, y, prompt, label):
    s.append(f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="15" font-weight="700">'
             f'<tspan fill="{AMBER}">{prompt}</tspan><tspan fill="{CYAN}"> {label}</tspan></text>')

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def chip(s, x, y, text, bg, fg, star=False):
    label = text + ("  ★" if star else "")
    w = 18 + len(label) * 7.3
    h = 23
    s.append(f'<rect x="{x+2}" y="{y+2}" width="{w:.0f}" height="{h}" rx="3" fill="#000" opacity="0.5"/>')
    s.append(f'<rect x="{x}" y="{y}" width="{w:.0f}" height="{h}" rx="3" fill="{bg}" stroke="#000" stroke-opacity="0.3" stroke-width="1.5"/>')
    s.append(f'<text x="{x+w/2:.0f}" y="{y+16}" text-anchor="middle" font-family="{MONO}" '
             f'font-size="12" font-weight="700" fill="{fg}">{esc(label)}</text>')
    return x + w + 9

# ---------------- STACK ----------------
def gen_stack():
    W, H = 820, 262
    s = head(W, H, 7)
    heading(s, 30, 40, "const", "stack = [")
    rows = [
        ("// languages", [("PHP", "#777bb4", "#fff", False), ("TypeScript", "#3178c6", "#fff", False), ("Python", "#3776ab", "#fff", False)]),
        ("// backend", [("Symfony", "#0b0b0b", "#fff", True), ("Laravel", "#ff2d20", "#fff", False), ("NestJS", "#e0234e", "#fff", False), ("Express", "#151515", "#fff", False)]),
        ("// data & msg", [("PostgreSQL", "#4169e1", "#fff", False), ("MySQL", "#4479a1", "#fff", False), ("Redis", "#dc382d", "#fff", False), ("RabbitMQ", "#ff6600", "#fff", False)]),
        ("// infra", [("Docker", "#2496ed", "#fff", False), ("Kubernetes", "#326ce5", "#fff", False), ("AWS", "#ff9900", "#0a0a14", False), ("Grafana", "#f46800", "#fff", False)]),
    ]
    y = 70
    for cat, chips in rows:
        s.append(f'<text x="30" y="{y+16}" font-family="{MONO}" font-size="11.5" fill="{CYAN}">{esc(cat)}</text>')
        x = 168
        for txt, bg, fg, st in chips:
            x = chip(s, x, y, txt, bg, fg, st)
        y += 40
    heading(s, 30, y + 14, "]", "")
    open(os.path.join(OUT, "stack.svg"), "w").write(foot(s, W, H))

# ---------------- NOW ----------------
def gen_now():
    W, H = 820, 210
    s = head(W, H, 13, glow="92%,10%")
    heading(s, 30, 40, "whoami", "--now")
    lines = [
        ("\U0001F6F0", "Shipping billing & payments infra at Orange Labs — usebill"),
        ("\U0001F331", "Going deep on Kubernetes & distributed systems"),
        ("\U0001F30C", "After hours: tinkering with Go & systems programming"),
        ("\U0001F4E1", "Ping me: flipeaz342@gmail.com"),
    ]
    y = 74
    for ic, txt in lines:
        s.append(f'<text x="34" y="{y}" font-size="16">{ic}</text>')
        s.append(f'<text x="66" y="{y}" font-family="{MONO}" font-size="13.5" fill="#c7c7ee">{esc(txt)}</text>')
        y += 30
    open(os.path.join(OUT, "now.svg"), "w").write(foot(s, W, H))

# ---------------- FOOTER ----------------
def gen_footer():
    W, H = 820, 66
    s = head(W, H, 21, glow="50%,50%")
    # fuel bar
    bx, by, bw = 250, 30, 220
    filled = int(0.78 * 8)
    seg = bw / 8
    for i in range(8):
        col = AMBER if i < filled else "#23233f"
        s.append(f'<rect x="{bx + i*seg + 1:.0f}" y="{by}" width="{seg-3:.0f}" height="12" fill="{col}"/>')
    s.append(f'<text x="{bx}" y="{by-4}" font-family="{MONO}" font-size="10" letter-spacing="2" '
             f'fill="{MUTED}" text-anchor="start">FUEL STATUS: COFFEE</text>')
    s.append(f'<text x="{bx+bw+14}" y="{by+11}" font-family="{MONO}" font-size="11" fill="{AMBER}">78%</text>')
    s.append(f'<text x="{bx+bw+52}" y="{by+11}" font-family="{MONO}" font-size="11" fill="{MUTED}">— safe for launch ☕</text>')
    open(os.path.join(OUT, "footer.svg"), "w").write(foot(s, W, H))

gen_stack(); gen_now(); gen_footer()
print("wrote stack.svg, now.svg, footer.svg to", OUT)

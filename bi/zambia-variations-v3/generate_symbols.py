import math, random, sys, os
from PIL import Image, ImageDraw

OUT = sys.argv[1]
GREEN = (43, 218, 90); WHITE = (255, 255, 255); DEEP = (15, 61, 32)

def pack(region, size_at, n_try, gap, rng, seed_dots=None, rmin=0.006):
    """dart-throwing circle packing. region(x,y)->bool, size_at(x,y)->max radius"""
    dots = list(seed_dots or [])
    for _ in range(n_try):
        x, y = rng.uniform(-1, 1), rng.uniform(-1, 1)
        if not region(x, y): continue
        r = size_at(x, y) * rng.uniform(0.35, 1.0) ** 0.8
        if r < rmin: continue
        if all((x-a)**2 + (y-b)**2 >= (r + c + gap)**2 for a, b, c in dots):
            dots.append((x, y, r))
    return dots

def blob(cx, cy, rx, ry, rng, k=4):
    ph = [rng.uniform(0, 6.28) for _ in range(k)]
    am = [rng.uniform(0.04, 0.12) for _ in range(k)]
    def f(x, y):
        dx, dy = (x-cx)/rx, (y-cy)/ry
        t = math.atan2(dy, dx); d = math.hypot(dx, dy)
        lim = 1 + sum(a*math.sin((i+2)*t+p) for i, (a, p) in enumerate(zip(am, ph)))
        return d/lim
    return f  # <1 inside

def trunk(x0, y0, x1, y1, r0, r1, rng, sway=0.03, n=7, jit=0.25):
    pts = []
    for i in range(n):
        t = i/(n-1)
        x = x0+(x1-x0)*t + math.sin(t*3+rng.random())*sway
        y = y0+(y1-y0)*t
        r = (r0+(r1-r0)*t) * rng.uniform(1-jit, 1+jit)
        pts.append((x, y, r))
    return pts

def A(seed):  # 숲의 캔opy: 둥근 수관, 가장자리로 갈수록 작아지는 점
    rng = random.Random(seed)
    f = blob(0, -0.2, 0.62, 0.56, rng)
    tr = trunk(0.01, 0.12, -0.01, 0.9, 0.05, 0.04, rng, n=11)
    def sz(x, y):
        d = f(x, y); return 0.11*(1-d)**0.7 + 0.016
    return pack(lambda x, y: f(x, y) < 1, sz, 40000, 0.008, rng, tr)

def B(seed):  # 바람에 흩날리는 씨앗 점 — 수관이 흩어지며 열림
    rng = random.Random(seed)
    f = blob(-0.03, -0.18, 0.5, 0.5, rng)
    g = blob(0.0, -0.2, 0.9, 0.85, rng)
    tr = trunk(0.0, 0.1, 0.04, 0.9, 0.05, 0.035, rng, sway=0.05, n=11)
    def sz(x, y):
        d = g(x, y); return 0.1*max(0.0, 1.0-d)**0.9 + 0.012
    def reg(x, y):
        d = f(x, y)
        return d < 1 or (g(x, y) < 1 and rng.random() < 0.18*(1.0-g(x, y)) and x > 0)
    return pack(reg, sz, 60000, 0.007, rng, tr)

def C(seed):  # 숲: 큰 나무 한 그루 + 이웃 나무들
    rng = random.Random(seed)
    parts = [(-0.02, -0.18, 0.40, 0.42, 0.10), (-0.58, 0.02, 0.28, 0.30, 0.07), (0.56, 0.06, 0.30, 0.32, 0.075), (0.30, -0.5, 0.2, 0.2, 0.055), (-0.35, -0.48, 0.17, 0.18, 0.05)]
    fs = [(blob(cx, cy, rx, ry, rng), s) for cx, cy, rx, ry, s in parts]
    tr = []
    for (cx, cy, rx, ry, s) in parts[:3]:
        tr += trunk(cx, cy+ry*0.3, cx+0.01, cy+ry*0.9+(0.5 if s > 0.09 else 0.32), s*0.45, s*0.3, rng, sway=0.02, n=8)
    def reg(x, y): return any(f(x, y) < 1 for f, s in fs)
    def sz(x, y):
        best = 0.0
        for f, s in fs:
            d = f(x, y)
            if d < 1: best = max(best, s*(1-d)**0.6+0.012)
        return best
    # keep dots inside canvas
    return pack(reg, sz, 70000, 0.007, rng, tr)

def D(seed):  # 자라나는 나무: 아래는 큰 점, 위로 갈수록 작은 점 (성장)
    rng = random.Random(seed)
    f = blob(0, -0.12, 0.58, 0.72, rng, 3)
    tr = trunk(0.0, 0.2, 0.0, 0.92, 0.06, 0.05, rng, jit=0.15, n=11)
    def sz(x, y):
        d = f(x, y); h = (y+0.85)/1.7
        return (0.035+0.10*h)*(1-d)**0.5+0.012
    return pack(lambda x, y: f(x, y) < 1, sz, 40000, 0.008, rng, tr)

def E(seed):  # 아카시아: 잠비아 사바나의 납작한 우산형 수관
    rng = random.Random(seed)
    f = blob(0, -0.22, 0.78, 0.30, rng, 4)
    tr = trunk(0.02, 0.05, -0.02, 0.9, 0.055, 0.045, rng, sway=0.06, n=9)
    br = trunk(0.02, 0.05, -0.45, -0.24, 0.04, 0.02, rng, n=6) + trunk(0.02, 0.05, 0.48, -0.22, 0.04, 0.02, rng, n=6) + trunk(0.0, 0.05, 0.0, -0.3, 0.045, 0.03, rng, n=4)
    def sz(x, y):
        d = f(x, y); return 0.085*(1-d)**0.6+0.014
    return pack(lambda x, y: f(x, y) < 1, sz, 50000, 0.008, rng, tr+br)

VARS = {'A': (A, 7), 'B': (B, 11), 'C': (C, 5), 'D': (D, 3), 'E': (E, 8)}

def fit(dots):
    xs0 = min(x-r for x, y, r in dots); xs1 = max(x+r for x, y, r in dots)
    ys0 = min(y-r for x, y, r in dots); ys1 = max(y+r for x, y, r in dots)
    cx, cy = (xs0+xs1)/2, (ys0+ys1)/2
    s = max(xs1-xs0, ys1-ys0)
    return [((x-cx)/s, (y-cy)/s, r/s) for x, y, r in dots]

def render(dots, size, fg, bg, scale=0.72, ss=3):
    W = size*ss
    im = Image.new('RGBA', (W, W), bg + (255,) if bg else (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x, y, r in dots:
        px, py, pr = W/2 + x*W*scale, W/2 + y*W*scale, r*W*scale
        d.ellipse([px-pr, py-pr, px+pr, py+pr], fill=fg + (255,))
    return im.resize((size, size), Image.LANCZOS)

def svg(dots, fg):
    s = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-0.5 -0.5 1 1" width="800" height="800">']
    for x, y, r in dots: s.append(f'<circle cx="{x:.4f}" cy="{y:.4f}" r="{r:.4f}" fill="#{fg[0]:02x}{fg[1]:02x}{fg[2]:02x}"/>')
    return '\n'.join(s+['</svg>'])

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    wm = Image.open(sys.argv[2]).convert('RGB').crop((590, 280, 1810, 520))  # wordmark on green
    for k, (fn, seed) in VARS.items():
        dots = fit(fn(seed))
        print(k, len(dots), 'dots, rmax %.3f rmin %.3f' % (max(r for *_, r in dots), min(r for *_, r in dots)))
        render(dots, 1000, WHITE, GREEN).save(f'{OUT}/{k}_green.png')
        render(dots, 1000, GREEN, WHITE).save(f'{OUT}/{k}_white.png')
        render(dots, 1000, GREEN, None).save(f'{OUT}/{k}_mono.png'); render(dots, 1000, WHITE, None).save(f'{OUT}/{k}_monowhite.png')
        open(f'{OUT}/{k}_white.svg', 'w').write(svg(dots, GREEN))
        # horizontal lockup, same wordmark as v2
        sym = render(dots, 806, WHITE, GREEN, scale=0.62)
        lock = Image.new('RGB', (1984, 806), GREEN)
        lock.paste(sym.convert('RGB'), (-40, 0))
        lock.paste(wm, (650, 283))
        lock.save(f'{OUT}/{k}_lockup.png')

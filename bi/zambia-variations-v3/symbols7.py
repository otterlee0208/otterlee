import sys, math, random, os, shutil
sys.path.insert(0, os.path.dirname(__file__))
from symbols import fit, render, svg, GREEN, WHITE
from symbols2 import v2, one
from PIL import Image, ImageDraw
OUT, WMSRC, MEDIA = sys.argv[1], sys.argv[2], sys.argv[3]

def finger_strokes(seed=5):
    """지문: 겹겹이 쌓인 융선(아치)을 끊어진 둥근 선으로, 가운데에서 줄기가 내려옴"""
    rng = random.Random(seed); segs = []
    W = 24
    for k in range(4):
        a, b, p = 215-56*k, 285-64*k, 1.2
        N = 1200; pts = []
        for i in range(N+1):
            t = -0.38 + (math.pi+0.76)*i/N
            c, s = math.cos(t), math.sin(t)
            x = a*math.copysign(abs(c)**(2/p), c); y = 120 - b*math.copysign(abs(s)**(2/p), s)
            wob = 4*math.sin(i/55+k*1.7)                      # 융선의 미세한 흔들림
            pts.append((x+wob*0.6, y+wob))
        L = [0]
        for i in range(1, N+1): L.append(L[-1]+math.hypot(pts[i][0]-pts[i-1][0], pts[i][1]-pts[i-1][1]))
        pos = rng.uniform(0, 20)
        while pos < L[-1]-30:
            ln = rng.uniform(70, 130) if k < 3 else rng.uniform(55, 90)
            end = min(pos+ln, L[-1])
            seg = [pts[i] for i in range(N+1) if pos <= L[i] <= end]
            if len(seg) > 2: segs.append((seg, W*rng.uniform(.9, 1.1)))
            pos = end + rng.uniform(16, 24)
    y = 85                                                    # 줄기
    for i in range(4):
        ln = rng.uniform(46, 70)
        segs.append(([(rng.uniform(-2, 2), y), (rng.uniform(-2, 2), y+ln)], W*(1-.08*i))); y += ln + 20
    return segs

def fit_segs(segs):
    xs = [x for s, w in segs for x, y in s]; ys = [y for s, w in segs for x, y in s]
    x0, x1, y0, y1 = min(xs)-12, max(xs)+12, min(ys)-12, max(ys)+12
    cx, cy, sc = (x0+x1)/2, (y0+y1)/2, max(x1-x0, y1-y0)
    return [([((x-cx)/sc, (y-cy)/sc) for x, y in s], w/sc) for s, w in segs]

def render_s(segs, size, fg, bg, scale=0.72, ss=3):
    Wd = size*ss
    im = Image.new('RGBA', (Wd, Wd), bg+(255,) if bg else (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for s, w in segs:
        P = [(Wd/2+x*Wd*scale, Wd/2+y*Wd*scale) for x, y in s]; r = w*Wd*scale/2
        for (x0, y0), (x1, y1) in zip(P, P[1:]):
            n = max(1, int(math.hypot(x1-x0, y1-y0)/(r*0.25)))
            for i in range(n+1):
                px, py = x0+(x1-x0)*i/n, y0+(y1-y0)*i/n
                d.ellipse([px-r, py-r, px+r, py+r], fill=fg+(255,))
    return im.resize((size, size), Image.LANCZOS)

def svg_s(segs, fg):
    c = '#%02x%02x%02x' % fg
    o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="-0.5 -0.5 1 1" width="800" height="800">']
    for s, w in segs:
        o.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.4f" stroke-linecap="round" stroke-linejoin="round"/>' % (' '.join('%.4f,%.4f' % p for p in s), c, w))
    return '\n'.join(o+['</svg>'])


def whorl_dots(seed=8):
    """3안: 엄지 지문처럼 동글동글한 소용돌이 — 동심 고리 위의 점, 아래로 굵은 줄기"""
    rng = random.Random(seed); out = []
    cy0, p = -50, 1.7
    for k in range(4):
        a, b = 200-56*k, 250-64*k
        ox, oy = rng.uniform(-5, 5)+k*2, -k*9
        N = 1500; pts = []
        for i in range(N):
            t = 2*math.pi*i/N; c, sn = math.cos(t), math.sin(t)
            pts.append((ox+a*math.copysign(abs(c)**(2/p), c), cy0+oy+b*math.copysign(abs(sn)**(2/p), sn)))
        r = 21*(1-0.05*k); last = None; first = None
        for (x, y) in pts:
            rr = r*rng.uniform(.9, 1.1)
            if last is None or math.hypot(x-last[0], y-last[1]) >= 2*r*1.18:
                if first is not None and math.hypot(x-first[0], y-first[1]) < 2*r*1.05: continue
                out.append((x, y, rr)); last = (x, y)
                if first is None: first = (x, y)
    out.append((2, cy0-30, 14))
    y = cy0+250+46
    for i in range(4):
        r = 20*(1-.08*i); out.append((rng.uniform(-2, 2), y, r)); y += r*2+3
    return out

def whorl_spiral(seed=3):
    """3안 대안: 끊김 없이 둥글게 휘감기는 굵은 선(소용돌이) + 줄기"""
    rng = random.Random(seed); pts = []
    turns, N = 3.1, 2600
    for i in range(N+1):
        t = i/N; th = math.pi/2 + t*turns*2*math.pi
        s = 1-0.93*t
        pts.append((190*s*math.cos(th), -60+240*s*math.sin(th)))
    segs = [(pts, 26)]
    sx, sy = pts[0]
    segs.append(([(sx, sy+10), (sx, sy+150)], 26))
    return segs

os.makedirs(OUT, exist_ok=True)
wm = Image.open(WMSRC).convert('RGB').crop((590, 280, 1810, 520))
def lockup(sym, k):
    lock = Image.new('RGB', (1984, 806), GREEN); lock.paste(sym.convert('RGB'), (-40, 0)); lock.paste(wm, (650, 283)); lock.save(f'{OUT}/{k}_lockup.png')

# 1안: 최초안(v2) — 원본 이미지를 그대로 사용
for src, dst in [('image9', '1_green'), ('image11', '1_white'), ('image10', '1_mono'), ('image2', '1_lockup')]:
    shutil.copy(f'{MEDIA}/{src}.png', f'{OUT}/{dst}.png')
d1 = fit(v2()); render(d1, 1000, WHITE, None).save(f'{OUT}/1_monowhite.png')
open(f'{OUT}/1_white.svg', 'w').write(svg(d1, GREEN))
# 2안: 점을 살짝 푼 안
d2 = fit(one(4))
render(d2, 1000, WHITE, GREEN).save(f'{OUT}/2_green.png'); render(d2, 1000, GREEN, WHITE).save(f'{OUT}/2_white.png')
render(d2, 1000, GREEN, None).save(f'{OUT}/2_mono.png'); render(d2, 1000, WHITE, None).save(f'{OUT}/2_monowhite.png')
open(f'{OUT}/2_white.svg', 'w').write(svg(d2, GREEN)); lockup(render(d2, 806, WHITE, GREEN, scale=0.62), '2')
# 3안: 동글동글한 지문 (점 소용돌이)
d3 = fit(whorl_dots())
render(d3, 1000, WHITE, GREEN).save(f'{OUT}/3_green.png'); render(d3, 1000, GREEN, WHITE).save(f'{OUT}/3_white.png')
render(d3, 1000, GREEN, None).save(f'{OUT}/3_mono.png'); render(d3, 1000, WHITE, None).save(f'{OUT}/3_monowhite.png')
open(f'{OUT}/3_white.svg', 'w').write(svg(d3, GREEN)); lockup(render(d3, 806, WHITE, GREEN, scale=0.62), '3')
print('3안 dots', len(d3))
base = Image.new('RGB', (1500, 500), 'white')
for i, k in enumerate(['1','2','3']): base.paste(Image.open(f'{OUT}/{k}_green.png').convert('RGB').resize((500, 500)), (i*500, 0))
base.save(f'{OUT}/contact.png')

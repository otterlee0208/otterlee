import sys, math, random, os
sys.path.insert(0, os.path.dirname(__file__))
from symbols import fit, render, svg, GREEN, WHITE
from symbols2 import overlaps, one
from PIL import Image
OUT = sys.argv[1]

def ridge(px, H, W, rng):
    ph = rng.uniform(0, 6.28)
    def top(x):  # 능선: 정점에서 양쪽으로 완만하게, 살짝 울퉁불퉁
        u = max(0.0, 1-abs(x-px)/W)
        return -H*(u**1.12) + 6*math.sin(x/37+ph)*u
    return top

def mountain_dots(tops, base_y, seed, xr, rmax_base=40, rmin=9, gap=6, tries=60000):
    rng = random.Random(seed); d = []
    H = max(-t(px) for t, px in tops)
    for _ in range(tries):
        x = rng.uniform(*xr); y = rng.uniform(-H, base_y)
        yt = min(t(x) for t, _ in tops)           # 능선(가장 높은 선)
        if y < yt + 8 or y > base_y: continue
        frac = (base_y-y)/H                       # 0=바닥 1=꼭대기
        r = rng.uniform(rmin, rmax_base*(1-0.55*frac)) 
        r = min(r, (y-yt)*0.9)                    # 능선 밖으로 나가지 않게
        if r < rmin: continue
        if not overlaps(d, x, y, r, gap): d.append((x, y, r))
    return d

def two(seed=11):   # 2안: 숲/산 한 개 — 능선이 약간 비대칭
    rng = random.Random(seed)
    return mountain_dots([(ridge(10, 420, 330, rng), 10)], 0, seed, (-350, 350))

def three(seed=21): # 3안: 산 두 개
    rng = random.Random(seed)
    t1, t2 = ridge(-110, 400, 300, rng), ridge(190, 270, 230, rng)
    return mountain_dots([(t1, -110), (t2, 190)], 0, seed, (-420, 430))

def finger(seed=5):  # 4안: 지문 — 나무 모양으로 겹겹이 쌓인 능선(아치) + 가운데 줄기
    rng = random.Random(seed); out = []
    for k in range(3):
        a, b, p = 205-62*k, 270-70*k, 1.2
        pts = []
        N = 3000
        for i in range(N+1):
            t = -0.35 + (math.pi+0.70)*i/N
            c, s = math.cos(t), math.sin(t)
            pts.append((a*math.copysign(abs(c)**(2/p), c), 120 - b*math.copysign(abs(s)**(2/p), s)))
        last = None; rp = None; 
        for (x, y) in pts:
            r = (17 - 1.0*k)*rng.uniform(.86, 1.14)
            if last is None or math.hypot(x-last[0], y-last[1]) >= (r+rp)*1.3:
                q = (x+rng.uniform(-2,2), y+rng.uniform(-2,2), r)
                if not overlaps(out, *q, 1): out.append(q); last = (x, y); rp = r
    # 줄기: 가운데 능선이 아래로 이어짐
    y = 70; r0 = 16
    for i in range(7):
        r = r0*(1-.1*i)*rng.uniform(.92,1.08)
        q = (rng.uniform(-3,3), y, r)
        if not overlaps(out, *q, 1): out.append(q); y += r*2+3
    return out

V = {'1': ('1안 그대로', lambda: one(4)), '2': ('숲(산 하나)', two), '3': ('산 두 개', three), '4': ('지문', finger)}
if __name__=='__main__':
    os.makedirs(OUT,exist_ok=True)
    wm=Image.open(sys.argv[2]).convert('RGB').crop((590,280,1810,520))
    for k,(_,fn) in V.items():
        dots=fit(fn()); print(k,len(dots))
        render(dots,1000,WHITE,GREEN).save(f'{OUT}/{k}_green.png')
        render(dots,1000,GREEN,WHITE).save(f'{OUT}/{k}_white.png')
        render(dots,1000,GREEN,None).save(f'{OUT}/{k}_mono.png'); render(dots,1000,WHITE,None).save(f'{OUT}/{k}_monowhite.png')
        open(f'{OUT}/{k}_white.svg','w').write(svg(dots,GREEN))
        sym=render(dots,806,WHITE,GREEN,scale=0.62); lock=Image.new('RGB',(1984,806),GREEN)
        lock.paste(sym.convert('RGB'),(-40,0)); lock.paste(wm,(650,283)); lock.save(f'{OUT}/{k}_lockup.png')
    base=Image.new('RGB',(2000,500),'white')
    for i,k in enumerate(V): base.paste(Image.open(f'{OUT}/{k}_green.png').resize((500,500)),(i*500,0))
    base.save(f'{OUT}/contact.png')

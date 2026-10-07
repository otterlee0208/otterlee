import sys, math, random, os
sys.path.insert(0, os.path.dirname(__file__))
from symbols import fit, render, svg, GREEN, WHITE
from symbols2 import overlaps, one
from PIL import Image
OUT = sys.argv[1]

def tri_rows(n, cx, base_y, r=29, step=None, rng=None, jit=8, smin=.65, smax=1.2, gap=2):
    """삼각형: 맨 위 1개, 아래로 갈수록 한 줄에 1개씩 늘어남 (v2와 같은 간격)"""
    step = step or r*2*0.98
    out = []
    for i in range(n):
        y = base_y - (n-1-i)*step*0.88
        cnt = i+1
        for j in range(cnt):
            x = cx + (j-(cnt-1)/2)*step
            for _ in range(80):
                nx, ny = x+rng.uniform(-jit,jit), y+rng.uniform(-jit,jit); nr = r*rng.uniform(smin,smax)
                if not overlaps(out, nx, ny, nr, gap): out.append((nx,ny,nr)); break
    return out

def two(seed=3):    # 2안: 삼각형 (숲·산)
    rng = random.Random(seed)
    return tri_rows(8, 0, 0, rng=rng)

def three(seed=5):  # 3안: 산 두 개 (큰 산 + 작은 산, 앞에 겹침)
    rng = random.Random(seed)
    big = tri_rows(8, -70, 0, r=29, rng=rng)
    out = list(big)
    small = tri_rows(5, 215, 0, r=29, rng=rng)
    return out + [p for p in small if not overlaps(out, *p, 1)]

def spiral(seed=2):  # 4안: 1안의 잎 모양 안에서 지문처럼 휘감는 점 (바깥 끝이 줄기로 이어짐)
    rng = random.Random(seed)
    cx, cy, a, h, p = 0, -85, 195, 235, 1.12
    def pt(s, th):
        c, sn = math.cos(th), math.sin(th)
        return (cx + a*s*math.copysign(abs(c)**(2/p), c), cy + h*s*math.copysign(abs(sn)**(2/p), sn))
    turns, s0, s1 = 3.4, 1.0, 0.14
    N = 6000; pts = []
    for i in range(N+1):
        t = i/N; th = math.pi/2 + t*turns*2*math.pi*(-1)   # 아래(줄기)에서 시작해 반시계로 감김
        s = s0 + (s1-s0)*t
        pts.append(pt(s, th))
    out = []; last = None; r_prev = None
    for k, (x, y) in enumerate(pts):
        t = k/N
        r = (23 - 11*t)*rng.uniform(.88, 1.12)
        if last is None or math.hypot(x-last[0], y-last[1]) >= (r + r_prev)*1.1:
            out.append((x+rng.uniform(-2.5,2.5), y+rng.uniform(-2.5,2.5), r)); last = (x, y); r_prev = r
    sx, sy, sr = out[0]
    stem = []; py, pr = sy, sr
    for i in range(4):
        nr = 15*(1-.1*i); ny = py + (pr+nr)*1.0
        stem.append((sx+rng.uniform(-2,2), ny, nr)); py, pr = ny, nr
    return out + [q for q in stem if not overlaps(out, *q, 1)]

V = {'1': ('1안 그대로', lambda: one(4)), '2': ('삼각형(숲)', two), '3': ('산 두 개', three), '4': ('지문', spiral)}
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

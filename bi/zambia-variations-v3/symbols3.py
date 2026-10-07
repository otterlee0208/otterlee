import sys, math, random, os
sys.path.insert(0, os.path.dirname(__file__))
from symbols import fit, render, svg, GREEN, WHITE
from symbols2 import v2, overlaps, ROWS, one
from PIL import Image
OUT = sys.argv[1]

def loosen(seed, jit=9, smin=0.62, smax=1.22, lean=0, trunk_taper=False, drop=0, extra=(), gap=2, seq=True):
    rng = random.Random(seed); d = []
    base = v2()
    crown, trunk = base[:22], base[22:]
    drop_idx = set(rng.sample([i for i,(x,y,r) in enumerate(crown) if abs(x)>100 or y<-150], drop)) if drop else set()
    for i,(x,y,r) in enumerate(crown):
        if i in drop_idx: continue
        for _ in range(80):
            nx,ny=x+rng.uniform(-jit,jit),y+rng.uniform(-jit,jit); nr=r*rng.uniform(smin,smax)
            if not overlaps(d,nx,ny,nr,gap): d.append((nx,ny,nr)); break
    if seq:
        py, pr = None, None
        for k,(x,y,r) in enumerate(trunk):
            nr = r*(1-0.17*k)*rng.uniform(.9,1.1) if trunk_taper else r*rng.uniform(max(smin,0.7),min(smax,1.15))
            ny = y if py is None else py + (pr+nr)*0.97
            d.append((x+lean*k+rng.uniform(-jit/3,jit/3), ny, nr)); py, pr = ny, nr
    else:
        for k,(x,y,r) in enumerate(trunk):
            d.append((x+rng.uniform(-jit/3,jit/3), y+rng.uniform(-jit/2,jit/2), r*rng.uniform(smin,smax)))
    for e in extra:
        if not overlaps(d,*e,3): d.append(e)
    return d

V = {
 'a': ('1안 그대로', lambda: one(4)),
 'b': ('크기 차이 크게', lambda: loosen(4, smin=0.45, smax=1.4)),
 'c': ('위치 더 흩트리기', lambda: loosen(4, jit=15, smin=0.7, smax=1.15)),
 'd': ('줄기를 자유롭게', lambda: loosen(4, trunk_taper=True, lean=4)),
 'e': ('가장자리 비우기', lambda: loosen(7, jit=10, smin=0.55, smax=1.3, drop=3, extra=[(-215,-60,9),(240,-95,7)])),
}
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
    base=Image.new('RGB',(3000,500),'white')
    ims=[Image.open('in/x/ppt/media/image9.png').resize((500,500))]+[Image.open(f'{OUT}/{k}_green.png').resize((500,500)) for k in V]
    for i,m in enumerate(ims): base.paste(m,(i*500,0))
    base.save(f'{OUT}/contact.png')

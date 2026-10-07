import sys, math, random, os
sys.path.insert(0, os.path.dirname(__file__))
from symbols import fit, render, svg, GREEN, WHITE
from PIL import Image
OUT = sys.argv[1]
# v2 격자 (px, 중심 410,410)
ROWS = [(182,[410]),(230,[367,453]),(280,[325,410,495]),(335,[283,367,453,537]),(390,[245,325,410,495,573]),(445,[283,367,453,537]),(500,[325,410,495])]
def v2(): 
    d=[(x-410,y-410,29) for y,xs in ROWS for x in xs]
    d+=[(0,y-410,29) for y in (500,545,595,640)]
    return d
def overlaps(d,x,y,r,gap):
    return any((x-a)**2+(y-b)**2 < (r+c+gap)**2 for a,b,c in d)

def one(seed):  # 1. 살짝 풀기: v2 그대로, 점 위치·크기만 조금씩
    rng=random.Random(seed); d=[]
    for x,y,r in v2():
        for _ in range(50):
            nx,ny=x+rng.uniform(-9,9),y+rng.uniform(-9,9); nr=r*rng.uniform(0.62,1.22)
            if not overlaps(d,nx,ny,nr,2): d.append((nx,ny,nr)); break
    return d

def crown_in(x,y,cx=0,cy=-85,w=190,h=230,rng=None):  # 잎 모양 수관 (v2보다 약간 둥글게)
    dx,dy=(x-cx)/w,(y-cy)/h
    return abs(dx)**1.25+abs(dy)**1.25<1

def two(seed):  # 2. 크기 다양: 같은 실루엣 안에 큰 점~작은 점 (점 수 ≈ 45)
    rng=random.Random(seed); d=[]
    for _ in range(30000):
        x,y=rng.uniform(-200,200),rng.uniform(-330,130)
        if not crown_in(x,y): continue
        r=rng.choice([14,18,22,26,32,38,44])*rng.uniform(0.9,1.1)
        if (x*x+(y+85)**2)**.5 > 150 and r>26: continue   # 가장자리는 작은 점
        if not overlaps(d,x,y,r,7): d.append((x,y,r))
    tr=[(2,150,22),(-5,200,17),(4,246,13),(-2,288,9)]
    return d+tr

def three(seed):  # 3. 흩날림: 2의 수관 + 가장자리에서 떨어져 나가는 점
    rng=random.Random(seed); d=two(seed)[:-4]
    d=[(x,y,r) for x,y,r in d]
    tr=[(2,150,22),(-5,200,17),(4,246,13),(-2,288,9)]
    d+=tr
    for x,y,r in sorted(d,key=lambda t:-t[0])[:0]: pass
    extra=[(215,-30,11),(250,10,8),(236,70,6),(280,-65,5),(-225,40,9),(-258,85,6),(180,-175,7),(298,35,4)]
    for e in extra:
        if not overlaps(d,*e,4): d.append(e)
    return d

def tree_dots(rng,cx,cy,w,h,scale,n_trunk=3):
    d=[]
    for _ in range(25000):
        x,y=rng.uniform(cx-w,cx+w),rng.uniform(cy-h,cy+h)
        if not crown_in(x,y,cx,cy,w,h): continue
        r=rng.choice([20,24,28,34])*scale*rng.uniform(.9,1.1)
        if not overlaps(d,x,y,r,4*scale): d.append((x,y,r))
    for i in range(n_trunk):
        d.append((cx+rng.uniform(-3,3),cy+h*0.6+i*38*scale*1.2,(20-4*i)*scale))
    return d

def four(seed):  # 4. 숲: v2 실루엣의 나무 세 그루 (큰 것 하나 + 작은 둘), 서로 떨어져 있음
    out=[]
    for (ox,oy,sc,sd) in [(0,0,1.0,4),(-330,150,0.55,9),(320,110,0.65,12)]:
        for x,y,r in one(sd): out.append((ox+x*sc,oy+y*sc,r*sc))
    return out

V={'1':(one,4),'2':(two,3),'3':(three,3),'4':(four,6)}
if __name__=='__main__':
    os.makedirs(OUT,exist_ok=True)
    wm=Image.open(sys.argv[2]).convert('RGB').crop((590,280,1810,520))
    for k,(fn,seed) in V.items():
        dots=fit(fn(seed)); print(k,len(dots))
        render(dots,1000,WHITE,GREEN).save(f'{OUT}/{k}_green.png')
        render(dots,1000,GREEN,WHITE).save(f'{OUT}/{k}_white.png')
        render(dots,1000,GREEN,None).save(f'{OUT}/{k}_mono.png'); render(dots,1000,WHITE,None).save(f'{OUT}/{k}_monowhite.png')
        open(f'{OUT}/{k}_white.svg','w').write(svg(dots,GREEN))
        sym=render(dots,806,WHITE,GREEN,scale=0.62); lock=Image.new('RGB',(1984,806),GREEN)
        lock.paste(sym.convert('RGB'),(-40,0)); lock.paste(wm,(650,283)); lock.save(f'{OUT}/{k}_lockup.png')
    base=Image.new('RGB',(2500,500),'white')
    ims=[Image.open('in/x/ppt/media/image9.png').resize((500,500))]+[Image.open(f'{OUT}/{k}_green.png').resize((500,500)) for k in V]
    for i,m in enumerate(ims): base.paste(m,(i*500,0))
    base.save(f'{OUT}/contact.png')

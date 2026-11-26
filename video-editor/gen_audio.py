import numpy as np, wave, sys, os
SR=44100; O=sys.argv[1]; rng=np.random.default_rng(1)
def save(n,x):
    x=np.asarray(x,np.float32); x=x/ (np.abs(x).max()+1e-9)*0.9
    st=np.stack([x,x],-1) if x.ndim==1 else x
    w=wave.open(os.path.join(O,n+'.wav'),'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
t=lambda d: np.arange(int(SR*d))/SR
def lp(x,a):  # one-pole lowpass with varying coef
    y=np.zeros_like(x); s=0.
    a=np.broadcast_to(a,x.shape)
    for i in range(len(x)): s+= a[i]*(x[i]-s); y[i]=s
    return y
# whoosh
d=0.45; tt=t(d); n=rng.standard_normal(len(tt))
env=np.sin(np.pi*tt/d)**2; a=0.02+0.35*np.sin(np.pi*tt/d)**3
save('whoosh', lp(n,a)*env)
# pop
tt=t(0.12); f=900*np.exp(-tt*30)+300
save('pop', np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*40))
# ding
tt=t(1.2); x=sum(np.sin(2*np.pi*f*tt)*np.exp(-tt*k) for f,k in [(1760,3),(2637,4),(3520,6),(880,2.5)])
save('ding', x)
# kaching
tt=t(0.9); x=np.zeros(len(tt))
for st,f in [(0,2093),(0.08,3136)]:
    i=int(st*SR); u=tt[:len(tt)-i]; x[i:]+=sum(np.sin(2*np.pi*ff*u)*np.exp(-u*5) for ff in [f,f*1.5,f*2.01])
x[:2000]+=rng.standard_normal(2000)*np.exp(-np.arange(2000)/300)*2
save('kaching', x)
# impact/boom
tt=t(0.9); f=120*np.exp(-tt*4)+40
x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*4)+lp(rng.standard_normal(len(tt)),0.05)*np.exp(-tt*12)*2
save('boom', x)
# boing (comedic)
tt=t(0.6); f=300+120*np.sin(2*np.pi*14*tt)*np.exp(-tt*3)+200*np.exp(-tt*6)
save('boing', np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*4))
# riser
d=1.0; tt=t(d); f=200+1400*(tt/d)**2
x=np.sin(2*np.pi*np.cumsum(f)/SR)*0.4+lp(rng.standard_normal(len(tt)),0.05+0.4*tt/d)
save('riser', x*(tt/d)**1.5)
# record scratch / "huh" stop
tt=t(0.35); f=600+500*np.sin(2*np.pi*6*tt)
x=lp(rng.standard_normal(len(tt)),0.3)*np.sin(2*np.pi*np.cumsum(f)/SR)
save('scratch', x*np.exp(-tt*5))
# click/type
tt=t(0.04); save('click', rng.standard_normal(len(tt))*np.exp(-tt*200))
# sad trombone-ish (wah wah)
x=[]
for f0,d in [(392,0.35),(370,0.35),(349,0.35),(330,0.9)]:
    tt=t(d); f=f0*(1+0.01*np.sin(2*np.pi*5*tt)*(tt>0.3))
    ph=2*np.pi*np.cumsum(f)/SR; v=sum(np.sin(k*ph)/k for k in range(1,7))
    x.append(v*np.minimum(1,tt*30)*np.minimum(1,(d-tt)*10))
save('wahwah', np.concatenate(x))

# ---- background music: chill upbeat loop, 100 BPM
bpm=100; beat=60/bpm; bars=8; L=int(SR*beat*4*bars)
mus=np.zeros((L,2))
def add(x,pos,pan=0.):
    i=int(pos*SR); x=x[:max(0,L-i)]
    mus[i:i+len(x),0]+=x*(1-pan); mus[i:i+len(x),1]+=x*(1+pan)
kick=(lambda tt: np.sin(2*np.pi*np.cumsum(50+120*np.exp(-tt*25))/SR)*np.exp(-tt*7))(t(0.4))
hat=lp(rng.standard_normal(int(SR*0.05)),0.9)*np.exp(-t(0.05)*80); hat=hat-lp(hat,0.3)
snare=(lp(rng.standard_normal(int(SR*0.25)),0.6)*np.exp(-t(0.25)*18)+np.sin(2*np.pi*190*t(0.25))*np.exp(-t(0.25)*25))*0.7
# chords (Am - F - C - G) in Hz roots
prog=[[220,261.6,329.6],[174.6,220,261.6],[130.8,164.8,196,],[196,246.9,293.7]]
bassn=[110,87.3,65.4,98]
for b in range(bars):
    ch=prog[b%4]; t0=b*beat*4
    for k in range(4):
        add(kick*0.9,t0+k*beat) if k in (0,2) else add(snare*0.5,t0+k*beat)
        for h in (0,0.5): add(hat*0.25,t0+(k+h)*beat,0.3)
    if b%2==1: add(kick*0.6,t0+3.5*beat)
    tt=t(beat*4)
    pad=sum(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*f*2.003*tt) for f in ch)*0.12*np.minimum(1,tt*4)*np.minimum(1,(beat*4-tt)*4)
    add(pad,t0,-0.2)
    # pluck arp
    for k in range(8):
        f=ch[k%3]*2*(2 if k in (3,7) else 1); u=t(beat*0.5)
        add(np.sin(2*np.pi*f*u)*np.exp(-u*9)*0.18,t0+k*beat*0.5,0.25*(-1)**k)
    for k in range(4):
        u=t(beat*0.9); f=bassn[b%4]
        add((np.sin(2*np.pi*f*u)+0.3*np.sin(4*np.pi*f*u))*np.exp(-u*2)*0.35,t0+k*beat)
mus/=np.abs(mus).max()*1.1
w=wave.open(os.path.join(O,'music.wav'),'w'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mus*32767).astype(np.int16).tobytes()); w.close()
print('ok')

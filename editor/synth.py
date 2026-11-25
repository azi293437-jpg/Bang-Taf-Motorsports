# Original royalty-free music bed + SFX, synthesized from scratch.
import numpy as np, wave, sys
SR=48000; out=sys.argv[1]
def save(name,x):
    x=np.clip(x,-1,1); st=np.stack([x,x],1) if x.ndim==1 else x
    w=wave.open(f"{out}/{name}.wav","w");w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR)
    w.writeframes((st*32767).astype(np.int16).tobytes());w.close()
rng=np.random.default_rng(7)
def env(n,a,d):
    t=np.arange(n)/SR; return np.minimum(t/a,1)*np.exp(-t/d)
# ---------- music: 118 BPM, Am-F-C-G ----------
BPM=118; beat=60/BPM; dur=40.0; N=int(dur*SR); mus=np.zeros(N)
def add(buf,x,t):
    i=int(t*SR); j=min(len(buf),i+len(x))
    if j>i: buf[i:j]+=x[:j-i]
def kick():
    n=int(.35*SR);t=np.arange(n)/SR;f=50+90*np.exp(-t*35)
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*9)*0.9
def hat(o=False):
    n=int((.18 if o else .05)*SR); x=rng.standard_normal(n); x=np.diff(np.r_[0,x]); return x*env(n,.001,.06 if o else .015)*.18
def clap():
    n=int(.25*SR); x=rng.standard_normal(n); x=np.convolve(x,np.ones(8)/8,'same')-np.convolve(x,np.ones(40)/40,'same')
    return x*env(n,.002,.07)*.55
def saw(f,n,det=0):
    t=np.arange(n)/SR; s=0
    for d in (-det,0,det): s=s+2*((t*f*(1+d))%1)-1
    return s/3
def lp(x,a):  # one-pole lowpass
    y=np.empty_like(x); z=0
    for i in range(len(x)): z+=a*(x[i]-z); y[i]=z
    return y
roots={'A':55.0,'F':43.65,'C':65.41,'G':49.0}
chords={'A':[220,261.63,329.63],'F':[174.61,220,261.63],'C':[261.63,329.63,392],'G':[196,246.94,293.66]}
prog=['A','F','C','G']; bar=4*beat
nb=int(dur/bar)+1
for b in range(nb):
    t0=b*bar; ch=prog[b%4]
    for k in range(4):
        tb=t0+k*beat
        add(mus,kick(),tb)
        if k in (1,3): add(mus,clap(),tb)
        add(mus,hat(),tb+beat/2); add(mus,hat(),tb+beat/4*3) if k%2 else None
        add(mus,hat(True) if k==3 else hat(),tb+beat/2)
    # offbeat bass 8ths
    for e in range(8):
        n=int(beat/2*SR*.9); f=roots[ch]*(2 if e%2 else 1)
        x=lp(saw(f,n),.08)*env(n,.005,.12)*.5; add(mus,x,t0+e*beat/2)
    # chord stabs on the "and"
    for e in (1,3,5,6):
        n=int(.22*SR); x=sum(saw(f,n,.006) for f in chords[ch]); x=lp(x,.15)*env(n,.004,.09)*.22; add(mus,x,t0+e*beat/2)
mus=np.tanh(mus*1.2)*0.6
# stereo widen hats a little via short delay
L=mus; R=np.r_[np.zeros(240),mus[:-240]]*0.9+mus*0.1
save("music",np.stack([L,R],1))
# ---------- SFX ----------
def whoosh():
    n=int(.45*SR);t=np.arange(n)/SR;x=rng.standard_normal(n)
    cut=np.linspace(.02,.35,n)**1.5; y=np.empty(n);z=0
    for i in range(n): z+=cut[i]*(x[i]-z); y[i]=z
    e=np.sin(np.pi*t/t[-1])**2; return y*e*1.6
def pop():
    n=int(.12*SR);t=np.arange(n)/SR;f=900*np.exp(-t*25)+300
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*40)*.7
def impact():
    n=int(1.2*SR);t=np.arange(n)/SR;f=38+120*np.exp(-t*12)
    b=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3)
    nz=rng.standard_normal(n)*np.exp(-t*18)*.4
    return np.tanh((b+nz)*1.5)*.8
def ding():
    n=int(.7*SR);t=np.arange(n)/SR
    return (np.sin(2*np.pi*1318.5*t)+.5*np.sin(2*np.pi*2637*t)+.3*np.sin(2*np.pi*1975.5*t))*np.exp(-t*6)*.35
def riser():
    n=int(1.4*SR);t=np.arange(n)/SR;f=200+1400*(t/t[-1])**2
    x=saw(1,1)  # dummy
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*.15+lp(rng.standard_normal(n),.3)*.2
    return s*(t/t[-1])**2
save("whoosh",whoosh());save("pop",pop());save("impact",impact());save("ding",ding());save("riser",riser())

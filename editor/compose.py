import subprocess, sys, math, numpy as np
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S=sys.argv[1]; W,H,FPS=1080,1920,30
BASE=f"{S}/build/base.mp4"; OUT=f"{S}/build/video_only.mp4"
ANTON=f"{S}/fonts/Anton-Regular.ttf.ttf"; MONT=f"{S}/fonts/Montserrat.ttf"
EMOJI="/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
import glob; e=glob.glob("/usr/share/fonts/**/NotoColorEmoji.ttf",recursive=True); EMOJI=e[0] if e else None
YEL=(255,210,31); BLUE=(30,110,255); RED=(230,30,45); WHITE=(255,255,255); BLACK=(0,0,0)
CUTS=[8.40,13.66,21.66,26.56,31.51]; END=37.53

# ---------- easing ----------
def clamp(x,a=0,b=1): return max(a,min(b,x))
def eo(x): x=clamp(x); return 1-(1-x)**3
def eob(x): x=clamp(x); c=1.9; return 1+(c+1)*(x-1)**3+c*(x-1)**2
def prog(t,a,d): return clamp((t-a)/d)
def inout(t,a,b,fi=.25,fo=.25):  # alpha envelope
    if t<a or t>b: return 0
    return min(eo((t-a)/fi), eo((b-t)/fo))

# ---------- fonts / text ----------
@lru_cache(None)
def font(path,size,var=None):
    f=ImageFont.truetype(path,size)
    if var:
        try: f.set_variation_by_name(var)
        except Exception: pass
    return f
@lru_cache(None)
def text_img(txt,path,size,fill=WHITE,stroke=0,sfill=BLACK,var=None,shadow=True,track=0):
    f=font(path,size,var)
    if track:
        ims=[text_img(c,path,size,fill,stroke,sfill,var,shadow) for c in txt]
        w=sum(i.width for i in ims)+track*(len(ims)-1); h=max(i.height for i in ims)
        out=Image.new("RGBA",(w,h)); x=0
        for i in ims: out.alpha_composite(i,(x,0)); x+=i.width+track
        return out
    b=f.getbbox(txt,stroke_width=stroke); pad=24
    w=b[2]-b[0]+pad*2; h=b[3]-b[1]+pad*2
    im=Image.new("RGBA",(w,h)); d=ImageDraw.Draw(im)
    if shadow:
        sh=Image.new("RGBA",(w,h)); ImageDraw.Draw(sh).text((pad-b[0]+5,pad-b[1]+7),txt,font=f,fill=(0,0,0,150),stroke_width=stroke,stroke_fill=(0,0,0,150))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d.text((pad-b[0],pad-b[1]),txt,font=f,fill=fill,stroke_width=stroke,stroke_fill=sfill)
    return im
@lru_cache(None)
def emoji(ch,size):
    f=ImageFont.truetype(EMOJI,109); im=Image.new("RGBA",(160,160)); ImageDraw.Draw(im).text((10,10),ch,font=f,embedded_color=True)
    im=im.crop(im.getbbox()); r=size/im.height; return im.resize((int(im.width*r),size),Image.LANCZOS)

def place(cv,im,cx,cy,scale=1.0,alpha=1.0,rot=0):
    if alpha<=0.01 or scale<=0.01: return
    if scale!=1: im=im.resize((max(1,int(im.width*scale)),max(1,int(im.height*scale))),Image.BILINEAR)
    if rot: im=im.rotate(rot,resample=Image.BICUBIC,expand=True)
    if alpha<1:
        a=im.getchannel("A").point(lambda v:int(v*alpha)); im=im.copy(); im.putalpha(a)
    cv.alpha_composite(im,(int(cx-im.width/2),int(cy-im.height/2))) if 0<=int(cx-im.width/2) and 0<=int(cy-im.height/2) and int(cx-im.width/2)+im.width<=W and int(cy-im.height/2)+im.height<=H else paste_clip(cv,im,int(cx-im.width/2),int(cy-im.height/2))
def paste_clip(cv,im,x,y):
    x0,y0=max(0,x),max(0,y); x1,y1=min(W,x+im.width),min(H,y+im.height)
    if x1<=x0 or y1<=y0: return
    cv.alpha_composite(im.crop((x0-x,y0-y,x1-x,y1-y)),(x0,y0))

@lru_cache(None)
def rbox(w,h,r,fill,outline=None,ow=0,shadow=True):
    pad=30; im=Image.new("RGBA",(w+pad*2,h+pad*2))
    if shadow:
        sh=Image.new("RGBA",im.size); ImageDraw.Draw(sh).rounded_rectangle((pad+4,pad+10,pad+w+4,pad+h+10),r,fill=(0,0,0,140))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    ImageDraw.Draw(im).rounded_rectangle((pad,pad,pad+w,pad+h),r,fill=fill,outline=outline,width=ow)
    return im
def fit(im,mw):
    return im if im.width<=mw else im.resize((mw,int(im.height*mw/im.width)),Image.LANCZOS)
def compose(base,items):  # items: (img, x, y) relative to base top-left incl. its pad
    out=base.copy()
    for im,x,y in items: out.alpha_composite(im,(int(x),int(y)))
    return out

# ---------- assets ----------
logo=Image.open(f"{S}/dl2/logo.png").convert("RGBA")
def rounded(im,r):
    m=Image.new("L",im.size,0); ImageDraw.Draw(m).rounded_rectangle((0,0,im.width-1,im.height-1),r,fill=255)
    o=im.copy(); o.putalpha(m); return o
logo_r=rounded(logo,26)
def logo_at(w):  # keep aspect ratio
    return logo_r.resize((w,int(logo_r.height*w/logo_r.width)),Image.LANCZOS)
LOGO_SMALL=logo_at(190)
LOGO_BIG=logo_at(560)
# subtle readability gradients
grad=Image.new("RGBA",(W,H)); gd=np.zeros((H,W,4),np.uint8)
y=np.arange(H)[:,None]
top=np.clip(1-y/520,0,1)**1.6*120; bot=np.clip((y-1250)/670,0,1)**1.4*150
gd[...,3]=(top+bot).astype(np.uint8).repeat(W,1); GRAD=Image.fromarray(gd,"RGBA")

def bolt(size,fill=YEL):
    im=Image.new("RGBA",(size,size)); s=size/100
    ImageDraw.Draw(im).polygon([(58*s,2*s),(18*s,56*s),(46*s,56*s),(38*s,98*s),(82*s,40*s),(54*s,40*s)],fill=fill,outline=BLACK,width=max(2,int(3*s))); return im
@lru_cache(None)
def check(size):
    im=Image.new("RGBA",(size,size)); d=ImageDraw.Draw(im)
    d.ellipse((0,0,size-1,size-1),fill=(25,190,90)); s=size/100
    d.line([(26*s,52*s),(44*s,70*s),(76*s,32*s)],fill=WHITE,width=int(11*s),joint="curve"); return im
@lru_cache(None)
def arrow_down(w,h,fill=YEL):
    im=Image.new("RGBA",(w,h)); d=ImageDraw.Draw(im)
    d.polygon([(w*.32,0),(w*.68,0),(w*.68,h*.5),(w,h*.5),(w/2,h),(0,h*.5),(w*.32,h*.5)],fill=fill,outline=BLACK,width=5); return im
@lru_cache(None)
def bag(size):
    im=Image.new("RGBA",(size,size)); d=ImageDraw.Draw(im); s=size/100
    d.arc((30*s,4*s,70*s,48*s),180,360,fill=WHITE,width=int(7*s))
    d.rounded_rectangle((14*s,26*s,86*s,96*s),int(10*s),fill=BLUE,outline=WHITE,width=int(5*s))
    d.arc((36*s,36*s,64*s,62*s),0,180,fill=WHITE,width=int(6*s)); return im

# ---------- built components ----------
def chip(txt,bg=YEL,fg=BLACK,size=56):
    t=text_img(txt,MONT,size,fg,var="Black",shadow=False); b=rbox(t.width+20,t.height-10,22,bg)
    return compose(b,[(t,30+10,30-5)])

# subtitles (from transcript word timings of IMG_0911, timeline == source in segment A)
SUBS=[ (0.00,0.74,[("ASSALAMUALAIKUM",0.00,0.56,0),("GUYS!",0.56,0.74,0)]),
       (0.90,1.76,[("MANA",0.94,1.22,0),("KORANG",1.22,1.58,0),("NAK",1.58,1.76,0)]),
       (1.76,3.00,[("DAPATKAN",1.76,2.30,0),("KERETA",2.30,3.00,0)]),
       (3.00,4.02,[("e.MAS 5",3.00,4.02,1)]),
       (4.02,5.30,[("YANG",4.02,4.50,0),("READY",4.50,4.86,1),("STOCK,",4.86,5.06,1),("GUYS?",5.06,5.30,0)]),
       (5.30,6.52,[("SO,",5.30,5.60,0),("ADA",5.60,6.20,0),("KITA",6.20,6.52,0)]),
       (6.52,6.98,[("KAT",6.52,6.72,0),("SINI",6.72,6.98,1)]),
       (6.98,8.40,[("READY",6.98,7.46,1),("STOCK!",7.46,8.26,1)]) ]
SUB_SIZE=84; SUB_Y=1440
def draw_subs(cv,t):
    for a,b,words in SUBS:
        if not (a<=t<b): continue
        k=eob(prog(t,a,0.14)); sc=0.8+0.2*k
        imgs=[]
        for w,ws,we,kw in words:
            active= ws<=t<we+0.05
            col=BLACK if active else (YEL if kw else WHITE)
            ti=text_img(w,MONT,SUB_SIZE,col,stroke=0 if active else 9,var="Black",shadow=not active)
            if active:
                bx=rbox(ti.width-24,ti.height-30,18,YEL if not kw else (255,255,255),shadow=False)
                ti=compose(bx,[(ti,30-12,30-15)])
            imgs.append((ti,active))
        gap=4; tw=sum(i.width for i,_ in imgs)+gap*(len(imgs)-1)
        line=Image.new("RGBA",(tw,max(i.height for i,_ in imgs))); x=0
        for i,act in imgs: line.alpha_composite(i,(x,(line.height-i.height)//2)); x+=i.width+gap
        s=sc*min(1,1000/line.width)
        place(cv,line,W/2,SUB_Y,s,clamp(k*1.5))

# ---------- scene overlays ----------
HOOK_A=text_img("e.MAS 5",ANTON,250,YEL,stroke=10)
HOOK_P=text_img("PROTON",MONT,64,WHITE,stroke=6,var="Black",track=-30)
HOOK_R=chip("READY STOCK!",RED,WHITE,84)
PIN=emoji("📍",120) if EMOJI else None
KATSINI=text_img("KAT SINI!",ANTON,150,WHITE,stroke=9)
STAMP=None
def make_stamp():
    t=text_img("READY STOCK",ANTON,120,RED,shadow=False)
    w,h=t.width+30,t.height+10; im=Image.new("RGBA",(w+40,h+40)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((20,20,20+w,20+h),18,fill=(255,255,255,235),outline=RED,width=12)
    im.alpha_composite(t,(20+15,20+5)); return im
STAMP=make_stamp()

def ev_card():
    w,h=900,330; b=rbox(w,h,36,(12,14,20,225),outline=YEL,ow=5)
    t1=fit(text_img("PROTON e.MAS 5",ANTON,120,WHITE,shadow=False),660)
    t2=fit(text_img("KERETA ELEKTRIK (EV)",MONT,58,YEL,var="Black",shadow=False),660)
    return b,t1,t2
EVB,EV1,EV2=ev_card(); BOLT=bolt(150)

COLORS=[("PINK",(200,178,190)),("KELABU",(92,94,98)),("KRIM",(233,226,207)),("HIJAU MINT",(205,224,196))]
@lru_cache(None)
def swatch(i):
    name,c=COLORS[i]; im=Image.new("RGBA",(240,330)); d=ImageDraw.Draw(im)
    sh=Image.new("RGBA",im.size); ImageDraw.Draw(sh).ellipse((32,38,212,218),fill=(0,0,0,160)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d.ellipse((30,25,210,205),fill=c,outline=WHITE,width=8)
    d.ellipse((70,55,120,90),fill=(255,255,255,90))
    t=text_img(name,MONT,40,WHITE,stroke=5,var="Black"); im.alpha_composite(t,(int(120-t.width/2),215)); return im
PANEL=rbox(1000,560,40,(10,12,18,200),outline=(255,255,255,90),ow=3)
PT=text_img("PILIHAN WARNA",ANTON,110,YEL,stroke=6)
NOTE=text_img("*warna seperti dalam video",MONT,34,(230,230,230),var="SemiBold")
PINKSTK=None
def pink_sticker():
    t=text_img("WARNA PINK PUN ADA",ANTON,92,BLACK,shadow=False)
    e=emoji("👀",96) if EMOJI else Image.new("RGBA",(1,1))
    w=t.width+e.width+40; b=rbox(w,150,30,(255,160,205),outline=WHITE,ow=8)
    return compose(b,[(t,30+10,30+150/2-t.height/2),(e,30+20+t.width,30+75-e.height/2)])
PINKSTK=pink_sticker()

CHECKS=["PROTON e.MAS 5","READY STOCK","BANYAK PILIHAN WARNA"]
CL_PANEL=rbox(960,520,40,(10,12,18,210),outline=YEL,ow=4)
CL_T=text_img("KENAPA TUNGGU LAGI?",ANTON,100,WHITE,stroke=5)
CL_ITEMS=[fit(text_img(c,MONT,62,WHITE,var="Black",shadow=False),720) for c in CHECKS]

FLOW_T=text_img("CARA NAK DAPATKAN",ANTON,110,YEL,stroke=7)
STEPS=["HUBUNGI BANG TAF","SEMAK KELAYAKAN LOAN","PILIH WARNA & AMBIL KERETA"]
@lru_cache(None)
def step(i):
    num=Image.new("RGBA",(120,120)); d=ImageDraw.Draw(num); d.ellipse((0,0,119,119),fill=YEL,outline=BLACK,width=5)
    n=text_img(str(i+1),ANTON,80,BLACK,shadow=False); num.alpha_composite(n,(60-n.width//2,60-n.height//2))
    t=fit(text_img(STEPS[i],MONT,52,WHITE,var="Black",shadow=False),720)
    b=rbox(930,150,32,(12,14,20,225),outline=(255,255,255,120),ow=3)
    return compose(b,[(num,30+20,30+15),(t,30+165,30+75-t.height/2)])

END_Q=fit(text_img("NAK e.MAS 5 READY STOCK?",ANTON,104,WHITE,stroke=7),1000)
END_H=text_img("HUBUNGI BANG TAF",ANTON,130,YEL,stroke=8)
def bag_button():
    t=text_img("TEKAN BEG BIRU SEKARANG!",MONT,58,WHITE,var="Black",shadow=False)
    bg=bag(110); w=t.width+bg.width+70; b=rbox(w,150,75,BLUE,outline=WHITE,ow=6)
    return compose(b,[(bg,30+25,30+20),(t,30+50+bg.width,30+75-t.height/2)])
END_B=fit(bag_button(),990)
TAG=text_img("BANG TAF – CONFIRM LULUS",MONT,56,WHITE,stroke=6,var="Black")

def overlays(cv,t):
    cv.alpha_composite(GRAD)
    # ---- HOOK 0-3.2 ----
    if t<3.4:
        out=eo(prog(t,3.0,0.35)); a=1-out
        place(cv,HOOK_P,W/2,250-out*80,1,inout(t,0.05,3.35,.2,.3))
        k=eob(prog(t,0.12,0.35)); place(cv,HOOK_A,W/2,420-out*120,(2.2-1.2*k),a*clamp(prog(t,0.12,0.12)))
        k2=eob(prog(t,0.55,0.35)); place(cv,HOOK_R,W/2-(1-k2)*900,640-out*120,1,a*clamp(prog(t,0.55,0.1)),rot=-3)
    # ---- KAT SINI 5.3-8.4 ----
    if 5.35<=t<8.4:
        a=inout(t,5.35,8.38,.15,.15); k=eob(prog(t,5.4,0.3))
        bob=math.sin((t-5.35)*9)*14
        place(cv,KATSINI,W/2+40,380,0.6+0.4*k,a)
        if PIN: place(cv,PIN,W/2-260,370+bob,k,a)
        place(cv,arrow_down(130,170),W/2,600+bob,k,a)
    if 6.98<=t<8.4:
        k=eob(prog(t,6.98,0.25)); place(cv,STAMP,W/2,1180,2.0-1.0*k,clamp(prog(t,6.98,0.08))*inout(t,6.98,8.38,.05,.15),rot=8)
    # logo watermark
    if 0<=t<31.4:
        place(cv,LOGO_SMALL,40+95,90+67,1,0.95*inout(t,0.0,31.4,.4,.3))
    # ---- B: EV card 8.4-13.66 ----
    if 8.5<=t<13.6:
        a=inout(t,8.5,13.55,.2,.25); k=eob(prog(t,8.55,.4))
        card=compose(EVB,[(EV1,30+200,30+20)])
        if t>=9.3: card=compose(card,[(EV2,30+200,30+200)])
        place(cv,card,W/2,420+(1-k)*-200,1,a*clamp(k*2))
        kb=eob(prog(t,8.8,.35)); place(cv,BOLT,W/2-345,410+math.sin(t*6)*8,kb,a,rot=math.sin(t*4)*6)
        if t>=9.3:
            k2=eob(prog(t,9.3,.25))
    # ---- C: pink sticker 13.8-16.4, colour panel 16.5-21.5 ----
    if 13.8<=t<16.4:
        k=eob(prog(t,13.85,.35)); a=inout(t,13.85,16.35,.1,.2)
        place(cv,PINKSTK,W/2,430,0.3+0.7*k,a,rot=4+math.sin((t-13.8)*7)*3)
    if 16.5<=t<21.6:
        a=inout(t,16.5,21.55,.2,.25); k=eob(prog(t,16.5,.35))
        y0=520+(1-k)*120
        place(cv,PANEL,W/2,y0,1,a)
        place(cv,PT,W/2,y0-195,1,a)
        for i in range(4):
            ki=eob(prog(t,16.9+i*0.45,.3))
            place(cv,swatch(i),W/2-375+i*250,y0+30,ki,a*clamp(ki*3))
        place(cv,NOTE,W/2,y0+250,1,a*clamp(prog(t,18.8,.3)))
    # ---- D: checklist 21.8-26.4 ----
    if 21.8<=t<26.45:
        a=inout(t,21.8,26.4,.2,.25); k=eob(prog(t,21.8,.35)); y0=560+(1-k)*120
        place(cv,CL_PANEL,W/2,y0,1,a)
        place(cv,CL_T,W/2,y0-170,1,a)
        for i,it in enumerate(CL_ITEMS):
            ki=eob(prog(t,22.3+i*0.75,.3)); yy=y0-40+i*120
            place(cv,check(84),W/2-370,yy,ki,a)
            place(cv,it,W/2-300+it.width/2+(1-ki)*200,yy,1,a*clamp(ki*2))
    # ---- E: flow 26.7-31.4 ----
    if 26.7<=t<31.45:
        a=inout(t,26.7,31.4,.2,.25); k=eob(prog(t,26.7,.35))
        place(cv,FLOW_T,W/2,300+(1-k)*-150,1,a)
        for i in range(3):
            ki=eob(prog(t,27.1+i*1.0,.35)); yy=500+i*260
            place(cv,step(i),W/2+(1-ki)*(1100 if i%2==0 else -1100),yy,1,a)
            if i<2:
                ka=eob(prog(t,27.6+i*1.0,.3)); place(cv,arrow_down(70,80),W/2,yy+130+math.sin(t*8)*6,ka,a)
    # ---- F: end card 31.51- ----
    if t>=31.51:
        k=eob(prog(t,31.6,.5)); place(cv,LOGO_BIG,W/2,500,0.4+0.6*k,clamp(k*2))
        k=eob(prog(t,32.1,.35)); place(cv,END_Q,W/2,860,0.6+0.4*k,clamp(k*2))
        k=eob(prog(t,32.5,.35)); place(cv,END_H,W/2,1010,1.6-0.6*k,clamp(prog(t,32.5,.1)))
        k=eob(prog(t,33.1,.4)); pulse=1+0.05*math.sin(max(0,t-33.5)*7)
        place(cv,END_B,W/2,1230,k*pulse,clamp(k*2))
        k=eob(prog(t,33.9,.4)); place(cv,TAG,W/2,1440,1,clamp(k*2))

def transform(fr,t):
    # Ken Burns + punch-in at cuts + hook push
    sc=1.0
    seg_start=max([0]+[c for c in CUTS if c<=t]); sc*=1+0.035*min(1,(t-seg_start)/5)
    for c in CUTS:
        if c<=t<c+0.3: sc*=1+0.14*(1-eo((t-c)/0.3))
    if t<0.7: sc*=1+0.18*(1-eo(t/0.7))
    if sc>1.001:
        nw,nh=int(W*sc),int(H*sc); fr=fr.resize((nw,nh),Image.BILINEAR)
        x=(nw-W)//2; y=(nh-H)//2; fr=fr.crop((x,y,x+W,y+H))
    if t>=31.51:  # end card bg: blur + darken
        k=eo(prog(t,31.51,.5))
        small=fr.resize((270,480)).filter(ImageFilter.GaussianBlur(3*k+0.01)).resize((W,H),Image.BILINEAR)
        fr=Image.blend(fr,small,k); dark=Image.new("RGB",(W,H),(5,6,10)); fr=Image.blend(fr,dark,0.55*k)
    return fr

def flash(cv,t):
    for c in CUTS:
        if c<=t<c+0.12:
            a=int(150*(1-(t-c)/0.12)); cv.alpha_composite(Image.new("RGBA",(W,H),(255,255,255,a)))

dec=subprocess.Popen(["ffmpeg","-v","error","-i",BASE,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
     "-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p","-r",str(FPS),OUT],stdin=subprocess.PIPE)
n=0; only=set(map(float,sys.argv[2:])) if len(sys.argv)>2 else None
while True:
    buf=dec.stdout.read(W*H*3)
    if len(buf)<W*H*3: break
    t=n/FPS; n+=1
    if only is not None and not any(abs(t-o)<0.5/FPS for o in only): continue
    fr=Image.frombuffer("RGB",(W,H),buf)
    fr=transform(fr,t).convert("RGBA")
    flash(fr,t); overlays(fr,t); draw_subs(fr,t)
    if only is not None: fr.convert("RGB").save(f"{S}/build/prev_{t:.2f}.jpg",quality=85); continue
    enc.stdin.write(fr.convert("RGB").tobytes())
    if n%150==0: print("frame",n,flush=True)
enc.stdin.close(); enc.wait(); print("done",n)

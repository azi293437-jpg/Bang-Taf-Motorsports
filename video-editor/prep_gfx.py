import sys, numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance, ImageFont
S=sys.argv[1]; A=S+'/assets/'; G=S+'/gfx/'
W,H=1080,1920
def cover(im,blur=0,dark=1.0):
    im=im.convert('RGB'); s=max(W/im.width,H/im.height)
    im=im.resize((int(im.width*s+1),int(im.height*s+1)),Image.LANCZOS)
    x=(im.width-W)//2; y=(im.height-H)//2; im=im.crop((x,y,x+W,y+H))
    if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
    return ImageEnhance.Brightness(im).enhance(dark)
info=Image.open(A+'3F7F.png').convert('RGB')
bnm=Image.open(A+'IMG_9745.webp').convert('RGB')
red=Image.open(A+'IMG_9746.jpg').convert('RGB')
cover(bnm,2,0.85).save(G+'bg_bnm.png')
cover(info.crop((560,60,941,700)),6,0.8).save(G+'bg_kl.png')
cover(red.crop((0,0,495,330)),10,0.75).save(G+'bg_red.png')
# studio gradient bg
y=np.linspace(0,1,H)[:,None]; x=np.linspace(0,1,W)[None,:]
c1=np.array([8,14,38]); c2=np.array([22,40,92])
r=np.sqrt((x-0.5)**2+(y-0.35)**2)
t=np.clip(1-r*1.4,0,1)[...,None]
img=(c1*(1-t)+c2*t).astype(np.uint8)
im=Image.fromarray(img); d=ImageDraw.Draw(im)
for i in range(-H,W,90): d.line([(i,0),(i+H,H)],fill=(30,52,110),width=2)
im=im.filter(ImageFilter.GaussianBlur(1))
d=ImageDraw.Draw(im)
d.polygon([(0,1500),(1080,1300),(1080,1340),(0,1540)],fill=(242,186,42))
d.polygon([(0,1560),(1080,1360),(1080,1372),(0,1572)],fill=(242,186,42))
im.save(G+'bg_studio.png')
# money/red alert bg
img=(np.array([60,8,12])*(1-t)+np.array([150,20,30])*t).astype(np.uint8)
im=Image.fromarray(img); d=ImageDraw.Draw(im)
for i in range(-H,W,90): d.line([(i,0),(i+H,H)],fill=(170,40,45),width=2)
im.filter(ImageFilter.GaussianBlur(1)).save(G+'bg_alert.png')
# green-ish positive bg
img=(np.array([6,40,24])*(1-t)+np.array([20,110,60])*t).astype(np.uint8)
im=Image.fromarray(img); d=ImageDraw.Draw(im)
for i in range(-H,W,90): d.line([(i,0),(i+H,H)],fill=(30,125,70),width=2)
im.filter(ImageFilter.GaussianBlur(1)).save(G+'bg_green.png')
# cards
def card(im,name,rad=28):
    im=im.convert('RGBA'); m=Image.new('L',im.size,0)
    ImageDraw.Draw(m).rounded_rectangle([0,0,im.width-1,im.height-1],rad,fill=255)
    im.putalpha(m); im.save(G+name+'.png')
card(info.crop((40,450,632,622)),'c_opr',24)
card(info.crop((12,642,931,1074)),'c_graf',24)
card(info.crop((487,1086,931,1548)),'c_kesan',24)
card(info.crop((12,1086,472,1548)),'c_jadual',24)
card(info.crop((0,0,941,640)),'c_title',24)
card(info,'c_info',24)
card(bnm,'c_bnm',24)
card(red,'c_poster',24)
print('ok')

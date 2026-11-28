import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
P=sys.argv[1]; A=P+'/assets/'; G=P+'/gfx/'
W,H=1080,1920
def card(im,name,rad=24):
    im=im.convert('RGBA'); m=Image.new('L',im.size,0)
    ImageDraw.Draw(m).rounded_rectangle([0,0,im.width-1,im.height-1],rad,fill=255); im.putalpha(m); im.save(G+name+'.png')
def autocrop(im):
    a=np.asarray(im.convert('L')).astype(int)
    rows=np.where(a[:, :].mean(1)>25)[0]; rows=rows[(rows>350)&(rows<2400)]
    return im.crop((0,rows.min(),im.width,rows.max()+1))
shots={'p50e6':'protontamanmelawati.com','p61fc':'paultan.org','paa65':'paultan.org','pc61f':'proton.com','pcb95':'paultan.org','pd247':'mudah.my','pdb67':'carz.com.my','pe508':'mudah.my'}
for k,src in shots.items():
    im=autocrop(Image.open(A+k+'.png').convert('RGB')); card(im,'c_'+k); print(k,im.size,src)
for k,f in [('jc232','jc232.jpg'),('wc857','wc857.webp'),('i9699','IMG_9699.jpg'),('i9701','IMG_9701.jpg')]:
    card(Image.open(A+f),'c_'+k)
def cover(im,blur=0,dark=1.0):
    im=im.convert('RGB'); s=max(W/im.width,H/im.height)
    im=im.resize((int(im.width*s+1),int(im.height*s+1)),Image.LANCZOS)
    x=(im.width-W)//2; y=(im.height-H)//2; im=im.crop((x,y,x+W,y+H))
    if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
    return ImageEnhance.Brightness(im).enhance(dark)
cover(Image.open(A+'wc857.webp'),3,0.8).save(G+'bg_proton.png')
cover(Image.open(A+'jc232.jpg'),3,0.8).save(G+'bg_cars.png')
cover(Image.open(A+'IMG_9699.jpg'),4,0.75).save(G+'bg_factory.png')
cover(autocrop(Image.open(A+'p50e6.png')),4,0.8).save(G+'bg_showroom.png')

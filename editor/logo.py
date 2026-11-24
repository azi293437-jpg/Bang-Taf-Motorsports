import numpy as np, sys
from PIL import Image, ImageFilter
from scipy import ndimage
im=Image.open(sys.argv[1]).convert('RGB')
a=np.asarray(im).astype(np.float32)
mx=a.max(2); mn=a.min(2); sat=(mx-mn)
# "logo ink": bright (white) or saturated gold/yellow
ink=(mx>150)|((sat>60)&(mx>110))
ink=ndimage.binary_closing(ink,iterations=2)
# fill enclosed holes (black outlines inside the logo)
filled=ndimage.binary_fill_holes(ink)
# remove specks / the stray gold element at left edge: keep big components
lab,n=ndimage.label(ndimage.binary_dilation(filled,iterations=6))
sizes=ndimage.sum(np.ones_like(lab),lab,range(1,n+1))
keep=np.isin(lab,[i+1 for i,s in enumerate(sizes) if s>1500])
mask=filled&keep
# expand slightly to include dark outline strokes around letters
mask=ndimage.binary_dilation(mask,iterations=2)|mask
alpha=Image.fromarray((mask*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
out=im.convert('RGBA'); out.putalpha(alpha)
bb=alpha.getbbox(); out=out.crop(bb)
out=out.resize((out.width*3,out.height*3),Image.LANCZOS)
out.save(sys.argv[2]); print(out.size, n, sorted(sizes)[-5:])

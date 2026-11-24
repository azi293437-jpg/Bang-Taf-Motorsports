"""Graphics helpers: fonts, text sprites, emoji, easing."""
import math, functools
from PIL import Image, ImageDraw, ImageFont, ImageFilter

GOLD = (245, 196, 40)
GOLD_D = (190, 140, 20)
WHITE = (255, 255, 255)
BLACK = (10, 10, 12)
PANEL = (14, 14, 18)
RED = (230, 45, 45)
GREEN = (60, 200, 110)

F_HEAD = "/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf"
F_BLACK = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
F_XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
F_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
F_EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

@functools.lru_cache(None)
def font(path, size):
    return ImageFont.truetype(path, size)

def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def ease_out_cubic(x):
    x = clamp(x); return 1 - (1 - x) ** 3

def ease_in_cubic(x):
    x = clamp(x); return x ** 3

def ease_in_out(x):
    x = clamp(x); return 3 * x * x - 2 * x * x * x

def ease_out_back(x, s=1.70158):
    x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1

def ease_out_elastic(x):
    x = clamp(x)
    if x in (0, 1): return x
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi / 3)) + 1

@functools.lru_cache(512)
def text_sprite(txt, path, size, fill=WHITE, stroke=0, stroke_fill=BLACK, shadow=True, tracking=0):
    f = font(path, size)
    if tracking:
        widths = [f.getlength(c) + tracking for c in txt]
        w = int(sum(widths)) + stroke * 2 + 20
    else:
        bb = f.getbbox(txt, stroke_width=stroke)
        w = bb[2] + stroke * 2 + 20
    asc, desc = f.getmetrics()
    h = asc + desc + stroke * 2 + 20
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    def draw(dr, col, scol):
        if tracking:
            x = 10 + stroke
            for c, cw in zip(txt, widths):
                dr.text((x, 10 + stroke), c, font=f, fill=col, stroke_width=stroke, stroke_fill=scol)
                x += cw
        else:
            dr.text((10 + stroke, 10 + stroke), txt, font=f, fill=col, stroke_width=stroke, stroke_fill=scol)
    draw(d, fill, stroke_fill)
    if shadow:
        sh = Image.new("RGBA", (w + 30, h + 30), (0, 0, 0, 0))
        a = im.split()[3]
        sh.paste((0, 0, 0, 170), (8, 10), a)
        sh = sh.filter(ImageFilter.GaussianBlur(7))
        sh.alpha_composite(im, (0, 0))
        im = sh
    return im.crop(im.getbbox())

@functools.lru_cache(64)
def emoji(ch, size):
    f = font(F_EMOJI, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    r = size / max(im.size)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)

def scaled(sprite, s):
    if abs(s - 1) < 1e-3: return sprite
    w, h = max(1, int(sprite.width * s)), max(1, int(sprite.height * s))
    return sprite.resize((w, h), Image.BILINEAR)

def with_alpha(sprite, a):
    if a >= 0.999: return sprite
    s = sprite.copy()
    al = s.split()[3].point(lambda v: int(v * a))
    s.putalpha(al)
    return s

def paste_c(canvas, sprite, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    """paste sprite centered at (cx,cy)"""
    if alpha <= 0.01 or scale <= 0.01: return
    sp = scaled(sprite, scale)
    if rot: sp = sp.rotate(rot, resample=Image.BICUBIC, expand=True)
    sp = with_alpha(sp, alpha)
    canvas.alpha_composite(sp, (int(cx - sp.width / 2), int(cy - sp.height / 2))) if _inside(canvas, sp, cx, cy) else _safe(canvas, sp, int(cx - sp.width / 2), int(cy - sp.height / 2))

def paste_xy(canvas, sprite, x, y, alpha=1.0):
    if alpha <= 0.01: return
    _safe(canvas, with_alpha(sprite, alpha), int(x), int(y))

def _inside(canvas, sp, cx, cy):
    x, y = int(cx - sp.width / 2), int(cy - sp.height / 2)
    return x >= 0 and y >= 0 and x + sp.width <= canvas.width and y + sp.height <= canvas.height

def _safe(canvas, sp, x, y):
    # crop sprite to canvas bounds
    x0, y0 = max(0, -x), max(0, -y)
    x1, y1 = min(sp.width, canvas.width - x), min(sp.height, canvas.height - y)
    if x1 <= x0 or y1 <= y0: return
    canvas.alpha_composite(sp.crop((x0, y0, x1, y1)), (x + x0, y + y0))

def rounded(w, h, r, fill, outline=None, width=0):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=fill, outline=outline, width=width)
    return im

def shadowed(im, blur=14, off=(0, 10), op=150):
    pad = blur * 3
    out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    sh.paste((0, 0, 0, op), (pad + off[0], pad + off[1]), im.split()[3])
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    sh.alpha_composite(im, (pad, pad))
    return sh

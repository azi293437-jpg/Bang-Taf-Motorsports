import sys, os, json, math, re, subprocess, wave, importlib.util
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location('spec', os.path.join(S, 'spec.py')); SP = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(SP)
P, O = SP.P, SP.O

FPS = 30; W, H = 1080, 1920; SPEED = 1.1
CLIPS = {'A': S + '/raw/A_C2C7.mov', 'B': S + '/raw/B_CFC2.mov', 'C': S + '/raw/C_F48F.mov'}
ISL = {'A': 'A_C2C7', 'B': 'B_CFC2', 'C': 'C_F48F'}
FD = '/usr/share/fonts/opentype/inter/'
GOLD = (255, 201, 40); RED = (255, 72, 72); GREEN = (80, 230, 120); NAVY = (12, 22, 52); WHITE = (255, 255, 255)
CMAP = {'*': GOLD, '{': RED, '[': GREEN}

_fc = {}
def font(name, size):
    k = (name, size)
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + name, size)
    return _fc[k]
EMOJI_F = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
_ec = {}
def emoji(ch, size):
    k = (ch, size)
    if k not in _ec:
        im = Image.new('RGBA', (180, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), ch, font=EMOJI_F, embedded_color=True)
        im = im.crop(im.getbbox())
        s = size / max(im.width, im.height)
        _ec[k] = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    return _ec[k]

# ------------------------------------------------------------------ timeline
pieces = []
cur = 0
for i, (c, s, e, txt, op) in enumerate(P):
    n = int(round((e - s) / SPEED * FPS))
    pieces.append(dict(i=i, clip=c, s=s, e=e, n=n, f0=cur, txt=txt, op=op))
    cur += n
TOTAL = cur

def anchor(a):
    c, t = a
    for p in pieces:
        if p['clip'] == c and p['s'] - 0.06 <= t <= p['e'] + 0.06:
            return p['f0'] / FPS + (min(max(t, p['s']), p['e']) - p['s']) / SPEED
    raise ValueError('anchor not in any piece: %r' % (a,))

# ------------------------------------------------------------------ markup + captions
def parse_markup(txt):
    toks = []; col = None; buf = ''
    closing = {'*': '*', '{': '}', '[': ']'}
    opener = None
    for ch in txt:
        if opener is None and ch in '*{[':
            opener = ch; continue
        if opener is not None and ch == closing[opener]:
            opener = None; continue
        if ch == ' ':
            if buf: toks.append((buf, col_prev)); buf = ''
            continue
        col_prev = CMAP[opener] if opener else WHITE
        if buf and toks is not None:
            pass
        buf += ch
        # colour of a word = colour of its last char (fine for our markup)
    if buf: toks.append((buf, col_prev))
    return [(w.replace(' ', ' '), c) for w, c in toks]

isl = {c: json.load(open(f'{S}/work/isl_{ISL[c]}.json')) for c in ISL}
def piece_words(p):
    ws = []
    for I in isl[p['clip']]:
        for w in I['words']:
            if p['s'] - 0.25 <= w['s'] < p['e']:
                ws.append(dict(w=w['w'].strip(), s=w['s'], e=w['e']))
    m = []
    for w in ws:
        if m and w['w'] and not w['w'][0].isalnum():
            m[-1]['w'] += w['w']; m[-1]['e'] = w['e']
        else:
            m.append(dict(w))
    return m

captions = []  # (t0, t1, [(word,color)])
for p in pieces:
    if p['op'].get('nocap'): continue
    toks = parse_markup(p['txt'])
    ws = piece_words(p)
    T0 = p['f0'] / FPS; ps, pe = p['s'], p['e']
    def o(t): return T0 + (min(max(t, ps), pe) - ps) / SPEED
    if len(ws) == len(toks) and ws:
        times = [o(w['s'] + 0.04) for w in ws]
    else:
        a = ws[0]['s'] if ws else ps + 0.1; b = ws[-1]['e'] if ws else pe - 0.1
        L = [len(t[0]) + 2 for t in toks]; tot = sum(L); acc = 0; times = []
        for l in L: times.append(o(a + (b - a) * acc / tot)); acc += l
    times[0] = min(times[0], T0 + 0.05) if times[0] - T0 < 0.25 else times[0]
    # chunking
    chunks = []; cw = []; ct = []
    for (w, c), t in zip(toks, times):
        cw.append((w, c)); ct.append(t)
        chars = sum(len(x[0]) + 1 for x in cw)
        if chars >= 17 or w[-1] in '.,?!' or len(cw) >= 4:
            chunks.append((ct[0], cw)); cw = []; ct = []
    if cw: chunks.append((ct[0], cw))
    pend = (p['f0'] + p['n']) / FPS
    for k, (t, cw) in enumerate(chunks):
        t1 = chunks[k + 1][0] if k + 1 < len(chunks) else pend
        captions.append([t, t1, cw])
# allow last caption of a piece to linger into a following short gap
captions.sort(key=lambda x: x[0])

# ------------------------------------------------------------------ drawing helpers
def ease_back(x):
    x = min(max(x, 0), 1); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def ease_out(x):
    x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_io(x):
    x = min(max(x, 0), 1); return x * x * (3 - 2 * x)

def paste(canvas, im, cx, cy, scale=1.0, alpha=1.0, rot=0):
    if scale <= 0.01 or alpha <= 0.01: return
    if abs(scale - 1) > 0.005:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if rot: im = im.rotate(rot, Image.BILINEAR, expand=True)
    if alpha < 0.999:
        a = im.getchannel('A').point(lambda v: int(v * alpha)); im = im.copy(); im.putalpha(a)
    x = int(cx - im.width / 2); y = int(cy - im.height / 2)
    sx = max(0, -x); sy = max(0, -y)
    ex = min(im.width, W - x); ey = min(im.height, H - y)
    if ex <= sx or ey <= sy: return
    if sx or sy or ex < im.width or ey < im.height: im = im.crop((sx, sy, ex, ey))
    canvas.alpha_composite(im, (x + sx, y + sy))

def shadowed(im, r=14, off=8, op=150):
    pad = r * 2 + off
    out = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, op)); sh.putalpha(im.getchannel('A').point(lambda v: v * op // 255))
    out.alpha_composite(sh, (pad, pad + off)); out = out.filter(ImageFilter.GaussianBlur(r))
    out.alpha_composite(im, (pad, pad)); return out

def rich(tokens, f, maxw=900, stroke=0, sc=(0, 0, 0), lh=1.18, align='center'):
    """tokens [(word,color)] -> RGBA image, wrapped"""
    sp = f.getlength(' ')
    lines = []; line = []; lw = 0
    for w, c in tokens:
        wl = f.getlength(w)
        if line and lw + sp + wl > maxw:
            lines.append((line, lw)); line = []; lw = 0
        lw = lw + (sp if line else 0) + wl; line.append((w, c, wl))
    if line: lines.append((line, lw))
    asc, desc = f.getmetrics(); lhpx = int((asc + desc) * lh)
    wmax = int(max(l[1] for l in lines)) + stroke * 2 + 4
    im = Image.new('RGBA', (wmax, lhpx * len(lines) + stroke * 2 + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for li, (ln, lw) in enumerate(lines):
        x = stroke + 2 + ((wmax - stroke * 2 - 4 - lw) / 2 if align == 'center' else 0); y = stroke + 2 + li * lhpx
        for w, c, wl in ln:
            d.text((x, y), w, font=f, fill=c, stroke_width=stroke, stroke_fill=sc); x += wl + sp
    return im

def toks(txt, base=WHITE):
    return [(w, base if c == WHITE else c) for w, c in parse_markup(txt)]

def rbox(w, h, r, fill, outline=None, ow=0):
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, w - 1, h - 1], r, fill=fill, outline=outline, width=ow)
    return im

def pill(emo, txt, fsize=50, base=WHITE, fill=(14, 20, 44, 235), border=GOLD, maxw=860):
    t = rich(toks(txt, base), font('Inter-ExtraBold.otf', fsize), maxw=maxw - 140)
    e = emoji(emo, int(fsize * 1.3)) if emo else None
    ew = (e.width + 18) if e else 0
    w = t.width + ew + 56; h = max(t.height, e.height if e else 0) + 34
    b = rbox(w, h, min(h // 2, 40), fill, border, 4)
    if e: b.alpha_composite(e, (28, (h - e.height) // 2))
    b.alpha_composite(t, (28 + ew, (h - t.height) // 2))
    return shadowed(b, 10, 6, 120)

# ------------------------------------------------------------------ backgrounds
BG = {}
def load_bg(name):
    if name not in BG:
        p = f'{S}/gfx/bg_{name}.png'
        if name == 'dream' and not os.path.exists(p):
            y = np.linspace(0, 1, H)[:, None]; x = np.linspace(0, 1, W)[None, :]
            r = np.sqrt((x - 0.5) ** 2 + (y - 0.4) ** 2); t = np.clip(1 - r * 1.3, 0, 1)[..., None]
            img = (np.array([120, 40, 160]) * (1 - t) + np.array([255, 150, 210]) * t).astype(np.uint8)
            im = Image.fromarray(img).convert('RGBA'); rng = np.random.default_rng(3)
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            for _ in range(40):
                cx, cy, rr = rng.integers(0, W), rng.integers(0, H), rng.integers(20, 90)
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(255, 255, 255, int(rng.integers(25, 70))))
            im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(8))); im.convert('RGB').save(p)
        im = Image.open(p).convert('RGBA')
        BG[name] = im.resize((int(W * 1.07), int(H * 1.07)), Image.LANCZOS)
    return BG[name]
def bg_frame(name, t):
    im = load_bg(name)
    mx = (im.width - W) / 2; my = (im.height - H) / 2
    x = mx + mx * 0.8 * math.sin(t / 4.0); y = my + my * 0.8 * math.cos(t / 5.3)
    return im.crop((int(x), int(y), int(x) + W, int(y) + H))

# ------------------------------------------------------------------ keying
RAMP = np.clip((1280 - np.arange(1280)) / 140.0, 0, 1)[:, None]
def key(fr):
    f = fr.astype(np.int16)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    mx = np.maximum(r, b)
    d = g - mx
    a = 1 - np.clip((d - 6) / 14.0, 0, 1)
    a = a * RAMP
    g2 = np.where(d > 0, mx + np.minimum(d, 4), g)  # despill
    out = np.dstack([r, g2, b, (a * 255)]).clip(0, 255).astype(np.uint8)
    im = Image.fromarray(out, 'RGBA')
    A = im.getchannel('A').filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    im.putalpha(A)
    return im

def person_full(canvas, kim, z, dx=0, dy=0):
    s = 1.5 * z
    cx, cy = 540 + dx, 650 + dy
    data = (1 / s, 0, 360 - cx / s, 0, 1 / s, 600 - cy / s)
    p = kim.transform((W, H), Image.AFFINE, data, resample=Image.BILINEAR)
    canvas.alpha_composite(p)

PIPR = 200; PIPC = (262, 1440)
_pipmask = Image.new('L', (PIPR * 2, PIPR * 2), 0); ImageDraw.Draw(_pipmask).ellipse([0, 0, PIPR * 2 - 1, PIPR * 2 - 1], fill=255)
def person_pip(canvas, kim, sc=1.0):
    crop = kim.crop((360 - 330, 560 - 330, 360 + 330, 560 + 330)).resize((PIPR * 2, PIPR * 2), Image.BILINEAR)
    base = Image.new('RGBA', (PIPR * 2, PIPR * 2), (0, 0, 0, 0))
    disc = Image.new('RGBA', (PIPR * 2, PIPR * 2), (30, 50, 110, 255)); base.paste(disc, (0, 0), _pipmask)
    base.alpha_composite(crop)
    m = Image.new('L', base.size, 0); m.paste(_pipmask, (0, 0))
    base.putalpha(Image.fromarray(np.minimum(np.asarray(base.getchannel('A')), np.asarray(m))))
    ring = Image.new('RGBA', (PIPR * 2 + 20, PIPR * 2 + 20), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([0, 0, PIPR * 2 + 19, PIPR * 2 + 19], fill=GOLD)
    ring.alpha_composite(base, (10, 10))
    paste(canvas, shadowed(ring, 12, 6, 140), PIPC[0], PIPC[1], sc)

# ------------------------------------------------------------------ overlays
class Ov:
    def __init__(s, kind, a, b, prm):
        s.kind = kind; s.t0 = anchor(a); s.t1 = anchor(b); s.p = prm; s.cache = {}
        for k in ('t1', 't2', 't3', 'strike_at'):
            if k in prm: prm[k] = anchor(prm[k])
        if 'items' in prm:
            prm['items'] = [tuple(list(it[:-1]) + [anchor(it[-1])]) for it in prm['items']]
    def c(s, k, fn):
        if k not in s.cache: s.cache[k] = fn()
        return s.cache[k]
    def env(s, t, tin=0.22, tout=0.15):
        u = t - s.t0; v = s.t1 - t
        return ease_back(u / tin), min(1, max(0, v / tout)) if v < tout else 1.0

    def draw(s, cv, t):
        k = s.kind; p = s.p; u = t - s.t0
        sc, al = s.env(t)
        if k == 'title':
            def mk():
                f = font('Inter-Black.otf', 82)
                lines = [rich([(w, (220, 30, 40) if c == GOLD else c) for w, c in toks(l, (10, 10, 10))], f, maxw=900, align='left') for l in p['lines']]
                # recolour highlight gold -> red for white card
                hh = sum(l.height for l in lines) + 40 + 70
                b = rbox(960, hh, 10, (255, 255, 255, 250))
                y = 30
                for l in lines: b.alpha_composite(l, (34, y)); y += l.height - 6
                lab = rich([('BANG TAF', (10, 10, 10))], font('Inter-Black.otf', 40))
                b.alpha_composite(lab, (960 - lab.width - 30, hh - lab.height - 18))
                ImageDraw.Draw(b).rectangle([34, hh - 44, 134, hh - 36], fill=(230, 30, 40))
                return shadowed(b)
            im = s.c('i', mk); yy = 1450 + (1 - ease_out(u / 0.3)) * 120
            paste(cv, im, 540, yy, 1.0, min(1, u / 0.15) * al)
        elif k == 'bignum':
            def mk():
                f = font('Inter-Black.otf', p['size'])
                t_ = rich([(p['text'], GOLD)], f, stroke=12, sc=(20, 10, 0))
                sub = pill(None, p['sub'], 40, WHITE, (220, 30, 40, 245), WHITE)
                o = Image.new('RGBA', (max(t_.width, sub.width), t_.height + sub.height - 20), (0, 0, 0, 0))
                o.alpha_composite(sub, ((o.width - sub.width) // 2, 0)); o.alpha_composite(t_, ((o.width - t_.width) // 2, sub.height - 30))
                return o
            im = s.c('i', mk); paste(cv, im, 540, p['y'], sc * (1 + 0.02 * math.sin(u * 6)), al)
        elif k == 'sticker':
            e = emoji(p['emoji'], p['size'])
            rot = 6 * math.sin(u * 5)
            paste(cv, e, p['x'], p['y'] + 6 * math.sin(u * 4), sc, al, rot)
            if p.get('cross') and u > 0.25:
                def mk():
                    sz = int(p['size'] * 1.05); im = Image.new('RGBA', (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
                    d.line([12, 12, sz - 12, sz - 12], fill=(235, 30, 30), width=22); d.line([sz - 12, 12, 12, sz - 12], fill=(235, 30, 30), width=22)
                    return im
                paste(cv, s.c('x', mk), p['x'], p['y'], ease_back((u - 0.25) / 0.18), al)
        elif k == 'chip':
            im = s.c('i', lambda: pill(p['emoji'], p['text'], 46))
            paste(cv, im, 540, p['y'], sc, al)
        elif k == 'card':
            def mk():
                im = Image.open(f"{S}/gfx/{p['img']}.png").convert('RGBA')
                w = p['w']; h = int(im.height * w / im.width)
                im = im.resize((w, h), Image.LANCZOS)
                b = rbox(w + 16, h + 16, 30, (255, 255, 255, 255)); b.alpha_composite(im, (8, 8))
                return shadowed(b, 16, 10, 160)
            im = s.c('i', mk)
            paste(cv, im, 540, p['y'] + im.height / 2 - 30, 0.85 + 0.15 * sc, min(1, u / 0.12) * al)
        elif k in ('icons',):
            def mkt(): return rich(toks(p['title']), font('Inter-ExtraBold.otf', 52), stroke=5)
            ti = s.c('t', mkt); paste(cv, ti, 540, p['y'], sc, al)
            n = len(p['items']); tw = 220; gap = 20; x0 = 540 - (n * tw + (n - 1) * gap) / 2 + tw / 2
            for j, (em, lab, tt) in enumerate(p['items']):
                if t < tt: continue
                def mk(em=em, lab=lab):
                    b = rbox(tw, 250, 28, (255, 255, 255, 240), GOLD, 5)
                    e = emoji(em, 110); b.alpha_composite(e, ((tw - e.width) // 2, 30))
                    l = rich([(lab, NAVY)], font('Inter-ExtraBold.otf', 40)); b.alpha_composite(l, ((tw - l.width) // 2, 165))
                    return shadowed(b, 10, 6, 120)
                paste(cv, s.c(('it', j), mk), x0 + j * (tw + gap), p['y'] + 230, ease_back((t - tt) / 0.22), al)
        elif k == 'list':
            rows = len(p['items']); ph = 130 + rows * 150
            def mkp():
                b = rbox(960, ph, 36, (10, 16, 40, 225), GOLD, 4)
                ti = rich(toks(p['title'], GOLD), font('Inter-Black.otf', 50), maxw=900)
                b.alpha_composite(ti, ((960 - ti.width) // 2, 34)); return shadowed(b)
            panel = s.c('p', mkp); paste(cv, panel, 540, p['y'] + panel.height / 2, 0.9 + 0.1 * sc, min(1, u / 0.12) * al)
            for j, (em, lab, tt) in enumerate(p['items']):
                if t < tt: continue
                v = ease_out((t - tt) / 0.25)
                def mk(em=em, lab=lab, j=j):
                    last = p.get('check') and j == rows - 1
                    b = rbox(880, 124, 26, (255, 201, 40, 255) if last else (255, 255, 255, 245))
                    e = emoji(em, 84); b.alpha_composite(e, (22, (124 - e.height) // 2))
                    l = rich([(lab, NAVY)], font('Inter-ExtraBold.otf', 52)); b.alpha_composite(l, (130, (124 - l.height) // 2))
                    if p.get('check'):
                        c = emoji('✅', 70); b.alpha_composite(c, (880 - 96, (124 - c.height) // 2))
                    return b
                paste(cv, s.c(('r', j), mk), 540 - (1 - v) * 300, p['y'] + 150 + 40 + j * 150 + 62 + 30, 1.0, v * al)
        elif k == 'stamp':
            def mk():
                f = font('Inter-Black.otf', 170)
                t_ = rich([(p['text'], (235, 30, 30))], f)
                b = Image.new('RGBA', (t_.width + 60, t_.height + 40), (255, 255, 255, 215))
                d = ImageDraw.Draw(b); d.rectangle([0, 0, b.width - 1, b.height - 1], outline=(235, 30, 30), width=14)
                b.alpha_composite(t_, (30, 14)); return b
            sc2 = 2.2 - 1.2 * ease_out(u / 0.12)
            paste(cv, s.c('i', mk), 540, 1400, sc2, al, -10)
        elif k == 'neq':
            def mk():
                o = Image.new('RGBA', (960, 470), (0, 0, 0, 0))
                a = pill('🏦', '*OPR* (kadar dasar BNM)', 50); b = pill('🚗', 'Interest *loan kereta* korang', 50)
                o.alpha_composite(a, ((960 - a.width) // 2, 0))
                ne = rich([('≠', (255, 60, 60))], font('Inter-Black.otf', 170), stroke=8, sc=WHITE)
                o.alpha_composite(ne, ((960 - ne.width) // 2, 95))
                o.alpha_composite(b, ((960 - b.width) // 2, 470 - b.height)); return o
            paste(cv, s.c('i', mk), 540, 1440, sc, al)
        elif k == 'strike':
            im = s.c('i', lambda: pill('🤑', p['text'], 52, NAVY, (255, 255, 255, 245), GOLD))
            paste(cv, im, 540, p['y'], sc, al)
            if t > p['strike_at']:
                v = ease_out((t - p['strike_at']) / 0.2)
                L = int((im.width - 60) * v)
                ln = Image.new('RGBA', (max(1, L), 16), (235, 30, 30, 255))
                cv.alpha_composite(ln, (int(540 - im.width / 2 + 30), int(p['y'] - 8)))
        elif k == 'pricetag':
            def mk():
                t_ = rich([(p['text'], NAVY)], font('Inter-Black.otf', 96))
                e = emoji('🚗', 110)
                w = t_.width + e.width + 110; h = 170
                b = rbox(w, h, 30, (255, 201, 40, 255), (20, 20, 20, 255), 6)
                b.alpha_composite(e, (40, (h - e.height) // 2)); b.alpha_composite(t_, (e.width + 70, (h - t_.height) // 2))
                return shadowed(b)
            paste(cv, s.c('i', mk), 540, 1460, sc, al, 8 * math.sin(u * 7) * math.exp(-u * 2))
        elif k == 'ad':
            def mk(blink):
                w, h = 900, 250
                b = rbox(w, h, 26, (225, 25, 35, 250), (255, 230, 0, 255) if blink else WHITE, 10)
                f = font('Inter-Black.otf', 62)
                l1 = rich([('🔥', WHITE)], f) if False else None
                e = emoji('🔥', 80)
                t1 = rich([('PROMOSI!', (255, 230, 0)), ('Interest', WHITE), ('serendah', WHITE)], font('Inter-Black.otf', 56))
                t2 = rich([('X.XX%*', (255, 230, 0))], font('Inter-Black.otf', 80))
                t3 = rich([('*Terma & syarat dikenakan', (255, 230, 230))], font('Inter-SemiBold.otf', 30))
                b.alpha_composite(e, (30, 30)); b.alpha_composite(t1, (125, 32)); b.alpha_composite(t2, ((w - t2.width) // 2, 105))
                b.alpha_composite(t3, (w - t3.width - 80, h - t3.height - 14)); sm = emoji('😏', 40); b.alpha_composite(sm, (w - 70, h - sm.height - 12))
                return shadowed(b)
            blink = int(u * 6) % 2 == 0
            paste(cv, s.c(('i', blink), lambda: mk(blink)), 540, 1480, sc, al, -3)
        elif k == 'stats':
            for j, (em, lab, val, tt) in enumerate(p['items']):
                if t < tt: continue
                v = ease_out((t - tt) / 0.8)
                num = float(val.rstrip('%')); dec = len(val.split('.')[1].rstrip('%')) if '.' in val else 0
                shown = f"{num * v:.{dec}f}%"
                def mkb(em=em, lab=lab):
                    b = rbox(940, 240, 30, (255, 255, 255, 245), GOLD, 5)
                    e = emoji(em, 120); b.alpha_composite(e, (34, (240 - e.height) // 2))
                    l = rich([(lab, (70, 80, 110))], font('Inter-Bold.otf', 42), align='left'); b.alpha_composite(l, (190, 40))
                    return shadowed(b, 10, 6, 120)
                base = s.c(('b', j), mkb).copy()
                nt = rich([(shown, (20, 120, 60) if j < 2 else NAVY)], font('Inter-Black.otf', 104), align='left')
                base.alpha_composite(nt, (190 + 30, 30 + 92))
                paste(cv, base, 540, p['y'] + j * 275 + 135, ease_back((t - tt) / 0.25), al)
        elif k == 'chips':
            for j, (em, lab, tt) in enumerate(p['items']):
                if t < tt: continue
                im = s.c(('c', j), lambda em=em, lab=lab: pill(em, lab, 44))
                if p.get('row'):
                    n = len(p['items']); x = 540 + (j - (n - 1) / 2) * 300; y = p['y'] + 40
                else:
                    x = 540; y = p['y'] + j * 100
                paste(cv, im, x, y, ease_back((t - tt) / 0.22), al)
        elif k == 'banner':
            def mk():
                txt = p['text']; em, rest = txt.split(' ', 1)
                col = (230, 30, 40, 250) if p.get('color') != 'gold' else (255, 201, 40, 250)
                return pill(em, rest, 64, WHITE if p.get('color') != 'gold' else NAVY, col, WHITE)
            j = 5 * math.sin(u * 40) * math.exp(-u * 4)
            paste(cv, s.c('i', mk), 540 + j, 300, sc, al)
        elif k == 'compare':
            def mkp():
                b = rbox(960, 760, 36, (10, 16, 40, 230), GOLD, 4)
                t_ = rich(toks('Contoh: Loan *RM54,000* • *9 tahun*', WHITE), font('Inter-Black.otf', 46), maxw=900)
                t2 = rich([('(kiraan kadar rata, ilustrasi sahaja)', (170, 180, 210))], font('Inter-SemiBold.otf', 30))
                b.alpha_composite(t_, ((960 - t_.width) // 2, 30)); b.alpha_composite(t2, ((960 - t2.width) // 2, 98))
                return shadowed(b)
            pan = s.c('p', mkp); top = 220; paste(cv, pan, 540, top + pan.height / 2 - 30, 0.9 + 0.1 * sc, min(1, u / 0.12) * al)
            rows = [('2.5%', 12150, 'RM12,150', p['t1'], (80, 200, 120)), ('3.0%', 14580, 'RM14,580', p['t2'], (255, 90, 90))]
            for j, (rate, val, lab, tt, col) in enumerate(rows):
                if t < tt: continue
                v = ease_out((t - tt) / 0.5)
                y = top + 190 + j * 190
                lt = s.c(('l', j), lambda rate=rate: rich([('Kadar ' + rate, WHITE)], font('Inter-ExtraBold.otf', 44), align='left'))
                cv.alpha_composite(lt, (110, int(y)))
                bw = int(700 * val / 14580 * v)
                if bw > 2: cv.alpha_composite(rbox(bw, 62, 16, col + (255,)), (110, int(y + 62)))
                if v > 0.6:
                    vt = s.c(('v', j), lambda lab=lab: rich([('Faedah ' + lab, WHITE)], font('Inter-Black.otf', 40), stroke=4))
                    cv.alpha_composite(vt, (int(min(110 + bw + 14, 990 - vt.width)), int(y + 62 + (62 - vt.height) // 2)) if 110 + bw + 14 + vt.width < 1000 else (int(130), int(y + 62 + 3)))
            if t > p['t3']:
                im = s.c('d', lambda: pill('😱', 'Beza 0.5% = *RM2,430* lebih!', 50, WHITE, (220, 30, 40, 250), WHITE))
                paste(cv, im, 540, top + 640, ease_back((t - p['t3']) / 0.25), al)
        elif k == 'tenor':
            def mkp():
                b = rbox(960, 780, 36, (10, 16, 40, 230), GOLD, 4)
                t_ = rich(toks('Loan *RM54,000* @ *3.0%*', WHITE), font('Inter-Black.otf', 50), maxw=900)
                t2 = rich([('(kiraan kadar rata, ilustrasi sahaja)', (170, 180, 210))], font('Inter-SemiBold.otf', 30))
                b.alpha_composite(t_, ((960 - t_.width) // 2, 30)); b.alpha_composite(t2, ((960 - t2.width) // 2, 98))
                return shadowed(b)
            pan = s.c('p', mkp); top = 220; paste(cv, pan, 540, top + pan.height / 2 - 30, 0.9 + 0.1 * sc, min(1, u / 0.12) * al)
            cols = [('5 tahun', 'RM1,035', 'RM62,100', p['t1'], '🙂'), ('9 tahun', 'RM635', 'RM68,580', p['t2'], '😍')]
            for j, (ten, inst, tot, tt, em) in enumerate(cols):
                if t < tt: continue
                def mk(ten=ten, inst=inst, em=em, j=j):
                    b = rbox(420, 300, 28, (255, 255, 255, 245), GOLD if j == 1 else None, 6 if j == 1 else 0)
                    a = rich([(ten, (70, 80, 110))], font('Inter-ExtraBold.otf', 44)); b.alpha_composite(a, ((420 - a.width) // 2, 22))
                    c = rich([(inst, NAVY)], font('Inter-Black.otf', 78)); b.alpha_composite(c, ((420 - c.width) // 2, 90))
                    d = rich([('sebulan', (70, 80, 110))], font('Inter-Bold.otf', 36)); b.alpha_composite(d, ((420 - d.width) // 2, 190))
                    e = emoji(em, 70); b.alpha_composite(e, (420 - e.width - 16, 16))
                    return b
                paste(cv, s.c(('c', j), mk), 300 + j * 480, top + 160 + 150, ease_back((t - tt) / 0.22), al)
            if t > p['t3']:
                for j, (ten, inst, tot, tt, em) in enumerate(cols):
                    im = s.c(('t', j), lambda tot=tot, j=j: pill('😱' if j else '👍', 'Total ' + tot, 40, WHITE, ((220, 30, 40, 250) if j else (30, 140, 70, 250)), WHITE))
                    paste(cv, im, 300 + j * 480, top + 520, ease_back((t - p['t3']) / 0.22), al)
                im = s.c('x', lambda: rich(toks('Bayar *+RM6,480* lagi!', WHITE), font('Inter-Black.otf', 58), stroke=6))
                paste(cv, im, 540, top + 640, ease_back((t - p['t3'] - 0.3) / 0.25), al)
        elif k == 'qcards':
            for j, (em, lab, tt) in enumerate(p['items']):
                if t < tt: continue
                im = s.c(('q', j), lambda em=em, lab=lab: pill(em, lab, 54, NAVY, (255, 255, 255, 248), GOLD, maxw=940))
                paste(cv, im, 540, p['y'] + j * 260 + 100, ease_back((t - tt) / 0.25), al)
        elif k == 'rain':
            rng = np.random.default_rng(7)
            for j in range(18):
                x = rng.uniform(60, 1020); sp = rng.uniform(900, 1500); d0 = rng.uniform(0, 0.6); sz = int(rng.uniform(80, 140))
                y = -100 + (u - d0) * sp
                if u > d0: paste(cv, emoji(p['emoji'], sz), x, y, 1, al, (u * 200 + j * 40) % 360 - 180)

overlays = [Ov(*o) for o in O]

QM = None
def qmarks():
    global QM
    if QM is None:
        QM = rich([('??', (40, 110, 230))], font('Inter-Black.otf', 700), stroke=16, sc=(255, 255, 255))
    return QM

def cap_img(words):
    f = font('Inter-ExtraBold.otf', 64)
    t = rich(words, f, maxw=860)
    b = rbox(t.width + 44, t.height + 22, 22, (0, 0, 0, 170)); b.alpha_composite(t, (22, 10))
    return b
_capc = {}

# ------------------------------------------------------------------ frame composer
def compose(fr_raw, p, fi):
    """fi = global frame index"""
    t = fi / FPS; u = (fi - p['f0']) / FPS; dur = p['n'] / FPS
    op = p['op']
    cv = bg_frame(op.get('bg', 'studio'), t).copy()
    kim = key(fr_raw)
    layout = op.get('layout', 'full')
    if op.get('qmarks'):
        paste(cv, qmarks(), 540, 470, 1 + 0.03 * math.sin(t * 3), min(1, u / 0.2) if p['i'] > 0 and not pieces[p['i'] - 1]['op'].get('qmarks') else 1)
    if layout == 'full':
        z = op.get('z', 1.0); z2 = op.get('z2')
        if z2: z = z + (z2 - z) * ease_io(u / dur)
        dx = dy = 0
        sh = op.get('shake')
        if sh:
            rng = np.random.default_rng(fi); amp = sh * max(0.2, 1 - u * 1.5)
            dx, dy = rng.uniform(-amp, amp, 2)
        person_full(cv, kim, z, dx, dy)
    else:
        prev = pieces[p['i'] - 1]['op'].get('layout', 'full') if p['i'] > 0 else 'full'
        sc = ease_back(u / 0.25) if prev != 'pip' else 1.0
        person_pip(cv, kim, sc)
    for o in overlays:
        if o.t0 <= t < o.t1: o.draw(cv, t)
    # captions
    cy = 1300 if layout == 'full' else 1125
    for c in captions:
        if c[0] <= t < c[1]:
            k = id(c)
            if k not in _capc: _capc[k] = cap_img(c[2])
            v = (t - c[0]) / 0.12
            paste(cv, _capc[k], 540, cy, 0.85 + 0.15 * ease_back(v))
            break
    # flash on background change
    if p['i'] > 0 and pieces[p['i'] - 1]['op'].get('bg') != op.get('bg') and u < 0.14:
        a = int(150 * (1 - u / 0.14))
        cv.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, a)))
    return cv.convert('RGB')

# ------------------------------------------------------------------ workers
def render_range(a, b, out):
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
    for p in pieces:
        lo = max(a, p['f0']); hi = min(b, p['f0'] + p['n'])
        if lo >= hi: continue
        st = p['s'] + (lo - p['f0']) / FPS * SPEED
        dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{st:.4f}', '-i', CLIPS[p['clip']], '-vf', f'setpts=(PTS-STARTPTS)/{SPEED},fps={FPS}', '-frames:v', str(hi - lo),
                                '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
        last = None
        for fi in range(lo, hi):
            buf = dec.stdout.read(720 * 1280 * 3)
            if len(buf) == 720 * 1280 * 3: last = np.frombuffer(buf, np.uint8).reshape(1280, 720, 3)
            enc.stdin.write(compose(last, p, fi).tobytes())
        dec.stdout.close(); dec.wait()
    enc.stdin.close(); enc.wait()

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'info':
        print('pieces', len(pieces), 'frames', TOTAL, 'sec', TOTAL / FPS)
        for c in captions[:8]: print(round(c[0], 2), round(c[1], 2), ' '.join(w for w, _ in c[2]))
    elif cmd == 'still':
        # still <frame> <out.png>
        fi = int(sys.argv[2])
        p = [q for q in pieces if q['f0'] <= fi < q['f0'] + q['n']][0]
        st = p['s'] + (fi - p['f0']) / FPS * SPEED
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{st:.4f}', '-i', CLIPS[p['clip']], '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        im = compose(np.frombuffer(raw, np.uint8).reshape(1280, 720, 3), p, fi)
        # warm previous overlays' state not needed
        im.save(sys.argv[3])
    elif cmd == 'range':
        render_range(int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])

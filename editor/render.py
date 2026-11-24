"""Frame-by-frame compositor for the Bang Taf Motorsport Proton Saga reel."""
import os, sys, math, json, subprocess, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from timeline import *
from gfx import *

ROOT = os.path.abspath(os.path.join(HERE, ".."))
G = os.path.join(ROOT, "graded")
LOGO = Image.open(os.path.join(HERE, "logo.png")).convert("RGBA")

# ---------------------------------------------------------------- sources
class Reader:
    def __init__(self, path):
        self.path = path
        info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                               "stream=r_frame_rate:format=duration", "-of", "json", path],
                              capture_output=True, text=True).stdout
        j = json.loads(info)
        n, d = j["streams"][0]["r_frame_rate"].split("/")
        self.fps = float(n) / float(d)
        self.dur = float(j["format"]["duration"])
        self.p = None; self.t = -1; self.frame = None

    def _open(self, t):
        if self.p: self.p.kill()
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", "%.3f" % max(0, t), "-i", self.path,
                                   "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=10 ** 8)
        self.t = max(0, t) - 1 / self.fps; self.frame = None

    def _next(self):
        b = self.p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: return False
        self.frame = b; self.t += 1 / self.fps; return True

    def get(self, t):
        t = min(max(0, t), self.dur - 0.05)
        if self.p is None or t < self.t - 0.5 / self.fps or t > self.t + 1.5:
            self._open(t)
        while self.frame is None or self.t < t - 0.5 / self.fps:
            if not self._next(): break
        return Image.frombuffer("RGB", (W, H), self.frame, "raw", "RGB", 0, 1)

R = {k: Reader(os.path.join(G, k + ".mp4")) for k in
     ["IMG_1132", "IMG_1117", "IMG_1118", "IMG_1119", "IMG_1121", "IMG_1122", "IMG_1124"]}

o = src2out  # shorthand

# ---------------------------------------------------------------- shots
# (out_start, out_end, clip, src_func(local_t), zoom_func(local_t, dur), transition-in)
def ramp(points):
    """piecewise speed ramp: points = [(local_t, speed)] -> returns func local_t -> clip time offset"""
    def f(t):
        acc, last_t, last_s = 0.0, 0.0, points[0][1]
        for pt, sp in points[1:]:
            if t <= pt: return acc + (t - last_t) * last_s
            acc += (pt - last_t) * last_s; last_t, last_s = pt, sp
        return acc + (t - last_t) * last_s
    return f

SHOTS = []
def broll(o0, o1, clip, start, speeds, z0, z1, pan=(0, 0)):
    rf = ramp(speeds)
    SHOTS.append(dict(o0=o0, o1=o1, clip=clip, src=lambda lt, rf=rf, s=start: s + rf(lt),
                      zoom=lambda lt, d, z0=z0, z1=z1: z0 + (z1 - z0) * ease_in_out(lt / d), pan=pan, broll=True))

_aroll_n = [0]
def aroll(o0, o1, zbase=None):
    n = _aroll_n[0]; _aroll_n[0] += 1
    zb = zbase if zbase is not None else (1.0 if n % 2 == 0 else 1.12)
    SHOTS.append(dict(o0=o0, o1=o1, clip="IMG_1132", src=None,
                      zoom=lambda lt, d, zb=zb: zb + 0.035 * lt / max(d, 0.1), pan=(0, -40 if zb > 1.05 else 0), broll=False))

# hook: showroom car, slow-mo then ramp
broll(0.0, o(5.95), "IMG_1117", 0.2, [(0, 0.55), (1.6, 1.25)], 1.22, 1.04)
broll(o(6.76), o(9.0), "IMG_1118", 0.1, [(0, 1.9), (0.9, 0.75)], 1.12, 1.0)
aroll(o(9.6), o(15.38), 1.0)
aroll(o(15.38), o(21.42), 1.12)
broll(o(22.94), o(26.2), "IMG_1121", 0.6, [(0, 1.5), (2.0, 0.9)], 1.05, 1.16)
aroll(o(30.22), o(32.95), 1.0)
aroll(o(35.04), o(38.86), 1.12)
broll(o(38.86), o(41.62), "IMG_1119", 0.0, [(0, 0.8)], 1.0, 1.12)
broll(o(41.62), o(44.42), "IMG_1122", 0.4, [(0, 1.3), (1.2, 0.8)], 1.15, 1.02)
aroll(o(44.42), o(46.42), 1.0)
aroll(o(46.78), o(51.9), 1.12)
broll(o(51.9), o(55.6), "IMG_1124", 0.0, [(0, 0.78)], 1.25, 1.02)
aroll(o(55.52), o(58.08), 1.0)
aroll(o(58.08), NARR_END, 1.12)
# 'cut' points that get a transition
CUTS = [s["o0"] for s in SHOTS[1:]]

def out2src_aroll(t):
    for o0, o1, a, b in MAP:
        if o0 <= t < o1 + 1e-6: return a + (t - o0)
    return SEGMENTS[-1][1]

def shot_at(t):
    for s in SHOTS:
        if s["o0"] <= t < s["o1"]: return s
    return SHOTS[-1]

def base_frame(t, shot=None):
    s = shot or shot_at(t)
    lt = t - s["o0"]; d = s["o1"] - s["o0"]
    if s["src"] is None:
        img = R["IMG_1132"].get(out2src_aroll(t))
    else:
        img = R[s["clip"]].get(s["src"](lt))
    z = s["zoom"](lt, d)
    # transition punch-in at shot start
    if lt < 0.28 and s is not SHOTS[0]:
        z *= 1 + 0.10 * (1 - ease_out_cubic(lt / 0.28))
    if z != 1.0:
        w, h = int(W * z), int(H * z)
        img = img.resize((w, h), Image.BILINEAR)
        px, py = s["pan"]
        x = (w - W) // 2 + int(px * min(1, (z - 1) / 0.12)); y = (h - H) // 2 + int(py * min(1, (z - 1) / 0.12))
        x = max(0, min(w - W, x)); y = max(0, min(h - H, y))
        img = img.crop((x, y, x + W, y + H))
    return img

# ---------------------------------------------------------------- static layers
def make_vignette():
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    a = np.clip((d - 0.55) / 0.6, 0, 1) ** 1.6 * 150
    # extra top & bottom gradient for text legibility
    top = np.clip(1 - yy / 520, 0, 1) ** 2 * 90
    bot = np.clip((yy - 1150) / 770, 0, 1) ** 1.5 * 120
    a = np.clip(a + top + bot, 0, 210).astype(np.uint8)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); im.putalpha(Image.fromarray(a))
    return im
VIGNETTE = make_vignette()

LOGO_SMALL = shadowed(scaled(LOGO, 200 / LOGO.width), blur=8, off=(0, 4), op=160)

# ---------------------------------------------------------------- subtitles
WORDS = words()
KEYWORDS = {"saga", "saga,", "proton", "fresh", "graduate", "mula", "kerja,", "mak", "ayah", "komitmen", "tinggi",
            "pencen", "low", "cost", "maintenance", "pasangan", "muda", "kereta", "penat", "ulang-alik", "motor", "kedua",
            "keempat,", "kelima,", "family", "ready", "stock,", "tekan", "beg", "biru", "bawah", "pertama"}
HIDE_SUBS = [(0, o(5.95))]  # hook headline already carries the words

def chunk_words(ws):
    chunks, cur = [], []
    for i, w in enumerate(ws):
        if cur:
            gap = w["s"] - cur[-1]["e"]
            txtlen = sum(len(x["t"]) + 1 for x in cur) + len(w["t"])
            seg_break = w["seg"] != cur[-1]["seg"]
            if len(cur) >= 3 or txtlen > 16 or gap > 0.3 or cur[-1]["t"][-1] in ",?." or seg_break:
                chunks.append(cur); cur = []
        cur.append(w)
    if cur: chunks.append(cur)
    out = []
    for i, c in enumerate(chunks):
        end = c[-1]["e"] + 0.25
        if i + 1 < len(chunks): end = min(end + 0.4, chunks[i + 1][0]["s"])
        out.append(dict(words=c, s=c[0]["s"], e=end))
    return out
CHUNKS = chunk_words(WORDS)

SUB_Y = 1330
CARD_Y = 285
SUB_SIZE = 74

def word_sprite(txt, active, key):
    t = txt.upper().strip(",")
    if active:
        sp = text_sprite(t, F_BLACK, SUB_SIZE, fill=BLACK, stroke=0, shadow=False)
        box = rounded(sp.width + 34, sp.height + 30, 16, GOLD)
        box.alpha_composite(sp, (17, 15))
        return shadowed(box, blur=8, off=(0, 6), op=140)
    col = GOLD if key else WHITE
    return text_sprite(t, F_BLACK, SUB_SIZE, fill=col, stroke=7, stroke_fill=BLACK)

def draw_subs(cv, t):
    if any(a <= t < b for a, b in HIDE_SUBS): return
    for c in CHUNKS:
        if c["s"] - 0.02 <= t < c["e"]:
            lt = t - c["s"]
            pop = ease_out_back(lt / 0.18, 2.2) if lt < 0.18 else 1.0
            sprites = []
            for w in c["words"]:
                active = w["s"] - 0.03 <= t < max(w["e"], w["s"] + 0.12) + 0.04
                key = w["t"].lower().strip("?") in KEYWORDS
                sprites.append((word_sprite(w["t"], active, key), active, w))
            gap = 18
            total = sum(s.width for s, _, _ in sprites) + gap * (len(sprites) - 1)
            fit = min(1.0, 900 / total)
            x = 520 - total * fit / 2
            for sp, active, w in sprites:
                sc = pop * (1.0 + (0.06 * (1 - ease_out_cubic((t - w["s"]) / 0.15)) if active else 0))
                paste_c(cv, sp, x + sp.width * fit / 2, SUB_Y, scale=sc * fit, alpha=clamp(lt / 0.08))
                x += (sp.width + gap) * fit
            return

# ---------------------------------------------------------------- hook headline
def draw_hook(cv, t):
    end = o(5.95)
    if t >= end + 0.0: return
    out_a = 1 - clamp((t - (end - 0.15)) / 0.15)
    lines = [
        ("KORANG RASA,", o(2.64), 60, WHITE, 370),
        ("SIAPA YANG PATUT", o(3.86), 92, WHITE, 470),
        ("PAKAI KERETA NI?", o(4.8), 104, GOLD, 585),
    ]
    for txt, ts, size, col, y in lines:
        lt = t - ts + 0.08
        if lt < 0: continue
        sp = text_sprite(txt, F_HEAD, size, fill=col, stroke=6, stroke_fill=BLACK)
        if sp.width > 980: sp = scaled(sp, 980 / sp.width)
        sc = ease_out_back(lt / 0.32, 2.0)
        paste_c(cv, sp, 540, y, scale=0.6 + 0.4 * sc, alpha=clamp(lt / 0.1) * out_a)
    # thinking emoji bounce
    lt = t - o(5.3)
    if lt > 0:
        e = emoji("🤔", 120)
        paste_c(cv, e, 900, 690 - 20 * math.sin(lt * 9) * math.exp(-lt * 3), scale=ease_out_back(lt / 0.3, 3), alpha=out_a)
    # gold accent bar wipe under headline
    lt = t - o(4.8)
    if lt > 0:
        wv = int(560 * ease_out_cubic(lt / 0.35))
        if wv > 4:
            bar = rounded(wv, 12, 6, GOLD)
            paste_xy(cv, bar, 540 - 280, 660, alpha=out_a)

# ---------------------------------------------------------------- PROTON SAGA title
@functools.lru_cache(4)
def saga_sprite():
    return text_sprite("SAGA", F_HEAD, 250, fill=GOLD, stroke=8, stroke_fill=BLACK)

def draw_saga(cv, t):
    a0, a1 = o(7.0), o(9.0)
    if not (a0 <= t < a1 + 0.2): return
    out_a = 1 - clamp((t - a1) / 0.2)
    lt = t - a0
    sp = text_sprite("PROTON", F_HEAD, 84, fill=WHITE, stroke=5, tracking=22)
    x = 540 + (1 - ease_out_cubic(lt / 0.35)) * -700
    paste_c(cv, sp, x, 360, alpha=out_a)
    lt2 = t - o(7.92) + 0.05
    if lt2 > 0:
        s = saga_sprite()
        sc = 1.0 + 0.9 * (1 - ease_out_cubic(lt2 / 0.25))
        # light sweep
        if 0.2 < lt2 < 0.9:
            s = s.copy(); sw = Image.new("L", s.size, 0)
            px = int((lt2 - 0.2) / 0.7 * (s.width + 300)) - 150
            ImageDraw.Draw(sw).polygon([(px, 0), (px + 70, 0), (px + 10, s.height), (px - 60, s.height)], fill=170)
            sw = sw.filter(ImageFilter.GaussianBlur(10))
            white = Image.new("RGBA", s.size, (255, 255, 255, 0)); white.putalpha(Image.fromarray(np.minimum(np.asarray(sw), np.asarray(s.split()[3]))))
            s.alpha_composite(white)
        paste_c(cv, s, 540, 520, scale=sc, alpha=clamp(lt2 / 0.1) * out_a)
        lt3 = lt2 - 0.25
        if lt3 > 0:
            wv = int(600 * ease_out_cubic(lt3 / 0.3))
            if wv > 4: paste_xy(cv, rounded(wv, 10, 5, WHITE), 540 - 300, 650, alpha=out_a)

# ---------------------------------------------------------------- numbered cards
CARDS = [
    (1, "🎓", "FRESH GRADUATE", "Baru nak mula kerja", o(9.7), o(15.3)),
    (2, "👴", "MAK AYAH PENCEN", "Tak nak komitmen tinggi", o(16.3), o(21.42) - 0.05),
    (3, "💑", "PASANGAN MUDA", "Baru nak mula hidup", o(30.28), o(32.95) - 0.05),
    (4, "🔑", "KERETA PERTAMA", "Baru nak ada kereta", o(35.1), o(38.86) - 0.05),
    (5, "🚗", "KERETA KEDUA", "Untuk family", o(47.0), o(51.9) - 0.05),
]

@functools.lru_cache(8)
def card_sprite(n, em, title, sub):
    cw, ch = 900, 200
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    panel = rounded(cw - 150, ch, 22, PANEL + (225,))
    im.alpha_composite(panel, (150, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 190, ch - 1), 22, fill=GOLD)
    num = text_sprite("%02d" % n, F_HEAD, 104, fill=BLACK, shadow=False)
    im.alpha_composite(num, (95 - num.width // 2, ch // 2 - num.height // 2))
    lab = text_sprite("SESUAI UNTUK", F_XB, 30, fill=GOLD, shadow=False, tracking=4)
    im.alpha_composite(lab, (225, 26))
    tt = text_sprite(title, F_HEAD, 66, fill=WHITE, shadow=False)
    if tt.width > 515: tt = scaled(tt, 515 / tt.width)
    im.alpha_composite(tt, (222, 66))
    st = text_sprite(sub, F_BOLD, 34, fill=(210, 210, 215), shadow=False)
    im.alpha_composite(st, (225, 66 + tt.height + 8))
    d.rectangle((190, ch - 8, cw - 22, ch - 1), fill=GOLD)
    return shadowed(im, blur=16, off=(0, 12), op=170)

def draw_cards(cv, t):
    for n, em, title, sub, a, b in CARDS:
        if not (a <= t < b): continue
        lt, rt = t - a, b - t
        sp = card_sprite(n, em, title, sub)
        if rt < 0.25:
            x = 60 - 1100 * ease_in_cubic(1 - rt / 0.25)
        else:
            x = 60 - 1100 * (1 - ease_out_back(lt / 0.45, 1.3))
        pad = (sp.width - 900) // 2
        paste_xy(cv, sp, x - pad, CARD_Y - pad)
        # emoji pops in after the card lands
        el = lt - 0.3
        if el > 0 and rt > 0.15:
            e = emoji(em, 120)
            paste_c(cv, e, x + 830, CARD_Y + 100 + 6 * math.sin(lt * 5), scale=ease_out_back(el / 0.35, 3.0))
        # progress dots 1..5
        dl = lt - 0.45
        if dl > 0 and rt > 0.25:
            for i in range(5):
                on = i < n
                r = 13 if i == n - 1 else 10
                if i == n - 1: r = int(10 + 6 * ease_out_elastic(dl / 0.6))
                dot = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
                ImageDraw.Draw(dot).ellipse((20 - r, 20 - r, 20 + r, 20 + r), fill=GOLD if on else (255, 255, 255, 120),
                                            outline=BLACK, width=2)
                paste_c(cv, dot, x + 250 + i * 46, CARD_Y + 240)

# ---------------------------------------------------------------- low cost maintenance gauge
def draw_maintenance(cv, t):
    a, b = o(22.98), o(26.2)
    if not (a <= t < b): return
    lt, rt = t - a, b - t
    out_a = clamp(rt / 0.2)
    pw, ph = 860, 470
    # panel
    sc = ease_out_back(lt / 0.4, 1.5)
    panel = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(panel)
    d.rounded_rectangle((0, 0, pw - 1, ph - 1), 30, fill=PANEL + (215,), outline=GOLD, width=4)
    lab = text_sprite("KOS PENYELENGGARAAN", F_XB, 34, fill=GOLD, shadow=False, tracking=3)
    panel.alpha_composite(lab, (pw // 2 - lab.width // 2, 28))
    # gauge arc
    cx, cy, r = pw // 2, 330, 190
    segs = [(GREEN, 180, 240), ((240, 200, 40), 240, 300), (RED, 300, 360)]
    for col, s0, s1 in segs:
        d.arc((cx - r, cy - r, cx + r, cy + r), s0, s1, fill=col, width=34)
    for txt, ang in (("RENDAH", 200), ("TINGGI", 340)):
        sp = text_sprite(txt, F_XB, 26, fill=WHITE, shadow=False)
        rr = r + 52
        px = cx + rr * math.cos(math.radians(ang)); py = cy + rr * math.sin(math.radians(ang))
        panel.alpha_composite(sp, (int(px - sp.width / 2), int(py - sp.height / 2)))
    # needle: swings from high (330deg) down to low (205deg) with overshoot
    k = ease_out_elastic(clamp((lt - 0.35) / 1.1))
    ang = 335 + (205 - 335) * k
    nx = cx + (r - 30) * math.cos(math.radians(ang)); ny = cy + (r - 30) * math.sin(math.radians(ang))
    d.line((cx, cy, nx, ny), fill=WHITE, width=12)
    d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=GOLD, outline=BLACK, width=3)
    sp = shadowed(panel)
    paste_c(cv, sp, 540, 545, scale=0.5 + 0.5 * sc, alpha=clamp(lt / 0.12) * out_a)
    # kinetic words
    for txt, ts, col, size, y in (("LOW COST", o(24.32), GOLD, 120, 870), ("MAINTENANCE", o(25.3), WHITE, 92, 985)):
        l2 = t - ts + 0.05
        if l2 <= 0: continue
        s2 = text_sprite(txt, F_HEAD, size, fill=col, stroke=7, stroke_fill=BLACK)
        paste_c(cv, s2, 540, y, scale=1 + 0.6 * (1 - ease_out_cubic(l2 / 0.22)), alpha=clamp(l2 / 0.08) * out_a)
    l3 = t - o(25.9)
    if l3 > 0:
        paste_c(cv, emoji("✅", 110), 950, 870, scale=ease_out_back(l3 / 0.3, 3), alpha=out_a)

# ---------------------------------------------------------------- penat naik motor
def draw_motor(cv, t):
    a, b = o(39.9), o(44.42)
    if not (a <= t < b): return
    lt, rt = t - a, b - t
    out_a = clamp(rt / 0.2)
    sp = text_sprite("PENAT ULANG-ALIK?", F_HEAD, 92, fill=WHITE, stroke=7, stroke_fill=BLACK)
    if sp.width > 980: sp = scaled(sp, 980 / sp.width)
    paste_c(cv, sp, 540, 360, scale=ease_out_back(lt / 0.3, 2), alpha=out_a)
    l2 = t - o(43.25)
    if l2 > 0:
        tag = text_sprite("NAIK MOTOR", F_HEAD, 120, fill=GOLD, stroke=8, stroke_fill=BLACK)
        e = emoji("🛵", 140)
        cx = 540
        paste_c(cv, e, 540, 660, scale=ease_out_back(l2 / 0.3, 2.5), alpha=out_a)
        paste_c(cv, tag, cx, 515, scale=ease_out_back(l2 / 0.3, 2), alpha=out_a)
        # red strike-through wipe
        l3 = l2 - 0.35
        if l3 > 0:
            wv = int((tag.width + 200) * ease_out_cubic(l3 / 0.25))
            if wv > 4:
                bar = Image.new("RGBA", (wv, 22), RED + (255,))
                paste_c(cv, bar.rotate(-4, expand=True, resample=Image.BICUBIC), cx - (tag.width + 200) / 2 + wv / 2, 515, alpha=out_a)

# ---------------------------------------------------------------- family
def draw_family(cv, t):
    a, b = o(54.5), o(55.6)
    l1 = t - o(52.3)
    if o(51.9) <= t < b:
        out_a = clamp((b - t) / 0.2)
        if l1 > 0:
            sp = text_sprite("KERETA KEDUA", F_HEAD, 96, fill=WHITE, stroke=7, stroke_fill=BLACK)
            paste_c(cv, sp, 540, 360, scale=ease_out_back(l1 / 0.3, 2), alpha=out_a)
        lt = t - a
        if lt > 0:
            sp = text_sprite("UNTUK FAMILY", F_HEAD, 118, fill=GOLD, stroke=8, stroke_fill=BLACK)
            paste_c(cv, sp, 540, 500, scale=1 + 0.7 * (1 - ease_out_cubic(lt / 0.22)), alpha=clamp(lt / 0.08) * out_a)
            paste_c(cv, emoji("🏠", 130), 540, 660, scale=ease_out_back((lt - 0.2) / 0.35, 3), alpha=out_a)

# ---------------------------------------------------------------- CTA
def draw_cta(cv, t):
    # 'dapatkan kereta saga' question
    a = o(56.56)
    if a <= t < o(58.0):
        lt = t - a
        sp = text_sprite("NAK DAPATKAN SAGA?", F_HEAD, 84, fill=WHITE, stroke=6, stroke_fill=BLACK)
        paste_c(cv, sp, 540, 330, scale=ease_out_back(lt / 0.3, 2), alpha=clamp((o(58.0) - t) / 0.12))
    a = o(58.08) - 0.04
    if a <= t < NARR_END:
        lt = t - a
        stamp = ready_stock_sprite()
        sc = 1 + 1.4 * (1 - ease_out_cubic(lt / 0.2))
        paste_c(cv, stamp, 540, 370, scale=sc, alpha=clamp(lt / 0.06), rot=6 if lt > 0 else 6)
    a = o(59.78) - 0.05
    if a <= t < NARR_END:
        lt = t - a
        btn = cta_button()
        pulse = 1 + 0.04 * math.sin(lt * 10) if lt > 0.4 else ease_out_back(lt / 0.4, 2.2)
        paste_c(cv, btn, 520, 1110, scale=pulse)
    a = o(60.85) - 0.1
    if a <= t < NARR_END:
        lt = t - a
        for i in range(3):
            ph = (lt * 2.2 - i * 0.18) % 1.0
            al = clamp(math.sin(ph * math.pi)) * clamp(lt / 0.2)
            paste_c(cv, chevron(), 520, 1450 + i * 44 + 10 * ph, alpha=al)

@functools.lru_cache(1)
def ready_stock_sprite():
    tx = text_sprite("READY STOCK", F_HEAD, 120, fill=BLACK, shadow=False)
    w, h = tx.width + 90, tx.height + 60
    im = rounded(w, h, 18, GOLD, outline=WHITE, width=8)
    im.alpha_composite(tx, (45, 30))
    return shadowed(im, blur=18, off=(0, 14), op=180)

@functools.lru_cache(1)
def cta_button():
    tx = text_sprite("TEKAN BEG BIRU", F_HEAD, 70, fill=WHITE, shadow=False)
    e = emoji("🛍", 80)
    w, h = tx.width + e.width + 120, max(tx.height, e.height) + 56
    im = rounded(w, h, h // 2, (22, 110, 235), outline=WHITE, width=6)
    im.alpha_composite(e, (44, h // 2 - e.height // 2))
    im.alpha_composite(tx, (44 + e.width + 26, h // 2 - tx.height // 2))
    return shadowed(im, blur=16, off=(0, 12), op=170)

@functools.lru_cache(1)
def chevron():
    im = Image.new("RGBA", (130, 70), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.line((10, 10, 65, 55, 120, 10), fill=BLACK, width=26, joint="curve")
    d.line((10, 10, 65, 55, 120, 10), fill=GOLD, width=16, joint="curve")
    return im

# ---------------------------------------------------------------- brand lower third (first A-roll)
def draw_lower_third(cv, t):
    a, b = o(9.8), o(13.4)
    if not (a <= t < b): return
    lt, rt = t - a, b - t
    k = ease_out_cubic(lt / 0.4) if rt > 0.3 else ease_out_cubic(rt / 0.3)
    w = int(560 * k)
    if w < 10: return
    im = Image.new("RGBA", (580, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 10, 119), fill=GOLD)
    d.rectangle((10, 0, w, 72), fill=PANEL + (230,))
    d.rectangle((10, 72, int(w * 0.8), 119), fill=GOLD + (255,))
    l1 = text_sprite("BANG TAF MOTORSPORT", F_HEAD, 40, fill=WHITE, shadow=False)
    l2 = text_sprite("PROTON SAGA", F_XB, 28, fill=BLACK, shadow=False, tracking=2)
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rectangle((0, 0, w, 120), fill=255)
    tmp = Image.new("RGBA", im.size, (0, 0, 0, 0))
    tmp.alpha_composite(l1, (26, 36 - l1.height // 2)); tmp.alpha_composite(l2, (26, 96 - l2.height // 2))
    tmp.putalpha(Image.fromarray(np.minimum(np.asarray(tmp.split()[3]), np.asarray(m))))
    im.alpha_composite(tmp)
    paste_xy(cv, shadowed(im, blur=10), 40 - 30, 1080 - 30)

# ---------------------------------------------------------------- end card
@functools.lru_cache(1)
def endcard_bg():
    last = R["IMG_1117"].get(4.5).copy()
    bg = last.filter(ImageFilter.GaussianBlur(28))
    bg = ImageEnhance.Brightness(bg).enhance(0.35).convert("RGBA")
    stripes = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(stripes)
    for i in range(-H, W + H, 26):
        d.line((i, 0, i + H, H), fill=(255, 255, 255, 10), width=8)
    bg.alpha_composite(stripes)
    return bg

def draw_endcard(cv, t):
    lt = t - NARR_END
    if lt < 0: return
    bg = endcard_bg()
    a = clamp(lt / 0.25)
    cv.alpha_composite(with_alpha(bg, a))
    lg = shadowed(scaled(LOGO, 820 / LOGO.width), blur=20, op=200)
    sc = 0.6 + 0.4 * ease_out_back((lt - 0.05) / 0.5, 1.8)
    paste_c(cv, lg, 540, 700 + 8 * math.sin(lt * 2), scale=sc, alpha=clamp((lt - 0.05) / 0.2))
    l2 = lt - 0.45
    if l2 > 0:
        s1 = text_sprite("PROTON SAGA", F_HEAD, 96, fill=WHITE, stroke=5)
        paste_c(cv, s1, 540, 1070, alpha=clamp(l2 / 0.2), scale=ease_out_back(l2 / 0.35, 1.6))
        s2 = ready_stock_sprite()
        paste_c(cv, s2, 540, 1215, alpha=clamp((l2 - 0.15) / 0.2), scale=0.62 * ease_out_back((l2 - 0.15) / 0.35, 2))
    l3 = lt - 0.9
    if l3 > 0:
        paste_c(cv, cta_button(), 520, 1390, scale=0.82 * (ease_out_back(l3 / 0.35, 2) if l3 < 0.35 else 1 + 0.03 * math.sin(l3 * 9)))
    # fade to black last 0.25s
    fb = clamp((t - (TOTAL - 0.3)) / 0.3)
    if fb > 0: cv.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fb))))

# ---------------------------------------------------------------- transitions
def transition_fx(cv, t):
    for c in CUTS:
        lt = t - c
        if 0 <= lt < 0.12:
            cv.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(110 * (1 - lt / 0.12)))))
    lt = t - NARR_END
    if 0 <= lt < 0.15:
        cv.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(150 * (1 - lt / 0.15)))))

def shake(t):
    for ts, amp in ((o(58.08), 22), (o(7.92), 12), (o(24.32), 10)):
        lt = t - ts
        if 0 <= lt < 0.3:
            k = amp * (1 - lt / 0.3)
            return int(k * math.sin(lt * 90)), int(k * math.cos(lt * 70))
    return 0, 0

def motion_blur(img, t):
    """short directional smear on the first frames after a cut (zoom-whip feel)"""
    for c in CUTS:
        lt = t - c
        if 0 <= lt < 0.1:
            k = 1 - lt / 0.1
            small = img.resize((W // 4, H // 4), Image.BILINEAR)
            a = np.asarray(small).astype(np.float32)
            n = int(2 + 10 * k)
            acc = sum(np.roll(a, i, axis=0) for i in range(-n, n + 1)) / (2 * n + 1)
            bl = Image.fromarray(acc.astype(np.uint8)).resize((W, H), Image.BILINEAR)
            return Image.blend(img, bl, 0.65 * k)
    return img

# ---------------------------------------------------------------- frame
def render(t):
    img = base_frame(min(t, NARR_END - 1e-3))
    img = motion_blur(img, t)
    dx, dy = shake(t)
    if dx or dy:
        img = img.resize((W + 60, H + 106), Image.BILINEAR).crop((30 + dx, 53 + dy, 30 + dx + W, 53 + dy + H))
    cv = img.convert("RGBA")
    cv.alpha_composite(VIGNETTE)
    if t < NARR_END:
        draw_hook(cv, t); draw_saga(cv, t); draw_cards(cv, t); draw_lower_third(cv, t)
        draw_maintenance(cv, t); draw_motor(cv, t); draw_family(cv, t); draw_cta(cv, t)
        draw_subs(cv, t)
        if t > 0.6:
            paste_xy(cv, LOGO_SMALL, 30, 150, alpha=0.92 * clamp((t - 0.6) / 0.3))
    transition_fx(cv, t)
    draw_endcard(cv, t)
    return cv.convert("RGB")

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "still":
        for ts in sys.argv[2:]:
            t = float(ts)
            render(t).save(os.path.join(ROOT, os.environ.get("STILLS", "stills"), "f_%06.2f.jpg" % t), quality=88)
    elif mode == "video":
        out = sys.argv[2]
        a0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0
        a1 = float(sys.argv[4]) if len(sys.argv) > 4 else TOTAL
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
                                "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "15",
                                "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
        n0, n1 = int(round(a0 * FPS)), int(round(a1 * FPS))
        for i in range(n0, n1):
            enc.stdin.write(render(i / FPS).tobytes())
            if i % 60 == 0: print("frame", i, "/", n1, flush=True)
        enc.stdin.close(); enc.wait()

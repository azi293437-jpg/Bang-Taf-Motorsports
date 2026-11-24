"""Builds narration (cleaned), original synthesized music bed and SFX, then mixes."""
import os, subprocess, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt
import render as RD
from timeline import *

SR = 48000
ROOT = RD.ROOT
B = HERE
N = int(TOTAL * SR) + SR // 2
rng = np.random.default_rng(7)

def load_src():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(ROOT, "src", "IMG_1132.MOV"), "-map", "0:a:0",
                          "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)

def narration():
    a = load_src(); out = np.zeros(N, np.float32)
    f = int(0.025 * SR)
    for o0, o1, s0, s1 in MAP:
        seg = a[int(s0 * SR):int(s1 * SR)].copy()
        ramp = np.linspace(0, 1, f)
        seg[:f] *= ramp; seg[-f:] *= ramp[::-1]
        i = int(o0 * SR); out[i:i + len(seg)] += seg
    wavfile.write(os.path.join(B, "narr_raw.wav"), SR, out)
    # denoise + clean voice chain
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(B, "narr_raw.wav"), "-af",
                    "highpass=f=85,afftdn=nr=14:nf=-30:tn=1,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3500:t=q:w=1.0:g=3,"
                    "acompressor=threshold=-20dB:ratio=3.5:attack=8:release=120:makeup=4,alimiter=limit=0.89",
                    "-ar", str(SR), "-ac", "1", os.path.join(B, "narr.wav")], check=True)

# ------------------------------------------------------------------ synth helpers
def env(n, a, d, s=0.0, r=0.0):
    e = np.ones(n, np.float32) * s
    na, nd = int(a * SR), int(d * SR)
    e[:na] = np.linspace(0, 1, na)
    e[na:na + nd] = np.linspace(1, s, len(e[na:na + nd]))
    return e

def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, "low", fs=SR, output="sos"), x).astype(np.float32)

def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, "high", fs=SR, output="sos"), x).astype(np.float32)

def bp(x, f1, f2):
    return sosfilt(butter(2, [f1, f2], "band", fs=SR, output="sos"), x).astype(np.float32)

def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= len(buf) or i + len(x) <= 0: return
    if i < 0: x = x[-i:]; i = 0
    x = x[:len(buf) - i]; buf[i:i + len(x)] += g * x

def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 50 + 110 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t * 7) + 0.3 * np.tanh(4 * np.sin(ph)) * np.exp(-t * 25)).astype(np.float32)

def clap():
    n = int(0.3 * SR); x = rng.standard_normal(n).astype(np.float32)
    e = np.zeros(n, np.float32)
    for k in (0, 0.011, 0.022):
        i = int(k * SR); e[i:] += np.exp(-np.arange(n - i) / SR * (60 if k < 0.02 else 18))
    return bp(x * e, 900, 5000) * 0.8

def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR); x = rng.standard_normal(n).astype(np.float32)
    return hp(x, 7000) * np.exp(-np.arange(n) / SR * (12 if open_ else 70)).astype(np.float32) * 0.5

def saw(freq, dur, detune=(0,)):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for d in detune:
        f = freq * 2 ** (d / 1200)
        out += 2 * ((t * f + rng.random()) % 1) - 1
    return (out / len(detune)).astype(np.float32)

def midi(m): return 440 * 2 ** ((m - 69) / 12)

# ------------------------------------------------------------------ music
BPM = 112
BEAT = 60 / BPM
BAR = 4 * BEAT
CHORDS = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [55, 60, 64]), (55, [55, 59, 62])]  # Am F C G

def music():
    drums = np.zeros(N, np.float32); bass = np.zeros(N, np.float32); pad = np.zeros(N, np.float32); arp = np.zeros(N, np.float32)
    K, C, H, HO = kick(), clap(), hat(), hat(True)
    drop = RD.o(6.76) - 0.0          # beat drops at "ini ada kereta Saga"
    # align grid so that a downbeat lands on the drop
    start = drop - BAR * 2
    end = NARR_END
    t = start; bar = 0
    while t < TOTAL:
        root, notes = CHORDS[bar % 4]
        intro = t < drop - 1e-3
        outro = t >= end - 1e-3
        # pad (always, filtered in intro)
        dur = BAR
        p = sum(saw(midi(n), dur, (-12, -4, 5, 13)) for n in notes) / 3
        p = lp(p, 900 if intro else 1800) * env(len(p), 0.25, 0.1, 0.8)[:len(p)]
        p[-int(0.2 * SR):] *= np.linspace(1, 0, int(0.2 * SR))
        add(pad, p, t, 0.16)
        if not outro:
            for b in range(4):
                bt = t + b * BEAT
                if not intro:
                    add(drums, K, bt, 0.9)
                    if b in (1, 3): add(drums, C, bt, 0.45)
                    if b == 3: add(drums, K, bt + BEAT * 0.75, 0.45)
                for s in range(4):
                    st = bt + s * BEAT / 4
                    if intro and s % 2: continue
                    add(drums, HO if (s == 2 and not intro) else H, st, (0.35 if s % 2 == 0 else 0.2) * (0.6 if intro else 1))
                # bass 8ths
                if not intro:
                    for e8 in range(2):
                        n = int(BEAT / 2 * SR)
                        f = midi(root - 24 + (12 if (b == 3 and e8 == 1) else 0))
                        tt = np.arange(n) / SR
                        x = (np.sin(2 * np.pi * f * tt) + 0.35 * np.tanh(3 * np.sin(2 * np.pi * f * tt))) * np.exp(-tt * 4)
                        x[-200:] *= np.linspace(1, 0, 200)
                        add(bass, x.astype(np.float32), bt + e8 * BEAT / 2, 0.5)
                # arp 16ths (pluck)
                seq = notes + [notes[1] + 12]
                for s in range(4):
                    if intro and (bar % 2 == 0): break
                    n = int(BEAT / 4 * SR * 0.95)
                    x = saw(midi(seq[(b * 4 + s) % 4] + 12), n / SR, (-6, 6))
                    x = lp(x, 3200) * np.exp(-np.arange(n) / SR * 18).astype(np.float32)
                    add(arp, x, bt + s * BEAT / 4, 0.11)
        t += BAR; bar += 1
    # simple stereo-ish reverb on pad/arp via comb sum
    def verb(x, g=0.3):
        y = x.copy()
        for d, a in ((0.037, 0.5), (0.053, 0.45), (0.071, 0.4), (0.113, 0.3), (0.157, 0.25)):
            i = int(d * SR); y[i:] += a * g * x[:-i]
        return lp(y, 6000)
    m = drums + bass + verb(pad, 0.6) + verb(arp, 0.8)
    # intro high-pass sweep / riser to the drop
    t0 = int(start * SR) if start > 0 else 0
    # fade-in from video start
    m[:int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
    return m.astype(np.float32)

# ------------------------------------------------------------------ SFX
def whoosh(d=0.45, up=True):
    n = int(d * SR); x = rng.standard_normal(n).astype(np.float32)
    t = np.linspace(0, 1, n)
    out = np.zeros(n, np.float32); hop = 1024
    for i in range(0, n, hop):
        k = t[i]; fc = 300 + 5000 * (k if up else 1 - k) ** 1.5
        out[i:i + hop] = bp(x[i:i + hop], max(100, fc * 0.6), min(20000, fc * 1.4 + 200))
    e = np.sin(np.pi * t) ** 2
    return lp(out * e, 8000) * 2.2

def pop():
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = 900 * np.exp(-t * 25) + 300
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)).astype(np.float32) * 0.7

def impact():
    n = int(1.6 * SR); t = np.arange(n) / SR
    f = 38 + 80 * np.exp(-t * 12)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.5)
    nz = lp(rng.standard_normal(n).astype(np.float32), 2500) * np.exp(-t * 9)
    return (np.tanh(1.6 * boom) + 0.5 * nz).astype(np.float32) * 0.9

def ding():
    n = int(0.9 * SR); t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((1568, 1), (2349, 0.5), (3136, 0.25)))
    return (x * np.exp(-t * 6)).astype(np.float32) * 0.35

def riser(d):
    n = int(d * SR); t = np.linspace(0, 1, n)
    x = rng.standard_normal(n).astype(np.float32)
    out = np.zeros(n, np.float32); hop = 1024
    for i in range(0, n, hop):
        fc = 400 + 7000 * t[i] ** 2
        out[i:i + hop] = bp(x[i:i + hop], fc * 0.7, min(20000, fc * 1.3))
    tone = np.sin(2 * np.pi * np.cumsum(200 + 600 * t ** 2) / SR)
    return ((out * 1.5 + 0.15 * tone) * t ** 2).astype(np.float32)

def sfx():
    s = np.zeros(N, np.float32)
    o = RD.o
    for c in RD.CUTS: add(s, whoosh(0.4), c - 0.22, 0.45)
    add(s, impact(), 0.0, 0.55)                     # opening hit
    for ts in (o(2.64), o(3.86), o(4.8)): add(s, pop(), ts - 0.06, 0.5)
    add(s, pop(), o(5.3), 0.4)
    add(s, riser(1.4), o(6.76) - 1.4, 0.35)
    add(s, impact(), o(7.92) - 0.03, 0.6)           # SAGA
    for n, em, title, sub, a, b in RD.CARDS:
        add(s, whoosh(0.35), a - 0.05, 0.4); add(s, pop(), a + 0.3, 0.45)
    add(s, pop(), o(22.98), 0.4); add(s, whoosh(0.6, up=False), o(22.98) + 0.35, 0.3)
    add(s, impact(), o(24.32) - 0.03, 0.35); add(s, ding(), o(25.9), 0.8)
    add(s, pop(), o(39.9), 0.45); add(s, pop(), o(43.25), 0.5); add(s, whoosh(0.25), o(43.6), 0.4)
    add(s, pop(), o(52.3), 0.45); add(s, impact(), o(54.5) - 0.03, 0.35)
    add(s, pop(), o(56.56), 0.45)
    add(s, riser(1.0), o(58.08) - 1.0, 0.3); add(s, impact(), o(58.08) - 0.04, 0.75)
    add(s, pop(), o(59.78) - 0.05, 0.5)
    add(s, whoosh(0.5), NARR_END - 0.3, 0.5); add(s, impact(), NARR_END, 0.75)
    add(s, pop(), NARR_END + 0.45, 0.4); add(s, pop(), NARR_END + 0.9, 0.4)
    return s

if __name__ == "__main__":
    narration()
    m = music(); m = m / (np.abs(m).max() + 1e-6) * 0.8
    wavfile.write(os.path.join(B, "music.wav"), SR, m[:N])
    x = sfx(); x = np.clip(x, -1, 1)
    wavfile.write(os.path.join(B, "sfx.wav"), SR, x[:N])
    # mix: music ducked under voice (sidechain), sfx on top, final loudness for TikTok
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(B, "narr.wav"), "-i", os.path.join(B, "music.wav"),
                    "-i", os.path.join(B, "sfx.wav"), "-filter_complex",
                    "[0:a]asplit=2[v][sc];[1:a]volume=0.45[mu];[mu][sc]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350[duck];"
                    "[2:a]volume=0.6[fx];[v][duck][fx]amix=inputs=3:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000",
                    "-ac", "2", "-t", "%.3f" % TOTAL, os.path.join(B, "mix.wav")], check=True)
    print("ok")

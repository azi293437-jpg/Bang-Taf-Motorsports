"""Original synthesized score + sound design, mixed under the voice-over.

python build_audio.py <lang> <build_dir>   ->  <build_dir>/mix_<lang>.wav (48 kHz stereo)

Everything is generated procedurally with numpy/scipy (no third-party audio), so there are
no music licensing issues. Music is ducked under the narration with a sidechain envelope.
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000
DUR = 60.0
N = int(SR * DUR)
rng = np.random.default_rng(42)
T = np.arange(N) / SR


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env_adsr(n, a, d, s, r, sr=SR):
    a, d, r = int(a * sr), int(d * sr), int(r * sr)
    e = np.ones(n) * s
    if a: e[:a] = np.linspace(0, 1, a)
    if d: e[a:a + d] = np.linspace(1, s, min(d, max(0, n - a)))
    if r and n > r: e[-r:] *= np.linspace(1, 0, r)
    return e


def lp(x, fc, order=2):
    b, a = signal.butter(order, min(fc, SR * 0.45) / (SR / 2), 'low')
    return signal.lfilter(b, a, x)


def hp(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), 'high')
    return signal.lfilter(b, a, x)


def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi, SR * 0.45) / (SR / 2)], 'band')
    return signal.lfilter(b, a, x)


def saw(f, n, phase=0.0):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k in range(1, 24):
        if f * k > 14000: break
        out += np.sin(2 * np.pi * f * k * t + phase * k) / k
    return out * 0.55


def place(buf, x, t0, gain=1.0, pan=0.0):
    s = int(t0 * SR)
    if s >= len(buf) or s + len(x) <= 0: return
    if s < 0: x = x[-s:]; s = 0
    x = x[:len(buf) - s]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[s:s + len(x), 0] += x * gain * l * 1.414
    buf[s:s + len(x), 1] += x * gain * r * 1.414


def reverb(stereo, seconds=2.2, wet=0.25, seed=1):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    decay = np.exp(-np.linspace(0, 7, n))
    out = stereo.copy()
    for ch in range(2):
        ir = r.standard_normal(n) * decay
        ir = lp(ir, 6000)
        ir /= np.sqrt(np.sum(ir ** 2))
        out[:, ch] = stereo[:, ch] * (1 - wet) + signal.fftconvolve(stereo[:, ch], ir)[:len(stereo)] * wet
    return out


def intensity(t):
    """Arrangement curve (0..1) per scene."""
    pts = [(0, 0.25), (6.8, 0.35), (7.2, 0.5), (16.8, 0.55), (17.2, 0.65), (26.8, 0.7), (27.2, 0.8),
           (38.8, 0.8), (39.2, 0.85), (50.8, 0.9), (51.2, 1.0), (55.8, 1.0), (56.2, 0.75), (60, 0.5)]
    xs, ys = zip(*pts)
    return np.interp(t, xs, ys)


# ------------------------------------------------------------------ music
def music():
    out = np.zeros((N, 2))
    bpm = 100; beat = 60 / bpm; bar = beat * 4
    prog = [(50, [62, 65, 69]), (46, [62, 65, 70]), (53, [60, 65, 69]), (48, [60, 64, 67])]  # Dm Bb F C (roots + voicing)
    nbar = int(np.ceil(DUR / bar)) + 1
    # pads
    for b in range(nbar):
        t0 = b * bar; root, chord = prog[b % 4]
        n = int((bar + 1.2) * SR)
        pad = np.zeros(n)
        for m in chord + [root + 12]:
            for det in (-0.12, 0.0, 0.11):
                pad += saw(midi(m + det), n, phase=rng.uniform(0, 6))
        pad = lp(pad, 1400 + 900 * float(intensity(t0))) * env_adsr(n, 0.9, 0.5, 0.85, 1.4) * 0.05
        place(out, pad, t0 - 0.3, gain=1.0, pan=-0.2 if b % 2 else 0.2)
        # sub bass drone with gentle 8th pulse
        nb = int(bar * SR)
        tb = np.arange(nb) / SR
        pulse = 0.55 + 0.45 * (1 - ((tb / (beat / 2)) % 1)) ** 2
        sub = np.sin(2 * np.pi * midi(root - 12) * tb) * pulse * env_adsr(nb, 0.05, 0.1, 1, 0.2) * 0.22
        place(out, sub, t0)
    # arpeggio (from scene 2)
    step = beat / 4
    k = 0
    t = 7.0
    while t < 56.0:
        b = int(t / bar); root, chord = prog[b % 4]
        notes = chord + [chord[0] + 12, chord[1] + 12]
        m = notes[[0, 2, 1, 3, 2, 4, 1, 3][k % 8]] + 12
        n = int(0.32 * SR)
        tt = np.arange(n) / SR
        tone = (signal.sawtooth(2 * np.pi * midi(m) * tt, 0.5) * 0.6 + np.sin(2 * np.pi * midi(m) * tt))
        tone = lp(tone * np.exp(-tt * 14), 2600 + 2400 * float(intensity(t)))
        g = 0.045 * float(intensity(t)) * (1.0 if k % 4 == 0 else 0.7)
        place(out, tone, t, gain=g, pan=0.45 if k % 2 else -0.45)
        place(out, tone, t + beat * 0.75, gain=g * 0.35, pan=-0.6 if k % 2 else 0.6)  # ping-pong delay
        t += step; k += 1
    # kick + ticks (from scene 3)
    kn = int(0.45 * SR); kt = np.arange(kn) / SR
    kick = np.sin(2 * np.pi * (45 + 90 * np.exp(-kt * 30)) * kt) * np.exp(-kt * 7)
    tick = hp(rng.standard_normal(int(0.05 * SR)), 7000) * np.exp(-np.arange(int(0.05 * SR)) / SR * 90)
    t = 17.0
    while t < 56.0:
        i = float(intensity(t))
        place(out, kick, t, gain=0.32 * i)
        if t > 27: place(out, tick, t + beat / 2, gain=0.05 * i, pan=0.3)
        if t > 39: place(out, tick, t + beat / 4, gain=0.025 * i, pan=-0.3); place(out, tick, t + 3 * beat / 4, gain=0.025 * i, pan=-0.3)
        t += beat
    # final chord swell
    n = int(4.4 * SR)
    fin = np.zeros(n)
    for m in [50, 57, 62, 65, 69, 74]:
        fin += saw(midi(m), n, phase=rng.uniform(0, 6))
    fin = lp(fin, 2200) * env_adsr(n, 0.05, 0.6, 0.6, 2.6) * 0.06
    place(out, fin, 55.9)
    out = reverb(out, 2.8, 0.3, seed=2)
    return out


# ------------------------------------------------------------------ sfx
def noise(sec):
    return rng.standard_normal(int(sec * SR))


def whoosh(sec=0.9, lo=300, hi=6000):
    n = int(sec * SR); x = noise(sec)
    tt = np.linspace(0, 1, n)
    out = np.zeros(n); hop = 2048
    for s in range(0, n, hop):  # sweeping band-pass
        f = lo * (hi / lo) ** (np.sin(np.pi * tt[s]) ** 1.5)
        seg = bp(x[s:s + hop + 512], f * 0.6, f * 1.6, 1)[:hop]
        out[s:s + len(seg)] = seg
    return out * np.sin(np.pi * tt) ** 2 * 0.9


def impact(sec=2.2, depth=1.0):
    n = int(sec * SR); tt = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (28 + 70 * np.exp(-tt * 9)) * tt) * np.exp(-tt * 2.2)
    crack = lp(noise(sec), 1800) * np.exp(-tt * 18) * 0.6
    return (boom + crack) * depth


def riser(sec=1.6, f0=200, f1=1600):
    n = int(sec * SR); tt = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (tt / sec)
    ph = 2 * np.pi * np.cumsum(f) / SR
    trem = 0.7 + 0.3 * np.sin(2 * np.pi * 14 * tt)
    return (np.sin(ph) + 0.3 * np.sin(2 * ph)) * trem * (tt / sec) ** 1.5 * np.exp(-np.maximum(0, tt - sec + 0.15) * 30)


def blip(f=1800, sec=0.09, harm=True):
    n = int(sec * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * tt) + (0.3 * np.sin(2 * np.pi * f * 2 * tt) if harm else 0)
    return x * np.exp(-tt * 40)


def ping(f=1200, sec=1.2):
    n = int(sec * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * f * tt) * np.exp(-tt * 5) * (1 - np.exp(-tt * 400))


def scan(sec=1.0):
    n = int(sec * SR); tt = np.arange(n) / SR
    f = 600 + 2400 * tt / sec
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / sec) ** 2 * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 30 * tt)))


def click():
    n = int(0.025 * SR); tt = np.arange(n) / SR
    return bp(noise(0.025), 1500, 5000) * np.exp(-tt * 260)


def hum(sec):
    n = int(sec * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 55 * tt) * 0.5 + np.sin(2 * np.pi * 110.3 * tt) * 0.3 + lp(noise(sec), 300) * 0.4) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.2 * tt))


def sfx():
    out = np.zeros((N, 2))
    place(out, hum(DUR) * 0.04, 0)
    # scene 1
    place(out, impact(2.6, 1.0), 0.3, 0.55)
    place(out, whoosh(1.6, 200, 4000), 0.2, 0.18)
    place(out, riser(0.7, 300, 1400), 1.35, 0.10)
    for i, tt in enumerate([1.72, 1.86]): place(out, blip(2200 + i * 500), tt, 0.10, 0.2)
    place(out, scan(1.6), 2.9, 0.05, -0.3)
    for i, tt in enumerate([3.6, 4.1, 4.7, 5.3]): place(out, blip(1400 + i * 300, 0.12), tt, 0.10, -0.2 + 0.15 * i)
    # transitions
    for c in [7, 17, 27, 39, 51]:
        place(out, whoosh(0.9), c - 0.45, 0.32, 0)
        place(out, impact(1.6, 0.5), c, 0.22)
    for c in [6.0, 16.0, 26.0, 38.0, 50.0]: place(out, riser(1.0, 250, 1800), c, 0.05)
    # scene 2: mechanical ratchet, electronic glitch, intelligence shimmer
    t = 7.4
    while t < 9.7: place(out, click(), t, 0.35, -0.3); place(out, lp(click(), 900), t + 0.04, 0.25, 0.3); t += 0.085
    for i in range(9): place(out, blip(900 + 250 * (i % 4), 0.05), 9.85 + i * 0.06, 0.08, 0.5 * np.sin(i))
    for i, tt in enumerate([10.6, 11.1, 11.6]): place(out, blip(1600, 0.1), tt, 0.09, -0.3 + 0.3 * i)
    place(out, scan(1.2), 14.2, 0.07, 0.2)
    for i in range(6): place(out, ping(1800 + 200 * i, 0.6), 14.35 + i * 0.08, 0.03, -0.5 + 0.2 * i)
    # scene 3: data blips
    place(out, impact(1.8, 0.4), 17.2, 0.25)
    for i, tt in enumerate([20.9, 22.8, 23.5, 24.2, 24.8]):
        place(out, blip(1200 + 180 * i, 0.12), tt, 0.13, -0.5 + 0.25 * i)
        for k in range(4): place(out, blip(2600 + 300 * k, 0.03, False), tt + 0.15 + k * 0.05, 0.05, 0.4)
    for i in range(3): place(out, blip(1500 + 300 * i, 0.09), 25.45 + 0.22 * i, 0.1)
    # scene 4: scanning
    for tt in [27.7, 28.5, 29.3, 30.1]: place(out, scan(0.7), tt, 0.06, -0.4)
    for tt in [31.2, 31.5, 31.8, 32.1]: place(out, blip(1046, 0.12), tt, 0.12, 0.5); place(out, blip(1318, 0.12), tt + 0.12, 0.10, 0.5)
    for i in range(6): place(out, click(), 33.1 + i * 0.12, 0.25, -0.2)
    place(out, ping(1400, 0.9), 33.6, 0.07)
    for tt in np.arange(35.5, 38.8, 0.9): place(out, ping(880, 1.0), tt, 0.07, 0.1)
    place(out, blip(1100, 0.15), 36.0, 0.1)
    # scene 5: callout beeps
    for c0 in [39.0, 45.1]:
        place(out, scan(1.0), c0 + 0.1, 0.05)
        for i in range(4): place(out, blip(1300 + 200 * i, 0.1), c0 + 1.2 + i * 0.75, 0.11, -0.3 + 0.2 * i)
    place(out, whoosh(0.8), 44.75, 0.2)
    # scene 6
    t = 51.3
    while t < 55.7: place(out, whoosh(0.5, 800, 7000), t, 0.05, rng.uniform(-0.8, 0.8)); t += 0.55
    place(out, whoosh(0.9, 400, 5000), 53.7, 0.16)
    place(out, riser(1.3, 200, 2400), 54.6, 0.09)
    place(out, impact(3.2, 1.0), 55.9, 0.6)
    for i in range(8): place(out, ping(2093 * (1 + 0.5 * (i % 3)), 1.4), 56.0 + i * 0.07, 0.025, -0.7 + 0.2 * i)
    place(out, blip(1600, 0.1), 57.35, 0.12); place(out, blip(2100, 0.1), 57.45, 0.1)
    return reverb(out, 1.8, 0.22, seed=3)


def duck_env(vo):
    a = np.abs(vo)
    win = int(0.03 * SR)
    rms = np.sqrt(np.convolve(a ** 2, np.ones(win) / win, 'same'))
    on = (rms > 0.02).astype(float)
    # attack 40 ms, release 450 ms
    out = np.zeros_like(on); g = 0.0
    att, rel = np.exp(-1 / (0.04 * SR)), np.exp(-1 / (0.45 * SR))
    for i in range(0, len(on), 64):
        target = on[i]
        k = att if target > g else rel
        g = target + (g - target) * k ** 64
        out[i:i + 64] = g
    return out


def main():
    lang, build = sys.argv[1], Path(sys.argv[2])
    vo, sr = sf.read(build / f'vo_{lang}.wav')
    assert sr == SR
    if vo.ndim > 1: vo = vo.mean(1)
    vo = np.pad(vo, (0, max(0, N - len(vo))))[:N]
    # voice polish: high-pass, gentle presence lift, light compression
    v = hp(vo, 80)
    v = v + 0.25 * bp(v, 2500, 6000)
    v = v / (np.max(np.abs(v)) + 1e-9)
    thr = 0.12
    mag = np.abs(v); comp = np.where(mag > thr, thr + (mag - thr) / 4, mag)
    v = np.sign(v) * comp
    v = v / (np.max(np.abs(v)) + 1e-9) * 0.9
    voice = np.stack([v, v], 1)
    voice = reverb(voice, 0.9, 0.07, seed=4)

    mus = music(); fx = sfx()
    d = duck_env(v)[:, None]
    mus_g = 0.45 * (1 - 0.55 * d)
    fx_g = 0.6 * (1 - 0.45 * d)
    mix = voice * 1.0 + mus * mus_g + fx * fx_g
    fade = np.ones(N); fade[-int(0.8 * SR):] = np.linspace(1, 0, int(0.8 * SR)) ** 1.5
    mix *= fade[:, None]
    mix = np.tanh(mix * 1.1) / 1.1
    mix /= np.max(np.abs(mix)) + 1e-9
    mix = mix * 0.9
    # loudness-normalise to -14 LUFS (social platform target), true peak kept below -1 dBTP
    tmp = build / f'_tmp_{lang}.wav'
    sf.write(tmp, mix.astype(np.float32), SR, subtype='FLOAT')
    import re, subprocess
    log = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(tmp), '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    lufs = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', log)[-1])
    gain = 10 ** ((-14.0 - lufs) / 20)
    mix = mix * min(gain, 0.89 / np.max(np.abs(mix)))
    tmp.unlink()
    print(f'integrated {lufs:.1f} LUFS -> gain {20 * np.log10(gain):+.1f} dB')
    sf.write(build / f'mix_{lang}.wav', mix.astype(np.float32), SR, subtype='PCM_24')
    sp = d[:, 0] > 0.5
    db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
    bed = (mus * mus_g + fx * fx_g).mean(1)
    print(f'voice {db(v[sp]):.1f} dB | music+sfx under voice {db(bed[sp]):.1f} dB | in gaps {db(bed[~sp]):.1f} dB')
    sf.write(build / 'music_sfx_bed.wav', (np.clip(mus * 0.55 + fx * 0.75, -1, 1) * 0.8).astype(np.float32), SR, subtype='PCM_24')
    print('mix written', build / f'mix_{lang}.wav')


if __name__ == '__main__':
    main()

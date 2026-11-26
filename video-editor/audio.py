import sys, os, subprocess, wave, importlib.util
import numpy as np
S = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location('render', os.path.join(S, 'render.py')); R = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(R)
SR = 44100; FPS = R.FPS; SPEED = R.SPEED
OUT = S + '/out'; os.makedirs(OUT, exist_ok=True)
pieces = R.pieces; SPEECH = R.TOTAL / FPS; TOTAL = (R.TOTAL + R.OUT_N) / FPS

# ---------- 1. voice: cut, speed, clean, normalise
ins = {'A': 0, 'B': 1, 'C': 2}
fl = []
for k, p in enumerate(pieces):
    d = p['n'] / FPS * SPEED
    fl.append(f"[{ins[p['clip']]}:a]atrim=start={p['s']:.4f}:duration={d:.4f},asetpts=PTS-STARTPTS,"
              f"afade=t=in:d=0.012,afade=t=out:st={d - 0.025:.4f}:d=0.025,atempo={SPEED}[a{k}]")
fl.append(''.join(f'[a{k}]' for k in range(len(pieces))) + f'concat=n={len(pieces)}:v=0:a=1,'
          'pan=mono|c0=0.5*c0+0.5*c1,highpass=f=85,afftdn=nf=-30,'
          'equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3500:t=q:w=1:g=2.5,'
          'acompressor=threshold=-20dB:ratio=3:attack=6:release=120:makeup=2,'
          'loudnorm=I=-16:TP=-2:LRA=7,aresample=44100[v]')
open(OUT + '/voice_filter.txt', 'w').write(';\n'.join(fl))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', R.CLIPS['A'], '-i', R.CLIPS['B'], '-i', R.CLIPS['C'],
                '-filter_complex_script', OUT + '/voice_filter.txt', '-map', '[v]', '-ac', '1', '-ar', str(SR), OUT + '/voice.wav'], check=True)

def load(p):
    w = wave.open(p); n = w.getnframes(); ch = w.getnchannels()
    a = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
    return a.reshape(-1, ch).mean(1) if ch > 1 else a
voice = load(OUT + '/voice.wav')
N = int(TOTAL * SR) + SR // 2
v = np.zeros(N, np.float32); v[:min(N, len(voice))] = voice[:N]

# ---------- 2. music with ducking
mus = load(S + '/sfx/music.wav')
music = np.tile(mus, N // len(mus) + 1)[:N]
win = int(0.05 * SR)
env = np.sqrt(np.convolve(v ** 2, np.ones(win) / win, 'same'))
act = (env > 0.02).astype(np.float32)
# smooth activity (attack fast, release slow)
k = int(0.3 * SR); act = np.convolve(act, np.ones(k) / k, 'same'); act = np.clip(act * 2, 0, 1)
gain = 0.22 - 0.13 * act       # ~-13dB when idle, ~-21dB under voice
def piece_t(txt):
    for p in pieces:
        if txt in p['txt']: return p['f0'] / FPS, p['n'] / FPS
for key, hold in (('{TAK!}', 1.0), ('{TETAPI!}', 0.9)):
    t0, _ = piece_t(key); a = int((t0 - 0.05) * SR); b = int((t0 + hold) * SR)
    gain[a:b] = 0.0
    r = int(0.4 * SR); gain[b:b + r] *= np.linspace(0, 1, r)
fi = int(0.4 * SR); fo = int(1.5 * SR)
gain[:fi] *= np.linspace(0, 1, fi); gain[int(SPEECH * SR):] = 0.22; gain[-fo:] *= np.linspace(1, 0, fo)
mix = v * 1.0 + music * gain

# ---------- 3. sfx
SFX = {n: load(f'{S}/sfx/{n}.wav') for n in ['whoosh', 'pop', 'ding', 'kaching', 'boom', 'boing', 'riser', 'scratch', 'click', 'wahwah']}
VOL = dict(whoosh=0.30, pop=0.32, ding=0.22, kaching=0.35, boom=0.45, boing=0.40, riser=0.28, scratch=0.45, click=0.25, wahwah=0.30)
ev = []
for o in R.overlays:
    p = o.p
    if p.get('sfx'): ev.append((o.t0, p['sfx']))
    if o.kind in ('list', 'icons', 'chips', 'qcards', 'stats'):
        for it in p['items']:
            if abs(it[-1] - o.t0) > 0.05: ev.append((it[-1], 'click' if o.kind == 'list' else 'pop'))
    if o.kind == 'compare': ev += [(p['t1'], 'pop'), (p['t2'], 'pop'), (p['t3'], 'boom')]
    if o.kind == 'tenor': ev += [(p['t1'], 'pop'), (p['t2'], 'ding'), (p['t3'], 'wahwah')]
    if o.kind == 'strike': ev.append((p['strike_at'], 'scratch'))
for p in pieces:
    if p['i'] > 0 and pieces[p['i'] - 1]['op'].get('bg') != p['op'].get('bg'):
        t = p['f0'] / FPS
        if not any(abs(t - e[0]) < 0.25 and e[1] == 'whoosh' for e in ev): ev.append((t - 0.12, 'whoosh'))
t0, _ = piece_t('{TETAPI!}'); ev.append((t0 - 1.0, 'riser'))
ev += [(SPEECH - 0.15, 'whoosh'), (SPEECH + 0.05, 'boom'), (SPEECH + 0.45, 'pop')]
for t, n in ev:
    a = SFX[n] * VOL[n]; i = max(0, int(t * SR)); j = min(N, i + len(a))
    mix[i:j] += a[:j - i]
mix = np.tanh(mix * 0.95) / np.tanh(0.95)
w = wave.open(OUT + '/mix.wav', 'w'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
print('audio ok', TOTAL, 'sfx events', len(ev))

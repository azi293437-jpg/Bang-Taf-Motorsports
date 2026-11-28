"""Build the voice-over track + subtitle cues for one language.

python build_vo.py <lang en|ms> <models_dir> <out_dir>

Outputs in out_dir:
  vo_<lang>.wav      48 kHz mono voice-over, exactly 60 s
  cues_<lang>.json   subtitle cues [{start,end,show}] used by the renderer
  <title>.srt        subtitle file
"""
import json
import re
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

from tts import SR, EnglishTTS, MalayTTS

TOTAL = 60.0
OUT_SR = 48000
HERE = Path(__file__).parent


def trim(y, top_db=38):
    _, (a, b) = librosa.effects.trim(y, top_db=top_db, frame_length=1024, hop_length=128)
    a = max(0, a - int(0.02 * SR)); b = min(len(y), b + int(0.06 * SR))
    return y[a:b]


def deepen(y, f0_ratio=0.72, formant=0.92):
    """WORLD vocoder: lower pitch and formants (used for the Malay voice)."""
    import pyworld as pw
    x = y.astype(np.float64)
    f0, t = pw.harvest(x, SR, f0_floor=60, f0_ceil=400, frame_period=5)
    sp = pw.cheaptrick(x, f0, t, SR)
    ap = pw.d4c(x, f0, t, SR)
    n = sp.shape[1]
    idx = np.clip(np.arange(n) / formant, 0, n - 1)
    lo = np.floor(idx).astype(int); hi = np.minimum(lo + 1, n - 1); w = idx - lo
    sp2 = np.ascontiguousarray(sp[:, lo] * (1 - w) + sp[:, hi] * w)
    out = pw.synthesize(np.ascontiguousarray(f0 * f0_ratio), sp2, ap, SR, 5)
    return out.astype(np.float32)


def gap_after(text):
    return 0.34 if re.search(r'[.!?]$', text.strip()) else 0.16


def srt_time(t):
    ms = int(round(t * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


def main():
    lang, models, out_dir = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    out_dir.mkdir(parents=True, exist_ok=True)
    data = json.loads((HERE / 'script.json').read_text())
    L = data[lang]
    tts = EnglishTTS(models, voice='am_michael', speed=1.0) if lang == 'en' else MalayTTS(models, speed=1.0)
    base_speed = 1.0
    asr = None
    if lang == 'ms':  # pick the clearest of several takes per phrase using Whisper
        import difflib
        from transformers import pipeline
        asr = pipeline('automatic-speech-recognition', model=f'{models}/whisper')
        norm = lambda s: re.sub(r'[^a-z ]', '', s.lower())

        def clarity(y, text):
            y16 = librosa.resample(y, orig_sr=SR, target_sr=16000)
            hyp = asr(y16, generate_kwargs={'language': 'malay', 'max_new_tokens': 64})['text']
            return difflib.SequenceMatcher(None, norm(text), norm(hyp)).ratio()

    track = np.zeros(int(TOTAL * SR), np.float32)
    cues = []
    for sc in data['scenes']:
        phrases = L['vo'][str(sc['id'])]
        lead = 0.55 if sc['id'] == 1 else 0.30
        tail = 0.85 if sc['id'] == 6 else 0.30
        avail = sc['end'] - sc['start'] - lead - tail
        speed = base_speed
        for attempt in range(5):
            clips = []
            for i, p in enumerate(phrases):
                if asr is None:
                    clips.append(trim(tts.synth(p['say'], speed=speed, seed=i)))
                    continue
                takes = [trim(deepen(trim(tts.synth(p['say'], speed=speed, seed=k)))) for k in range(4)]
                scored = sorted(((clarity(y, p['say']), k, y) for k, y in enumerate(takes)), key=lambda x: -x[0])
                clips.append(scored[0][2])
            gaps = [gap_after(p['say']) for p in phrases[:-1]]
            need = sum(len(c) for c in clips) / SR + sum(gaps)
            print(f"[{lang}] scene {sc['id']} speed {speed:.2f}: {need:.2f}s / {avail:.2f}s")
            if need <= avail:
                break
            if speed >= 1.17:
                print('  WARNING: still long; phrases will use the scene tail')
                break
            speed = min(1.18, speed * min(1.06, need / avail + 0.01))
        # spread any spare time: a little more breathing room between phrases
        spare = max(0.0, avail - need)
        extra = min(0.12, spare / max(1, len(gaps))) if gaps else 0
        t = sc['start'] + lead
        for i, (p, c) in enumerate(zip(phrases, clips)):
            s = int(t * SR)
            track[s:s + len(c)] += c[:len(track) - s]
            d = len(c) / SR
            cues.append({'scene': sc['id'], 'start': round(t, 3), 'end': round(t + d, 3), 'show': p['show'], 'say': p['say']})
            t += d + (gaps[i] + extra if i < len(gaps) else 0)

    # subtitle display window: hold each cue until shortly before the next (max +0.6 s)
    for i, c in enumerate(cues):
        nxt = cues[i + 1]['start'] if i + 1 < len(cues) else TOTAL
        c['hold'] = round(min(nxt - 0.04, c['end'] + 0.6), 3)

    peak = np.max(np.abs(track)) + 1e-9
    track = track / peak * 0.89
    track48 = librosa.resample(track, orig_sr=SR, target_sr=OUT_SR)
    sf.write(out_dir / f'vo_{lang}.wav', track48, OUT_SR, subtype='PCM_24')
    (out_dir / f'cues_{lang}.json').write_text(json.dumps(cues, ensure_ascii=False, indent=1))
    srt = []
    for i, c in enumerate(cues, 1):
        srt.append(f"{i}\n{srt_time(c['start'])} --> {srt_time(c['hold'])}\n{c['show'].replace('*', '')}\n")
    (out_dir / f"{L['title']}.srt").write_text('\n'.join(srt), encoding='utf-8')
    print('done', out_dir)


if __name__ == '__main__':
    main()

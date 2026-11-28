"""QA: transcribe each voice-over cue with Whisper and compare with the script."""
import json, sys, difflib, re
import librosa
from transformers import pipeline
lang, models, build = sys.argv[1:4]
asr = pipeline('automatic-speech-recognition', model=f'{models}/whisper')
y, sr = librosa.load(f'{build}/{sys.argv[4] if len(sys.argv)>4 else "vo_"+lang}.wav', sr=16000)
norm = lambda s: re.sub(r'[^a-z0-9 ]', '', s.lower().replace('-', ' '))
scores = []
for c in json.load(open(f'{build}/cues_{lang}.json')):
    seg = y[int(c['start'] * sr): int(c['end'] * sr)]
    txt = asr(seg, generate_kwargs={'language': 'english' if lang == 'en' else 'malay', 'max_new_tokens': 64})['text'].strip()
    r = difflib.SequenceMatcher(None, norm(c['say']), norm(txt)).ratio()
    scores.append(r)
    print(f"{c['start']:6.2f}-{c['end']:6.2f} {r:.2f} | {c['say']}\n{'':19}-> {txt}")
print('mean similarity', round(sum(scores) / len(scores), 3))

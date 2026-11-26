import sys, json, wave, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=4)
for p in sys.argv[1:]:
    segs, info = m.transcribe((lambda w:(np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768))(wave.open(p)), language="ms", word_timestamps=True, vad_filter=False, beam_size=5)
    out=[]
    for s in segs:
        out.append({"start":s.start,"end":s.end,"text":s.text,"words":[{"w":w.word,"s":w.start,"e":w.end,"p":w.probability} for w in s.words]})
    json.dump(out, open(p.replace(".wav",".json"),"w"), ensure_ascii=False, indent=0)
    print("done", p, flush=True)

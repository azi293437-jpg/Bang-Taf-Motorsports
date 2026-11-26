import sys, json, wave, re, numpy as np
from faster_whisper import WhisperModel
S=sys.argv[1]; m=WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=4)
for clip in sys.argv[2:]:
    w=wave.open(f'{S}/work/{clip}.wav'); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    dur=len(a)/16000
    sil=[tuple(map(float,re.findall(r'[0-9.]+',l))) for l in open(f'{S}/work/sil_{clip}.txt') if l.strip()]
    sil=[(s[0],s[1] if len(s)>1 else dur) for s in sil]
    isl=[]; cur=0.
    for s,e in sil:
        if s-cur>0.08: isl.append([cur,s])
        cur=e
    if dur-cur>0.08: isl.append([cur,dur])
    out=[]
    for s,e in isl:
        seg=a[int(max(0,s-0.15)*16000):int(min(dur,e+0.15)*16000)]
        segs,_=m.transcribe(seg,language="ms",word_timestamps=True,beam_size=5,condition_on_previous_text=False)
        words=[]; 
        for sg in segs:
            for x in sg.words: words.append({"w":x.word,"s":round(x.start+max(0,s-0.15),2),"e":round(x.end+max(0,s-0.15),2)})
        txt=''.join(x["w"] for x in words).strip()
        out.append({"s":round(s,2),"e":round(e,2),"text":txt,"words":words})
        print(f"{clip} {s:7.2f}-{e:7.2f} {txt}",flush=True)
    json.dump(out,open(f'{S}/work/isl_{clip}.json','w'),ensure_ascii=False)

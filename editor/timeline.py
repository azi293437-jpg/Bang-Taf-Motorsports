"""Edit decision list for the Bang Taf Motorsport - Proton Saga video.
All 'src' times refer to the narration clip IMG_1132 (seconds)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
W, H = 1080, 1920
END_CARD = 2.8

# narration blocks kept (src_in, src_out). Off-topic / repeated words removed.
BASE = [
    (2.52, 5.95),   # korang rasa, siapa yang patut pakai kereta ni?
    (6.76, 9.00),   # ini ada kereta Saga guys
    (9.60, 15.38),  # #1 fresh graduate
    (15.38, 21.42), # #2 mak ayah ... yang dah pencen
    (22.94, 26.20), # Proton Saga, memang low cost maintenance
    (30.22, 32.95), # #3 pasangan muda baru nak mula hidup guys  (spoken "yang kedua" removed)
    (35.04, 38.84), # #4 orang yang baru nak ada kereta guys
    # removed 38.84-41.78: repeated "sebelum ni korang dah penat ulang alik"
    (41.78, 46.42), # korang dah penat ulang alik naik motor guys, jadi ini sesuai untuk korang
    (46.78, 55.60), # #5 kereta kedua ... family
    (55.52, 61.60), # CTA
]
REMOVED = [(38.84, 41.78)]
GAP_MIN, GAP_PAD = 0.20, 0.07   # silences >= 0.20s are shrunk to 2*GAP_PAD

def _silences():
    import numpy as np
    from scipy.io import wavfile
    sr, a = wavfile.read(os.path.join(HERE, "..", "a1132.wav"))
    a = a.astype(np.float64) / 32768
    h = int(0.01 * sr); n = len(a) // h
    db = 20 * np.log10(np.sqrt((a[:n * h].reshape(n, h) ** 2).mean(1)) + 1e-9)
    q = db < np.percentile(db, 20) + 8
    out, i = [], 0
    while i < n:
        if q[i]:
            j = i
            while j < n and q[j]: j += 1
            if (j - i) * 0.01 >= GAP_MIN: out.append((i * 0.01 + GAP_PAD, j * 0.01 - GAP_PAD))
            i = j
        else: i += 1
    return out

def _subtract(a, b, cuts):
    pieces = [(a, b)]
    for c0, c1 in cuts:
        nxt = []
        for p0, p1 in pieces:
            if c1 <= p0 or c0 >= p1: nxt.append((p0, p1)); continue
            if c0 > p0: nxt.append((p0, c0))
            if c1 < p1: nxt.append((c1, p1))
        pieces = nxt
    return [p for p in pieces if p[1] - p[0] > 0.06]

SIL = _silences()
SEGMENTS = []
for a, b in BASE:
    SEGMENTS += _subtract(a, b, SIL)

def build_map():
    """returns list of (out_start, out_end, src_in, src_out)"""
    m, t = [], 0.0
    for a, b in SEGMENTS:
        m.append((t, t + (b - a), a, b))
        t += b - a
    return m

MAP = build_map()
NARR_END = MAP[-1][1]
TOTAL = NARR_END + END_CARD

def src2out(s):
    for o0, o1, a, b in MAP:
        if a - 0.02 <= s <= b + 0.02:
            return o0 + (min(max(s, a), b) - a)
    for o0, o1, a, b in MAP:      # inside a removed gap -> next kept piece
        if a > s: return o0
    return NARR_END

def piece_index(out_t):
    for i, m in enumerate(MAP):
        if m[0] <= out_t < m[1]: return i
    return len(MAP) - 1

# word list (corrected spelling), with output times
FIX = {"pension": "pencen", "bag": "beg", "ni?": "ni?", "Saga,": "Saga,"}
def words():
    tr = json.load(open(os.path.join(HERE, "..", "tr1132.json")))
    out = []
    for seg in tr:
        for w in seg["words"]:
            txt = w["w"].strip()
            mid = (w["s"] + w["e"]) / 2
            if any(r0 <= mid <= r1 for r0, r1 in REMOVED): continue
            blk = [i for i, (a, b) in enumerate(BASE) if a <= mid <= b]
            if not blk: continue
            s0, s1 = src2out(w["s"]), src2out(w["e"])
            if s1 < s0 + 0.08: s1 = s0 + 0.08
            keep = (s0, s1)
            txt = FIX.get(txt, txt)
            seg = blk[0]
            if txt.lower().startswith("alik") and out and out[-1]["t"].lower() == "ulang":
                out[-1]["t"] += "-" + txt; out[-1]["e"] = keep[1]; continue
            out.append(dict(t=txt, s=keep[0], e=keep[1], src=w["s"], seg=seg))
    return out

if __name__ == "__main__":
    for m in MAP: print(["%.2f" % x for x in m])
    print("TOTAL", TOTAL)
    for w in words(): print("%.2f %.2f %s" % (w["s"], w["e"], w["t"]))

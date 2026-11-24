"""Edit decision list for the Bang Taf Motorsport - Proton Saga video.
All 'src' times refer to the narration clip IMG_1132 (seconds)."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
W, H = 1080, 1920
END_CARD = 2.8

# narration segments kept (src_in, src_out). Pauses / repeated words removed.
SEGMENTS = [
    (2.52, 5.95),   # korang rasa, siapa yang patut pakai kereta ni?
    (6.76, 9.00),   # ini ada kereta Saga guys
    (9.60, 15.38),  # #1 fresh graduate
    (15.38, 21.42), # #2 mak ayah ... yang dah pencen
    (22.94, 26.20), # Proton Saga, memang low cost maintenance
    (30.22, 32.95), # #3 pasangan muda baru nak mula hidup guys  (spoken "yang kedua" removed)
    (35.04, 46.42), # #4 orang yang baru nak ada kereta ... naik motor
    (46.78, 55.60), # #5 kereta kedua ... family
    (55.52, 61.60), # CTA
]

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
        if a - 0.05 <= s <= b + 0.05:
            return o0 + (min(max(s, a), b) - a)
    raise ValueError(s)

# word list (corrected spelling), with output times
FIX = {"pension": "pencen", "bag": "beg", "ni?": "ni?", "Saga,": "Saga,"}
def words():
    tr = json.load(open(os.path.join(HERE, "..", "tr1132.json")))
    out = []
    for seg in tr:
        for w in seg["words"]:
            txt = w["w"].strip()
            mid = (w["s"] + w["e"]) / 2
            keep = None
            for o0, o1, a, b in MAP:
                if a <= mid <= b:
                    keep = (o0 + max(w["s"], a) - a, o0 + min(w["e"], b) - a)
            if keep is None:
                continue
            txt = FIX.get(txt, txt)
            seg = [i for i, m in enumerate(MAP) if m[2] <= mid <= m[3]][0]
            if txt.lower().startswith("alik") and out and out[-1]["t"].lower() == "ulang":
                out[-1]["t"] += "-" + txt; out[-1]["e"] = keep[1]; continue
            out.append(dict(t=txt, s=keep[0], e=keep[1], src=w["s"], seg=seg))
    return out

if __name__ == "__main__":
    for m in MAP: print(["%.2f" % x for x in m])
    print("TOTAL", TOTAL)
    for w in words(): print("%.2f %.2f %s" % (w["s"], w["e"], w["t"]))

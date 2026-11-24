# Bang Taf Motorsport – Video Editor

## Output
- `output/BangTaf_ProtonSaga_TikTok_1080x1920.mp4` – Proton Saga reel (9:16, 1080×1920, 30 fps, H.264 + AAC, ~42 s, -14 LUFS)
- `output/preview_contact_sheet.jpg` – frame preview for QC

## Struktur edit
| Masa | Babak |
|---|---|
| 0–2.6s | HOOK: "Siapa yang patut pakai kereta ni?" (B-roll showroom, slow-mo → speed ramp) |
| 2.6–4.7s | "PROTON SAGA" title reveal + impact |
| 4.7–36.4s | 5 kad "SESUAI UNTUK" (01–05) + gauge "kos penyelenggaraan rendah", B-roll interior |
| 36.4–39.5s | CTA: READY STOCK + "TEKAN BEG BIRU" + anak panah |
| 39.5–42.2s | End card logo Bang Taf Motorsport |

## Pipeline (`editor/`)
Source clips (from Google Drive) are pre-graded to 1080×1920 into `graded/`, then:
- `timeline.py` – narration cut list: repeated sentence removed, every silence ≥0.2 s auto-shrunk to 0.14 s, word timings
- `render.py` – frame compositor (zoom/punch transitions, motion graphics, karaoke subtitles)
- `audio.py` – voice cleanup, original synthesized music bed (royalty-free), SFX, sidechain ducking, loudness
- `logo.py` – extracts the transparent logo from the brand image

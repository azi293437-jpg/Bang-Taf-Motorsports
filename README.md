# Bang-Taf-Motorsports

## BANG TAF Automotive Intelligence — *Why are modern cars becoming smarter?*

A 60-second, fully animated infographic documentary in two language versions, made for TikTok, Reels and Shorts.

| Deliverable | Format |
|---|---|
| `output/Bang Taf Automotive Intelligence — English.mp4` | 1080×1920, 30 fps, H.264 + AAC 320k, 60 s, about −14 LUFS |
| `output/Bang Taf Automotive Intelligence — Bahasa Melayu.mp4` | same |
| `output/*.srt` | subtitle files, one per language |

Subtitles are also burned into each MP4. They use white text with electric-blue keywords, stay within two lines, and sit inside the TikTok safe zone. The burned-in text covers roughly y 1310–1440, and important content stays clear of the right-hand UI rail.

### Scene structure

| Time | Scene | Visual |
|---|---|---|
| 00:00–00:07 | Hook | Holographic 3D car materialises, headlights and dashboard power up, camera pushes in to reveal the ECU, engine and sensor wiring, then **CAR = COMPUTER + ENGINE + SENSORS** |
| 00:07–00:17 | Evolution | 3D morph from a boxy mechanical sedan to a modern SUV: gears turn into a chip and circuit traces, then a sensing field and neural links. **MECHANICAL → ELECTRONIC → INTELLIGENT** timeline |
| 00:17–00:27 | Brain of the car | Shaded 3D ECU (fins, connector, glowing die) with an animated input/output network to sensors, engine, transmission, brakes/ABS and control systems, then **ECU + SENSORS + CONTROL SYSTEMS** |
| 00:27–00:39 | Smart safety | Chase-cam road scene: 360° camera fields, blind-spot zone triggered by an overtaking car, lane detection with drift and correction, ADAS radar with following distance. On-screen disclaimer: *examples of available technologies, not standard on every vehicle* |
| 00:39–00:51 | Proton technology | Two model cards, **e.MAS 7** and **X50 Flagship**, each with a rotating 3D wireframe and four verified feature callouts plus a spec-source footnote |
| 00:51–01:00 | Ending | Highway drive with a crane-up move, **THE FUTURE OF DRIVING IS HERE.**, then the BANG TAF wordmark reveal and a follow CTA |

### Proton feature verification

Callouts cover only features that published Malaysian-market spec sheets and reviews agree on for that model and variant. Every card carries this footnote: *"Malaysian-market spec sheets (2026 model year). Features vary by variant — confirm at proton.com."*

- **Proton e.MAS 7, Prime & Premium:**
  - 15.4-inch 2.5K touchscreen running Flyme Auto, plus a 10.2-inch cluster
  - 360° surround-view camera on both variants
  - ADAS on both variants: adaptive cruise with stop & go, AEB and lane keeping
  - Wireless Apple CarPlay, added by OTA update in July 2025
- **Proton X50 Flagship, 2026:**
  - 14.6-inch touchscreen
  - 360° camera
  - Adaptive cruise with stop & go, and lane centring
  - Blind spot monitoring (rear-side radar / Lane Change Assist on the 2025+ model)
  - Panoramic sunroof

Sources:
- [paultan.org X50 Flagship 2025](https://paultan.org/research/proton/x50/sx11-fl/flagship-2025/) and [2026](https://paultan.org/research/proton/x50/sx11-fl/flagship-2026/)
- [autobuzz.my, 2025 X50 detailed](https://autobuzz.my/2025/07/02/all-new-2025-proton-x50-detailed/)
- [soyacincau, 2026 X50 price & specs](https://soyacincau.com/2025/07/24/all-new-2026-proton-x50-price-specs/)
- [carsifu X50 Flagship review](https://www.carsifu.my/car-reviews/proton-x50-flagship-tuned-for-success)
- [paultan.org e.MAS 7 Premium](https://paultan.org/research/proton/emas-7/mk1/premium-2026/)
- [autobuzz.my e.MAS 7 Prime vs Premium](https://autobuzz.my/2024/12/16/proton-emas7-prime-vs-premium-spec-by-spec-comparison-what-does-rm14k-extra-get-you/)
- [paultan.org e.MAS 7 interior](https://paultan.org/2024/10/17/proton-emas-7-first-look-at-interior-reveals-15-4-inch-2-5k-display-16-speaker-wanos-premium-audio-system/)
- [soyacincau, e.MAS 7 CarPlay OTA](https://soyacincau.com/2025/07/02/proton-emas7-apple-carplay-flyme-auto-os-update/)

Check the official Proton spec sheet before publishing, because specs change with each model-year update.

### How it is made

Everything is procedural. No stock footage or third-party images are used.

- **Visuals:** `src/render/render.js` is a deterministic HTML5-canvas renderer: `renderFrame(t)`, a custom 3D projection, parametric wireframe vehicle bodies (morphable), shaded 3D boxes, line icons, kinetic typography, bloom, vignette and grain. `src/render_video.js` drives headless Chromium with Playwright and pipes the frames into ffmpeg.
- **Voice-over:** `src/build_vo.py` synthesises each subtitle phrase separately, fits the phrases into their scene windows and writes the cue timings. Subtitles therefore line up with the voice to within a frame.
  - **English:** Kokoro-82M (Apache-2.0), male voice `am_michael`.
  - **Bahasa Melayu:** Meta MMS-TTS Malay (`facebook/mms-tts-zlm`, **CC-BY-NC-4.0**), deepened to a medium-deep male register with the WORLD vocoder. For each phrase, Whisper picks the clearest of four takes.
- **Music & SFX:** `src/build_audio.py` generates an original score (Dm–B♭–F–C pads, arpeggio, sub pulse, kick) and sound design (impacts, whooshes, scans, blips, mechanical ratchets). The score is side-chain ducked under the voice.
- **QA:** `src/qa_vo.py` transcribes every cue with Whisper and compares it against the script.

Rebuild with `MODELS=… BUILD=… src/build.sh all`. See the comments at the top of `build.sh` for the model files it expects.

### Notes before publishing

1. **Logo:** the official BANG TAF Motorsport logo (`assets/bangtaf_logo.jpg`, supplied by the client) is used unaltered in the **Bahasa Melayu** version: as a corner bug throughout and as the end-card reveal. It is only cropped to its frame. The English version keeps the typographic wordmark. To add the logo there too, copy the `"logo"` entry from `ms.text` to `en.text` in `src/script.json`. The supplied file is a small JPEG (365×259); a high-resolution PNG, ideally with a transparent background, would render sharper.
2. **Proton visuals:** the cars are illustrative 3D wireframes built to each model's rough proportions and labelled *"Illustrative 3D wireframe · not an official image"*. No Proton photos or logos are used. Licensed official Proton press imagery can be composited into scene 5 if you have it.
3. **Malay voice licence:** the Malay voice model is licensed **non-commercial (CC-BY-NC-4.0)**. If BANG TAF content is monetised or sponsored, re-voice the Malay track with a human narrator or a commercially licensed TTS. The scripts are in `src/script.json`, and only `vo_ms.wav` needs replacing. The English voice (Apache-2.0) and all music and SFX are free for commercial use.
4. **Scripts:** no narration script was provided, so the English and Malay scripts in `src/script.json` were written to fit the brief and the 60-second timing. Have a native speaker review the Malay.

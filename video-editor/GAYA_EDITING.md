# Standard Editing Bang Taf (TikTok)

Panduan ini ialah standard editing yang dipelajari daripada video rujukan. Ia digunakan untuk setiap video baharu.

## 1. Apa yang dipelajari daripada video rujukan

| Teknik | Dalam video rujukan | Cara ia diaplikasi untuk Bang Taf |
|---|---|---|
| Background berubah ikut topik | Talent dirakam depan green screen; background bertukar setiap kali topik baru (rumah → MRT → kelas → jalan → bandar) | Chroma key automatik. Background ikut topik: bangunan BNM (berita), KL skyline (ekonomi/OPR), studio navy-emas (penerangan), merah (amaran/salah faham), hijau (data positif), pink "dream" (lawak / angan-angan) |
| Kad tajuk gaya berita | Kotak putih, teks hitam besar, label jenama di bucu | Kad putih + highlight merah + logo Bang Taf di bucu, pada 3 saat pertama (hook) |
| Screenshot / bukti | Tweet, artikel, komen ditimbunkan atas dada | Kad grafik (infografik BNM, poster, graf OPR) muncul dengan animasi pop |
| Subtitle | Teks putih atas kotak gelap separa telus, di tengah skrin (paras dada) | Sama, + keyword diwarnakan: **emas** = penting, **merah** = negatif/salah, **hijau** = positif |
| Punch-in / extreme zoom | Zoom ekstrem ke muka untuk punchline ("gak mungkin") | Zoom 1.0 → 1.15 → 1.3 bergilir setiap jump cut; zoom 1.45–1.6 + goncangan untuk lawak/kejutan |
| Ending | Soalan kepada penonton + ikon "??" besar di belakang kepala | Soalan CTA + "??" biru di belakang kepala + ajak komen |
| Branding | Watermark TikTok | Logo Bang Taf Motorsport: watermark kiri atas sepanjang video, dalam kad tajuk hook, dan end card "FOLLOW Bang Taf" 2.2 saat |
| Pacing | Tiada dead air, setiap ayat bertukar visual | Semua jeda > 0.25s dibuang, retake dibuang, pertuturan dilaju 1.1x |

## 2. Peraturan wajib setiap video

1. **Buang semua jeda janggal** – kesan senyap pada -38dB/0.25s, potong, tinggal ~0.15s nafas antara ayat.
2. **Buang retake & salah sebut** – transkrip setiap "pulau percakapan" secara berasingan, kekalkan take terbaik sahaja.
3. **Hook 3 saat pertama** – kad tajuk + nombor besar + SFX boom.
4. **Tukar visual setiap 2–5 saat** – zoom, sticker, kad, background atau layout PiP.
5. **Layout PiP** (muka dalam bulatan emas, kiri bawah) bila infografik perlu ruang besar.
6. **Lawak** – emoji reaction, zoom ekstrem, SFX boing / record-scratch / wah-wah tepat pada punchline. Jangan paksa.
7. **Audio** – highpass + noise reduction + compressor + loudnorm suara; muzik diduck automatik bawah suara, senyap sekejap pada momen "TAK!" / "TETAPI!".
8. **Format** – 1080×1920, 30fps, MP4 H.264 + AAC, -14 LUFS.
9. **Safe zone TikTok** – teks penting antara y≈200 hingga y≈1650, x≈80 hingga x≈960 (elak bahagian bawah & kanan).
10. **Angka contoh** dilabel "ilustrasi" supaya tidak mengelirukan.

## 3. Pipeline (folder ini)

```
raw/      rakaman asal (.mov)            -> masukkan video baharu di sini
assets/   bahan grafik dari Drive
gfx/      background & kad (dijana oleh prep_gfx.py)
sfx/      SFX & muzik bebas hak cipta (dijana oleh gen_audio.py)
work/     audio 16k, transkrip, senarai senyap
spec.py   senarai keputusan edit (potongan, teks subtitle, overlay)  <- disunting untuk setiap video
render.py enjin render (chroma key, zoom, PiP, subtitle, overlay)
audio.py  potong suara, bersih audio, muzik + SFX
```

Langkah:
1. `python3 prep_gfx.py <dir>` dan `python3 gen_audio.py <dir>/sfx`
2. Ekstrak audio 16k ke `work/`, jalankan `ffmpeg silencedetect` → `work/sil_<klip>.txt`
3. `python3 islands.py <dir> <klip...>` → transkrip per pulau percakapan (faster-whisper medium, Bahasa Melayu)
4. Tulis `spec.py` (susunan potongan, subtitle dibetulkan, overlay)
5. `python3 render.py info` → semak durasi; `python3 render.py still <frame> out.png` → semak visual
6. `python3 audio.py` kemudian `python3 render.py range a b part.mp4` (selari), gabung & mux.

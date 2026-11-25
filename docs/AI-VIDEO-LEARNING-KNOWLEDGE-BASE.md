# AI VIDEO LEARNING KNOWLEDGE BASE

> Dokumen rujukan hidup. Setiap video baharu ditambah sebagai entri baharu di bawah — entri lama **tidak dibuang**.
>
> Legenda kebolehpercayaan:
> - ✅ **Disahkan** — dilihat/didengar terus dalam video, atau disahkan dari sumber rasmi (repo GitHub / fail config rasmi).
> - ⚠️ **Tidak jelas / andaian** — tidak ditunjukkan dalam video; diisi berdasarkan dokumentasi rasmi atau amalan biasa. Sila sahkan semasa setup.

## Indeks Video

| # | Tajuk | Sumber | Tarikh dianalisis |
|---|-------|--------|-------------------|
| 1 | "Cara nak buat AI agent" — Hermes Agent dengan VPS murah + DeepSeek | Google Drive folder *Cara nak buat ai agent* → `v1c044g50000dat6d2fog65n12pvmmbg.mp4` (klip TikTok, 79 saat) | 2026-11-25 |

---

# VIDEO 1 — "Cara nak buat AI agent" (Hermes Agent)

## 1.1 Maklumat Video

| Perkara | Butiran |
|---|---|
| Fail | `v1c044g50000dat6d2fog65n12pvmmbg.mp4` (8 MB, 576×1024 menegak, 79.5 saat) |
| Format | Klip TikTok "talking head" + overlay grafik animasi |
| Bahasa | Bahasa Melayu bercampur English |
| Jenis kandungan | **Video pengenalan / promosi konsep**, BUKAN tutorial langkah demi langkah |
| Penting | Video menyebut *"Kalau awak nak belajar, check my bio — ada ajar cara nak install dekat desktop ataupun VPS"*. Tutorial penuh berada di **pautan bio pencipta**, bukan dalam video ini. |

## 1.2 Transkrip (dibersihkan)

Transkrip dijana dengan Whisper, kemudian dibetulkan secara manual (contoh: "Cik GBT" → ChatGPT, "klod" → Claude, "deep sink" → DeepSeek, "10 cent" → Tencent, "PPS" → VPS).

| Masa | Ucapan | Overlay pada skrin |
|---|---|---|
| 0:00 | "2026 ini adalah tahun Agentic AI. Jadi kalau kita semua tak belajar Agentic AI, kita akan ketinggalan." | `2026`, `AGENTIC AI`, `KETINGGALAN — left behind` |
| 0:07 | "Tiga tahun lepas, 2023, ChatGPT was the thing. But this year is all about giving everything dekat bot. Bagi dia buat, jangan buat sendiri." | `2023 → 2026 ChatGPT`; ikon Emails / Tasks / Research / Code → "Give everything to the bot"; "✅ Let it do the work ❌ Don't do it yourself" |
| 0:17 | "Seumpama awak ada satu intern yang duduk depan PC 24 jam. Awal, first week dia bodoh sikit, tapi lepas awak dah train dia — self-learning." | `Your AI intern 24/7`; graf `LEARNING CURVE: Day 1 · a bit clueless → Trained` |
| 0:26 | "So agentic AI ni kita panggil dia **Hermes Agent**." | `Hermes Agent — Autonomous Agent` |
| 0:30 | "Dengan Hermes ni, dia seumpama robot kosong. Awak pasangkan otak dekat kepala dia. Otak ni kita boleh ambil — ChatGPT ke, Claude ke, DeepSeek — ikut suka awak." | `An empty robot — HERMES = ROBOT KOSONG`; `+ Plug in a brain`; `THE BRAIN: ChatGPT · Claude · DeepSeek` |
| 0:41 | "And then awak pakai *[tidak jelas — kemungkinan 'server']*. So kos untuk benda ni berapa?" | `RM ??` |
| 0:46 | "Ada satu server tengah promo — daripada **Tencent** — **RM40 setahun**. And then you masukkan model. Model tu pun dalam **RM10 ke RM15**. **DeepSeek API** kita pakai." | `YOUR SETUP: Cloud server — Tencent Cloud PROMO — RM40/year`; `AI model — RM10…`; `DeepSeek API` |
| 0:57 | "So ada robot kosong, ada otak. Nak run dia sebulan mungkin dalam **RM20**." | `ROBOT + BRAIN = ~RM0 /month` (⚠️ bercanggah dengan ucapan RM20) |
| 1:02 | "Apa yang awak boleh buat? Macam-macam." | `What can it do? Macam-macam!` Research · Emails · Coding · Content · Scheduling · Customer chat · Reports · + more |
| 1:04 | "Kalau awak nak belajar, check my bio. Ada ajar cara nak install dekat desktop ataupun cara nak install dekat VPS." | `Check out my bio — full install tutorial`; `Desktop — install locally ($ hermes install ✓ agent ready)` **or** `VPS — install on a server` |
| 1:15 | — | Skrin penutup TikTok |

## 1.3 Tools & Platform Yang Dikenal Pasti

| Komponen | Tool | Status | Peranan |
|---|---|---|---|
| "Robot kosong" (agent framework) | **Hermes Agent** oleh Nous Research — open source (MIT) — `github.com/NousResearch/hermes-agent` | ✅ nama disebut; butiran teknikal ✅ dari repo rasmi | Badan agent: alat (tools), memori, skills, scheduler, gateway mesej |
| "Otak" (LLM) | **DeepSeek API** (pilihan dalam video); alternatif ChatGPT (OpenAI) / Claude (Anthropic) | ✅ | Model bahasa yang membuat keputusan & menulis jawapan |
| Server | **Tencent Cloud** (harga promo RM40/tahun) — VPS | ✅ nama & harga dari overlay; ⚠️ produk/spesifikasi tepat tidak ditunjukkan (berkemungkinan Tencent Cloud *Lighthouse*) | Menjalankan agent 24/7 |
| Alternatif server | Desktop/PC sendiri | ✅ | Untuk cuba/belajar secara lokal |
| Arahan install | Overlay menunjukkan `$ hermes install` → `✓ agent ready` | ⚠️ ini **grafik ilustrasi**, bukan arahan sebenar. Arahan rasmi di bawah (1.5). | — |

**Tidak ditunjukkan dalam video** (jangan anggap ia sebahagian daripada sistem asal): prompt sebenar, konfigurasi, database, integrasi Telegram/WhatsApp, kod, automation khusus. Semua itu ada dalam tutorial "link in bio" yang tidak disertakan dalam folder Drive.

## 1.4 Rekonstruksi Sistem

### 1) Fungsi sistem
Pembantu AI autonomi ("AI intern 24/7") yang anda beri tugasan (research, email, coding, content, jadual, chat pelanggan, laporan). Ia bukan chatbot biasa — ia boleh **bertindak**: menjalankan arahan terminal, melayari web, membaca/menulis fail, menjadualkan kerja, dan **belajar** daripada tugasan lalu (memori + skills).

### 2) Cara sistem berfungsi

```
           ┌──────────────── VPS Tencent Cloud (24/7) ─────────────────┐
 Anda ───► │  Hermes Agent ("badan / robot")                           │
 (Terminal │   ├─ Gateway mesej (Telegram/WhatsApp/Discord/…)  ◄──────┼── Anda dari telefon
  atau     │   ├─ 40+ tools: terminal, web, fail, browser, MCP …       │
  telefon) │   ├─ Memori (MEMORY / USER profile) + carian sesi (SQLite) │
           │   ├─ Skills (dicipta sendiri selepas tugasan kompleks)    │
           │   └─ Cron scheduler (tugasan berjadual → hantar ke chat)  │
           │                │                                           │
           └────────────────┼───────────────────────────────────────────┘
                            ▼  HTTPS API call (bayar per token)
                    "Otak": DeepSeek API  (atau OpenAI / Claude / OpenRouter)
```

1. Anda hantar arahan (terminal atau chat telefon).
2. Hermes hantar konteks + senarai tools kepada LLM (DeepSeek).
3. LLM memilih tindakan (cth. cari web, tulis fail, jalankan arahan) → Hermes laksanakan → hasil dihantar balik ke LLM → ulang sehingga siap.
4. Hermes simpan pelajaran ke memori / skill → kali seterusnya lebih pandai ("self-learning" dalam video).

### 3) Tools diperlukan
VPS (atau PC), Hermes Agent, kunci API LLM (DeepSeek), dan (pilihan) bot Telegram untuk akses dari telefon.

### 4) Hubungan antara tools
- **VPS ↔ Hermes**: Hermes dipasang dan berjalan sebagai proses di VPS.
- **Hermes ↔ DeepSeek**: melalui API (kunci API disimpan dalam `~/.hermes/.env` atau `config.yaml`).
- **Hermes ↔ Telegram**: melalui *gateway* (`hermes gateway`) menggunakan token bot dari @BotFather.

### 5) Proses setup — lihat Bahagian 1.5.

### 6) Prompt yang digunakan
⚠️ **Tiada prompt ditunjukkan dalam video.** Prompt sedia guna (ciptaan kita) disediakan dalam Phase 4.

### 7) Bagaimana output dihasilkan
Output = jawapan chat, fail yang dijana (laporan, draf email, kod), atau mesej berjadual yang dihantar ke Telegram oleh cron.

### Analisis kos (dari video)
| Item | Video kata | Nota |
|---|---|---|
| Server | RM40/tahun (promo Tencent) ≈ RM3.30/bulan | Harga promo biasanya untuk tahun pertama / pelanggan baharu sahaja ⚠️ |
| Model (DeepSeek API) | RM10–15 | ⚠️ Tidak jelas sama ada sebulan atau top-up sekali. DeepSeek ialah bayar-ikut-guna (prepaid). |
| Jumlah | "~RM20 sebulan" (ucapan) vs "~RM0/month" (grafik) | Grafik bercanggah dengan ucapan. Anggaran realistik: **RM15–25/bulan** untuk penggunaan ringan. |

## 1.5 Panduan Implementasi Langkah demi Langkah

> Disasarkan kepada pengguna tanpa latar belakang teknikal. Ikut mengikut urutan. Arahan di bawah diambil dari README & fail config rasmi Hermes Agent (disemak 2026-11-25). Jika satu arahan gagal, jalankan `hermes doctor`.

### PHASE 1 — Preparation (Persediaan)
1. **Tentukan di mana agent akan berjalan:**
   - *Belajar dulu* → PC/laptop sendiri (Windows, macOS, Linux). Percuma, tetapi agent mati bila PC ditutup.
   - *Guna betul-betul 24/7* → VPS. **Disyorkan** selepas anda selesa.
2. **Sediakan akaun:**
   - Tencent Cloud (atau mana-mana VPS: Hetzner, DigitalOcean, Contabo…). Pilih **Ubuntu 22.04/24.04**, sekurang-kurangnya **2 GB RAM**, rantau **Singapura** (latensi rendah dari Malaysia).
   - **DeepSeek Platform** (`platform.deepseek.com`) → top-up kredit kecil (cth. USD 2–5) → **API Keys → Create** → salin kunci (`sk-...`). Simpan di tempat selamat; ia hanya ditunjuk sekali.
   - (Pilihan) **Telegram** → chat dengan **@BotFather** → `/newbot` → dapatkan **bot token**. Kemudian chat dengan **@userinfobot** untuk dapatkan **user ID** anda (nombor).
3. **Senarai semak:** IP VPS, kata laluan/SSH key VPS, DeepSeek API key, Telegram bot token, Telegram user ID.

### PHASE 2 — Tools Installation (Pemasangan)
**A. Di VPS (Linux) atau macOS / WSL2:**
```bash
# 1. Masuk ke VPS (dari Terminal / PowerShell di PC anda)
ssh root@IP_VPS_ANDA

# 2. Kemas kini sistem (VPS sahaja)
apt update && apt upgrade -y

# 3. Pasang Hermes Agent (arahan rasmi)
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# 4. Muat semula shell supaya arahan 'hermes' dikenali
source ~/.bashrc        # atau: source ~/.zshrc (macOS)

# 5. Semak
hermes doctor
```

**B. Di Windows (PowerShell biasa):**
```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```
Fail disimpan di `%LOCALAPPDATA%\hermes`. Jika antivirus (Defender/Bitdefender) mengkuarantin `uv.exe`, README menyatakan ia *false positive* — kecualikan folder tersebut.

> 💡 Amalan keselamatan: sebelum menjalankan `curl … | bash`, anda boleh muat turun dan baca skrip dahulu: `curl -fsSL https://hermes-agent.nousresearch.com/install.sh -o install.sh && less install.sh && bash install.sh`.

### PHASE 3 — Configuration (Konfigurasi)
1. **Jalankan wizard penuh:**
   ```bash
   hermes setup
   ```
2. **Pasang "otak" (DeepSeek):**
   ```bash
   hermes model
   ```
   - DeepSeek **tidak** tersenarai sebagai provider bernama dalam fail config contoh rasmi. Gunakan pilihan **custom (OpenAI-compatible endpoint)** dan masukkan:
     - Base URL: `https://api.deepseek.com/v1`
     - API key: kunci `sk-...` DeepSeek anda
     - Model: `deepseek-chat` (laju & murah) atau `deepseek-reasoner` (lebih "berfikir") — ⚠️ semak nama model terkini di laman DeepSeek.
   - Alternatif konfigurasi manual dalam `~/.hermes/config.yaml` (⚠️ sahkan nama medan dengan `hermes config get`):
     ```yaml
     model:
       provider: "custom"
       base_url: "https://api.deepseek.com/v1"
       default: "deepseek-chat"
       # api_key: lebih selamat diletak dalam ~/.hermes/.env, bukan di sini
     ```
   - **Pilihan lebih mudah:** gunakan **OpenRouter** (`provider: openrouter`, `OPENROUTER_API_KEY=` dalam `.env`) — satu kunci untuk DeepSeek, Claude, GPT. Boleh tukar model bila-bila dengan `/model` dalam chat.
3. **Pilih tools:** `hermes tools` — aktifkan hanya yang anda perlukan (web search, terminal, fail).
4. **Ujian pertama:**
   ```bash
   hermes
   ```
   Taip: `Hai, perkenalkan diri dan senaraikan tools yang kamu ada.`

### PHASE 4 — AI Prompt Setup
Video tidak menunjukkan prompt. Hermes mempunyai memori (`memory`) dan profil pengguna (`user_profile`) yang aktif secara lalai. Cara paling mudah: **tampal prompt di bawah sebagai mesej pertama** dan minta agent menyimpannya ke memori.

Prompt sedia ada dalam fail berasingan supaya mudah disalin: [`hermes-setup/PROMPTS.md`](hermes-setup/PROMPTS.md)
- Prompt 1 — Onboarding & identiti (siapa anda, perniagaan anda, gaya bahasa)
- Prompt 2 — Peraturan keselamatan (apa yang agent tidak boleh buat tanpa kebenaran)
- Prompt 3–6 — Templat tugasan: research, content media sosial, laporan harian, balas pelanggan

### PHASE 5 — Automation Setup
**A. Akses dari telefon (Telegram):**
```bash
hermes gateway setup     # wizard: pilih Telegram, tampal bot token
hermes gateway start     # mulakan gateway
```
Pastikan dalam `~/.hermes/.env` (nama pembolehubah dari `.env.example` rasmi):
```bash
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_ALLOWED_USERS=111111111        # user ID anda SAHAJA — sangat penting
TELEGRAM_HOME_CHANNEL=111111111         # tempat hasil cron dihantar
```
Dalam Telegram, hantar `/sethome` kepada bot untuk tetapkan chat utama.

**B. Jalankan 24/7 di VPS:** README tidak memberi arahan servis. Kami sediakan fail `systemd` sendiri: [`hermes-setup/hermes-gateway.service`](hermes-setup/hermes-gateway.service) (arahan pemasangan di dalam fail).

**C. Tugasan berjadual (cron):** Hermes ada scheduler terbina dalam yang menerima arahan **bahasa biasa**. Contoh, dalam chat:
> "Setiap hari jam 8 pagi waktu Malaysia, cari 5 berita terkini tentang industri motorsport & automotif Malaysia, ringkaskan dalam 5 poin, dan hantar ke Telegram saya."

### PHASE 6 — Database Integration
⚠️ Video tidak menyebut database. Apa yang sedia ada dalam Hermes:
- **Memori terbina dalam**: nota agent + profil pengguna, dan carian sejarah sesi (SQLite FTS5) — disimpan di `~/.hermes/`.
- **Skills**: fail dalam `~/.hermes/skills/` — prosedur yang agent pelajari.

Untuk data perniagaan (pelanggan, stok, tempahan), pilihan cadangan mengikut tahap:
1. **Paling mudah:** fail CSV / Markdown dalam folder kerja agent (cth. `~/bangtaf/data/pelanggan.csv`) — agent boleh baca/tulis terus.
2. **Pertengahan:** Google Sheets / Notion / Airtable melalui **MCP server** (Hermes menyokong MCP).
3. **Lanjutan:** Postgres / Supabase melalui MCP server pangkalan data.

### PHASE 7 — Testing
| # | Ujian | Arahan / tindakan | Lulus jika |
|---|---|---|---|
| 1 | Sambungan model | `hermes` → "Apa model yang kamu guna?" | Jawapan muncul tanpa ralat 401/402 |
| 2 | Tools | "Cari harga minyak RON95 terkini di Malaysia" | Agent guna web search & beri sumber |
| 3 | Memori | Beritahu fakta → `/new` → tanya semula | Agent ingat |
| 4 | Telegram | Hantar mesej dari telefon | Bot balas |
| 5 | Keselamatan | Minta rakan hantar mesej ke bot | Bot **tidak** layan (allowlist berfungsi) |
| 6 | Cron | Jadualkan tugasan 2 minit dari sekarang | Mesej sampai di Telegram |
| 7 | Ketahanan | `sudo reboot` VPS | Bot hidup semula sendiri (systemd) |
| 8 | Kos | `/usage` dan papan pemuka DeepSeek | Kos sepadan jangkaan |

### PHASE 8 — Optimization
- `/usage` & `/insights` untuk pantau token; `/compress` untuk sesi panjang.
- Gunakan `deepseek-chat` untuk kerja harian, model lebih kuat hanya untuk tugasan sukar (`/model`).
- `hermes update` setiap minggu.
- Semak & kemas kini skills yang agent cipta (`/skills`) — buang yang salah.
- Backup folder `~/.hermes` (memori + skills = "latihan intern" anda).

## 1.6 Masalah Lazim & Penyelesaian

| Masalah | Punca | Penyelesaian |
|---|---|---|
| `hermes: command not found` | Shell belum dimuat semula | `source ~/.bashrc` atau log keluar/masuk |
| Ralat 401 | API key salah | Semak `~/.hermes/.env`, jalankan semula `hermes model` |
| Ralat 402 / "insufficient balance" | Kredit DeepSeek habis | Top-up di platform DeepSeek |
| Bot Telegram diam | Gateway tak berjalan / user ID tiada dalam allowlist | `systemctl status hermes-gateway`; semak `TELEGRAM_ALLOWED_USERS` |
| Agent "lupa" | Sesi baharu tanpa memori | Minta agent "simpan ke memori"; pastikan `memory_enabled: true` |
| VPS lambat / proses mati | RAM tidak cukup | Tambah swap 2 GB atau naik taraf ke 4 GB RAM |
| Bil API tinggi | Sesi panjang, model mahal | `/compress`, `/new`, guna model lebih murah |

## 1.7 Konfigurasi Teknikal (Rujukan Cepat)

| Perkara | Nilai |
|---|---|
| Folder config | `~/.hermes/` (Linux/macOS/WSL2), `%LOCALAPPDATA%\hermes` (Windows) |
| Fail utama | `~/.hermes/config.yaml`, `~/.hermes/.env` |
| Arahan CLI | `hermes`, `hermes setup`, `hermes model`, `hermes tools`, `hermes config set/get`, `hermes gateway [setup\|start]`, `hermes doctor`, `hermes update` |
| Slash commands | `/new` `/reset` `/model` `/personality` `/retry` `/undo` `/compress` `/usage` `/insights` `/skills` `/status` `/sethome` `/stop` |
| Terminal backends | local (lalai), Docker, SSH, Modal, Daytona, Vercel Sandbox |
| Pemboleh ubah penting | `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`, `TELEGRAM_HOME_CHANNEL`, `GATEWAY_ALLOW_ALL_USERS=false`, `TERMINAL_ENV` |

## 1.8 Lessons Learned
1. **Agent = badan + otak.** Framework (Hermes) dan model (DeepSeek/Claude/GPT) adalah berasingan — boleh tukar otak tanpa bina semula.
2. **Kos boleh sangat rendah** (VPS murah + model murah), tetapi kos model bergantung pada penggunaan — bukan tetap.
3. **"Self-learning" = memori + skills**, bukan model yang dilatih semula. Kualiti bergantung pada maklum balas anda pada minggu pertama ("intern bodoh sikit").
4. **Desktop untuk belajar, VPS untuk 24/7.**
5. Video pendek ini ialah **corong pemasaran** ke tutorial penuh; butiran teknikal mesti diambil dari dokumentasi rasmi.

## 1.9 Cadangan Penambahbaikan

| Aspek | Cadangan |
|---|---|
| **Speed** | VPS rantau Singapura; `deepseek-chat` untuk tugasan rutin; hadkan tools yang aktif supaya prompt lebih pendek. |
| **Automation** | Cron harian (laporan, berita industri, peringatan servis pelanggan); skills khusus perniagaan; webhook Telegram dan bukannya polling bila skala besar. |
| **Accuracy** | Prompt identiti & peraturan (Phase 4); minta agent sentiasa beri sumber; semak skills mingguan; guna model lebih kuat sebagai *fallback* untuk tugasan kritikal. |
| **Cost efficiency** | Tetapkan had perbelanjaan di platform API; pantau `/usage`; `/compress` & `/new` kerap; OpenRouter untuk bandingkan harga model. |
| **Scalability** | Backend terminal Docker (pengasingan); subagents untuk kerja selari; pisahkan agent mengikut fungsi (sales, ops, content) dengan profil berbeza. |
| **User experience** | Telegram sebagai antara muka utama; `/personality` dalam Bahasa Melayu; *home channel* khusus untuk laporan. |
| **Integration** | MCP: Google Sheets/Calendar/Gmail, Notion; WhatsApp gateway untuk pelanggan (dengan allowlist ketat); e-mel. |
| **Keselamatan (tambahan penting)** | `TELEGRAM_ALLOWED_USERS` wajib; `GATEWAY_ALLOW_ALL_USERS=false`; jangan jalankan sebagai `root` (cipta user `hermes`); firewall (`ufw`) buka SSH sahaja; SSH key bukan kata laluan; jangan beri agent kunci/kata laluan bank; backup `~/.hermes`. |

**Ciri tambahan yang boleh menjadikan sistem lebih powerful (khusus Bang Taf Motorsports — cadangan):**
- 🔧 *Pembantu tempahan servis*: pelanggan tanya slot → agent semak Google Sheet → cadang masa.
- 📦 *Pemantau stok alat ganti*: cron harian baca CSV stok → amaran Telegram jika bawah paras minimum.
- 📣 *Kilang content*: setiap Isnin, jana 5 idea + kapsyen TikTok/IG tentang modifikasi & tips penjagaan motor.
- 📊 *Laporan mingguan*: ringkasan jualan/tempahan dari Sheet → hantar ke Telegram owner.
- 🔍 *Risikan pasaran*: pantau harga pesaing / trend alat ganti mingguan.

## 1.10 Maklumat Yang Tidak Jelas (jangan direka)
- Kandungan sebenar tutorial "link in bio" — **tidak tersedia**.
- Produk Tencent Cloud yang tepat, spesifikasi & tempoh promo.
- Sama ada RM10–15 DeepSeek itu sebulan atau sekali top-up; percanggahan "RM20/bulan" (ucapan) vs "~RM0/month" (grafik).
- Sama ada pencipta menggunakan Telegram/WhatsApp atau hanya terminal.
- Perkataan pada 0:42 ("awak pakai ___") tidak jelas dalam audio.
- Overlay `$ hermes install` ialah grafik ilustrasi; arahan install sebenar ialah skrip rasmi di Phase 2.

---
<!-- TAMBAH VIDEO BAHARU DI BAWAH INI: salin struktur "VIDEO 1" (1.1–1.10) dan tukar nombor. -->

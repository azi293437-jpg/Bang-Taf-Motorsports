# Edit decision list for "OPR 2.75% & loan kereta" — Bang Taf
# Piece: (clip, src_start, src_end, text_markup, opts)
#  markup: *gold*  {red}  [green]
#  opts: bg, z (zoom), z2 (push-to), layout ('full'|'pip'), shake, nocap
P = [
 # ---------------- HOOK
 ('A',  0.76,  4.25, "Bank Negara baru umumkan keputusan *OPR*", dict(bg='bnm', z=1.0, z2=1.08, nocap=True)),
 ('A',  6.90, 10.12, "*2.75%*", dict(bg='bnm', z=1.18, nocap=True)),
 ('A', 10.45, 11.20, "Tak naik?", dict(bg='bnm', z=1.0)),
 ('A', 11.84, 12.95, "Tak turun.", dict(bg='bnm', z=1.22)),
 ('A', 17.72, 19.25, "Tapi persoalannya...", dict(bg='studio', z=1.1)),
 ('A', 20.60, 23.42, "apa benda ni berkaitan dengan *loan* korang?", dict(bg='studio', z=1.0, z2=1.08)),
 # ---------------- APA ITU OPR
 ('A', 34.08, 38.75, "*OPR* adalah kadar dasar yang ditetapkan oleh *Bank Negara*.", dict(bg='kl', z=1.0, z2=1.06)),
 ('A', 39.66, 47.35, "Keputusan terbaru *3 September 2026*, OPR *kekal* pada *2.75%*", dict(bg='kl', layout='pip')),
 ('A', 47.86, 51.95, "Dan angka ni *penting* sebab ia mempengaruhi sistem kewangan.", dict(bg='kl', layout='pip')),
 # ---------------- SALAH FAHAM
 ('A', 61.00, 66.00, "Tapi ramai orang bila dengar saja OPR 2.75% ni terus fikir", dict(bg='studio', z=1.0, z2=1.1)),
 ('A', 66.45, 66.95, "Oh!", dict(bg='dream', z=1.45, shake=6)),
 ('A', 67.05, 70.40, "Interest loan kereta mesti *2.75* lah!", dict(bg='dream', z=1.25)),
 ('A', 71.52, 72.15, "{TAK!}", dict(bg='alert', z=1.6, shake=10)),
 ('A', 72.60, 75.55, "Ini benda yang ramai orang {salah faham}", dict(bg='alert', z=1.0)),
 ('A', 80.58, 84.35, "*OPR* {bukan} kadar interest loan kereta korang", dict(bg='alert', z=1.12, nocap=True)),
 ('A', 86.10, 92.40, "Kadar pinjaman kereta ditentukan berdasarkan *produk pembiayaan*, *bank*, *profil peminjam*", dict(bg='studio', layout='pip')),
 ('A', 92.60, 95.12, "dan juga *terma pinjaman*.", dict(bg='studio', layout='pip')),
 # ---------------- MAKSUD OPR KEKAL
 ('A',102.20,106.00, "Jadi kalau OPR *kekal 2.75%*", dict(bg='kl', z=1.0)),
 ('A',106.10,111.10, "apa maksudnya untuk korang yang nak beli kereta ataupun dah tengah beli kereta?", dict(bg='kl', z=1.15)),
 ('A',111.98,117.70, "Maksudnya kita tak boleh terus kata, OPR rendah, loan kereta {confirm murah}", dict(bg='studio', z=1.0, z2=1.08)),
 # ---------------- CONTOH KERETA
 ('A',142.10,145.87, "Contohnya kalau korang tengah tengok kereta harga *RM60,000*", dict(bg='studio', z=1.0, z2=1.06)),
 ('A',147.80,149.62, "kau mungkin nampak iklan", dict(bg='studio', z=1.15)),
 ('A',150.10,152.70, "interest *serendah* sekian-sekian *persen*", dict(bg='studio', z=1.15)),
 ('A',156.50,159.55, "Tapi jangan terus tengok angka interest tu je", dict(bg='studio', z=1.3)),
 ('A',161.98,166.25, "korang kena tengok juga berapa *deposit*, berapa *jumlah loan*", dict(bg='green', layout='pip')),
 ('A',167.80,169.20, "berapa *tahun*", dict(bg='green', layout='pip')),
 ('A',170.22,171.40, "*instalment*", dict(bg='green', layout='pip')),
 ('C',  0.10,  4.45, "dan paling penting, berapa *instalment sebenar setiap bulan*", dict(bg='green', layout='pip')),
 # ---------------- KONTEKS EKONOMI
 ('C', 15.58, 21.45, "Sekarang OPR dah berada pada *2.75%*", dict(bg='kl', layout='pip')),
 ('C', 37.70, 43.90, "Ekonomi Malaysia pula *berkembang 6.0%* pada suku kedua 2026", dict(bg='green', layout='pip')),
 ('C', 44.10, 46.70, "manakala *inflasi* Julai pada tahap", dict(bg='green', layout='pip')),
 ('C', 47.05, 49.15, "*1.8%*", dict(bg='green', layout='pip')),
 ('C', 49.42, 54.00, "Jadi situasi sekarang bukanlah cerita {ekonomi jatuh},", dict(bg='studio', z=1.0)),
 ('C', 54.02, 55.80, "{interest jatuh}.", dict(bg='studio', z=1.2)),
 # ---------------- AMARAN
 ('C', 73.82, 74.88, "{TETAPI!}", dict(bg='alert', z=1.5, shake=8)),
 ('C', 75.03, 77.80, "ada satu benda yang korang semua kena *hati-hati*", dict(bg='alert', z=1.0)),
 ('C', 79.04, 83.00, "{Jangan} beli kereta semata-mata bila korang dengar OPR rendah saja", dict(bg='alert', z=1.15, z2=1.22)),
 ('C', 84.63, 90.55, "sebab beza kadar yang *kecil* pun boleh jadi *besar* kalau korang kira tempoh *7 ke 9 tahun*", dict(bg='studio', layout='pip')),
 ('C', 93.16, 96.50, "dan instalment *murah* tak semestinya bermaksud", dict(bg='studio', z=1.0)),
 ('C', 96.62, 97.92, "kereta tu {murah}", dict(bg='studio', z=1.3)),
 ('C',100.67,103.57, "kadang-kadang instalment nampak *rendah*", dict(bg='studio', layout='pip')),
 ('C',105.40,107.12, "sebab korang punya", dict(bg='studio', layout='pip')),
 ('C',108.83,110.15, "instalment {panjang}.", dict(bg='studio', layout='pip')),
 # ---------------- KESIMPULAN
 ('C',118.12,119.78, "Jadi *kesimpulannya*", dict(bg='kl', z=1.2)),
 ('C',120.87,126.30, "OPR sekarang *2.75%*, tapi jangan tanya OPR", dict(bg='kl', z=1.0)),
 ('C',126.64,127.92, "rendah ke tinggi?", dict(bg='kl', z=1.15)),
 ('C',128.29,134.55, "Kalau korang nak beli kereta, soalannya yang lebih penting ialah *berapa sebenarnya korang kena bayar setiap bulan*", dict(bg='studio', layout='pip')),
 ('C',134.64,138.50, "dan berapa *jumlah* yang aku kena bayar *sampai habis loan*.", dict(bg='studio', layout='pip')),
 ('C',141.05,144.28, "Sebab tu yang betul-betul keluar daripada *poket korang*.", dict(bg='green', z=1.0, z2=1.15)),
 # ---------------- CTA
 ('C',149.59,150.62, "Kalau korang nak,", dict(bg='studio', z=1.0)),
 ('C',151.55,156.80, "*Bang Taf* boleh kirakan untuk korang, contohnya berapa instalmen kereta", dict(bg='studio', z=1.12)),
 ('B', 14.60, 20.30, "ataupun boleh terus tekan *link dekat bio* untuk buat *semakan kelayakan percuma*", dict(bg='studio', z=1.0, z2=1.06)),
 ('C',160.14,161.95, "Yang mana belum *follow*, boleh *follow*", dict(bg='studio', z=1.15)),
 ('C',162.18,164.15, "ataupun boleh *like* dan *share*.", dict(bg='studio', z=1.0)),
 ('C',164.17,165.98, "Cuba *komen* dekat bawah", dict(bg='studio', z=1.15)),
 ('C',168.89,173.33, "Apa pandangan korang untuk kadar *OPR* sekarang?", dict(bg='studio', z=1.0, qmarks=True)),
 ('C',173.45,177.25, "Waktu yang *terbaik* untuk beli kereta ataupun no?", dict(bg='studio', z=1.1, qmarks=True)),
]

# Overlays. Anchors are (clip, src_time) -> mapped to output time.
# kind, start_anchor, end_anchor, params
O = [
 # hook
 ('title', ('A',0.76), ('A',4.25), dict(lines=["Bank Negara umum", "OPR *2.75%*. Apa", "kesan pada *loan", "kereta* korang?"], sfx='whoosh')),
 ('bignum', ('A',6.95), ('A',10.12), dict(text="2.75%", color='gold', y=1430, size=230, sub="OPR TERKINI", sfx='boom')),
 ('sticker', ('A',10.45), ('A',12.95), dict(emoji="📈", x=230, y=1420, size=170, sfx='pop', cross=True)),
 ('sticker', ('A',11.86), ('A',12.95), dict(emoji="📉", x=850, y=1420, size=170, sfx='pop', cross=True)),
 ('sticker', ('A',17.72), ('A',19.25), dict(emoji="🤔", x=860, y=330, size=190, sfx='pop')),
 ('sticker', ('A',22.70), ('A',23.42), dict(emoji="🚗", x=830, y=1480, size=170, sfx='pop')),
 # apa itu OPR
 ('chip', ('A',34.08), ('A',38.75), dict(emoji="🏦", text="OPR = *Overnight Policy Rate*", y=1470, sfx='pop')),
 ('card', ('A',39.66), ('A',47.35), dict(img='c_graf', y=250, w=960, sfx='whoosh')),
 ('chip', ('A',43.97), ('A',47.35), dict(emoji="✅", text="*KEKAL* 2.75%", y=820, sfx='ding')),
 ('icons', ('A',47.86), ('A',51.95), dict(title="OPR beri kesan kepada:", items=[("🏠","Rumah",('A',48.2)),("🚗","Kereta",('A',49.0)),("🏢","Bisnes",('A',49.7)),("💳","Pinjaman",('A',50.6))], y=330)),
 # salah faham
 ('sticker', ('A',66.45), ('A',70.40), dict(emoji="🤩", x=850, y=330, size=180, sfx='boing')),
 ('sticker', ('A',67.80), ('A',70.40), dict(emoji="🚗", x=210, y=420, size=150)),
 ('sticker', ('A',68.94), ('A',70.40), dict(emoji="✨", x=190, y=260, size=120)),
 ('stamp', ('A',71.52), ('A',72.60), dict(text="SALAH!", sfx='scratch')),
 ('neq', ('A',80.58), ('A',84.35), dict(sfx='boom')),
 ('list', ('A',86.10), ('A',95.12), dict(title="Kadar loan kereta ditentukan oleh:", items=[("📦","Produk pembiayaan",('A',88.88)),("🏦","Bank",('A',90.42)),("👤","Profil peminjam",('A',90.84)),("📄","Terma pinjaman",('A',93.67))], y=250)),
 # maksud
 ('card', ('A',102.20), ('A',106.0), dict(img='c_opr', y=1390, w=820, sfx='whoosh')),
 ('sticker', ('A',108.5), ('A',111.1), dict(emoji="🚗", x=860, y=1480, size=160, sfx='pop')),
 ('strike', ('A',114.41), ('A',117.70), dict(text="OPR rendah = Loan murah", strike_at=('A',117.17), y=1480, sfx='scratch')),
 # contoh
 ('pricetag', ('A',144.94), ('A',145.87), dict(text="RM60,000", sfx='kaching')),
 ('ad', ('A',148.82), ('A',152.70), dict(sfx='ding')),
 ('sticker', ('A',156.5), ('A',159.55), dict(emoji="👀", x=860, y=330, size=170, sfx='pop')),
 ('list', ('A',161.98), ('C',4.45), dict(title="Yang korang WAJIB semak:", items=[("💰","Deposit",('A',163.57)),("🧾","Jumlah loan",('A',165.07)),("📅","Tempoh (tahun)",('A',168.42)),("⭐","Instalment bulanan",('C',2.39))], y=250, check=True)),
 # konteks ekonomi
 ('card', ('C',15.58), ('C',21.45), dict(img='c_poster', y=220, w=640, sfx='whoosh')),
 ('stats', ('C',37.70), ('C',49.15), dict(items=[("📈","KDNK Suku Ke-2 2026","6.0%",('C',39.78)),("🛒","Inflasi Julai 2026","1.8%",('C',47.08)),("🏦","OPR Semasa","2.75%",('C',37.70))], y=230)),
 ('sticker', ('C',52.71), ('C',55.80), dict(emoji="📉", x=230, y=1460, size=160, sfx='pop', cross=True)),
 ('sticker', ('C',54.04), ('C',55.80), dict(emoji="💸", x=850, y=1460, size=160, sfx='pop', cross=True)),
 # amaran
 ('banner', ('C',73.82), ('C',77.80), dict(text="⚠️ HATI-HATI", sfx='boom')),
 ('sticker', ('C',79.04), ('C',83.00), dict(emoji="🚫", x=860, y=330, size=170, sfx='pop')),
 ('compare', ('C',84.63), ('C',90.55), dict(t1=('C',85.39), t2=('C',87.33), t3=('C',90.11))),
 ('sticker', ('C',96.62), ('C',97.92), dict(emoji="🤨", x=860, y=330, size=170, sfx='boing')),
 ('tenor', ('C',100.67), ('C',110.15), dict(t1=('C',101.57), t2=('C',103.09), t3=('C',109.67))),
 # kesimpulan
 ('banner', ('C',118.12), ('C',119.78), dict(text="📌 KESIMPULAN", color='gold', sfx='whoosh')),
 ('sticker', ('C',126.64), ('C',127.92), dict(emoji="🤷", x=860, y=330, size=170, sfx='pop')),
 ('qcards', ('C',128.29), ('C',138.50), dict(items=[("📆","Berapa kena bayar *SETIAP BULAN*?",('C',131.57)),("🧮","Berapa *JUMLAH* sampai habis loan?",('C',135.20))], y=300)),
 ('rain', ('C',142.79), ('C',144.28), dict(emoji="💸", sfx='kaching')),
 # cta
 ('sticker', ('C',151.55), ('C',156.80), dict(emoji="🧮", x=860, y=330, size=170, sfx='pop')),
 ('chip', ('B',16.60), ('B',20.30), dict(emoji="🔗", text="Link di bio: *Semakan Kelayakan PERCUMA*", y=1470, sfx='ding')),
 ('chips', ('C',160.14), ('C',164.15), dict(items=[("➕","Follow",('C',160.96)),("❤️","Like",('C',163.16)),("↗️","Share",('C',163.67))], y=1400, row=True)),
 ('chip', ('C',164.17), ('C',165.98), dict(emoji="💬", text="Komen di bawah", y=1470, sfx='pop')),
]

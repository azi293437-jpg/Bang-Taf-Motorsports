# Bang Taf — "Ekonomi susah, tapi Proton jual 22,632 kereta sebulan?"
OUTRO = ("FOLLOW *Bang Taf*", "Part 2: Proton paling laku")
P = [
 # ---------------- HOOK
 ('A',  1.45,  4.90, "Ekonomi Malaysia orang kata tengah {susah} sekarang.", dict(bg='alert', z=1.0, z2=1.08, nocap=True)),
 ('A',  6.00,  7.85, "Kos sara hidup {naik}.", dict(bg='alert', z=1.2)),
 ('A', 10.00, 19.60, "Tapi peliknya, *Proton* baru je jual *22,632* biji kereta dalam satu bulan. Wow!", dict(bg='proton', z=1.0, z2=1.08)),
 ('A', 24.70, 29.35, "Jadi persoalannya, *siapa* sebenarnya yang tengah beli kereta sekarang?", dict(bg='studio', z=1.15)),
 # ---------------- DATA
 ('A', 32.75, 39.90, "Bulan Ogos 2026, Proton catat jualan sebanyak *22,632 unit*.", dict(bg='proton', layout='pip')),
 ('A', 42.62, 47.85, "Ini merupakan prestasi yang paling *terbaik* Proton sejak *Januari 2010*.", dict(bg='proton', layout='pip')),
 ('A', 48.90, 53.75, "Dan jualan domestik sahaja mencecah", dict(bg='cars', z=1.0)),
 ('A', 53.95, 57.85, "*20,155 unit*, rekod tertinggi dalam sejarah Proton.", dict(bg='cars', z=1.15, nocap=False)),
 ('A', 59.50, 63.10, "Kalau korang tengok angka *8 bulan pertama* tahun ni pula,", dict(bg='green', layout='pip')),
 ('A', 63.30, 70.95, "Proton dah jual *141,421 unit*,", dict(bg='green', layout='pip')),
 ('A', 73.80, 78.70, "[naik 40%] berbanding daripada tempoh yang tahun lepas.", dict(bg='green', layout='pip')),
 ('A', 78.75, 85.05, "*Market share* Proton pada bulan Ogos pula dah dianggarkan *27.9%*,", dict(bg='cars', layout='pip')),
 ('A', 85.20, 92.65, "bermaksud lebih kurang *1 daripada 4* kereta baru di atas jalan sekarang adalah datang daripada Proton.", dict(bg='cars', layout='pip')),
 # ---------------- PERSOALAN
 ('A', 98.00,100.95, "Tapi dekat sini, yang *menariknya*...", dict(bg='studio', z=1.2)),
 ('A',101.08,104.50, "Kalau betul ekonomi {betul-betul teruk},", dict(bg='studio', z=1.0)),
 ('A',106.25,110.20, "macam mana orang masih *mampu* beli kereta?", dict(bg='studio', z=1.15)),
 ('A',112.80,116.45, "Adakah rakyat Malaysia sebenarnya semakin *kaya*?", dict(bg='dream', z=1.3)),
 ('A',118.30,120.15, "Atau cara", dict(bg='alert', z=1.0, musicstop=0.6)),
 ('A',120.28,123.90, "kita tengok keadaan ekonomi selama ini yang {salah}?", dict(bg='alert', z=1.2)),
 # ---------------- JAWAPAN
 ('A',134.80,140.20, "Sebenarnya angka jualan kereta tak semestinya bermaksud semua orang tengah *berbelanja besar*.", dict(bg='showroom', z=1.0, z2=1.08)),
 ('A',142.80,147.70, "Ada orang beli kereta sebab kereta lama dah sampai masa nak *tukar*.", dict(bg='studio', layout='pip')),
 ('A',150.00,153.15, "Ada yang perlukan kereta sebab nak pergi *kerja*.", dict(bg='studio', layout='pip')),
 ('A',155.85,156.85, "Ada yang", dict(bg='studio', layout='pip')),
 ('A',157.15,162.75, "ambil kesempatan daripada *promosi* ataupun *trade-in* dan *kadar pembiayaan*.", dict(bg='studio', layout='pip')),
 ('A',163.05,166.50, "Dan satu lagi faktor yang tak boleh kita *abaikan*.", dict(bg='factory', z=1.15, riser=True)),
 ('A',168.20,171.12, "Proton sekarang bukan bergantung kepada", dict(bg='factory', z=1.0, z2=1.05)),
 ('A',171.58,173.40, "kereta {petrol} sahaja.", dict(bg='factory', z=1.15)),
 ('A',175.35,179.62, "Proton *e.MAS* juga sekarang sedang berkembang sangat *cepat*.", dict(bg='proton', layout='pip')),
 # ---------------- PENUTUP
 ('B',  1.45,  4.95, "Jadi daripada kita tanya ekonomi teruk ke tak,", dict(bg='studio', z=1.0)),
 ('B',  8.60, 10.65, "soalan yang lebih *menarik* ialah:", dict(bg='studio', z=1.15)),
 ('B', 13.95, 18.85, "Apa yang sebenarnya sedang berlaku kepada *kuasa membeli* rakyat Malaysia?", dict(bg='studio', z=1.0, qmarks=True)),
 ('B', 21.30, 23.35, "Sebab satu benda yang jelas,", dict(bg='proton', z=1.1)),
 ('B', 29.95, 36.95, "*22,632 unit* dalam masa satu bulan ini bukan angka yang *kecil*.", dict(bg='proton', z=1.0, z2=1.08)),
 ('B', 37.05, 40.05, "Dan sebagai orang yang memang dalam *industri kereta*,", dict(bg='showroom', z=1.15)),
 ('B', 40.25, 42.85, "aku akan *breakdown* satu lagi benda:", dict(bg='showroom', layout='pip')),
 ('B', 43.12, 49.30, "kereta Proton yang mana sebenarnya *paling banyak dibeli* oleh rakyat Malaysia sekarang.", dict(bg='showroom', layout='pip')),
]

O = [
 # hook
 ('title', ('A',1.45), ('A',4.90), dict(lines=["Ekonomi *susah*, tapi", "Proton jual *22,632*", "kereta sebulan?", "Siapa yang beli?"], sfx='whoosh')),
 ('gif', ('A',6.00), ('A',7.85), dict(file='g1.gif', w=560, y=1560, sfx='wahwah')),
 ('bignum', ('A',13.71), ('A',18.9), dict(text="22,632", count=True, color='gold', y=1545, size=190, sub="KERETA PROTON / SEBULAN", sfx='kaching')),
 ('gif', ('A',18.45), ('A',19.60), dict(file='g3.gif', w=620, y=1560, sfx='boom')),
 ('gif', ('A',25.75), ('A',29.35), dict(file='g4.gif', w=600, y=1580, sfx='pop')),
 # data
 ('card', ('A',32.75), ('A',39.90), dict(img='c_pc61f', y=280, w=940, src='proton.com', sfx='whoosh')),
 ('chip', ('A',37.26), ('A',39.90), dict(emoji="📈", text="Ogos 2026: *22,632 unit*", y=900, sfx='ding')),
 ('card', ('A',42.62), ('A',47.85), dict(img='c_pc61f', y=280, w=940, src='proton.com')),
 ('chip', ('A',44.55), ('A',47.85), dict(emoji="🏆", text="Terbaik sejak *Jan 2010*", y=900, sfx='ding')),
 ('bignum', ('A',54.0), ('A',57.85), dict(text="20,155", count=True, color='gold', y=1545, size=180, sub="JUALAN DOMESTIK • REKOD", sfx='boom')),
 ('stats', ('A',59.50), ('A',78.70), dict(items=[("📅","Jualan Jan–Ogos 2026","141,421",('A',64.82)),("📈","Berbanding tahun lepas","+40%",('A',74.79)),("🚗","Jualan Ogos 2026","22,632",('A',59.6))], y=265)),
 ('share', ('A',78.75), ('A',92.65), dict(t1=('A',82.84), t2=('A',86.89))),
 # persoalan
 ('sticker', ('A',98.0), ('A',100.95), dict(emoji="🤔", x=860, y=330, size=180, sfx='pop')),
 ('sticker', ('A',102.95), ('A',104.5), dict(emoji="📉", x=850, y=1520, size=160, sfx='pop')),
 ('sticker', ('A',108.67), ('A',110.2), dict(emoji="🚗", x=230, y=1520, size=160, sfx='pop')),
 ('gif', ('A',113.0), ('A',116.45), dict(file='g2.gif', w=520, y=1580, sfx='boing')),
 ('sticker', ('A',115.91), ('A',116.45), dict(emoji="🤑", x=860, y=330, size=170)),
 ('stamp', ('A',123.3), ('A',123.90), dict(text="SALAH?", sfx='scratch')),
 # jawapan
 ('list', ('A',142.80), ('A',162.75), dict(title="Kenapa orang masih beli kereta?", items=[("🔄","Kereta lama dah nak tukar",('A',145.06)),("💼","Perlu untuk pergi kerja",('A',151.43)),("🏷️","Promosi & trade-in",('A',159.33)),("💳","Kadar pembiayaan",('A',161.53))], y=250)),
 ('banner', ('A',163.05), ('A',166.50), dict(text="⚡ SATU LAGI FAKTOR", color='gold', sfx='boom')),
 ('sticker', ('A',172.27), ('A',173.40), dict(emoji="⛽", x=830, y=1520, size=160, sfx='pop', cross=True)),
 ('card', ('A',175.35), ('A',177.40), dict(img='c_pd247', y=280, w=900, src='mudah.my', sfx='whoosh')),
 ('card', ('A',177.40), ('A',179.62), dict(img='c_pcb95', y=280, w=900, src='paultan.org', sfx='whoosh')),
 ('chip', ('A',178.08), ('A',179.62), dict(emoji="⚡", text="EV makin laju!", y=930, sfx='ding')),
 # penutup
 ('bignum', ('B',30.0), ('B',36.95), dict(text="22,632", color='gold', y=1545, size=180, sub="UNIT DALAM 1 BULAN", sfx='boom')),
 ('chip', ('B',38.86), ('B',40.05), dict(emoji="🔧", text="Orang dalam *industri kereta*", y=1500, sfx='pop')),
 ('card', ('B',44.0), ('B',49.30), dict(img='c_p61fc', y=200, w=540, x=320, rot=4, label='Proton X50', sfx='whoosh')),
 ('card', ('B',45.3), ('B',49.30), dict(img='c_pe508', y=235, w=540, x=760, rot=-4, label='Proton Saga', sfx='whoosh')),
 ('card', ('B',46.4), ('B',49.30), dict(img='c_pd247', y=545, w=540, x=330, rot=-3, label='e.MAS 5', sfx='whoosh')),
 ('card', ('B',47.3), ('B',49.30), dict(img='c_paa65', y=575, w=540, x=750, rot=3, label='Proton S70', sfx='whoosh')),
 ('banner', ('B',46.42), ('B',49.30), dict(text="🔥 PART 2", color='gold', y=1045, sfx='ding')),
]

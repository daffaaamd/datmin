# 📊 Perbedaan: Recommender vs Personalized Picks

## 🎯 **Recommender** vs 💡 **Personalized Picks**

Sekarang ada 2 fitur rekomendasi yang berbeda dan saling melengkapi:

---

## 🎯 **Recommender** (Similarity-Based)

**Konsep:** Cari tempat lain yang **mirip** dengan 1 tempat pilihan Anda

**Cara Kerja:**

1. Pilih 1 tempat referensi
2. Sistem analisa: kategori, kota, harga, rating, fasilitas, suasana, deskripsi
3. Cari tempat lain dengan 7 faktor kesamaan
4. Hitung **skor kemiripan 0-1**

**Output:**

- Urutan berdasarkan **seberapa mirip** dengan referensi
- Alasan spesifik: "✓ Kategori sama", "✓ Harga mirip", dll
- Tempat yang paling identik peringkat pertama

**Contoh:**

```
User pilih: Taman Hiburan A
Sistem cari: Tempat mirip dengan Taman Hiburan A
Hasil: Taman Hiburan B (85% mirip), Taman Hiburan C (72% mirip), ...
```

**Gunakan ketika:** Anda sudah punya 1 tempat favorit dan ingin cari yang serupa

---

## 💡 **Personalized Picks** (Preference-Based)

**Konsep:** Dapatkan **top tempat terbaik** yang sesuai preferensi & budget Anda

**Cara Kerja:**

1. Atur preferensi: Kota, Kategori, Rating minimal, Budget maksimal
2. Filter tempat yang cocok
3. Hitung **skor kombinasi**:
   - **Rating** (40%) — Bagus atau jelek?
   - **Value for Money** (35%) — Murah atau mahal?
   - **Popularitas** (25%) — Banyak review atau sedikit?
4. Urutkan dari skor tertinggi

**Output:**

- **Top 3 Pick** dalam kartu keren (🥇🥈🥉)
- Daftar lengkap dengan skor %
- Random picker untuk kejutan

**Contoh:**

```
Filter: Yogyakarta, Pantai, Rating min 3.5, Budget max 50k
Hasil:
  🥇 Pantai A (95%) — Rating 4.8 ⭐, Rp 25k, Top rated!
  🥈 Pantai B (87%) — Rating 4.5 ⭐, Rp 30k, Value terbaik
  🥉 Pantai C (81%) — Rating 4.2 ⭐, Rp 35k, Banyak review
```

**Gunakan ketika:** Anda punya budget & preferensi, cari tempat terbaik

---

## 📋 Perbandingan Fitur

| Aspek           | 🎯 Recommender                      | 💡 Personalized Picks               |
| --------------- | ----------------------------------- | ----------------------------------- |
| **Input**       | 1 tempat referensi                  | Budget, kota, kategori, rating min  |
| **Algoritma**   | 7 faktor kesamaan                   | 3 skor (rating, value, populer)     |
| **Output**      | Mirip dengan referensi              | Top tempat terbaik                  |
| **Urutkan by**  | Similarity score                    | Combined score                      |
| **Cocok untuk** | "Ada tempat favorit, cari yg mirip" | "Cari tempat terbaik sesuai budget" |
| **Alasan**      | Detail (7 faktor)                   | Summary (3 skor)                    |

---

## 🎓 Kapan Pakai Mana?

### Gunakan 🎯 **Recommender** jika:

- ✓ Anda sudah pernah ke tempat tertentu dan suka
- ✓ Mau cari tempat yang mirip
- ✓ Ingin detail kenapa tempat itu mirip
- ✓ Analisis mendalam (kategori, fasilitas, suasana, deskripsi)

### Gunakan 💡 **Personalized Picks** jika:

- ✓ Punya budget tertentu
- ✓ Ingin tempat terbaik sesuai preferensi
- ✓ Lagi cari liburan gak tahu kemana (random picker)
- ✓ Ingin lihat top 3 pilihan tercepat

---

## 💡 Kombinasi Optimal

**Pengalaman terbaik:**

1. Mulai pakai **Personalized Picks** → Ketemu tempat X yang skor-nya bagus
2. Klik buka detail tempat X
3. Masuk **Recommender** → Cari tempat mirip dengan tempat X
4. Bandingkan hasilnya

Hasilnya: Anda punya pilihan komprehensif! 🎉

---

**Update:** Desember 2025 | Fitur dipisah untuk pengalaman lebih jelas

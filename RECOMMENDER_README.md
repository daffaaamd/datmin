# 🎯 Recommender Search — Sistem Rekomendasi Tempat Serupa

## Deskripsi Fitur

Fitur **Recommender Search** membantu pengguna menemukan tempat-tempat wisata yang paling mirip dengan satu tempat referensi yang mereka pilih. Sistem ini menganalisis 7 faktor kesamaan dan memberikan skor kemiripan 0–1, disertai penjelasan rinci tentang mengapa tempat tersebut serupa.

## Cara Kerja

### Algoritma Similarity Score

Sistem menghitung kemiripan dengan mempertimbangkan:

1. **Kategori (bobot: 25%)** - Apakah tempat masuk kategori yang sama?

   - Cocok: 100% (skor 1.0)
   - Berbeda: 0%

2. **Lokasi/Kota (bobot: 20%)** - Apakah dalam kota yang sama?

   - Sama kota: 100%
   - Beda kota: 10% (penalti kecil, tetap bisa relevan)

3. **Kisaran Harga (bobot: 20%)** - Berapa persen perbedaan harga?

   - Harga mirip: skor lebih tinggi
   - Contoh: Rp 50k vs Rp 55k: skor tinggi (mirip)
   - Contoh: Rp 10k vs Rp 500k: skor rendah (jauh berbeda)

4. **Rating (bobot: 15%)** - Apakah rating serupa?

   - Rating 4.5 ⭐ vs 4.6 ⭐: mirip (skor tinggi)
   - Rating 2.0 ⭐ vs 5.0 ⭐: jauh berbeda (skor rendah)

5. **Fasilitas (bobot: 10%)** - Jika ada kolom fasilitas, cek kesamaan kata kunci

   - Contoh: "wifi, parkir, restoran" vs "wifi, parkir, toko" → kesamaan tinggi

6. **Suasana (bobot: 10%)** - Jika ada kolom suasana, cek kesamaan kata kunci

   - Contoh: "alam, tenang, sejuk" vs "alam, santai, sejuk" → kesamaan tinggi

7. **Deskripsi (bobot: 10%)** - Text similarity: berapa banyak kata kunci yang sama?
   - Menggunakan word overlap untuk tempat dengan deskripsi panjang

**Skor Final** = Weighted average dari 7 faktor di atas, range 0–1

- 0.0 = Tidak mirip sama sekali
- 1.0 = Identik (hanya terjadi jika tempat yang sama)
- 0.5–0.8 = Mirip cukup baik (rekomendasi terbaik)

### Alasan Kemiripan

Sistem menjelaskan setiap rekomendasi dengan alasan konkret seperti:

- ✓ Kategori sama: Pantai
- ✓ Kota sama: Yogyakarta
- ✓ Kisaran harga mirip: Rp 25,000 vs Rp 28,000
- ✓ Rating mirip: 4.5⭐ vs 4.3⭐
- ✓ Fasilitas serupa
- ✓ Suasana serupa
- ✓ Tema deskripsi serupa

## Penggunaan

### Di Streamlit App

1. **Buka halaman:** Klik "🎯 Recommender" di sidebar
2. **Pilih tempat referensi:** Dropdown untuk memilih tempat yang ingin dibandingkan
3. **Atur jumlah rekomendasi:** Slider untuk memilih berapa banyak hasil (3–20)
4. **Klik tombol:** "🔍 Cari Tempat Serupa"
5. **Lihat hasil:**
   - Informasi lengkap tempat referensi (kota, kategori, rating, deskripsi)
   - Daftar tempat serupa, terurut dari yang paling mirip
   - Untuk setiap rekomendasi: skor kemiripan (%), alasan spesifik, detail tempat

### Filter Global

Sistem menggunakan filter global yang sudah diterapkan. Jika Anda filter hanya kota "Yogyakarta", maka rekomendasi hanya mencari dari data Yogyakarta.

## Contoh Output

```
🎯 Hasil Rekomendasi

#1 Pantai Parangtritis — Kemiripan: 85% (0.850)
   Kota: Yogyakarta
   Kategori: Pantai
   Rating: 4.4⭐
   Harga: Rp 25,000

   Skor Kemiripan: 0.850 (0–1)
   Alasan kemiripan:
   • ✓ Kategori sama: Pantai
   • ✓ Kota sama: Yogyakarta
   • ✓ Kisaran harga mirip: Rp 25,000 vs Rp 20,000
   • ✓ Rating mirip: 4.4⭐ vs 4.2⭐

   Deskripsi: Pantai indah di Yogyakarta dengan pasir putih...
```

## File-file

- `app.py` - Aplikasi Streamlit utama
- `recommender.py` - Modul sistem rekomendasi (fungsi-fungsi perhitungan skor)

## Fitur Unggulan

✅ **Data-driven:** Hanya menggunakan data yang ada di dataset, tidak mengarang  
✅ **Transparan:** Menjelaskan alasan setiap rekomendasi  
✅ **Fleksibel:** Bekerja dengan atau tanpa kolom fasilitas/suasana  
✅ **Cepat:** Perhitungan real-time  
✅ **User-friendly:** Interface Streamlit yang intuitif

## Keterbatasan

- Jika kolom fasilitas/suasana tidak ada, faktor tersebut tidak diperhitungkan (bobot tetap 0)
- Text similarity untuk deskripsi hanya menggunakan word overlap sederhana (bukan AI/embedding)
- Sistem tidak memperhitungkan kolom lain di luar kategori, kota, harga, rating, fasilitas, suasana, deskripsi

## Pengembangan Masa Depan

- [ ] Tambahkan text embedding (TF-IDF, BERT) untuk similarity deskripsi yang lebih akurat
- [ ] Tambahkan riwayat pencarian pengguna
- [ ] Tambahkan kolaboratif filtering (jika ada user ratings)
- [ ] Simpan preferensi pengguna untuk rekomendasi personal
- [ ] Visualisasi similarity matrix / network graph

---

**Dibuat untuk:** Dashboard Wisata Indonesia  
**Tanggal:** Desember 2025

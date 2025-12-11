# 🎯 Recommender Search — Panduan Cepat

## ✅ Status: SIAP DIGUNAKAN

File `recommender.py` sudah diperbaiki dan bersih dari error syntax.

## 📋 File-File yang Ditambahkan

1. **`recommender.py`** ✓

   - Modul sistem rekomendasi
   - Fungsi: `compute_similarity_score()` dan `get_similar_places()`
   - Status: Ready to import

2. **`app.py`** ✓ (Updated)

   - Import: `from recommender import get_similar_places`
   - Halaman baru: "🎯 Recommender" (ditambahkan ke sidebar)
   - Status: Siap pakai

3. **`RECOMMENDER_README.md`**

   - Dokumentasi lengkap fitur dan algoritma

4. **`run.bat`** (Opsional)
   - Script Windows untuk menjalankan app dengan satu klik

## 🚀 Cara Menjalankan

### Opsi 1: Command Line

```bash
cd c:\Users\Daffa Ahmad\Downloads\datmin
python -m streamlit run app.py
```

### Opsi 2: Double-click run.bat

Cukup double-click file `run.bat` yang sudah dibuat.

## 🎯 Fitur Recommender

### Lokasi di App

- Sidebar → Pilih halaman "🎯 Recommender"

### Cara Kerja

1. Pilih **tempat referensi** dari dropdown
2. Atur **jumlah rekomendasi** (slider 3–20)
3. Klik **"🔍 Cari Tempat Serupa"**
4. Lihat hasil dengan:
   - Skor kemiripan (0–1)
   - Alasan kemiripan spesifik
   - Detail lengkap setiap tempat

### Algoritma (7 Faktor)

- **Kategori** (25%) — Apakah sama kategori?
- **Kota** (20%) — Apakah di kota yang sama?
- **Harga** (20%) — Berapa persen perbedaan?
- **Rating** (15%) — Apakah rating mirip?
- **Fasilitas** (10%) — Word overlap fasilitas
- **Suasana** (10%) — Word overlap suasana
- **Deskripsi** (10%) — Text similarity deskripsi

## 🔧 Troubleshooting

### Error: "Python was not found"

**Solusi:**

- Instal Python dari https://www.python.org/downloads/
- Pilih "Add Python to PATH" saat install
- Restart terminal/command prompt

### Error: "No module named 'streamlit'"

**Solusi:**

```bash
pip install streamlit pandas numpy altair
```

### Error saat import recommender

**Status:** ✓ Sudah diperbaiki (file syntax clean)

## 📊 Output Contoh

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
```

## 📚 File Lengkap

- `recommender.py` — 207 baris, siap pakai ✓
- `app.py` — ~1226 baris (update: halaman 🎯 Recommender ditambahkan)
- `RECOMMENDER_README.md` — Dokumentasi teknis
- `QUICKSTART.md` — File ini

---

**Status:** ✅ Selesai dan siap digunakan  
**Tanggal:** 9 Desember 2025

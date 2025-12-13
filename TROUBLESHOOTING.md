# 🔧 Troubleshooting Streamlit Cloud Error

## Error: "ModuleNotFoundError: No module named 'openpyxl'"

### Penyebab

- `openpyxl` tidak ter-install di Streamlit Cloud
- `requirements.txt` tidak ter-update atau tidak ter-push ke GitHub

### Solusi

#### ✅ **Solusi 1: Update requirements.txt (Rekomendasi)**

1. Buka file `requirements.txt` di repo Anda
2. Pastikan berisi:

```txt
streamlit==1.40.0
pandas==2.1.0
numpy==1.26.0
altair==5.2.0
openpyxl==3.10.10
pillow==10.1.0
requests==2.31.0
```

3. Push ke GitHub:

```bash
git add requirements.txt
git commit -m "Fix: Update requirements with openpyxl"
git push origin main
```

4. Refresh/redeploy app di Streamlit Cloud

#### ✅ **Solusi 2: Gunakan File CSV (Alternatif)**

Jika masih error, konversi DATASET.xlsx ke CSV:

**Di Excel/Spreadsheet:**

1. Buka DATASET.xlsx
2. Save As → Format: CSV (.csv)
3. Nama: `DATASET.csv`
4. Push ke GitHub

**Di Python:**

```python
import pandas as pd
df = pd.read_excel('DATASET.xlsx')
df.to_csv('DATASET.csv', index=False)
```

Setelah itu, app akan otomatis baca DATASET.csv sebagai fallback.

#### ✅ **Solusi 3: Helper Module (Sudah Disediakan)**

Kami sudah menambahkan `data_loader.py` dengan fallback mechanism:

- Coba baca Excel dengan `openpyxl`
- Jika gagal, fallback ke `xlrd`
- Jika masih gagal, fallback ke CSV
- Jika CSV ada, baca CSV

File sudah ter-update di repo.

---

## Langkah-Langkah Untuk Deploy Ulang

### 1. Update Local Copy

```bash
cd c:\Users\Daffa Ahmad\Downloads\datmin
git pull origin main
```

### 2. Pastikan requirements.txt ada

```bash
type requirements.txt
```

Harus berisi:

```
streamlit==1.40.0
pandas==2.1.0
numpy==1.26.0
altair==5.2.0
openpyxl==3.10.10
pillow==10.1.0
requests==2.31.0
```

### 3. Push ke GitHub

```bash
git add requirements.txt
git commit -m "Fix: openpyxl requirement for Streamlit Cloud"
git push origin main
```

### 4. Streamlit Cloud akan otomatis redeploy

---

## Status File-File

| File               | Status     | Fungsi                                         |
| ------------------ | ---------- | ---------------------------------------------- |
| `requirements.txt` | ✅ Updated | List dependency                                |
| `data_loader.py`   | ✅ Baru    | Safe data loading dengan fallback              |
| `app.py`           | ✅ Ready   | Main app (bisa update untuk pakai data_loader) |

---

## Jika Masih Error

**Hubungi Streamlit Cloud Support:**

1. Klik "Manage app" (bawah kanan di app)
2. Lihat logs lengkap
3. Screenshot error
4. Contact Streamlit support di https://streamlit.io/cloud/contact

**Atau gunakan alternatif:**

- Deploy ke Heroku
- Deploy ke Railway.app
- Deploy ke render.com
- Jalankan lokal: `streamlit run app.py`

---

**Status:** ✅ Troubleshooting guide ready  
**Update:** 11 Desember 2025

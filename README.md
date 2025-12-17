# 🧭 Sistem Rekomendasi & Dashboard Wisata

🔗 **Live App (Streamlit):** [https://daffaaamd-datmin-app-galluj.streamlit.app/](https://daffaaamd-datmin-app-galluj.streamlit.app/)

Aplikasi ini adalah **dashboard analitik dan sistem rekomendasi wisata** berbasis data mining yang dibangun menggunakan **Python & Streamlit**. Aplikasi menampilkan eksplorasi data, visualisasi interaktif, serta rekomendasi destinasi wisata berdasarkan karakteristik data.

---

## ✨ Fitur Utama

* 📊 **Dashboard Wisata Interaktif**

  * Statistik dan ringkasan data wisata
  * Visualisasi interaktif (chart & grafik)

* 🧠 **Sistem Rekomendasi Wisata**

  * Rekomendasi destinasi berdasarkan data
  * Pendekatan data-driven

* ☁️ **Deploy Online dengan Streamlit Cloud**

  * Bisa diakses langsung tanpa instalasi

* 🖼️ **Visualisasi Teks (WordCloud)**

  * Analisis kata populer dari data

---

## 🛠️ Teknologi yang Digunakan

* **Python**
* **Streamlit** – Web app framework
* **Pandas & NumPy** – Data processing
* **Altair & Matplotlib** – Visualisasi
* **WordCloud** – Visualisasi teks
* **OpenPyXL** – Membaca file Excel

---

## 📂 Struktur Proyek

```bash
datmin/
├── app.py                     # Entry point Streamlit app
├── data_loader.py             # Load & preprocessing data
├── recommender.py             # Logic sistem rekomendasi
├── recommender_system_wisata.py
├── requirements.txt           # Dependency list
├── DATASET.xlsx               # Dataset utama
├── scripts/                   # Script pendukung
├── test_wordcloud.png         # Contoh output wordcloud
├── QUICKSTART.md
├── TROUBLESHOOTING.md
└── README.md
```

---

## 🚀 Cara Menjalankan Secara Lokal

1. **Clone repository**

   ```bash
   git clone https://github.com/daffaaamd/datmin.git
   cd datmin
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Jalankan aplikasi**

   ```bash
   streamlit run app.py
   ```

4. Buka browser di `http://localhost:8501`

---

## 📦 Deployment

Aplikasi ini dideploy menggunakan **Streamlit Community Cloud** dan terhubung langsung dengan repository GitHub.

🔗 **Live URL:** [https://daffaaamd-datmin-app-galluj.streamlit.app/](https://daffaaamd-datmin-app-galluj.streamlit.app/)

---

## 🧪 Dataset

Dataset utama disimpan dalam file:

```
DATASET.xlsx
```

Digunakan sebagai sumber data untuk analisis dan rekomendasi wisata.

---

## 👨‍💻 Pengembang

**Daffa Ahmad Baihaqi**
Mahasiswa / Data Enthusiast

* GitHub: [https://github.com/daffaaamd](https://github.com/daffaaamd)
* Streamlit App: [https://daffaaamd-datmin-app-galluj.streamlit.app/](https://daffaaamd-datmin-app-galluj.streamlit.app/)

---

## 📄 Lisensi

Proyek ini dibuat untuk keperluan **pembelajaran, riset, dan pengembangan sistem rekomendasi**. Silakan digunakan dan dikembangkan lebih lanjut dengan menyertakan atribusi.

---

⭐ Jika project ini membantu, jangan lupa beri **star** di GitHub!

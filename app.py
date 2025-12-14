
import os
from urllib.parse import quote

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import hashlib
import urllib.request
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Import recommender system
from recommender import get_similar_places

# =========================
# 0. KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="Dashboard Wisata",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Dashboard Wisata Indonesia")
st.caption("Analisis destinasi wisata")
# Custom CSS removed per user request (reverted to original Streamlit styles)
# =========================
# 1. LOAD DATA
# =========================
@st.cache_data
def load_data():
    # Folder tempat app.py berada
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Mencari file DATASET*.xlsx di folder; prioritas ke file yang mengandung kolom gambar
    image_cols = ["image", "image_url", "foto", "gambar", "photo", "photo_url"]
    required_cols = ["place", "city", "category", "rating", "fee"]

    dataset_candidates = [f for f in os.listdir(base_dir) if f.lower().endswith('.xlsx') and 'dataset' in f.lower()]
    selected_path = None
    # Coba pilih file yang berisi kolom required; prioritas file yang juga punya kolom gambar
    for fname in sorted(dataset_candidates):
        path = os.path.join(base_dir, fname)
        try:
            tmp = pd.read_excel(path, engine="openpyxl")
        except Exception:
            continue
        tmp.columns = [c.strip().lower() for c in tmp.columns]
        missing = [c for c in required_cols if c not in tmp.columns]
        if missing:
            continue
        # jika ada kolom gambar, langsung pilih
        if any(c in tmp.columns for c in image_cols):
            selected_path = path
            break
        # simpan sementara jika memenuhi required
        if selected_path is None:
            selected_path = path

    # fallback ke file DATASET.xlsx bila tidak ada kandidat
    if selected_path is None:
        file_path = os.path.join(base_dir, "DATASET.xlsx")
        if not os.path.exists(file_path):
            st.error(f"DATASET.xlsx tidak ditemukan di: {file_path}")
            st.stop()
    else:
        file_path = selected_path

    df = pd.read_excel(file_path, engine="openpyxl")

    # Normalisasi nama kolom (kalau ada spasi/kapital)
    df.columns = [c.strip().lower() for c in df.columns]

    # pastikan bekerja pada salinan untuk menghindari SettingWithCopyWarning
    df = df.copy()

    # Bersihkan kolom string: trim, hapus zero-width / NBSP, dan jadikan kosong menjadi NaN
    def _clean_string_val(v):
        if pd.isna(v):
            return v
        if isinstance(v, str):
            s = v.replace("\u00A0", " ")  # non-breaking space
            s = s.replace("\u200B", "")   # zero-width space
            s = s.strip()
            if s == "":
                return pd.NA
            return s
        return v

    obj_cols = df.select_dtypes(include=["object"]).columns.tolist()
    normalized_counts = {}
    for c in obj_cols:
        before_blank = int((df[c].astype(object).isna() | (df[c].astype(object).apply(lambda x: isinstance(x, str) and x.strip()==""))).sum())
        df[c] = df[c].apply(_clean_string_val)
        after_blank = int(df[c].isna().sum())
        if after_blank < before_blank:
            # unlikely, but keep track
            normalized_counts[c] = (before_blank, after_blank)
        elif after_blank > before_blank:
            normalized_counts[c] = (before_blank, after_blank)

    # Pastikan kolom penting ada
    required_cols = ["place", "city", "category", "rating", "fee"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        st.error(
            "Kolom berikut wajib ada di DATASET.xlsx: "
            + ", ".join(required_cols)
            + f"\nKolom yang hilang: {', '.join(missing)}"
        )
        st.stop()

    # Pastikan tipe data
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["fee"] = pd.to_numeric(df["fee"], errors="coerce")

    # Pastikan kolom koordinat ada: lat & lon
    # Jika belum ada, tambahkan dua kolom kosong dan simpan kembali file dataset
    lat_candidates = [c for c in df.columns if c in ("lat", "latitude")]
    lon_candidates = [c for c in df.columns if c in ("lon", "longitude")]
    need_save = False
    added_notice = None
    if not lat_candidates:
        df["lat"] = np.nan
        need_save = True
    else:
        # normalize name to 'lat'
        if "latitude" in df.columns and "lat" not in df.columns:
            df["lat"] = df["latitude"]
    if not lon_candidates:
        df["lon"] = np.nan
        need_save = True
    else:
        if "longitude" in df.columns and "lon" not in df.columns:
            df["lon"] = df["longitude"]

    if need_save:
        try:
            # tulis kembali ke file dataset yang dipilih
            df.to_excel(file_path, index=False, engine="openpyxl")
            # Note: don't announce lat/lon auto-added to avoid confusion for users
        except Exception:
            added_notice = "Gagal menyimpan dataset setelah menambahkan kolom lat/lon. Silakan tambahkan kolom secara manual."

    # Jika ada normalisasi string yang mengubah banyak nilai menjadi kosong, tambahkan info-notice
    if normalized_counts:
        parts = [f"{k}: {v[0]} → {v[1]} kosong" for k, v in normalized_counts.items()]
        note = "; ".join(parts)
        added_notice = (added_notice + "\n" if added_notice else "") + f"Normalisasi teks dilakukan (trim & hapus karakter tersembunyi): {note}"

    # Label harga (buat grouping di chart)
    max_fee = df["fee"].max()
    if pd.isna(max_fee) or not np.isfinite(max_fee):
        # fallback bila semua fee kosong: gunakan batas atas default
        max_fee = 100000
    # pastikan bins naik (gunakan sedikit buffer di atas max_fee)
    upper = max(max_fee, 100000) + 1
    bins = [-0.1, 0, 25000, 50000, 100000, upper]
    labels = ["Gratis", "<= 25k", "25k - 50k", "50k - 100k", "> 100k"]
    try:
        df["fee_group"] = pd.cut(df["fee"], bins=bins, labels=labels)
    except Exception:
        # jika terjadi masalah, isi dengan NaN dan lanjutkan
        df["fee_group"] = pd.Series([pd.NA] * len(df))

    # Bucket rating
    df["rating_group"] = pd.cut(
        df["rating"],
        bins=[0, 3, 3.5, 4, 4.5, 5],
        labels=["< 3", "3 - 3.5", "3.5 - 4", "4 - 4.5", "4.5 - 5"]
    )

    return df, added_notice, file_path


df, added_notice, dataset_file = load_data()

# Tampilkan notifikasi (jangan panggil st.* dari dalam fungsi yang di-cache)
if added_notice:
    try:
        if str(added_notice).lower().startswith("gagal"):
            st.warning(added_notice)
        else:
            st.info(added_notice)
    except Exception:
        pass

# =========================
# 2. UTILITIES
# =========================
def build_embed_url(row: pd.Series) -> str | None:
    """
    Bangun URL Google Maps embed dari place + city + alamat.
    Tidak tergantung kolom 'link', jadi bisa auto untuk semua tempat.
    """
    parts = []
    for col in ["place", "city", "alamat"]:
        if col in row.index:
            val = row.get(col)
            if isinstance(val, str) and val.strip():
                parts.append(val.strip())

    if not parts:
        return None

    query = quote(", ".join(parts))
    # format embed generik: q=keyword&output=embed
    return f"https://www.google.com/maps?q={query}&output=embed"


def get_safe_col(df: pd.DataFrame, col: str):
    return df[col] if col in df.columns else None


def haversine(lat1, lon1, lat2, lon2):
    """Return distance in kilometers between two points."""
    try:
        # Guard: if any input is missing or non-numeric, return NaN early
        arr = np.array([lat1, lon1, lat2, lon2], dtype=float)
        if np.any(np.isnan(arr)):
            return float('nan')

        # convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(np.radians, arr)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
        c = 2 * np.arcsin(np.sqrt(a))
        km = 6371.0 * c
        return float(km)
    except Exception:
        return float('nan')


# ============= Image fetch & cache helper =============
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(BASE_DIR, ".cache_images")
os.makedirs(CACHE_DIR, exist_ok=True)

def _normalize_shared_url(src: str) -> str:
    """Handle common sharing links (Dropbox, Google Drive) and convert to direct download when possible."""
    try:
        parsed = urlparse(src)
    except Exception:
        return src

    host = parsed.netloc.lower()
    # Dropbox: make dl=1
    if "dropbox.com" in host:
        if "dl=0" in src:
            return src.replace("dl=0", "dl=1")
        if "dl=1" in src:
            return src
        if "?" in src:
            return src + "&dl=1"
        return src + "?dl=1"

    # Google Drive share links -> convert to uc?export=download&id=FILEID
    if "drive.google.com" in host:
        # patterns: /file/d/FILEID/view?usp=sharing  or open?id=FILEID
        parts = parsed.path.split("/")
        if "/file/d/" in src and "/view" in src:
            # extract id between /d/ and /view
            try:
                fid = parts[parts.index('d') + 1]
            except Exception:
                fid = None
            if fid:
                return f"https://drive.google.com/uc?export=download&id={fid}"
        qs = parse_qs(parsed.query)
        if "id" in qs:
            fid = qs.get("id")[0]
            return f"https://drive.google.com/uc?export=download&id={fid}"
        return src

    return src


def fetch_image_to_cache(src: str) -> str | None:
    """Given a source (URL or local path string), try to return a local cached file path or None.

    - Normalizes common sharing urls
    - Downloads remote images into `.cache_images/` using a hash filename
    - If src is a local path, returns it if exists (absolute or relative to app)
    """
    if not isinstance(src, str):
        return None
    s = src.strip()
    if not s:
        return None

    # If looks like local path
    if os.path.exists(s):
        return s
    rel = os.path.join(BASE_DIR, s)
    if os.path.exists(rel):
        return rel

    # Normalize shared links
    s2 = _normalize_shared_url(s)

    # create cache filename
    h = hashlib.sha1(s2.encode('utf-8')).hexdigest()
    # try to preserve extension when possible
    path_ext = os.path.splitext(urlparse(s2).path)[1]
    if not path_ext:
        path_ext = ".jpg"
    dest = os.path.join(CACHE_DIR, f"{h}{path_ext}")
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return dest

    # Only attempt download for http(s)
    if s2.startswith("http://") or s2.startswith("https://"):
        try:
            req = urllib.request.Request(s2, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
                # Basic validate: ensure bytes length
                if not data or len(data) < 100:
                    # probably not an image
                    return None
                with open(dest, "wb") as f:
                    f.write(data)
                return dest
        except Exception:
            return None

    return None


def display_image(src: str | None, caption: str | None = None, small: bool = False):
    """Try to display an image given a source string. Uses cached local copy when possible."""
    if not src:
        return False
    try:
        cached = None
        if isinstance(src, str):
            cached = fetch_image_to_cache(src)
        if cached:
            st.image(cached, caption=caption or "", use_container_width=True)
            return True

        # fallback: if src is URL, try direct
        if isinstance(src, str) and (src.startswith("http://") or src.startswith("https://")):
            st.image(src, caption=caption or "", use_container_width=True)
            return True

        # fallback: local relative path
        rel = os.path.join(BASE_DIR, str(src))
        if os.path.exists(rel):
            st.image(rel, caption=caption or "", use_container_width=True)
            return True
    except Exception:
        return False
    return False


# =========================
# 3. SIDEBAR
# =========================
with st.sidebar:
    st.header("⚙️ Pengaturan")

    page = st.radio(
        "Pilih halaman",
        ["📊 Overview", "🔍 Eksplor Data", "🗺️ Peta & Detail", "🔎 Content", "📈 Insights", "🎯 Recommender", "💡 Personalized Picks"],
        index=0
    )

    st.markdown("---")
    st.subheader("Filter Data Global")

    # Filter kota
    city_col = get_safe_col(df, "city")
    if city_col is not None:
        all_cities = sorted(city_col.dropna().unique())
        selected_cities = st.multiselect(
            "Kota",
            options=all_cities,
            default=all_cities
        )
    else:
        selected_cities = []

    # Filter kategori
    cat_col = get_safe_col(df, "category")
    if cat_col is not None:
        all_categories = sorted(cat_col.dropna().unique())
        selected_categories = st.multiselect(
            "Kategori",
            options=all_categories,
            default=all_categories
        )
    else:
        selected_categories = []

    # Filter rating
    min_rating = float(df["rating"].min())
    max_rating = float(df["rating"].max())
    rating_range = st.slider(
        "Range rating",
        min_value=0.0,
        max_value=5.0,
        value=(min_rating, max_rating),
        step=0.1
    )

    # Filter harga
    min_fee = int(df["fee"].min())
    max_fee_slider = int(df["fee"].max())
    # Default cap at 99th percentile to avoid one huge outlier squashing the distribution
    try:
        default_cap = int(df["fee"].quantile(0.99))
        if default_cap < min_fee:
            default_cap = max_fee_slider
    except Exception:
        default_cap = max_fee_slider

    max_fee = st.slider(
        "Max harga tiket (IDR)",
        min_value=min_fee,
        max_value=max_fee_slider,
        value=default_cap,
        step=1000,
        help="Default diset ke 99th percentile untuk menghindari outlier ekstrem; geser untuk memasukkan seluruh rentang."
    )

    st.markdown("---")
    keyword = st.text_input(
        "Cari nama tempat / alamat / deskripsi",
        value=""
    )

    # Dataset info + reload / clean actions
    st.markdown("---")
    try:
        ds_name = os.path.basename(dataset_file)
        mtime = os.path.getmtime(dataset_file)
        mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        st.write(f"**Dataset:** {ds_name}")
        st.write(f"**Terakhir diubah:** {mtime_str}")
    except Exception:
        ds_name = None

    if st.button("🔄 Reload dataset (clear cache)"):
        st.cache_data.clear()
        st.experimental_rerun()

    st.write("**Pembersihan dataset**")
    confirm_save = st.checkbox("Saya yakin ingin menyimpan perubahan bersih ke file dataset")
    if st.button("🧹 Clean & Save dataset"):
        if not confirm_save:
            st.warning("Centang kotak konfirmasi sebelum menyimpan perubahan ke file.")
        else:
            try:
                tmp = pd.read_excel(dataset_file, engine="openpyxl")
                # cleaning logic: trim, remove zero-width/NBSP, turn empty -> NaN
                def _clean_string_val_local(v):
                    if pd.isna(v):
                        return v
                    if isinstance(v, str):
                        s = v.replace("\u00A0", " ")
                        s = s.replace("\u200B", "")
                        s = s.strip()
                        if s == "":
                            return pd.NA
                        return s
                    return v

                before = tmp.isna().sum()
                for c in tmp.select_dtypes(include=["object"]).columns:
                    tmp[c] = tmp[c].apply(_clean_string_val_local)
                after = tmp.isna().sum()
                tmp.to_excel(dataset_file, index=False, engine="openpyxl")
                diffs = []
                for col in before.index:
                    if after[col] != before[col]:
                        diffs.append(f"{col}: {before[col]} → {after[col]}")
                summary = "; ".join(diffs) if diffs else "Tidak ada perubahan (sudah bersih)."
                st.success(f"Berhasil membersihkan dan menyimpan {ds_name}: {summary}")
                st.cache_data.clear()
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Gagal menyimpan: {e}")


# =========================
# 4. FUNGSI FILTER
# =========================
def apply_filters(data: pd.DataFrame) -> pd.DataFrame:
    filtered = data.copy()

    if "city" in filtered.columns and selected_cities:
        filtered = filtered[filtered["city"].isin(selected_cities)]

    if "category" in filtered.columns and selected_categories:
        filtered = filtered[filtered["category"].isin(selected_categories)]

    filtered = filtered[
        (filtered["rating"] >= rating_range[0]) &
        (filtered["rating"] <= rating_range[1]) &
        (filtered["fee"] <= max_fee)
    ]

    if keyword:
        mask_parts = []
        for col in ["place", "alamat", "deskripsi"]:
            if col in filtered.columns:
                mask_parts.append(
                    filtered[col].astype(str).str.contains(keyword, case=False, na=False)
                )
        if mask_parts:
            mask = mask_parts[0]
            for m in mask_parts[1:]:
                mask |= m
            filtered = filtered[mask]

    return filtered


filtered_df = apply_filters(df)

if filtered_df.empty:
    st.warning("Tidak ada data yang cocok dengan filter. Coba longgarkan filter di sidebar 🙏")
    st.stop()

# =========================
# 5. HALAMAN OVERVIEW
# =========================
if page == "📊 Overview":
    st.subheader("📊 Gambaran Umum")

    # Tampilkan ringkasan dataset (jumlah baris asli & total fee) untuk verifikasi cepat
    raw_total = len(df)
    displayed_total = len(filtered_df)
    try:
        total_fee_dataset = int(df['fee'].dropna().sum())
    except Exception:
        total_fee_dataset = None
    try:
        total_fee_displayed = int(filtered_df['fee'].dropna().sum())
    except Exception:
        total_fee_displayed = None

    # (Summary values calculated but not displayed here by request)

    # Banner gambar umum dihapus (sesuai permintaan pengguna)

    # KPI / metric di atas dengan mini-chart
    k1, k2, k3, k4 = st.columns(4)

    # Jumlah tempat
    with k1:
        st.metric("Jumlah Tempat", f"{len(filtered_df):,}")
        city_counts_small = (
            filtered_df.groupby("city")["place"].count().reset_index(name="jumlah_tempat").sort_values("jumlah_tempat", ascending=False).head(5)
        )
        ch = alt.Chart(city_counts_small).mark_bar().encode(
            x=alt.X("jumlah_tempat:Q", title=None),
            y=alt.Y("city:N", title=None, sort='-x'),
            color=alt.Color("city:N", legend=None),
            tooltip=["city", "jumlah_tempat"]
        )
        st.altair_chart(ch, use_container_width=True)

    # Rata-rata rating
    with k2:
        mean_rating = filtered_df['rating'].mean()
        mean_rating_disp = f"{mean_rating:.2f}" if pd.notna(mean_rating) else "N/A"
        st.metric("Rata-rata Rating", mean_rating_disp)
        rh = alt.Chart(filtered_df).mark_bar(opacity=0.6).encode(
            x=alt.X("rating:Q", bin=alt.Bin(maxbins=10), title=None),
            y=alt.Y("count():Q", title=None)
        )
        st.altair_chart(rh, use_container_width=True)

    # Rata-rata harga tiket
    with k3:
        mean_fee = filtered_df['fee'].mean()
        mean_fee_disp = f"Rp {mean_fee:,.0f}" if pd.notna(mean_fee) else "N/A"
        st.metric("Rata-rata Harga (IDR)", mean_fee_disp)
        fh = alt.Chart(filtered_df).mark_bar(opacity=0.6).encode(
            x=alt.X("fee:Q", bin=alt.Bin(maxbins=8), title=None),
            y=alt.Y("count():Q", title=None)
        )
        st.altair_chart(fh, use_container_width=True)

    # Jumlah kota
    with k4:
        st.metric("Jumlah Kota", f"{filtered_df['city'].nunique():,}")
        cat_small = (
            filtered_df.groupby("category")["place"].count().reset_index(name="jumlah_tempat").sort_values("jumlah_tempat", ascending=False).head(5)
        )
        ch2 = alt.Chart(cat_small).mark_bar().encode(
            x=alt.X("jumlah_tempat:Q", title=None),
            y=alt.Y("category:N", title=None, sort='-x'),
            color=alt.Color("category:N", legend=None),
            tooltip=["category", "jumlah_tempat"]
        )
        st.altair_chart(ch2, use_container_width=True)

    st.markdown("---")

    # Grid charts (2x2)
    row1c1, row1c2 = st.columns(2)

    with row1c1:
        st.subheader("📍 Jumlah tempat per kota")
        city_counts = (
            filtered_df.groupby("city")["place"].count().reset_index(name="jumlah_tempat").sort_values("jumlah_tempat", ascending=False)
        )
        chart_city = (
            alt.Chart(city_counts)
            .mark_bar()
            .encode(
                x=alt.X("jumlah_tempat:Q", title="Jumlah tempat"),
                y=alt.Y("city:N", sort="-x", title="Kota"),
                color=alt.Color("city:N", legend=None),
                tooltip=["city", "jumlah_tempat"]
            )
        )
        st.altair_chart(chart_city, use_container_width=True)

    with row1c2:
        st.subheader("🎭 Jumlah tempat per kategori")
        cat_counts = (
            filtered_df.groupby("category")["place"].count().reset_index(name="jumlah_tempat").sort_values("jumlah_tempat", ascending=False)
        )
        chart_cat = (
            alt.Chart(cat_counts)
            .mark_bar()
            .encode(
                x=alt.X("jumlah_tempat:Q", title="Jumlah tempat"),
                y=alt.Y("category:N", sort="-x", title="Kategori"),
                color=alt.Color("category:N", legend=None),
                tooltip=["category", "jumlah_tempat"]
            )
        )
        st.altair_chart(chart_cat, use_container_width=True)

    row2c1, row2c2 = st.columns(2)

    with row2c1:
        st.subheader("⭐ Rata-rata rating per kota")
        avg_rating_city = (
            filtered_df.groupby("city")["rating"].mean().reset_index(name="avg_rating").sort_values("avg_rating", ascending=False)
        )
        chart_avg_rating = (
            alt.Chart(avg_rating_city)
            .mark_bar()
            .encode(
                x=alt.X("avg_rating:Q", title="Rata-rata rating"),
                y=alt.Y("city:N", sort="-x", title="Kota"),
                color=alt.Color("city:N", legend=None),
                tooltip=["city", "avg_rating"]
            )
        )
        st.altair_chart(chart_avg_rating, use_container_width=True)

    with row2c2:
        st.subheader("💰 vs ⭐ Harga tiket dan rating")
        scatter = (
            alt.Chart(filtered_df)
            .mark_circle(size=80, opacity=0.7)
            .encode(
                x=alt.X("fee:Q", title="Harga tiket (IDR)"),
                y=alt.Y("rating:Q", title="Rating"),
                color=alt.Color("category:N", title="Kategori"),
                tooltip=["place", "city", "category", "fee", "rating"]
            )
        )
        st.altair_chart(scatter, use_container_width=True)

    st.markdown("---")
    st.subheader("Distribusi Harga Tiket")
    # Show histogram but limit x-axis to the current max_fee so extreme highs don't squash the bars
    hist_fee = (
        alt.Chart(filtered_df)
        .mark_bar()
        .encode(
            x=alt.X("fee:Q", bin=alt.Bin(maxbins=20), title="Harga tiket (IDR)", scale=alt.Scale(domain=[0, max_fee])),
            y=alt.Y("count():Q", title="Jumlah tempat"),
            tooltip=["count()"]
        )
    )
    st.altair_chart(hist_fee, use_container_width=True)

    # Informasi: berapa data yang dikecualikan karena melebihi batas max_fee
    try:
        n_outliers = int((df["fee"] > max_fee).sum())
        if n_outliers > 0:
            st.caption(f"{n_outliers:,} tempat dikecualikan karena harga > Rp {max_fee:,} (outliers). Geser slider untuk menampilkannya.")
    except Exception:
        pass

    # Tambahkan chart tambahan: Donut chart kategori & boxplot harga per kategori
    rowc1, rowc2 = st.columns([1, 1])
    with rowc1:
        st.subheader("Proporsi Kategori (Donut)")
        cat_counts_all = (
            filtered_df.groupby("category")["place"].count().reset_index(name="jumlah_tempat").sort_values("jumlah_tempat", ascending=False)
        )
        pie = (
            alt.Chart(cat_counts_all)
            .mark_arc(innerRadius=60)
            .encode(
                theta=alt.Theta("jumlah_tempat:Q", title="Jumlah tempat"),
                color=alt.Color("category:N", title="Kategori"),
                tooltip=["category", "jumlah_tempat"]
            )
        )
        st.altair_chart(pie, use_container_width=True)

    with rowc2:
        st.subheader("Boxplot Harga per Kategori")
        try:
            box = (
                alt.Chart(filtered_df)
                .mark_boxplot()
                .encode(
                    x=alt.X("category:N", title="Kategori"),
                    y=alt.Y("fee:Q", title="Harga tiket (IDR)"),
                    color=alt.Color("category:N", legend=None),
                    tooltip=["category", "fee"]
                )
            )
            st.altair_chart(box, use_container_width=True)
        except Exception:
            st.write("Boxplot tidak tersedia untuk dataset ini.")

    st.markdown("---")

    # Fitur 'Smart Picks' — rekomendasi otomatis sederhana menggabungkan rating dan harga
    st.subheader("✨ Smart Picks — Rekomendasi Pintar")
    st.write("Saya gabungkan rating tinggi dan harga ramah kantong untuk merekomendasikan beberapa tempat.")

    def compute_score(df_in: pd.DataFrame) -> pd.DataFrame:
        dfc = df_in.copy()
        # Normalisasi rating (0-5) -> 0..1
        dfc["rating_norm"] = dfc["rating"].fillna(0) / 5.0
        # Normalisasi fee: inversely proportional (lebih kecil fee -> lebih baik)
        fee_min = dfc["fee"].min()
        fee_max = dfc["fee"].max()
        if pd.isna(fee_min) or pd.isna(fee_max) or fee_max == fee_min:
            dfc["fee_norm"] = 0.5
        else:
            dfc["fee_norm"] = 1 - ((dfc["fee"].fillna(fee_max) - fee_min) / (fee_max - fee_min))

        # score: 0.7 * rating_norm + 0.3 * fee_norm
        dfc["smart_score"] = (0.7 * dfc["rating_norm"]) + (0.3 * dfc["fee_norm"])
        return dfc

    scored = compute_score(filtered_df)
    top5 = scored.sort_values("smart_score", ascending=False).head(5)

    # Tampilkan top5 dalam baris kartu
    cards = st.columns(5)
    for i, (_, r) in enumerate(top5.iterrows()):
        with cards[i]:
            # (Image display removed) show textual card
            st.markdown(f"**{r['place']}**")
            st.markdown(f"{r['city']}")
            st.markdown(f"⭐ {r['rating']:.1f} — Rp {r['fee']:,.0f}")
            # link ke google maps
            em = build_embed_url(r)
            if isinstance(r.get('link'), str):
                st.markdown(f"[🌐 Buka di Google Maps]({r.get('link')})")
            elif em:
                st.markdown(f"[🌐 Buka di Google Maps (auto)]({em})")

    with st.expander("Lihat beberapa baris data mentah"):
        st.dataframe(filtered_df.head(20))

# =========================
# 6. HALAMAN EKSPLORASI
# =========================
elif page == "🔍 Eksplor Data":
    st.subheader("🔍 Eksplorasi Data Tempat Wisata")

    display_cols = [
        "place", "city", "category", "rating", "fee",
        "alamat", "deskripsi", "link",
        # Tambahan kolom review/ulasan dan opening hours (jika ada di dataset)
        "review", "ulasan", "opening_hours", "opening hours"
    ]
    display_cols = [c for c in display_cols if c in filtered_df.columns]

    # Untuk tampilan, ganti NaN/None dengan string kosong supaya tidak tampil sebagai 'None' atau 'nan'
    st.dataframe(filtered_df[display_cols].fillna("").reset_index(drop=True))

    st.markdown("---")

    # Tombol download CSV
    csv_bytes = filtered_df[display_cols].fillna("").to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download data (CSV) sesuai filter",
        data=csv_bytes,
        file_name="wisata_filtered.csv",
        mime="text/csv"
    )

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Top 10 tempat dengan rating tertinggi")
        top_rating = (
            filtered_df
            .sort_values(["rating", "fee"], ascending=[False, True])
            .head(10)
        )
        st.dataframe(top_rating[display_cols].fillna("").reset_index(drop=True))

    with col_b:
        st.subheader("Top 10 tempat paling murah (rating ≥ 4)")
        murah_bagus = (
            filtered_df[filtered_df["rating"] >= 4]
            .sort_values(["fee", "rating"], ascending=[True, False])
            .head(10)
        )
        st.dataframe(murah_bagus[display_cols].fillna("").reset_index(drop=True))

# =========================
# 7. HALAMAN PETA & DETAIL
# =========================
elif page == "🗺️ Peta & Detail":
    st.subheader("🗺️ Peta & Detail Tempat Wisata")

    col_left, col_right = st.columns([1, 2])

    with col_left:
        st.markdown("### Pilih tempat")

        selected_city_map = st.selectbox(
            "Kota",
            options=sorted(filtered_df["city"].unique())
        )

        df_city = filtered_df[filtered_df["city"] == selected_city_map]

        selected_place = st.selectbox(
            "Tempat wisata",
            options=df_city["place"].tolist()
        )

        place_row = df_city[df_city["place"] == selected_place].iloc[0]

        # Scoped card styling for this left panel: dark card with padding and subtle shadow
        st.markdown(
            """
            <style>
            .detail-card { background: #1E1E1E; color: #ffffff; padding: 22px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); }
            .detail-card .title { font-size: 20px; font-weight: 700; margin-bottom: 8px; line-height:1.2; }
            .detail-card .meta-row { display:flex; gap:12px; align-items:flex-start; margin:8px 0; }
            .detail-card .meta-label { width:120px; color:#b6bcc4; font-weight:600; }
            .detail-card .meta-value { color:#ffffff; line-height:1.6; }
            .detail-card .section { margin-top:10px; }
            .detail-card hr { border:none; border-top:1px solid rgba(255,255,255,0.06); margin:10px 0; }
            .detail-card .review-box { background: rgba(255,255,255,0.03); padding:10px; border-radius:8px; }
            .detail-card .hours { background: rgba(255,255,255,0.02); padding:8px; border-radius:6px; display:inline-block; }
            a.detail-link { color:#7dd3fc; }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # build card HTML
        try:
            name_v = place_row.get('place', '')
            city_v = place_row.get('city', '')
            cat_v = place_row.get('category', '')
            rating_v = place_row.get('rating')
            fee_v = place_row.get('fee')
            alamat_v = place_row.get('alamat') if 'alamat' in place_row.index else ''
            desc_v = place_row.get('deskripsi') if 'deskripsi' in place_row.index else ''

            rating_html = f"⭐ {float(rating_v):.1f}" if pd.notna(rating_v) else "N/A"
            try:
                fee_html = f"Rp {int(fee_v):,}"
            except Exception:
                fee_html = str(fee_v) if pd.notna(fee_v) else "N/A"

            html = f"<div class='detail-card'>"
            html += f"<div class='title'>{name_v}</div>"
            html += f"<div class='meta-row'><div class='meta-label'>Kota:</div><div class='meta-value'>{city_v}</div></div>"
            html += f"<div class='meta-row'><div class='meta-label'>Kategori:</div><div class='meta-value'>{cat_v}</div></div>"
            html += f"<div class='meta-row'><div class='meta-label'>Rating:</div><div class='meta-value'>{rating_html}</div></div>"
            html += f"<div class='meta-row'><div class='meta-label'>Harga tiket:</div><div class='meta-value'>{fee_html}</div></div>"

            if alamat_v and pd.notna(alamat_v):
                html += f"<div class='meta-row'><div class='meta-label'>Alamat:</div><div class='meta-value'>{alamat_v}</div></div>"

            if desc_v and pd.notna(desc_v):
                html += f"<hr><div class='meta-row'><div class='meta-label'>Deskripsi:</div><div class='meta-value'>{desc_v}</div></div>"

            # reviews
            rev_texts = []
            for rev_col in ("review", "ulasan"):
                if rev_col in place_row.index:
                    r = place_row.get(rev_col)
                    if pd.notna(r) and str(r).strip():
                        rev_texts.append(str(r))
            if rev_texts:
                html += f"<hr><div class='section'><div class='meta-row'><div class='meta-label'>Ulasan:</div><div class='meta-value'>"
                for r in rev_texts:
                    html += f"<div class='review-box'>{r}</div>"
                html += "</div></div></div>"

            # opening hours
            op_val = None
            for op_col in ("opening_hours", "opening hours", "jam_buka", "jam buka"):
                if op_col in place_row.index:
                    v = place_row.get(op_col)
                    if pd.notna(v) and str(v).strip():
                        op_val = v
                        break
            if op_val:
                html += f"<hr><div class='meta-row'><div class='meta-label'>Jam Buka:</div><div class='meta-value hours'>{op_val}</div></div>"

            # google maps link
            link_col = place_row.get('link')
            embed_url = build_embed_url(place_row)
            if isinstance(link_col, str):
                html += f"<hr><div class='meta-row'><div class='meta-label'></div><div class='meta-value'><a class='detail-link' href='{link_col}' target='_blank'>🌐 Buka di Google Maps (link)</a></div></div>"
            elif embed_url:
                html += f"<hr><div class='meta-row'><div class='meta-label'></div><div class='meta-value'><a class='detail-link' href='{embed_url}' target='_blank'>🌐 Buka di Google Maps (auto)</a></div></div>"

            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)

            # (Deskripsi dan Ulasan sekarang ditampilkan langsung di dalam card)
        except Exception:
            # fallback to simple prints on error
            st.markdown(f"**Nama:** {place_row.get('place','')}")
            st.markdown(f"**Kota:** {place_row.get('city','')}")
            st.markdown(f"**Kategori:** {place_row.get('category','')}")
            st.markdown(f"**Rating:** ⭐ {place_row.get('rating','')}")
            st.markdown(f"**Harga tiket:** Rp {place_row.get('fee','')}")

    with col_right:
        st.markdown("### Peta (Google Maps embed)")

        embed_url = build_embed_url(place_row)

        if embed_url:
            st.components.v1.iframe(embed_url, height=450)
        else:
            st.info("Tidak bisa membuat link embed untuk tempat ini.")

        st.markdown("---")

        # Peta titik sederhana dengan st.map kalau ada lat/lon
        if {"lat", "lon"}.issubset(filtered_df.columns):
            df_map = df_city.rename(columns={"lat": "latitude", "lon": "longitude"}).copy()
            # Pastikan ada nilai numerik (coerce non-numeric -> NaN) lalu dropna
            try:
                df_map["latitude"] = pd.to_numeric(df_map["latitude"], errors="coerce")
                df_map["longitude"] = pd.to_numeric(df_map["longitude"], errors="coerce")
                coords = df_map[["latitude", "longitude"]].dropna()
                if not coords.empty:
                    # st.map expects column names 'lat'/'lon' or 'latitude'/'longitude'
                    st.map(coords)
                else:
                    # kolom ada tapi belum diisi; tidak menampilkan pesan tambahan
                    pass
            except Exception:
                # jangan menampilkan traceback; cukup lewati peta bila ada masalah
                pass

# =========================
# =========================
# 8. HALAMAN SPOTLIGHT (pengganti Content)
# =========================
elif page == "🔎 Content":
    st.subheader("✨ Spotlight — Pilihan Menarik")

    st.write("Sorotan sederhana: acak satu tempat, leaderboard ekstrim, dan bandingkan dua kota.")

    # ---- Sorotan acak (random spotlight) ----
    with st.expander("🎯 Sorotan Acak"):
        # tombol untuk mengganti sorotan
        if "spotlight_idx" not in st.session_state:
            st.session_state["spotlight_idx"] = None

        if st.button("🎲 Acak tempat sorotan"):
            st.session_state["spotlight_idx"] = int(filtered_df.sample(1).index[0])

        if st.session_state.get("spotlight_idx") is None:
            st.session_state["spotlight_idx"] = int(filtered_df.sample(1).index[0])

        try:
            spr = filtered_df.loc[st.session_state["spotlight_idx"]]
        except Exception:
            spr = filtered_df.sample(1).iloc[0]
            st.session_state["spotlight_idx"] = int(spr.name)

        st.markdown(f"**{spr['place']}** — {spr['city']}")
        st.markdown(f"Kategori: {spr['category']}")
        st.markdown(f"⭐ Rating: {spr.get('rating', 'N/A')}")
        try:
            st.markdown(f"Harga: Rp {int(spr.get('fee',0)):,}")
        except Exception:
            st.markdown(f"Harga: {spr.get('fee', 'N/A')}")
        if 'alamat' in spr.index and pd.notna(spr.get('alamat')):
            st.markdown(f"**Alamat:** {spr.get('alamat')}")
        if 'deskripsi' in spr.index and pd.notna(spr.get('deskripsi')):
            st.write(spr.get('deskripsi'))

        # embed maps kecil bila tersedia
        em = build_embed_url(spr)
        if em:
            st.components.v1.iframe(em, height=280)

    st.markdown("---")

    # ---- Leaderboard ekstrim ----
    st.subheader("🏆 Leaderboard Ekstrem")
    lcol1, lcol2 = st.columns(2)
    with lcol1:
        st.markdown("**Termurah (top 5)**")
        cheap = filtered_df.sort_values("fee").head(5)[[c for c in ["place","city","fee","rating"] if c in filtered_df.columns]]
        st.dataframe(cheap.reset_index(drop=True))

    with lcol2:
        st.markdown("**Termahal (top 5)**")
        exp = filtered_df.sort_values("fee", ascending=False).head(5)[[c for c in ["place","city","fee","rating"] if c in filtered_df.columns]]
        st.dataframe(exp.reset_index(drop=True))

    lcol3, lcol4 = st.columns(2)
    with lcol3:
        st.markdown("**Rating Tertinggi (top 5)**")
        top_r = filtered_df.sort_values("rating", ascending=False).head(5)[[c for c in ["place","city","rating","fee"] if c in filtered_df.columns]]
        st.dataframe(top_r.reset_index(drop=True))

    with lcol4:
        st.markdown("**Deskripsi Terpanjang (top 5)**")
        if "deskripsi" in filtered_df.columns:
            long = (
                filtered_df.assign(desc_len=filtered_df["deskripsi"].fillna("").astype(str).str.len())
                .sort_values("desc_len", ascending=False)
                .head(5)[[c for c in ["place","city","desc_len","rating"] if c in filtered_df.columns or c=="desc_len"]]
            )
            st.dataframe(long.reset_index(drop=True))
        else:
            st.write("Tidak ada kolom `deskripsi` di dataset.")

    st.markdown("---")

    # ---- Bandingkan dua kota ----
    st.subheader("📊 Bandingkan Dua Kota")
    city_opts = sorted(filtered_df["city"].dropna().unique())
    if len(city_opts) < 2:
        st.info("Butuh minimal dua kota di dataset untuk membandingkan.")
    else:
        ca, cb = st.columns(2)
        with ca:
            city_a = st.selectbox("Kota A", options=city_opts, index=0)
        with cb:
            default_idx = 1 if len(city_opts) > 1 else 0
            city_b = st.selectbox("Kota B", options=city_opts, index=default_idx)

        if city_a and city_b:
            da = filtered_df[filtered_df["city"] == city_a]
            db = filtered_df[filtered_df["city"] == city_b]

            comp = pd.DataFrame({
                "metric": ["avg_rating", "avg_fee", "count_places"],
                city_a: [round(float(da["rating"].mean()) if not da.empty else 0, 2),
                         round(float(da["fee"].mean()) if not da.empty else 0, 0),
                         int(da["place"].count())],
                city_b: [round(float(db["rating"].mean()) if not db.empty else 0, 2),
                         round(float(db["fee"].mean()) if not db.empty else 0, 0),
                         int(db["place"].count())]
            })

            st.table(comp.set_index("metric"))

    st.markdown("---")
    st.write()

    # ---- Word Cloud ----
    st.subheader("☁️ Word Cloud dari Teks")
    text_cols = [c for c in ["deskripsi", "review", "place", "alamat"] if c in filtered_df.columns]
    if not text_cols:
        st.info("Tidak ada kolom teks (deskripsi/review/place/alamat) di dataset untuk membuat Word Cloud.")
    else:
        col_choice = st.selectbox("Pilih kolom teks", options=text_cols)
        stopword_choice = st.checkbox("Gunakan stopwords bahasa Inggris default (hilangkan kata umum)", value=True)
        stopword_id = st.checkbox("Gunakan stopwords bahasa Indonesia (tambahan)", value=False)
        min_font = st.slider("Minimum font size", min_value=8, max_value=50, value=10)
        max_words = st.slider("Jumlah kata maksimum", min_value=20, max_value=300, value=100)

        if st.button("🔍 Buat Word Cloud"):
            text = " ".join(filtered_df[col_choice].dropna().astype(str).tolist())
            if not text.strip():
                st.info("Tidak ada teks untuk kolom ini setelah filter.")
            else:
                # Try to use the wordcloud library; if missing, fall back to a bar chart of most common words
                try:
                    from wordcloud import WordCloud, STOPWORDS
                    sw = set(STOPWORDS) if stopword_choice else set()
                    if stopword_id:
                        # small extra id stopwords list
                        id_sw = {
                            'dan','di','ke','yang','dari','untuk','pada','dengan','ada','ini','itu','sangat','di',
                            'atau','sebagai','akan','lebih','dengan','saja','lagi','juga','karena','oleh'
                        }
                        sw = sw.union(id_sw)
                    wc = WordCloud(width=800, height=400, background_color="white", stopwords=sw,
                                   collocations=False, min_font_size=min_font, max_words=max_words)
                    wc.generate(text)
                    img = wc.to_image()
                    st.image(img, use_container_width=True)
                    # Offer download as PNG
                    import io
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    buf.seek(0)
                    st.download_button("⬇️ Download Word Cloud (PNG)", data=buf, file_name="wordcloud.png", mime="image/png")
                except Exception as e:
                    # Fallback: build word frequency bar chart
                    import re
                    from collections import Counter

                    st.warning("wordcloud tidak tersedia; menampilkan fallback berupa bar chart frekuensi kata. (Untuk WordCloud PNG, jalankan `pip install wordcloud`)")
                    # basic preprocessing: lowercase, remove non-alphanumeric except whitespace
                    txt = text.lower()
                    txt = re.sub(r"[^\w\s]", " ", txt)
                    txt = re.sub(r"\d+", " ", txt)
                    tokens = [t for t in txt.split() if len(t) > 1]
                    # assemble stopwords
                    sw = set()
                    try:
                        from wordcloud import STOPWORDS as WC_STOP
                        if stopword_choice:
                            sw = set(WC_STOP)
                    except Exception:
                        if stopword_choice:
                            # a small english stopword subset fallback
                            sw = {"the","and","for","with","that","this","from","are","was","but","not","you","have"}
                    if stopword_id:
                        sw = sw.union({'dan','di','ke','yang','dari','untuk','pada','dengan','ada','ini','itu','sangat','saja','lagi','juga','karena','oleh'})

                    filtered_tokens = [t for t in tokens if t not in sw]
                    if not filtered_tokens:
                        st.info("Setelah pembersihan/stopwords, tidak ada kata tersisa untuk divisualisasikan.")
                    else:
                        cnt = Counter(filtered_tokens)
                        top = cnt.most_common(max_words)
                        df_wc = pd.DataFrame(top, columns=["word","count"])
                        # bar chart
                        chart = (
                            alt.Chart(df_wc.head(50)).mark_bar().encode(
                                x=alt.X("count:Q", title="Frekuensi"),
                                y=alt.Y("word:N", sort='-x', title="Kata"),
                                tooltip=["word","count"]
                            ).properties(height=400)
                        )
                        st.altair_chart(chart, use_container_width=True)
                        st.dataframe(df_wc.reset_index(drop=True).head(200))
                        csvb = df_wc.to_csv(index=False).encode('utf-8')
                        st.download_button("⬇️ Download frekuensi kata (CSV)", data=csvb, file_name="word_freq.csv", mime="text/csv")
elif page == "📈 Insights":
    st.subheader("📈 Insights & Heatmaps")

    st.write("Halaman analitik tambahan: heatmap kategori vs kota, bubble chart, dan ringkasan top kategori.")

    # Heatmap: jumlah tempat per kota x kategori
    pivot = (
        filtered_df.groupby(["city", "category"])["place"].count().reset_index(name="count")
    )

    if pivot.empty:
        st.info("Tidak cukup data untuk membuat insight.")
    else:
        heat = (
            alt.Chart(pivot)
            .mark_rect()
            .encode(
                x=alt.X("category:N", sort=alt.EncodingSortField(field="count", op="sum", order="descending"), title="Kategori"),
                y=alt.Y("city:N", sort=alt.EncodingSortField(field="count", op="sum", order="descending"), title="Kota"),
                color=alt.Color("count:Q", title="Jumlah tempat", scale=alt.Scale(scheme="greens")),
                tooltip=["city", "category", "count"]
            )
            .properties(height=400)
        )

        st.subheader("Heatmap: Kota × Kategori (Jumlah tempat)")
        st.altair_chart(heat, use_container_width=True)

        st.markdown("---")

        # Bubble chart: avg fee vs avg rating per kota
        agg_city = (
            filtered_df.groupby("city").agg(
                avg_rating=("rating", "mean"),
                avg_fee=("fee", "mean"),
                count_places=("place", "count")
            ).reset_index()
        )

        st.subheader("Bubble: Rata-rata Harga vs Rata-rata Rating (per Kota)")
        bubble = (
            alt.Chart(agg_city)
            .mark_circle(opacity=0.7)
            .encode(
                x=alt.X("avg_fee:Q", title="Rata-rata Harga (IDR)"),
                y=alt.Y("avg_rating:Q", title="Rata-rata Rating"),
                size=alt.Size("count_places:Q", title="Jumlah Tempat", scale=alt.Scale(range=[50, 1500])),
                color=alt.Color("city:N", legend=None),
                tooltip=["city", "avg_fee", "avg_rating", "count_places"]
            )
        )
        st.altair_chart(bubble, use_container_width=True)

        st.markdown("---")

        # Top categories
        cat_counts_all = (
            filtered_df.groupby("category")["place"].count().reset_index(name="jumlah_tempat").sort_values("jumlah_tempat", ascending=False)
        )
        st.subheader("Top Kategori")
        top_cat = cat_counts_all.head(10)
        bar = (
            alt.Chart(top_cat)
            .mark_bar()
            .encode(
                x=alt.X("jumlah_tempat:Q", title="Jumlah tempat"),
                y=alt.Y("category:N", sort="-x", title="Kategori"),
                tooltip=["category", "jumlah_tempat"]
            )
        )
        st.altair_chart(bar, use_container_width=True)

        # Download CSV pivot
        csv_bytes = pivot.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download heatmap data (CSV)",
            data=csv_bytes,
            file_name="insights_heatmap.csv",
            mime="text/csv"
        )

# =========================
# 9. HALAMAN REKOMENDASI
# =========================
# 9. HALAMAN RECOMMENDER SEARCH
# =========================
elif page == "🎯 Recommender":
    st.subheader("🎯 Recommender Search — Temukan Tempat Serupa")
    st.write("Pilih satu tempat referensi, kemudian sistem akan menemukan tempat-tempat lain yang paling mirip berdasarkan kategori, lokasi, harga, fasilitas, suasana, dan deskripsi.")

    # Filter data berdasarkan filter global yang sudah diterapkan
    if filtered_df.empty:
        st.warning("Tidak ada data yang cocok dengan filter. Coba longgarkan filter.")
    else:
        # Pilih tempat referensi
        ref_options = filtered_df['place'].tolist()
        ref_place_name = st.selectbox(
            "Pilih tempat yang ingin Anda bandingkan:",
            options=ref_options,
            key="recommender_selectbox"
        )

        # Slider untuk jumlah rekomendasi
        top_n = st.slider("Berapa banyak rekomendasi yang ditampilkan?", 3, 20, 10)

        # Tombol cari
        if st.button("🔍 Cari Tempat Serupa"):
            with st.spinner("Mencari tempat serupa..."):
                # Reset index agar cocok dengan index di recommender
                df_reset = filtered_df.reset_index(drop=True)
                # Cari indeks ref_place di df_reset
                try:
                    ref_idx_reset = df_reset[df_reset['place'] == ref_place_name].index[0]
                    similar_df = get_similar_places(ref_idx_reset, df_reset, top_n=top_n)
                except Exception as e:
                    st.error(f"Terjadi kesalahan: {str(e)}")
                    similar_df = None

            if similar_df is not None and not similar_df.empty:
                # Ambil data referensi
                ref_place = filtered_df[filtered_df['place'] == ref_place_name].iloc[0]

                st.success(f"Ditemukan {len(similar_df)} tempat serupa dengan '{ref_place_name}'")
                st.markdown("---")

                # Tampilkan detail tempat referensi
                st.subheader(f"📍 Tempat Referensi: {ref_place['place']}")
                ref_col1, ref_col2, ref_col3 = st.columns(3)
                with ref_col1:
                    st.metric("Kota", ref_place['city'])
                with ref_col2:
                    st.metric("Kategori", ref_place['category'])
                with ref_col3:
                    rating_val = ref_place.get('rating', 'N/A')
                    st.metric("Rating", f"{rating_val}⭐" if pd.notna(rating_val) else "N/A")

                if 'deskripsi' in ref_place.index and pd.notna(ref_place.get('deskripsi')):
                    st.markdown(f"**Deskripsi:** {ref_place.get('deskripsi')}")

                st.markdown("---")
                st.subheader("🎯 Hasil Rekomendasi")

                # Tampilkan hasil dalam expander untuk setiap tempat
                for rank, (_, row) in enumerate(similar_df.iterrows(), 1):
                    score_pct = int(row['score'] * 100)
                    with st.expander(
                        f"#{rank} {row['place']} — Kemiripan: {score_pct}% ({row['score']:.3f})",
                        expanded=(rank == 1)  # expand yang pertama
                    ):
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Kota", row['city'])
                        with col2:
                            st.metric("Kategori", row['category'])
                        with col3:
                            rating_val = row['rating']
                            st.metric("Rating", f"{rating_val}⭐" if pd.notna(rating_val) else "N/A")
                        with col4:
                            fee_val = row['fee']
                            if pd.notna(fee_val):
                                st.metric("Harga", f"Rp {fee_val:,.0f}" if isinstance(fee_val, (int, float)) else fee_val)
                            else:
                                st.metric("Harga", "N/A")

                        # Alasan kemiripan
                        st.markdown(f"**Skor Kemiripan:** {row['score']:.3f} (0–1)")
                        st.markdown("**Alasan kemiripan:**")
                        if row['reasons']:
                            for reason in row['reasons']:
                                st.write(f"• {reason}")
                        else:
                            st.write("• Kemiripan berdasarkan keseluruhan karakteristik tempat.")

                        # Tampilkan deskripsi jika ada
                        orig_row = filtered_df[filtered_df['place'] == row['place']]
                        if not orig_row.empty and 'deskripsi' in orig_row.columns:
                            desc = orig_row.iloc[0].get('deskripsi')
                            if pd.notna(desc) and desc:
                                st.markdown(f"**Deskripsi:** {desc}")

            elif similar_df is not None:
                st.info("Tidak ada tempat serupa ditemukan dengan skor > 0.")

# =========================
elif page == "💡 Personalized Picks":
    st.subheader("💡 Personalized Picks — Rekomendasi Terbaik untuk Anda")
    st.write("Atur preferensi Anda, dan saya akan menampilkan tempat-tempat terbaik yang paling sesuai dengan kebutuhan Anda berdasarkan rating, harga, dan kategori favorit.")

    # Preferensi user
    pref_col1, pref_col2, pref_col3 = st.columns(3)

    with pref_col1:
        kota_pref = st.multiselect(
            "Kota yang diinginkan",
            options=sorted(df["city"].unique()),
            help="Kosongkan untuk melihat semua kota"
        )

    with pref_col2:
        kategori_pref = st.multiselect(
            "Kategori favorit",
            options=sorted(df["category"].unique()),
            help="Kosongkan untuk melihat semua kategori"
        )

    with pref_col3:
        min_rating_pref = st.slider(
            "Minimal rating yang diterima",
            min_value=0.0,
            max_value=5.0,
            value=3.5,
            step=0.1,
            help="Hanya tampilkan tempat dengan rating >= nilai ini"
        )

    max_budget_pref = st.slider(
        "Budget maksimal tiket (IDR)",
        min_value=int(df["fee"].min()) if pd.notna(df["fee"].min()) else 0,
        max_value=int(df["fee"].max()) if pd.notna(df["fee"].max()) else 500000,
        value=int(df["fee"].quantile(0.75)) if pd.notna(df["fee"].quantile(0.75)) else 100000,
        step=5000,
        help="Hanya tampilkan tempat dengan harga tiket <= budget ini"
    )

    # Filter berdasarkan preferensi
    rec_df = df.copy()

    if kota_pref:
        rec_df = rec_df[rec_df["city"].isin(kota_pref)]

    if kategori_pref:
        rec_df = rec_df[rec_df["category"].isin(kategori_pref)]

    rec_df = rec_df[
        (rec_df["rating"].fillna(0) >= min_rating_pref) &
        (rec_df["fee"].fillna(rec_df["fee"].max()) <= max_budget_pref)
    ]

    st.markdown("---")

    if rec_df.empty:
        st.warning("❌ Tidak ada tempat yang cocok dengan preferensi Anda. Coba ubah filter (turunkan rating minimal atau naikkan budget) 😊")
    else:
        # Hitung skor untuk setiap tempat
        rec_df = rec_df.copy()
        
        # Skor 1: Rating (normalisasi 0-5 ke 0-1)
        rec_df['score_rating'] = (rec_df['rating'].fillna(0) / 5.0)
        
        # Skor 2: Value for Money (inverse of price: lebih murah = lebih bagus)
        max_fee = rec_df['fee'].max()
        # Guard: jika semua fee kosong atau max_fee tidak valid, gunakan 1 sebagai denom supaya tidak NaN/div0
        if pd.isna(max_fee) or max_fee == 0:
            max_fee = 1.0
        rec_df['score_value'] = 1 - (rec_df['fee'].fillna(max_fee) / max_fee)
        
        # Skor 3: Popularitas (berdasarkan jumlah review/ulasan jika ada)
        if 'ulasan' in rec_df.columns or 'review' in rec_df.columns:
            review_col = 'ulasan' if 'ulasan' in rec_df.columns else 'review'
            rec_df['review_count'] = rec_df[review_col].fillna('').astype(str).apply(lambda x: len(str(x).split(',')) if x else 0)
            max_reviews = max(rec_df['review_count'].max(), 1)
            rec_df['score_popularity'] = rec_df['review_count'] / max_reviews
        else:
            rec_df['score_popularity'] = 0.5  # default jika tidak ada kolom review
        
        # Combined score (weighted)
        # Rating: 40%, Value: 35%, Popularity: 25%
        rec_df['combined_score'] = (
            rec_df['score_rating'] * 0.40 +
            rec_df['score_value'] * 0.35 +
            rec_df['score_popularity'] * 0.25
        )
        
        # Sort by combined score
        rec_df = rec_df.sort_values('combined_score', ascending=False)
        
        st.subheader(f"✨ Top {len(rec_df)} Rekomendasi untuk Anda")
        
        # Tampilkan top 3 dalam card style
        st.markdown("**🏆 Top 3 Pick:**")
        top_3_cols = st.columns(3)
        
        for idx, (_, row) in enumerate(rec_df.head(3).iterrows()):
            with top_3_cols[idx]:
                medal = ["🥇", "🥈", "🥉"][idx]

                with st.container(border=True):
                    st.markdown(f"### {medal} {row['place']}")
                    st.markdown(f"📍 {row['city']} • 🏷️ {row['category']}")
                    st.markdown(f"⭐ {row['rating']:.1f} | 💰 Rp {row['fee']:,.0f}")
        
        st.markdown("---")
        
        # Tampilkan daftar lengkap dalam tabel
        st.markdown("**📋 Daftar Lengkap:**")
        
        display_cols = [c for c in ["place", "city", "category", "rating", "fee"] if c in rec_df.columns]
        # Tampilkan daftar lengkap tanpa kolom skor (skor masih dihitung untuk Top-3)
        
        display_df = rec_df[display_cols].copy()
        # Safely format combined_score: replace NaN with 0 before converting to int
        display_df = display_df.rename(columns={'combined_score': 'Skor (%)'})
        display_df = display_df.rename(columns={'combined_score': 'Skor (%)'})
        
        st.dataframe(
            display_df.reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        # Random pick feature
        col_random, col_info = st.columns([1, 3])
        with col_random:
            if st.button("🎲 Tampilkan 1 Random", use_container_width=True):
                random_row = rec_df.sample(1).iloc[0]
                st.session_state['random_pick'] = random_row
        
        if 'random_pick' in st.session_state:
            row = st.session_state['random_pick']
            with col_info:
                st.success(
                    f"**{row['place']}** · {row['city']} · {row['category']}\n\n"
                    f"⭐ Rating: {row['rating']:.1f} | 💰 Tiket: Rp {row['fee']:,.0f}"
                )



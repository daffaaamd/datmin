"""
Data loading helper dengan fallback untuk Excel dan CSV
"""

import os
import pandas as pd
import streamlit as st


def safe_read_data(file_path: str) -> pd.DataFrame:
    """
    Baca file Excel atau CSV dengan fallback mechanism.
    
    Args:
        file_path: path ke file Excel atau CSV
    
    Returns:
        DataFrame
    
    Raises:
        FileNotFoundError jika file tidak ada
        ValueError jika gagal membaca file
    """
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File tidak ditemukan: {file_path}")
    
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # Coba baca file
    try:
        if file_ext == '.csv':
            return pd.read_csv(file_path)
        elif file_ext == '.xlsx':
            # Coba dengan openpyxl (default)
            try:
                return pd.read_excel(file_path, engine="openpyxl")
            except ImportError:
                # Fallback ke xlrd jika openpyxl tidak tersedia
                try:
                    return pd.read_excel(file_path, engine="xlrd")
                except ImportError:
                    # Fallback terakhir: coba baca sebagai CSV
                    csv_path = file_path.replace('.xlsx', '.csv')
                    if os.path.exists(csv_path):
                        return pd.read_csv(csv_path)
                    else:
                        raise ImportError(
                            "openpyxl tidak tersedia dan file CSV tidak ditemukan. "
                            "Silakan upload file DATASET.csv atau pastikan openpyxl terinstal."
                        )
        else:
            raise ValueError(f"Format file tidak didukung: {file_ext}")
    
    except Exception as e:
        raise ValueError(f"Error saat membaca file {file_path}: {str(e)}")


def find_dataset_file(base_dir: str, image_cols: list = None, required_cols: list = None) -> str:
    """
    Cari file dataset di folder dengan prioritas.
    
    Args:
        base_dir: direktori untuk mencari file
        image_cols: list kolom gambar (prioritas tinggi)
        required_cols: list kolom wajib
    
    Returns:
        path ke file dataset terpilih
    
    Raises:
        FileNotFoundError jika tidak ada dataset yang valid
    """
    
    if image_cols is None:
        image_cols = ["image", "image_url", "foto", "gambar", "photo", "photo_url"]
    if required_cols is None:
        required_cols = ["place", "city", "category", "rating", "fee"]
    
    # Cari file xlsx dan csv
    dataset_xlsx = [f for f in os.listdir(base_dir) if f.lower().endswith('.xlsx') and 'dataset' in f.lower()]
    dataset_csv = [f for f in os.listdir(base_dir) if f.lower().endswith('.csv') and 'dataset' in f.lower()]
    dataset_candidates = sorted(dataset_xlsx) + sorted(dataset_csv)
    
    selected_path = None
    
    # Coba setiap kandidat
    for fname in dataset_candidates:
        path = os.path.join(base_dir, fname)
        try:
            tmp = safe_read_data(path)
            tmp.columns = [c.strip().lower() for c in tmp.columns]
            
            # Cek kolom required
            missing = [c for c in required_cols if c not in tmp.columns]
            if missing:
                continue
            
            # Prioritas: ada kolom gambar
            if any(c in tmp.columns for c in image_cols):
                return path
            
            # Simpan sebagai fallback
            if selected_path is None:
                selected_path = path
        
        except Exception:
            continue
    
    if selected_path:
        return selected_path
    
    # Fallback terakhir: cari DATASET.xlsx atau DATASET.csv
    for fname in ["DATASET.xlsx", "DATASET.csv"]:
        path = os.path.join(base_dir, fname)
        if os.path.exists(path):
            return path
    
    raise FileNotFoundError(
        f"Dataset tidak ditemukan di {base_dir}. "
        "Silakan upload DATASET.xlsx atau DATASET.csv"
    )

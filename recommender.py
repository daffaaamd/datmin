"""
Recommender Search System untuk Dashboard Wisata
Menemukan tempat serupa berdasarkan kategori, lokasi, harga, fasilitas, suasana, dan deskripsi.
"""

import pandas as pd
import numpy as np
import re
from math import log1p
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_similarity_score(ref_place: pd.Series, candidate_place: pd.Series, df: pd.DataFrame, desc_sim: float = None) -> tuple:
    """
    Hitung skor kemiripan (0-1) antara ref_place dan candidate_place.

    Args:
        ref_place: pd.Series - tempat referensi
        candidate_place: pd.Series - tempat kandidat
        df: pd.DataFrame - dataset lengkap (untuk cek kolom yang tersedia)
        desc_sim: Optional precomputed TF-IDF cosine similarity (float 0-1) between ref and candidate

    Returns:
        (score: float, reasons: list[str])
        score: nilai 0-1, semakin tinggi semakin mirip
        reasons: daftar alasan kemiripan
    """
    
    # Jika tempat yang sama, skip
    try:
        if ref_place.name == candidate_place.name:
            return 0.0, ["Tempat yang sama"]
    except Exception:
        pass

    scores = {}
    reasons = []

    # 1. Kesamaan kategori (bobot: 0.25)
    cat_ref = str(ref_place.get('category', '')).strip().lower() if pd.notna(ref_place.get('category')) else ''
    cat_cand = str(candidate_place.get('category', '')).strip().lower() if pd.notna(candidate_place.get('category')) else ''
    if cat_ref and cat_cand:
        if cat_ref == cat_cand:
            scores['category'] = 1.0
            reasons.append(f"✓ Kategori sama: {candidate_place.get('category')}")
        else:
            scores['category'] = 0.0
    else:
        scores['category'] = 0.0

    # 2. Kesamaan kota (bobot: 0.20)
    city_ref = str(ref_place.get('city', '')).strip().lower() if pd.notna(ref_place.get('city')) else ''
    city_cand = str(candidate_place.get('city', '')).strip().lower() if pd.notna(candidate_place.get('city')) else ''
    if city_ref and city_cand:
        if city_ref == city_cand:
            scores['city'] = 1.0
            reasons.append(f"✓ Kota sama: {candidate_place.get('city')}")
        else:
            scores['city'] = 0.1  # penalti kecil untuk kota berbeda
    else:
        scores['city'] = 0.0

    # 3. Kesamaan kisaran harga (bobot: 0.20) — log-normalized
    fee_ref = pd.to_numeric(ref_place.get('fee'), errors='coerce')
    fee_cand = pd.to_numeric(candidate_place.get('fee'), errors='coerce')
    max_fee_all = pd.to_numeric(df.get('fee', pd.Series(dtype='float')), errors='coerce').max()
    if pd.notna(fee_ref) and pd.notna(fee_cand):
        if fee_ref == 0 and fee_cand == 0:
            scores['fee'] = 1.0
            reasons.append("✓ Kedua tempat gratis")
        else:
            # log-normalize untuk mengurangi pengaruh perbedaan absolut besar
            denom = max_fee_all if pd.notna(max_fee_all) and max_fee_all > 0 else max(fee_ref, fee_cand, 1)
            norm_ref = log1p(fee_ref) / log1p(denom)
            norm_cand = log1p(fee_cand) / log1p(denom)
            diff = abs(norm_ref - norm_cand)
            scores['fee'] = max(0.0, 1 - diff)
            if scores['fee'] > 0.7:
                reasons.append(f"✓ Kisaran harga mirip: Rp {fee_cand:,.0f} vs Rp {fee_ref:,.0f}")
    else:
        scores['fee'] = 0.0

    # 4. Kesamaan rating (bobot: 0.15)
    rating_ref = pd.to_numeric(ref_place.get('rating'), errors='coerce')
    rating_cand = pd.to_numeric(candidate_place.get('rating'), errors='coerce')
    if pd.notna(rating_ref) and pd.notna(rating_cand):
        rating_diff = abs(rating_ref - rating_cand) / 5.0  # normalized ke 0-1
        scores['rating'] = max(0, 1 - rating_diff)
        if scores['rating'] > 0.75:
            reasons.append(f"✓ Rating mirip: {rating_cand:.1f}⭐ vs {rating_ref:.1f}⭐")
    else:
        scores['rating'] = 0.0

    # 5. Kesamaan fasilitas (bobot: 0.10) - improved tokenization
    facility_cols = [c for c in df.columns if 'fasilitas' in c.lower() or 'facilities' in c.lower()]
    if facility_cols:
        fac_ref = str(ref_place.get(facility_cols[0], '')).strip().lower() if pd.notna(ref_place.get(facility_cols[0])) else ''
        fac_cand = str(candidate_place.get(facility_cols[0], '')).strip().lower() if pd.notna(candidate_place.get(facility_cols[0])) else ''
        if fac_ref and fac_cand:
            ref_tokens = set(re.findall(r'\w{3,}', fac_ref))
            cand_tokens = set(re.findall(r'\w{3,}', fac_cand))
            if ref_tokens and cand_tokens:
                overlap = len(ref_tokens & cand_tokens) / len(ref_tokens | cand_tokens)
                scores['facility'] = overlap
                if overlap > 0.25:
                    reasons.append("✓ Fasilitas serupa")
            else:
                scores['facility'] = 0.0
        else:
            scores['facility'] = 0.0
    else:
        scores['facility'] = 0.0

    # 6. Kesamaan suasana (bobot: 0.10) - improved tokenization
    atmosphere_cols = [c for c in df.columns if 'suasana' in c.lower() or 'atmosphere' in c.lower()]
    if atmosphere_cols:
        atm_ref = str(ref_place.get(atmosphere_cols[0], '')).strip().lower() if pd.notna(ref_place.get(atmosphere_cols[0])) else ''
        atm_cand = str(candidate_place.get(atmosphere_cols[0], '')).strip().lower() if pd.notna(candidate_place.get(atmosphere_cols[0])) else ''
        if atm_ref and atm_cand:
            ref_tokens = set(re.findall(r'\w{3,}', atm_ref))
            cand_tokens = set(re.findall(r'\w{3,}', atm_cand))
            if ref_tokens and cand_tokens:
                overlap = len(ref_tokens & cand_tokens) / len(ref_tokens | cand_tokens)
                scores['atmosphere'] = overlap
                if overlap > 0.25:
                    reasons.append("✓ Suasana serupa")
            else:
                scores['atmosphere'] = 0.0
        else:
            scores['atmosphere'] = 0.0
    else:
        scores['atmosphere'] = 0.0

    # 7. Kesamaan deskripsi (bobot: 0.10) - use precomputed TF-IDF similarity if available
    if desc_sim is not None:
        scores['description'] = float(desc_sim)
        if scores['description'] > 0.15:
            reasons.append("✓ Tema deskripsi mirip (TF-IDF)")
    else:
        desc_ref = str(ref_place.get('deskripsi', '')).strip().lower() if pd.notna(ref_place.get('deskripsi')) else ''
        desc_cand = str(candidate_place.get('deskripsi', '')).strip().lower() if pd.notna(candidate_place.get('deskripsi')) else ''
        if desc_ref and desc_cand and len(desc_ref) > 10 and len(desc_cand) > 10:
            ref_tokens = set(re.findall(r'\w{4,}', desc_ref))
            cand_tokens = set(re.findall(r'\w{4,}', desc_cand))
            if ref_tokens and cand_tokens:
                overlap = len(ref_tokens & cand_tokens) / len(ref_tokens | cand_tokens)
                scores['description'] = overlap
                if overlap > 0.15:
                    reasons.append("✓ Tema deskripsi serupa")
            else:
                scores['description'] = 0.0
        else:
            scores['description'] = 0.0

    # Bobot untuk setiap faktor
    weights = {
        'category': 0.25,
        'city': 0.20,
        'fee': 0.20,
        'rating': 0.15,
        'facility': 0.10,
        'atmosphere': 0.10,
        'description': 0.10
    }

    # Hitung weighted score
    total_score = 0.0
    total_weight = 0.0
    for factor, weight in weights.items():
        if factor in scores:
            total_score += scores.get(factor, 0) * weight
            total_weight += weight

    final_score = total_score / total_weight if total_weight > 0 else 0.0
    final_score = round(max(0, min(1, final_score)), 3)  # clamp ke 0-1

    return final_score, reasons


def get_similar_places(ref_idx: int, df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Cari tempat-tempat yang mirip dengan ref_idx.
    
    Args:
        ref_idx: index dari tempat referensi di df
        df: pd.DataFrame - dataset
        top_n: jumlah hasil teratas
    
    Returns:
        DataFrame dengan kolom: idx, place, city, category, rating, fee, score, reasons
    """
    ref_place = df.loc[ref_idx]
    results = []

    # Precompute TF-IDF similarity for descriptions (faster and more accurate than word overlap)
    desc_series = df.get('deskripsi', pd.Series([''] * len(df))).fillna('').astype(str)
    try:
        tfidf = TfidfVectorizer(ngram_range=(1,2), min_df=1)
        tfidf_matrix = tfidf.fit_transform(desc_series)
        ref_vec = tfidf_matrix[ref_idx]
        desc_similarities = cosine_similarity(ref_vec, tfidf_matrix).flatten()
    except Exception:
        desc_similarities = np.zeros(len(df))

    for idx, row in df.iterrows():
        desc_sim_val = float(desc_similarities[idx]) if idx < len(desc_similarities) else None
        score, reasons = compute_similarity_score(ref_place, row, df, desc_sim=desc_sim_val)
        results.append({
            'idx': idx,
            'place': row.get('place', 'Unknown'),
            'city': row.get('city', 'Unknown'),
            'category': row.get('category', 'Unknown'),
            'rating': row.get('rating', 'N/A'),
            'fee': row.get('fee', 'N/A'),
            'deskripsi': row.get('deskripsi', ''),
            'score': score,
            'reasons': reasons
        })
    result_df = pd.DataFrame(results)
    # Filter score > 0 dan sort
    result_df = result_df[result_df['score'] > 0].sort_values('score', ascending=False).head(top_n)
    return result_df

"""
Recommender Search System untuk Dashboard Wisata
Menemukan tempat serupa berdasarkan kategori, lokasi, harga, fasilitas, suasana, dan deskripsi.
"""

import pandas as pd
import numpy as np


def compute_similarity_score(ref_place: pd.Series, candidate_place: pd.Series, df: pd.DataFrame) -> tuple:
    """
    Hitung skor kemiripan (0-1) antara ref_place dan candidate_place.
    
    Args:
        ref_place: pd.Series - tempat referensi
        candidate_place: pd.Series - tempat kandidat
        df: pd.DataFrame - dataset lengkap (untuk cek kolom yang tersedia)
    
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

    # 3. Kesamaan kisaran harga (bobot: 0.20)
    fee_ref = pd.to_numeric(ref_place.get('fee'), errors='coerce')
    fee_cand = pd.to_numeric(candidate_place.get('fee'), errors='coerce')
    if pd.notna(fee_ref) and pd.notna(fee_cand):
        # hitung persentase perbedaan harga
        if fee_ref == 0 and fee_cand == 0:
            scores['fee'] = 1.0
            reasons.append("✓ Kedua tempat gratis")
        elif fee_ref == 0 or fee_cand == 0:
            # satu gratis, satu berbayar
            max_fee = max(fee_ref, fee_cand)
            price_diff = abs(fee_ref - fee_cand) / max_fee if max_fee > 0 else 1.0
            scores['fee'] = max(0, 1 - price_diff)
        else:
            # keduanya berbayar
            price_diff = abs(fee_ref - fee_cand) / max(fee_ref, fee_cand)
            scores['fee'] = max(0, 1 - price_diff)
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

    # 5. Kesamaan fasilitas (bobot: 0.10)
    facility_cols = [c for c in df.columns if 'fasilitas' in c.lower() or 'facilities' in c.lower()]
    if facility_cols:
        fac_ref = str(ref_place.get(facility_cols[0], '')).strip().lower() if pd.notna(ref_place.get(facility_cols[0])) else ''
        fac_cand = str(candidate_place.get(facility_cols[0], '')).strip().lower() if pd.notna(candidate_place.get(facility_cols[0])) else ''
        if fac_ref and fac_cand:
            # overlap check
            ref_words = set(fac_ref.split())
            cand_words = set(fac_cand.split())
            if ref_words and cand_words:
                overlap = len(ref_words & cand_words) / len(ref_words | cand_words)
                scores['facility'] = overlap
                if overlap > 0.3:
                    reasons.append("✓ Fasilitas serupa")
            else:
                scores['facility'] = 0.0
        else:
            scores['facility'] = 0.0
    else:
        scores['facility'] = 0.0

    # 6. Kesamaan suasana (bobot: 0.10)
    atmosphere_cols = [c for c in df.columns if 'suasana' in c.lower() or 'atmosphere' in c.lower()]
    if atmosphere_cols:
        atm_ref = str(ref_place.get(atmosphere_cols[0], '')).strip().lower() if pd.notna(ref_place.get(atmosphere_cols[0])) else ''
        atm_cand = str(candidate_place.get(atmosphere_cols[0], '')).strip().lower() if pd.notna(candidate_place.get(atmosphere_cols[0])) else ''
        if atm_ref and atm_cand:
            ref_words = set(atm_ref.split())
            cand_words = set(atm_cand.split())
            if ref_words and cand_words:
                overlap = len(ref_words & cand_words) / len(ref_words | cand_words)
                scores['atmosphere'] = overlap
                if overlap > 0.3:
                    reasons.append("✓ Suasana serupa")
            else:
                scores['atmosphere'] = 0.0
        else:
            scores['atmosphere'] = 0.0
    else:
        scores['atmosphere'] = 0.0

    # 7. Kesamaan deskripsi (bobot: 0.10) - text similarity
    desc_ref = str(ref_place.get('deskripsi', '')).strip().lower() if pd.notna(ref_place.get('deskripsi')) else ''
    desc_cand = str(candidate_place.get('deskripsi', '')).strip().lower() if pd.notna(candidate_place.get('deskripsi')) else ''
    if desc_ref and desc_cand and len(desc_ref) > 10 and len(desc_cand) > 10:
        # tokenize: ambil kata-kata yang panjang (> 3 karakter)
        ref_tokens = set(w for w in desc_ref.split() if len(w) > 3)
        cand_tokens = set(w for w in desc_cand.split() if len(w) > 3)
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

    for idx, row in df.iterrows():
        score, reasons = compute_similarity_score(ref_place, row, df)
        results.append({
            'idx': idx,
            'place': row.get('place', 'Unknown'),
            'city': row.get('city', 'Unknown'),
            'category': row.get('category', 'Unknown'),
            'rating': row.get('rating', 'N/A'),
            'fee': row.get('fee', 'N/A'),
            'score': score,
            'reasons': reasons
        })

    result_df = pd.DataFrame(results)
    # Filter score > 0 dan sort
    result_df = result_df[result_df['score'] > 0].sort_values('score', ascending=False).head(top_n)
    return result_df

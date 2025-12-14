import pandas as pd
from pathlib import Path
p = Path(__file__).parent.parent / 'DATASET.xlsx'
print('checking path:', p)
print('exists:', p.exists())
if not p.exists():
    raise SystemExit('DATASET.xlsx not found')

df = pd.read_excel(p, engine='openpyxl')
print('shape:', df.shape)
print('\nNull counts:')
print(df.isna().sum())

# whitespace-only detection
from collections import defaultdict
ws_only = defaultdict(int)
zw = defaultdict(list)
for c in df.select_dtypes(include=['object']).columns:
    for i,val in df[c].items():
        if pd.isna(val):
            continue
        if isinstance(val, str):
            if val.strip() == '':
                ws_only[c] += 1
            if any(ch in val for ch in ['\u200B','\u200C','\u200D','\uFEFF','\u00A0']):
                zw[c].append((i+2, repr(val[:80])))

print('\nWhitespace-only counts:')
for k,v in ws_only.items():
    print(k, v)

print('\nZero-width/NBSP examples:')
for k,v in zw.items():
    print(k, v[:5])

# simulate cleaning

def _clean_string_val(v):
    if pd.isna(v):
        return v
    if isinstance(v, str):
        s = v.replace('\u00A0', ' ')
        s = s.replace('\u200B', '')
        s = s.strip()
        if s == '':
            return pd.NA
        return s
    return v

cdf = df.copy()
for c in cdf.select_dtypes(include=['object']).columns:
    cdf[c] = cdf[c].apply(_clean_string_val)

print('\nNull counts after cleaning:')
print(cdf.isna().sum())

print('\nDone')
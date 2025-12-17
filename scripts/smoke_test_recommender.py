import pandas as pd
from recommender import compute_similarity_score, get_similar_places

# small smoke-test dataset
df = pd.DataFrame([
    {'place':'A','city':'Semarang','category':'Pantai','rating':4.2,'fee':10000,'deskripsi':'pantai indah pasir putih','fasilitas':'toilet parkir','suasana':'tenang pemandangan'},
    {'place':'B','city':'Semarang','category':'Pantai','rating':4.1,'fee':12000,'deskripsi':'pantai pasir putih indah','fasilitas':'toilet shop parkir','suasana':'tenang ramai'},
    {'place':'C','city':'Jakarta','category':'Budaya','rating':4.5,'fee':0,'deskripsi':'kawasan budaya museum','fasilitas':'guide','suasana':'ramai edukasi'}
])

res = get_similar_places(0, df, top_n=5)
print(res.to_string(index=False))

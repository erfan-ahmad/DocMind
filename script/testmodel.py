from sentence_transformers import  SentenceTransformer
from  pathlib import Path
from sentence_transformers.util import  cos_sim
from sympy.vector import vector

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / 'model'

model = SentenceTransformer(str(MODEL_PATH), device='cpu')

vec =  model.encode('passage:سلام این یک متن ازمایشی است',normalize_embeddings=True)

print(vec.shape[0])


query_text = "query: پایتخت فرانسه کجاست؟"
passage_relevant = "passage: پاریس پایتخت فرانسه است."
passage_irrelevant = "passage: تهران پایتخت ایران است."

query_vector = model.encode(query_text,normalize_embeddings=True)
relevant_vec = model.encode(passage_relevant,normalize_embeddings=True)
irrelevant_vec = model.encode(passage_irrelevant,normalize_embeddings=True)

sim_relevant = cos_sim(query_vector,relevant_vec).item()
sim_irrelevant = cos_sim(query_vector,irrelevant_vec).item()

print("Similarity (query vs relevant):  ", sim_relevant)
print("Similarity (query vs irrelevant):", sim_irrelevant)

if sim_relevant > sim_irrelevant:
    print("OK: passage مربوط بالاتر از نامربوط بود.")
else:
    print("WARNING: نتیجه غیرمنتظره است.")


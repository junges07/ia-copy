from openai import OpenAI
import json
from numpy import dot
from numpy.linalg import norm
from ..config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def get_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(vec1, vec2):
    return dot(vec1, vec2) / (norm(vec1) * norm(vec2))

def is_duplicate_embedding(new_embedding, existing_embeddings, threshold=0.9):
    for emb in existing_embeddings:
        emb_vec = json.loads(emb) if isinstance(emb, str) else emb
        if cosine_similarity(new_embedding, emb_vec) >= threshold:
            return True
    return False

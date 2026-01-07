import json

from ..hooks.embedding_hook import cosine_similarity
from ..hooks.supabase_hook import get_team_memory_bomma


def filter_by_similarity(query_embedding, threshold=0.72):
    memories = get_team_memory_bomma()
    relevant = []

    for mem in memories:
        # pegar embedding salvo no banco
        emb_str = mem.get("embedding")
        if not emb_str:
            continue

        # transformar string → vetor float
        emb_vec = json.loads(emb_str)

        sim = cosine_similarity(query_embedding, emb_vec)

        print(f"Memória analisada: tag={mem.get('tag')}, similarity={sim}")

        if sim >= threshold:
            relevant.append(mem)

    return relevant


# 3. FILTRO 2: Tags
# def filter_by_tag(memories, allowed_tags):

# 4. FUNÇÃO PRINCIPAL DE RECUPERAÇÃO
# def retrieve_relevant_memory(message, intent_type):
# 1) gerar embedding do input
# 2) buscar candidatos
# 3) aplicar filtro de similaridade
# 4) aplicar filtro de tags
# 5) retornar o que sobrar

from ..config import supabase

def insert_team_memory(reference: str, content: str, embedding: list):
    """Insere nova memória na tabela team_memory."""
    supabase.table("team_memory").insert({
        "reference": reference,
        "content": content,
        "embedding": embedding
    }).execute()

def get_team_memory(reference: str):
    """Retorna todas as memórias relacionadas a uma referência."""
    clean_ref = reference.strip().lower()
    print(f"🔍 Buscando memórias com reference='{clean_ref}'")

    result = supabase.table("team_memory") \
        .select("content, embedding") \
        .filter("reference", "eq", clean_ref) \
        .execute()

    return result

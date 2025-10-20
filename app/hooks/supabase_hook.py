from ..config import supabase
import json

def _normalize(s: str) -> str:
    return (s or "").strip().lower()

# === TEAM MEMORY ===
def insert_team_memory(reference: str, content: str, embedding: list):
    ref = (reference or "").strip().lower()
    if not ref or not content:
        return
    supabase.table("team_memory").insert({
        "reference": ref,
        "content": content,
        "embedding": json.dumps(embedding)
    }).execute()


def get_team_memory(reference: str):
    """Busca memórias coletivas da empresa (case-insensitive)."""
    ref = (reference or "").strip().lower()
    if not ref:
        print("⚠️ Nenhuma referência fornecida ao get_team_memory.")
        return None

    print(f"🔍 Buscando memórias coletivas para referência '{ref}' (case-insensitive)")
    result = supabase.table("team_memory") \
        .select("content, embedding, reference") \
        .execute()

    # Filtra manualmente pelo nome da empresa (sem case sensitivity)
    matched = [
        row for row in result.data
        if row.get("reference", "").strip().lower() == ref
    ]
    print(f"✅ Encontradas {len(matched)} memórias para '{ref}'")
    return type("Result", (), {"data": matched})


# === INDIVIDUAL MEMORY ===
def insert_individual_memory(user: str, content: str, embedding: list):
    """Insere memória individual do usuário."""
    usr = _normalize(user)
    if not usr or not content:
        print("⚠️ Tentativa de inserir individual_memory com dados vazios. Ignorado.")
        return
    supabase.table("individual_memory").insert({
        "user": usr,
        "content": content,
        "embedding": json.dumps(embedding)
    }).execute()
    print(f"✅ Inserido individual_memory: {usr} -> {content[:80]}")

def get_individual_memory(user: str):
    """Busca memórias individuais do usuário (case-insensitive)."""
    usr = (user or "").strip().lower()
    if not usr:
        print("⚠️ Nenhum user fornecido ao get_individual_memory.")
        return None

    print(f"🔍 Buscando memórias individuais para '{usr}' (case-insensitive)")
    result = supabase.table("individual_memory") \
        .select("content, embedding, user") \
        .execute()

    matched = [
        row for row in result.data
        if row.get("user", "").strip().lower() == usr
    ]
    print(f"✅ Encontradas {len(matched)} memórias individuais para '{usr}'")
    return type("Result", (), {"data": matched})


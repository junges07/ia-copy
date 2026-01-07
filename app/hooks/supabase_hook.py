from ..config import supabase
from ..hooks.embedding_hook import get_embedding
import json
import uuid


def _normalize(s: str) -> str:
    return (s or "").strip().lower()


# === USERS ===
def getUsers():
    result = supabase.table("login_bd").select("id, nome").execute()
    return result.data


# === TEAM MEMORY ===
def insert_team_memory(reference: str, content: str, embedding: list):
    ref = (reference or "").strip().lower()
    if not ref or not content:
        return
    supabase.table("team_memory").insert(
        {"reference": ref, "content": content, "embedding": json.dumps(embedding)}
    ).execute()


def get_team_memory(reference: str):
    """Busca memórias coletivas da empresa (case-insensitive)."""
    ref = (reference or "").strip().lower()
    if not ref:
        print("⚠️ Nenhuma referência fornecida ao get_team_memory.")
        return None

    print(f"🔍 Buscando memórias coletivas para referência '{ref}' (case-insensitive)")
    result = (
        supabase.table("team_memory").select("content, embedding, reference").execute()
    )

    # Filtra manualmente pelo nome da empresa (sem case sensitivity)
    matched = [
        row for row in result.data if row.get("reference", "").strip().lower() == ref
    ]
    print(f"✅ Encontradas {len(matched)} memórias para '{ref}'")
    return type("Result", (), {"data": matched})


# === TEAM MEMORY - BOMMA (novo bloco isolado) ===
def insert_team_memory_bomma(tag: str, context: str, content: str):
    embedding = get_embedding(context + " " + content)
    supabase.table("team_memory_bomma").insert(
        {
            "tag": tag,
            "context": context,
            "content": content,
            "embedding": json.dumps(embedding),
        }
    ).execute()

    print(
        f"✅ INSERIDO em team_memory_bomma:\ntag: ${tag}, context: ${context}, content: ${content}"
    )


def get_team_memory_bomma():
    result = (
        supabase.table("team_memory_bomma")
        .select("tag, context, content, embedding")
        .execute()
    )
    return result.data


# === INDIVIDUAL MEMORY ===
def insert_individual_memory(user: str, content: str, embedding: list):
    """Insere memória individual do usuário."""
    usr = _normalize(user)
    if not usr or not content:
        print("⚠️ Tentativa de inserir individual_memory com dados vazios. Ignorado.")
        return
    supabase.table("individual_memory").insert(
        {"user": usr, "content": content, "embedding": json.dumps(embedding)}
    ).execute()
    print(f"✅ Inserido individual_memory: {usr} -> {content[:80]}")


def get_individual_memory(user: str):
    """Busca memórias individuais do usuário (case-insensitive)."""
    usr = (user or "").strip().lower()
    if not usr:
        print("⚠️ Nenhum user fornecido ao get_individual_memory.")
        return None

    print(f"🔍 Buscando memórias individuais para '{usr}' (case-insensitive)")
    result = (
        supabase.table("individual_memory").select("content, embedding, user").execute()
    )

    matched = [row for row in result.data if row.get("user", "").strip().lower() == usr]
    print(f"✅ Encontradas {len(matched)} memórias individuais para '{usr}'")
    return type("Result", (), {"data": matched})


# === CHAT FUNCTIONS ===


def create_chat(user_id: str, title: str, business: str):
    """Cria um novo chat no banco."""
    try:
        result = (
            supabase.table("chats")
            .insert({"user_id": user_id, "title": title, "business": business})
            .execute()
        )
        print(f"📝 Chat criado: {result}")
        return result
    except Exception as e:
        print(f"❌ Erro ao criar chat: {e}")
        return None


def get_chats_by_user(user_id: str):
    try:
        result = (
            supabase.table("chats")
            .select("*, messages(*)")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .execute()
        )

        # print("result: ", result)
        # print(f"📚 {len(result.data)} chats encontrados para user {user_id}")
        return result.data

    except Exception as e:
        print(f"❌ Erro ao buscar chats por usuário: {e}")
        return None


def get_chat(chat_id: str):
    try:
        result = (
            supabase.table("chats").select("*").eq("id", chat_id).single().execute()
        )

        print(f"🔍 Chat encontrado: {chat_id}")
        return result.data
    except Exception as e:
        print(f"❌ Erro ao buscar chat {chat_id}: {e}")
        return None


def delete_chat(chat_id: str):
    """Remove um chat e suas mensagens."""
    try:
        # Remove mensagens do chat
        supabase.table("messages").delete().eq("chatId", chat_id).execute()

        # Remove o chat
        supabase.table("chats").delete().eq("id", chat_id).execute()

        print(f"🗑️ Chat deletado: {chat_id}")
        return True

    except Exception as e:
        print(f"❌ Erro ao deletar chat {chat_id}: {e}")
        return False


def update_chat_title(chat_id: str, new_title: str):
    """Atualiza o título do chat."""
    try:
        supabase.table("chats").update({"title": new_title}).eq("id", chat_id).execute()

        print(f"✏️ Título atualizado do chat {chat_id}: {new_title}")
        return True

    except Exception as e:
        print(f"❌ Erro ao atualizar título do chat {chat_id}: {e}")
        return False


# === CHAT MESSAGES FUNCTIONS ===


def add_message(chat_id: str, content: str, from_user: bool):
    """Insere uma mensagem no chat."""
    try:
        result = (
            supabase.table("messages")
            .insert({"chatId": chat_id, "content": content, "fromUser": from_user})
            .execute()
        )

        return result.data

    except Exception as e:
        print(f"❌ Erro ao adicionar mensagem ao chat {chat_id}: {e}")
        return None


def get_messages(chat_id: int):
    try:
        result = (
            supabase.table("messages")
            .select("*")
            .eq("chatId", chat_id)
            .order("created_at", desc=False)
            .execute()
        )

        return result.data

    except Exception as e:
        print(f"❌ Erro ao buscar mensagens do chat {chat_id}: {e}")
        return None


def update_message_feedback(message_id: str, feedback: bool):
    """Atualiza o campo goodFeedBack de uma mensagem."""
    try:
        result = (
            supabase.table("messages")
            .update({"goodFeedback": feedback})
            .eq("id", message_id)
            .execute()
        )

        print(f"⭐ Feedback atualizado na mensagem {message_id}: {feedback}")
        return result.data

    except Exception as e:
        print(f"❌ Erro ao atualizar feedback da mensagem {message_id}: {e}")
        return None


def get_contexts():
    try:
        result = (
            supabase.table("team_memory_bomma")
            .select("id, tag, context, content, embedding")
            .execute()
        )
        print(f"✅ get de todos os contextos Bomma realizado com sucesso!")
        return result.data
    except Exception as e:
        print(f"❌ Erro ao pegar todos os contextos Bomma: {e}")
        return None

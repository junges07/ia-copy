import json
import re

from ..hooks.llm_hook import run_llm_structured
from ..hooks.supabase_hook import get_contexts, get_individual_memory
from ..hooks.embedding_hook import get_embedding, cosine_similarity


def should_save_embedding(
    new_context: str, scope: str, user: str, threshold: float = 0.85
):

    new_embedding = get_embedding(new_context)

    if scope == "personal":
        individual_memorys = get_individual_memory(user)
        if not individual_memorys.data:
            print("📦 Memória individual vazia — salvando direto")
            return True

        for memory in individual_memorys.data:
            stored_embedding = memory.get("embedding")

            if not stored_embedding:
                print("⚠️ Memória individual sem embedding — ignorando")
                continue

            if isinstance(stored_embedding, str):
                try:
                    stored_embedding = json.loads(stored_embedding)
                except Exception as e:
                    print("⚠️ Erro ao converter embedding individual:", e)
                    continue

            if not isinstance(stored_embedding, list):
                print("⚠️ Embedding individual inválido — ignorando")
                continue

            similarity = cosine_similarity(new_embedding, stored_embedding)
            print(f"🔁 Similaridade (individual) detectada: {similarity:.4f}")

            if similarity >= threshold:
                print("🚫 Memória individual duplicada — NÃO SALVAR")
                return False

        print("✅ Memória individual nova — PODE SALVAR")
        return True

    else:
        existing = get_contexts()

        if not existing:
            print("📦 Banco vazio — salvando direto")
            return True

        for memory in existing:
            stored_embedding = memory.get("embedding")

            if not stored_embedding:
                print("⚠️ Registro sem embedding — ignorando")
                continue

            if isinstance(stored_embedding, str):
                try:
                    stored_embedding = json.loads(stored_embedding)
                except Exception as e:
                    print("⚠️ Erro ao converter embedding:", e)
                    continue

            if not isinstance(stored_embedding, list):
                print("⚠️ Embedding inválido — ignorando")
                continue

            similarity = cosine_similarity(new_embedding, stored_embedding)

            print(f"🔁 Similaridade detectada: {similarity:.4f}")

            if similarity >= threshold:
                print("🚫 Memória duplicada detectada — NÃO VAI SALVAR")
                return False

        print("✅ Memória nova — PODE SALVAR")
        return True


def classify_global_memory(message: str, user):
    """
    Classifica se a mensagem deve gerar memória global.
    Depois valida se essa memória já existe usando embedding.
    """

    prompt = f"""
Você é um classificador EXTREMAMENTE RIGOROSO de MEMÓRIA da IA.

Sua função é identificar:
1) Se a mensagem deve virar memória
2) Se ela é memória COLETIVA (global) ou INDIVIDUAL (personal)

DEFINIÇÕES IMPORTANTES:

🟨 MEMÓRIA INDIVIDUAL (scope = "personal")
Deve ser salva quando a informação for:
- uma preferência pessoal do usuário
- um estilo que só ele quer usar
- uma forma específica como ele quer receber suas copys
- rotinas ou padrões privados
- salvar quando houver pronome próprio EXPLÍCITO, JUNTAMENTE com uma PREFERÊNCIA (minha, eu gosto, eu prefiro…)
- ajustes que NÃO devem afetar outros usuários

🟦 MEMÓRIA COLETIVA (scope = "global")
Deve ser salva apenas quando a instrução for:
- uma regra permanente da MARCA BOMMA
- um padrão de escrita oficial
- um posicionamento fixo da marca
- uma diretriz estrutural do sistema
- um processo universal aplicado para TODOS os usuários

⚠️ NUNCA salvar:
- Briefings específicos
- Informações de um único projeto
- Ajustes temporários
- Respostas de refinamento
- Tarefas únicas
- Pedidos de execução

Exemplos de memória INDIVIDUAL:
- “minhas copys devem sempre começar com X”
- “prefiro textos mais diretos”
- “sempre deixe minhas legendas curtas”

IMPORTANTE para memórias INDIVIDUAIS:
- as memórias individuais tem APENAS o "content", ou seja, ele tem que ser autoexplicativo, sem depender da tag ou context.

Exemplos de memória COLETIVA:
- “a BOMMA nunca usa emoji”
- “a comunicação da marca evita termos de venda agressiva”
- “o posicionamento da BOMMA é maduro e técnico”

Responda SEMPRE com JSON válido:

{{
  "should_save": true ou false,
  "scope": "global" ou "personal",
  "content": "o que deve ser salvo",
  "context": "quando aplicar",
  "tag": "regra | estilo | script | fato | processo | misc"
}}

Mensagem do usuário:
\"{message}\"
"""

    # ✅ Classificação inicial via LLM
    # print("PROMPT CLASSIFY MEMORY: ", prompt)
    memory = run_llm_structured(prompt)

    # ✅ Proteção contra erro de JSON da LLM
    if not isinstance(memory, dict):
        return {
            "should_save": False,
            "scope": "none",
            "content": "",
            "context": "",
            "tag": "misc",
        }

    if not memory.get("context"):
        memory["should_save"] = False
        memory["scope"] = "none"
        return memory

    if memory.get("should_save") is False:
        return memory

    is_new = should_save_embedding(
        memory["context"] + " " + memory["content"], memory["scope"], user
    )

    memory["should_save"] = is_new

    return memory

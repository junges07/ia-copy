from ..hooks.llm_hook import run_llm_structured


def classify_context_message(
    str_messages: str, global_contexts: list, personal_contexts: list
):

    prompt = f"""
Você é um analisador de ATIVAÇÃO DE CONTEXTOS para uma IA criativa.

Você receberá:
1. O HISTÓRICO DA CONVERSA
2. UMA LISTA DE CONTEXTOS GLOBAIS (memória coletiva)
3. UMA LISTA DE MEMÓRIAS INDIVIDUAIS (memória pessoal do usuário)

IMPORTANTE — ESTRUTURA DOS DADOS:
- CONTEXTOS GLOBAIS sempre possuem: 
    "tag", "context" e "content".
- MEMÓRIAS INDIVIDUAIS possuem APENAS:
    "content"
  Elas NÃO possuem "tag" nem "context".  
  Portanto, ao ativá-las, você deve preencher:
    "tag": "personal_preference"
    "context": "preferência individual do usuário"
    "content": <texto da memória individual>
    "scope": "personal"

OBJETIVO:
Identificar quais memórias (globais ou individuais) devem ser ativadas para interpretar corretamente a mensagem atual.

RESTRIÇÕES:
❌ Não crie novos contextos.
❌ Não modifique textos existentes.
❌ Não misture memórias individuais com globais.
❌ Não ative memória individual para outro usuário.

FORMATO DE SAÍDA (OBRIGATÓRIO):

{{
  "active_contexts": [
    {{
      "tag": "...",
      "context": "...",
      "content": "...",
      "scope": "global" | "personal"
    }}
  ]
}}

REGRAS DE ATIVAÇÃO:

1. Ative CONTEXTO GLOBAL quando:
   - A conversa envolver diretrizes estruturais, estilo da marca ou regras gerais.

2. Ative MEMÓRIA INDIVIDUAL quando:
   - O usuário está dizendo algo que reflete gosto pessoal, preferência permanente ou estilo próprio.
   - A memória individual seja relevante para interpretar a situação atual.

3. Caso nenhum contexto seja aplicável:
   → Retorne "active_contexts": []

---

HISTÓRICO DA CONVERSA:
{str_messages}

---

CONTEXTOS GLOBAIS EXISTENTES:
{global_contexts}

---

MEMÓRIAS INDIVIDUAIS DO USUÁRIO (APENAS content):
{personal_contexts}
    """

    result = run_llm_structured(prompt)
    return result

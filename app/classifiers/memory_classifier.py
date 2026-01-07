import json, re

from ..hooks.llm_hook import run_llm
from ..hooks.embedding_hook import get_embedding, is_duplicate_embedding
from ..hooks.supabase_hook import insert_individual_memory, get_individual_memory


def classify_individual_memory(message: str, username: str):

    individual_verification = (
        """
        Você é um **classificador lógico** responsável por identificar **preferências pessoais permanentes** de um usuário — especialmente arquitetos, designers e profissionais criativos. Sua função é analisar a mensagem recebida e decidir **objetivamente** se ela contém uma instrução ou preferência **individual e persistente**, ou se é apenas um pedido operacional momentâneo. --- ### ⚙️ REGRAS GERAIS Você **NÃO deve interpretar criativamente**. Você **NÃO deve inventar informações**. Responda **apenas com JSON válido**, sem texto adicional. --- ## 🎯 OBJETIVO Detectar qualquer instrução, ajuste ou preferência pessoal que altere **como o sistema deve responder a este usuário de forma duradoura**. Essas preferências normalmente dizem respeito a: - estilo de texto ou linguagem; - formato de entrega (ex: apenas legenda, com ou sem roteiro); - tom emocional ou visual; - profundidade das legendas ou das narrativas; - instruções permanentes de estilo, tom, estrutura ou estética. --- ### 🧱 REGRAS DE EXCLUSÃO **Nunca classifique como “individual” se:** - a mensagem se refere a um arquiteto, escritório, cliente ou projeto; - o contexto indicar que a preferência é sobre **como comunicar o trabalho de outra pessoa**; - a frase for puramente operacional (“faça um post sobre o projeto novo”, “crie um roteiro para o Studio X”). **Classifique como “individual” quando:** - o sujeito é o próprio usuário (“eu”, “a gente”, “nós”, “meu estilo”, “minha página”, “meus posts”, “meu portfólio”); - a mensagem altera o modo de escrita ou estilo que ele deseja receber; - ele define preferências de comunicação, estética, profundidade ou formato pessoal. --- ### 💡 EXEMPLOS CLAROS **Individual (relevante):** quero legendas mais poéticas e curtas
json
        
        {
          "relevante": "individual",
          "informacao": "o usuário prefere legendas poéticas e curtas"
        }
        
        Individual (relevante):
        sou arquiteto e prefiro textos que valorizem a estética do projeto
        {
         "relevante": "individual",
         "informacao": "o usuário é arquiteto e prefere textos que valorizem a estética do projeto"
        }
        
        Individual (relevante):
        não quero que os posts pareçam comerciais, prefiro algo mais inspiracional
        {
        "relevante": "individual",
        "informacao": "o usuário prefere que os posts sejam inspiracionais e não comerciais"
        }
        
        Não relevante (operacional):
        faça um post para o Studio Alma sobre o novo projeto
        {
        "relevante": false,
        "informacao": ""
        }
        
        ###🧩 FORMATO DE SAÍDA
        Retorne sempre um único JSON válido no formato:
        
        {
          "relevante": "individual" ou false,
          "informacao": "<descrição objetiva e curta da preferência pessoal>"
        }
        

        Mensagem do usuário:
    """
        + message
    )

    result = run_llm(individual_verification, model="gpt-4o-mini")

    try:
        match = re.search(r"\{.*\}", result, re.DOTALL)
        json_data = json.loads(match.group(0)) if match else {"relevante": False}
    except:
        json_data = {"relevante": False}

    taboo_terms = ["arquiteto", "arquiteta", "designer", "studio", "escritório"]

    if any(term in message.lower() for term in taboo_terms):
        if username.lower() not in message.lower():
            json_data["relevante"] = False

    return {
        "relevante": json_data.get("relevante", False),
        "info": json_data.get("informacao", "").strip(),
    }


def store_individual_memory(username: str, info: str):
    if not info:
        return False

    embedding = get_embedding(info)
    existing = get_individual_memory(username)

    existing_embs = [item["embedding"] for item in (existing.data or [])]

    if is_duplicate_embedding(embedding, existing_embs):
        return False

    insert_individual_memory(username, info, embedding)
    return True


def load_individual_memory(username: str) -> str:
    usercontent = get_individual_memory(username)

    if not usercontent or not usercontent.data:
        return "Nenhuma preferência individual registrada ainda."

    return "\n".join([f"- {item['content']}" for item in usercontent.data])

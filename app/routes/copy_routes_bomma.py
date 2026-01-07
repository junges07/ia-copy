import json, re
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .request_models import UserRequest

from ..classifiers.intent_classifier import classify_intent
from ..classifiers.memory_global_classifier import classify_global_memory
from ..classifiers.context_message_classifier import classify_context_message

from ..tools.copy_tool import generate_bomma_copy_debug
from ..tools.video_tool import generate_bomma_video_script_debug

from ..hooks.llm_hook import create_conversational_chain
from ..hooks.supabase_hook import (
    insert_team_memory_bomma,
    get_messages,
    get_contexts,
    insert_individual_memory,
    get_individual_memory,
)
from ..hooks.embedding_hook import get_embedding


print("✅ copy_routes carregado")

router = APIRouter()


def get_identity_prompt():
    return """
Você é uma Inteligência Artificial especializada em COPYWRITING E ROTEIROS
PARA ARQUITETOS.

Seu papel principal é ajudar o usuário a criar, analisar e refinar:
- copys escritas
- roteiros de vídeo
- estruturas de comunicação

sempre voltadas à comunicação de PROJETOS DE ARQUITETURA, interiores
e soluções espaciais criadas por arquitetos.

Você NÃO vende imóveis.
Você comunica o PROJETO DO ARQUITETO aplicado ao espaço.
O imóvel é apenas o suporte físico.
O produto real é a solução criativa, funcional e estética desenvolvida
pelo arquiteto.

Para construir uma comunicação verdadeiramente alinhada ao posicionamento
da BOMMA, você precisa dominar com clareza três pilares fundamentais:

1) Público-alvo  
— Identificado no espectro de AA+ até BC, pois cada nível exige tom,
ritmo, intenção e maturidade diferentes na comunicação.

2) Contexto do projeto  
— Tipo de espaço onde o PROJETO é aplicado (residência, apartamento,
cobertura, casa de campo, casa de praia, studio, comercial,
contexto urbano, etc.), pois isso define a experiência arquitetônica
que será comunicada.

3) Formato de aplicação  
— Onde o conteúdo será utilizado:
  • anúncios pagos (Meta Ads, Google Ads)
  • legendas de Instagram
  • posts institucionais
  • roteiros de vídeo (anúncios, institucionais ou explicativos)

Cada formato exige estrutura, ritmo, linguagem e estratégia próprios.

IMPORTANTE — GERAÇÃO DE CONTEÚDO:
- Você SÓ gera uma COPY quando o usuário ordenar explicitamente a criação de uma copy.
- Você SÓ gera um ROTEIRO DE VÍDEO quando o usuário ordenar explicitamente
  a criação de um roteiro de vídeo.
- Em todos os outros casos, você conversa, orienta, analisa ou explica.

Você também é capaz de:
- Conversar normalmente com o usuário
- Dar explicações técnicas e estratégicas
- Sugerir abordagens de comunicação
- Analisar textos enviados
- Criar copys quando solicitado explicitamente
- Criar roteiros de vídeo quando solicitado explicitamente

SOBRE VÍDEOS:
- Roteiros de vídeo devem priorizar:
  • clareza técnica
  • intenção de projeto
  • decisões arquitetônicas
  • funcionalidade e experiência do espaço
- Nunca utilizar linguagem sensacionalista ou emocional exagerada.
- Nunca utilizar termos típicos de venda imobiliária.

Você POSSUI um sistema de memória:
- Quando o usuário pede explicitamente para salvar alguma informação,
  você registra isso como uma regra, diretriz ou preferência.
- Essas informações podem ser reutilizadas no futuro.
- Você usa essas memórias somente quando forem relevantes ao contexto da conversa.
- As memórias podem ser individuais (apenas para aquele usuário)
  ou coletivas (válidas para todos os usuários da BOMMA).
- Essas informações são registradas de forma persistente.
- Portanto, se alguém perguntar se você consegue SALVAR coisas,
  a resposta correta é SIM.

REGRAS FUNDAMENTAIS:
- Você NÃO deve inventar memórias.
- Você só usa memórias quando elas forem fornecidas como CONTEXTO ATIVO.
- Você NÃO menciona banco de dados, embeddings ou sistemas internos.
- Você responde sempre de forma clara, coerente e direta.
"""


def handle_conversation(msg: str, session_id: str, identify_contexts: dict) -> str:
    active_contexts = identify_contexts.get("active_contexts", [])

    identity_prompt = get_identity_prompt()

    if active_contexts:
        injected_context = "\n".join(
            [f"- ({c['tag']}) {c['content']}" for c in active_contexts]
        )

        system_context_prompt = f"""
        INSTRUÇÕES DE CONTEXTO ATIVAS (OBRIGATÓRIAS):
        
        {injected_context}
        
        Essas regras devem ser consideradas na resposta abaixo.
        """
    else:
        system_context_prompt = ""

    conversation = create_conversational_chain(
        session_id=session_id, model="gpt-4o", temperature=0.6
    )

    final_input = f"""
    {identity_prompt}

    {system_context_prompt}

    Mensagem do usuário:
    {msg}
    """

    response = conversation.invoke({"input": final_input})

    if isinstance(response, dict):
        return response.get("response", "")

    return str(response)


def getStrMsgs(chat_id):
    messages = get_messages(chat_id)

    last_messages = messages[-10:]

    output = ""
    for msg in last_messages:
        if msg.get("fromUser"):
            output += f"[USER] {msg.get('content')}"
        else:
            output += f"[IA] {msg.get('content')}"
        output += "\n"
    return output


@router.options("/generate_copy_bomma")
async def options_generate_copy():
    return JSONResponse(
        content={},
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )


@router.post("/generate_copy_bomma")
async def classify_embedding(request: UserRequest):

    session_id = request.session_id
    message = request.data
    user_id = request.user.strip().lower()

    print("💬 Mensagem recebida:", message)
    print("👤 user: ", user_id)
    conversation_text = getStrMsgs(session_id)

    saveInMemory = classify_global_memory(message, user_id)
    print("Salvar Memória Colteviva: ", saveInMemory)

    if saveInMemory.get("should_save"):
        if saveInMemory.get("scope") == "personal":
            content = saveInMemory.get("content")
            embedding = get_embedding(content)
            insert_individual_memory(user_id, content, embedding)

        else:
            tag = saveInMemory.get("tag")
            context = saveInMemory.get("context")
            content = saveInMemory.get("content")

            if not all([tag, context, content]):
                print("❌ Dados insuficientes para salvar memória")
            else:
                insert_team_memory_bomma(tag, context, content)

    existing_contexts = get_contexts()
    individual_memorys = get_individual_memory(user_id)

    identify_contexts = classify_context_message(
        conversation_text, existing_contexts, individual_memorys.data
    )
    print("🧠 CONTEXTOS IDENTIFICADOS: ", identify_contexts.get("active_contexts"))

    intent_type = classify_intent(message)
    print(f"🧠 Tipo de conteúdo identificado: {intent_type}")

    if intent_type == "copy":
        result = generate_bomma_copy_debug(
            message,
            conversation_text,
            identify_contexts.get("active_contexts"),
            user_id,
        )
        return {"copy": result.get("copy")}

    elif intent_type == "video":
        result = generate_bomma_video_script_debug(
            message,
            conversation_text,
            identify_contexts.get("active_contexts"),
            user_id,
        )
        return {"copy": result.get("copy")}

    else:
        reply = handle_conversation(message, session_id, identify_contexts)
        return {"copy": reply}

import json, re
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .request_models import UserRequest

from ..prompts.prompt_base_bomma import get_prompt_base_bomma

from ..classifiers.intent_classifier import classify_intent, get_video_guidelines

from ..classifiers.public_classifier import classify_public, get_public_prompt

from ..classifiers.context_classifier import classify_context, get_context_prompt

from ..classifiers.format_classifier import classify_format, get_format_prompt

from ..prompts.style_correction_module import get_style_correction_examples

from ..classifiers.memory_classifier import (
    classify_individual_memory,
    store_individual_memory,
    load_individual_memory,
)

from ..hooks.llm_hook import run_llm, create_conversational_chain
from ..hooks.prompt_templates import (
    generate_prompt_copy_bomma,
    generate_prompt_video_bomma,
)

print("✅ copy_routes carregando...")

router = APIRouter()
CONVERSATIONS = {}


# ================================
#   OPTIONS
# ================================
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


# ================================
#   POST — MAIN ROUTE
# ================================
@router.post("/generate_copy_bomma")
async def classify_embedding(request: UserRequest):

    session_id = request.session_id
    message = request.data
    lovable_user_name = request.user.strip().lower()

    print("💬 Mensagem recebida:", message)

    content_type = classify_intent(message)
    print(f"🧠 Tipo de conteúdo identificado: {content_type}")

    if content_type == "video":
        video_prompt = get_video_guidelines()
    else:
        video_prompt = ""

    public = classify_public(message)
    print("🎯 Público identificado:", public)
    public_prompt = get_public_prompt(public)

    print("public_prompt: ", public_prompt)

    context = classify_context(message)
    print("🧠 Contexto identificado:", context)
    context_prompt = get_context_prompt(context)

    fmt = classify_format(message)
    print("🎯 Formato identificado:", fmt)
    format_prompt = get_format_prompt(fmt)

    json_verif = classify_individual_memory(message, lovable_user_name)
    store_individual_memory(lovable_user_name, json_verif.get("info"))

    user_res = load_individual_memory(lovable_user_name)

    base = get_prompt_base_bomma()

    style_examples = get_style_correction_examples()

    copy_prompt = f"""
        {base}
        
        INSTRUÇÃO IMPORTANTE (NÃO INCLUIR NA COPY):
        Siga a hierarquia de prioridade abaixo ao gerar o texto:

        1. Prompt-base Bomma (imutável, núcleo da identidade)
        2. Correções de estilo (style_examples)
        3. Contexto (residência, apartamento etc.)
        4. Público-Alvo
        5. Formato
        6. Preferências individuais
        7. Pedido original do usuário

        NUNCA inclua esta lista no texto final.
        NUNCA cite “hierarquia”, “passo a passo” ou termos estruturais.

        Mensagem do usuário:
        {message}

        Preferências individuais:
        {user_res}

        Tipo de conteúdo: {content_type}
        
        Módulo de Público-Alvo (se aplicável): {public_prompt}
        
        Módulo de Formato: {format_prompt} 
        
        Módulo de Contexto: {context_prompt}
        
        Orientações de Vídeo (se for vídeo): {video_prompt}
        
        EXEMPLOS PARA REFERÊNCIA DE ESTILO (NÃO UTILIZAR NA COPY):
        {style_examples}
        
        Gere o texto final seguindo tudo acima, inclusive sua hirearquia.
        """

    # ================================
    # 5) GERA COPY
    # ================================
    conversation = create_conversational_chain(session_id=session_id, model="gpt-4o")

    try:
        response = conversation.invoke({"input": copy_prompt})
        copy = response.get("response") if isinstance(response, dict) else str(response)
    except Exception as e:
        print("❌ Erro ao gerar copy:", e)
        return {"copy": f"Erro ao gerar copy: {str(e)}"}

    return {"copy": copy}

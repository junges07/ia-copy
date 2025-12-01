import json
import re
from ..hooks.llm_hook import run_llm


def classify_context(message: str) -> str:
    msg = message.lower().strip()

    # ==============================
    # 1) REGRAS DURAS (NÃO DELIRAM)
    # ==============================

    # Se contém "casa" mas não contém praia/litoral/mar → é residência
    if "casa" in msg:
        if not any(x in msg for x in ["praia", "litoral", "mar", "beira-mar"]):
            return "residencia"

    # Se contém apartamento
    if any(x in msg for x in ["apartamento", "apê"]):
        return "apartamento"

    # Se contém cobertura
    if "cobertura" in msg:
        return "cobertura"

    # Se contém studio
    if "studio" in msg or "stúdio" in msg:
        return "studio"

    # Se contém comércio
    if any(x in msg for x in ["loja", "comercial", "escritório"]):
        return "comercial"

    # Se contém alto andar
    if any(x in msg for x in ["alto andar", "andar alto", "vista alta"]):
        return "alto_andar"

    # Se contém praia
    if any(x in msg for x in ["praia", "litoral", "beira-mar", "mar"]):
        return "casa_praia"

    # Se contém campo
    if any(x in msg for x in ["campo", "sítio", "chácara", "fazenda"]):
        return "casa_campo"

    # Se contém rural
    if any(x in msg for x in ["rural", "fazenda", "sítio"]):
        return "rural"

    # ==============================
    # 2) FALLBACK — LLM
    # ==============================

    prompt = f"""
    Analise a mensagem abaixo e identifique o **contexto imobiliário principal**.

    Você só pode escolher uma das categorias:
    residencia, apartamento, casa_praia, casa_campo, studio, cobertura, comercial, rural, alto_andar, cidade, none

    REGRAS ABSOLUTAS:
    - Não classifique como "casa_praia" sem palavras como praia, litoral, mar, beira-mar.
    - Não invente ambientes não mencionados.
    - Escolha a categoria mais simples e direta possível.
    - Se falar "casa" sem indicação geográfica → residencia.

    Retorne somente JSON:
    {{
        "contexto": "<categoria>"
    }}

    Mensagem: "{message}"
    """

    result = run_llm(prompt, model="gpt-4o-mini")

    try:
        match = re.search(r"\{.*\}", result, re.DOTALL)
        data = json.loads(match.group(0)) if match else {"contexto": "none"}
    except:
        data = {"contexto": "none"}

    contexto = data.get("contexto", "none").strip().lower()
    return contexto if contexto != "none" else None


def get_context_prompt(context: str) -> str:
    """
    Retorna instruções específicas de escrita baseadas no contexto identificado.
    Isso funciona como o módulo independente de contexto,
    ajudando o modelo a adaptar a copy ao tipo de imóvel.
    """

    if not context or context == "none":
        return ""

    # ------------------------------------------------------------
    # RESIDÊNCIA (casa comum)
    # ------------------------------------------------------------
    if context == "residencia":
        return """
📌 CONTEXTO — RESIDÊNCIA
- Descreva um lar cotidiano, real, funcional.
- Foco na experiência de morar, praticidade, circulação e rotina.
- Linguagem simples e humana.
- Evite qualquer tom conceitual ou técnico.
- Destaque aspectos como luz, conforto, rotina, vida em família, garagem, quintal, etc.
"""

    # ------------------------------------------------------------
    # APARTAMENTO
    # ------------------------------------------------------------
    if context == "apartamento":
        return """
📌 CONTEXTO — APARTAMENTO
- Foco em praticidade urbana, integração e otimização do espaço.
- Valorize luz natural, ventilação, sensação de amplitude.
- Mencione circulação, integração, segurança e conveniência.
"""

    # ------------------------------------------------------------
    # CASA DE PRAIA
    # ------------------------------------------------------------
    if context == "casa_praia":
        return """
📌 CONTEXTO — CASA DE PRAIA
- Tom leve, arejado e natural.
- Foco em luz, brisa, descanso e integração com o entorno.
- Evitar qualquer linguagem poética excessiva.
- A copy deve transmitir leveza e vida desacelerada.
"""

    # ------------------------------------------------------------
    # CASA DE CAMPO
    # ------------------------------------------------------------
    if context == "casa_campo":
        return """
📌 CONTEXTO — CASA DE CAMPO
- Tom acolhedor e sereno.
- Destaque refúgio, calma, natureza, pausas e conforto sensorial.
- Evitar metáforas exageradas.
"""

    # ------------------------------------------------------------
    # COBERTURA
    # ------------------------------------------------------------
    if context == "cobertura":
        return """
📌 CONTEXTO — COBERTURA
- Foco em amplitude, vista, terraço, integração interna/externa.
- Linguagem madura e objetiva.
- Evite apelos de luxo.
"""

    # ------------------------------------------------------------
    # STUDIO
    # ------------------------------------------------------------
    if context == "studio":
        return """
📌 CONTEXTO — STUDIO
- Enfatize praticidade, rotina inteligente e uso eficiente do espaço.
- Tom jovem, direto, funcional.
"""

    # ------------------------------------------------------------
    # COMERCIAL
    # ------------------------------------------------------------
    if context == "comercial":
        return """
📌 CONTEXTO — IMÓVEL COMERCIAL
- Linguagem objetiva e racional.
- Foco em fluxo, visibilidade, localização, funcionalidade do uso diário.
"""

    # ------------------------------------------------------------
    # RURAL
    # ------------------------------------------------------------
    if context == "rural":
        return """
📌 CONTEXTO — IMÓVEL RURAL
- Destaque espaço aberto, terreno, autonomia, vida calma.
- Tom mais descritivo, prático e direto.
"""

    # ------------------------------------------------------------
    # APARTAMENTO EM ANDAR ALTO
    # ------------------------------------------------------------
    if context == "alto_andar":
        return """
📌 CONTEXTO — APARTAMENTO EM ANDAR ALTO
- Valorize luz natural, ventilação, vista e privacidade.
- Evitar qualquer tom luxuoso explícito.
"""

    # ------------------------------------------------------------
    # CONTEXTO URBANO (cidade)
    # ------------------------------------------------------------
    if context == "cidade":
        return """
📌 CONTEXTO — CIDADE
- Destaque conveniência, mobilidade, estilo de vida urbano.
- Tom moderno, direto e natural.
"""

    return ""

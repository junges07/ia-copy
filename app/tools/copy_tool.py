from app.hooks.llm_hook import run_llm
from app.classifiers.public_classifier import classify_public, get_public_prompt
from app.classifiers.format_classifier import classify_format, get_format_prompt
from app.classifiers.context_classifier import classify_context, get_context_prompt

# from app.classifiers.copy_readiness_classifier import (
#     build_missing_questions,
#     classify_copy_readiness,
# )

from typing import Any, Dict, List, Optional, Union
import json


def _normalize_contexts(
    raw_contexts: Union[str, Dict[str, Any], List[Dict[str, Any]], None],
) -> List[Dict[str, Any]]:
    if raw_contexts is None:
        return []

    # Se já veio lista de dicts
    if isinstance(raw_contexts, list):
        return [c for c in raw_contexts if isinstance(c, dict)]

    # Se veio um único dict
    if isinstance(raw_contexts, dict):
        return [raw_contexts]

    # Se veio string (possivelmente JSON)
    if isinstance(raw_contexts, str):
        raw = raw_contexts.strip()
        if not raw:
            return []
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [c for c in parsed if isinstance(c, dict)]
            if isinstance(parsed, dict):
                return [parsed]
        except Exception:
            # Se não for JSON válido, ignora silenciosamente
            return []

    return []


def _build_contexts_prompt(contexts: List[Dict[str, Any]]) -> str:
    """
    Constrói o bloco de prompt com as memórias/contextos ativos.
    """
    if not contexts:
        return ""

    lines = []
    for c in contexts:
        tag = (c.get("tag") or "").strip()
        content = (c.get("content") or c.get("context") or "").strip()

        if not content:
            continue

        if tag:
            lines.append(f"- ({tag}) {content}")
        else:
            lines.append(f"- {content}")

    if not lines:
        return ""

    return (
        "🎯 CONTEXTOS / REGRAS ATIVAS (OBRIGATÓRIO CONSIDERAR NA RESPOSTA):\n"
        + "\n".join(lines)
    )


def _extract_requested_quantity(message: str) -> Optional[int]:
    """
    Tenta identificar se o usuário pediu explicitamente N copys / legendas.
    Ex: "preciso de 3 copies", "faça 2 legendas", etc.
    Só considera números explícitos (dígitos).
    """
    import re

    msg = message.lower()
    pattern = r"(\d+)\s*(copy|copys|cópias|copias|legenda|legendas|textos|copies)"
    match = re.search(pattern, msg)
    if not match:
        return None

    try:
        n = int(match.group(1))
        if 1 <= n <= 10:
            return n
    except Exception:
        return None

    return None


def generate_bomma_copy_debug(
    input_text: str,
    conversation: str,
    contexts: Any,
    user_name: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Tool oficial de geração de copy da BOMMA.

    - Usa classificadores de público, formato e contexto.
    - Injeta memórias/contextos relevantes.
    - Aplica diretrizes oficiais da BOMMA.
    - Gera copy final pronta para uso.
    """

    # ==============================
    # 1) Log básico para debug
    # ==============================
    print("\n[COPY_TOOL] Tool acionada!")
    print(f"[COPY_TOOL] user_id: {user_name}")
    print(f"[COPY_TOOL] input_text: {input_text}")
    print(f"[COPY_TOOL] conversation: {conversation}")
    print(f"[COPY_TOOL] contexts (raw): {contexts}")
    print(f"[COPY_TOOL] extra_kwargs: {kwargs}\n")

    # ==============================
    # 2) Normalizar contextos/memórias
    # ==============================
    active_contexts = _normalize_contexts(contexts)
    contexts_prompt = _build_contexts_prompt(active_contexts)

    # ==============================
    # 3) Classificações principais
    # ==============================
    try:
        publico = classify_public(input_text) or "nenhum"
    except Exception as e:
        print(f"[COPY_TOOL] ERRO classify_public: {e}")
        publico = "nenhum"

    try:
        formato = classify_format(input_text) or "generico"
    except Exception as e:
        print(f"[COPY_TOOL] ERRO classify_format: {e}")
        formato = "generico"

    try:
        contexto = classify_context(input_text) or "none"
    except Exception as e:
        print(f"[COPY_TOOL] ERRO classify_context: {e}")
        contexto = "none"

    print(f"[COPY_TOOL] público classificado: {publico}")
    print(f"[COPY_TOOL] formato classificado: {formato}")
    print(f"[COPY_TOOL] contexto classificado: {contexto}")

    # ==============================
    # 4) Blocos de prompt específicos
    # ==============================
    public_block = ""
    format_block = ""
    context_block = ""

    try:
        public_block = get_public_prompt(publico)
    except Exception as e:
        print(f"[COPY_TOOL] ERRO get_public_prompt: {e}")

    try:
        format_block = get_format_prompt(formato)
    except Exception as e:
        print(f"[COPY_TOOL] ERRO get_format_prompt: {e}")

    try:
        context_block = get_context_prompt(contexto)
    except Exception as e:
        print(f"[COPY_TOOL] ERRO get_context_prompt: {e}")

    # ==============================
    # 5) Quantidade de variações (se houver)
    # ==============================
    requested_qty = _extract_requested_quantity(input_text)
    qty_instruction = ""
    if requested_qty is not None:
        qty_instruction = (
            f"\nINSTRUÇÃO DE QUANTIDADE:\n"
            f"- O usuário pediu explicitamente {requested_qty} variação(ões).\n"
            f"- Produza EXATAMENTE {requested_qty} copies, numeradas como:\n"
            f"  1) ...\n"
            f"  2) ...\n"
            f"  (e assim por diante).\n"
        )

    # ==============================
    # 6) Prompt-mestre BOMMA
    # ==============================
    system_core = f"""
Você é a IA copywriter oficial da BOMMA, especializada em arquitetura, interiores
e mercado imobiliário, com foco em textos que respeitam rigorosamente as diretrizes
da marca.

HIERARQUIA DE PRIORIDADE (SIGA SEMPRE NA ORDEM, SEM EXCEÇÕES):

1. REGRAS DA MARCA (NÍVEL MÁXIMO)
   - Nada pode violar as diretrizes oficiais da BOMMA.
   - Isso inclui tom, restrições de palavras, postura, função da copy e foco no arquiteto.

2. CONTEXTOS COLETIVOS ATIVOS (NÍVEL ALTO)
   - São instruções válidas para todos os usuários.
   - Podem complementar ou detalhar as regras da marca, mas não podem contrariá-las.

3. MEMÓRIAS INDIVIDUAIS DO USUÁRIO
   - São preferências pessoais de tom, estrutura ou estilo.
   - Devem ser respeitadas sempre que NÃO entrarem em conflito com os níveis 1 e 2.

4. PEDIDO ATUAL DO USUÁRIO
   - O pedido é atendido completamente, desde que não viole nenhum nível acima.

EM CASO DE CONFLITO:
- O nível mais alto sempre prevalece.
- Nunca tente conciliar se isso violaria os níveis superiores.

OBJETIVO:
- Transformar o pedido do usuário em uma copy final pronta para uso, SEM explicar o processo.
- Sempre priorizar clareza, maturidade e alinhamento com o posicionamento da BOMMA.

REGRA FUNDAMENTAL DE POSICIONAMENTO:
- Você NUNCA deve escrever uma copy vendendo o imóvel em si.
- Toda copy deve obrigatoriamente comunicar o projeto do arquiteto aplicado ao imóvel.
- O imóvel é apenas o suporte físico. O produto real é a solução arquitetônica.
- Sempre destaque decisão de projeto, intenção, funcionalidade, experiência e estética criadas pelo arquiteto.

RESTRIÇÕES GERAIS (SEM EXCEÇÃO):
- NÃO usar palavras como: "luxo", "sonho", "sonhos", "premium", "alto padrão", "exclusivo",
  "oportunidade imperdível", "venha conhecer", "agende uma visita", "condomínio clube",
  "localização privilegiada" ou qualquer clichê típico de anúncio imobiliário.
- NÃO usar tom de venda agressivo.
- NÃO escrever em caixa alta (NADA de frases inteiras em maiúsculas).
- NÃO usar emojis.
- NÃO explicar o que você está fazendo.
- NÃO repetir a mensagem do usuário.

FORMATO DA RESPOSTA:
- Entregue apenas a(s) copy(s), sem comentários, sem títulos, sem markdown.
- Se houver mais de uma variação, numere assim: "1) ...", "2) ...".
- Não escreva nada fora do texto que o usuário possa publicar.

REGRA DE CTA (OBRIGATÓRIA):
- Toda copy deve conter UM CTA no final, adequado ao formato:
  - Para ADS → CTA leve de ação (ex: conversar, saber mais, entrar em contato)
  - Para LEGENDA → CTA elegante e discreto
  - Para GENERICO → CTA suave e natural
- O CTA nunca deve ser agressivo.
- Nunca usar chamadas como:
  "compre agora", "últimas unidades", "imperdível", "corra", "promoção".

METADADOS CLASSIFICADOS (USE APENAS COMO GUIA INTERNO, NÃO MOSTRAR):
- Público-alvo: {publico}
- Formato: {formato}
- Contexto do imóvel: {contexto}

QUALQUER violação de regra acima invalida completamente a resposta.
Se qualquer termo proibido for usado, a resposta deve ser considerada incorreta.
"""

    # Monta bloco de módulos
    modules_block_parts = []

    if public_block.strip():
        modules_block_parts.append("=== MÓDULO DE PÚBLICO ===\n" + public_block.strip())

    if format_block.strip():
        modules_block_parts.append("=== MÓDULO DE FORMATO ===\n" + format_block.strip())

    if context_block.strip():
        modules_block_parts.append(
            "=== MÓDULO DE CONTEXTO ===\n" + context_block.strip()
        )

    modules_block = "\n\n".join(modules_block_parts)

    # Bloco de contextos/memórias
    if contexts_prompt:
        contexts_block = (
            "\n=== MÓDULO DE MEMÓRIA / CONTEXTO VIVO ===\n" + contexts_prompt
        )
    else:
        contexts_block = ""

    # Conversa recente (somente para dar contexto de diálogo)
    conversation_block = ""
    if conversation:
        conversation_block = f"""
=== HISTÓRICO RESUMIDO DA CONVERSA ===
Use apenas como referência contextual, mas responda ao pedido final do usuário.
{conversation.strip()}
"""

    final_prompt = f"""
    {system_core}
    
    {qty_instruction}
    
    {modules_block}
    
    {contexts_block}
    
    {conversation_block}
    
    === PEDIDO FINAL DO USUÁRIO ===
    {input_text}
    
    AGORA, GERE APENAS A COPY FINAL, JÁ PRONTA PARA USO, RESPEITANDO TODAS AS REGRAS ACIMA.
    """
    # print("final prompt: ", final_prompt)

    try:
        raw_response = run_llm(
            final_prompt,
            model="gpt-5.1",
            temperature=0.7,
        )
        copy_text = (raw_response or "").strip()
        if not copy_text:
            copy_text = (
                "Não foi possível gerar a copy neste momento. "
                "Tente reformular o pedido ou tentar novamente em instantes."
            )
    except Exception as e:
        print(f"[COPY_TOOL] ERRO ao chamar LLM: {e}")
        copy_text = (
            "Ocorreu um erro interno ao gerar a copy. "
            "Tente novamente em alguns instantes."
        )

    # ==============================
    # 8) Retorno estruturado
    # ==============================
    return {
        "copy": copy_text,
        "metadata": {
            "user_id": user_name,
            "publico": publico,
            "formato": formato,
            "contexto": contexto,
            "requested_quantity": requested_qty,
            "active_contexts": active_contexts,
            "model_used": "gpt-4o",
            "debug": False,
        },
    }

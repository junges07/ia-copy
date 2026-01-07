from typing import Any, Dict, List, Optional, Union
import json

from app.hooks.llm_hook import run_llm
from app.classifiers.public_classifier import classify_public, get_public_prompt
from app.classifiers.format_classifier import classify_format, get_format_prompt
from app.classifiers.context_classifier import classify_context, get_context_prompt


def _normalize_contexts(
    raw_contexts: Union[str, Dict[str, Any], List[Dict[str, Any]], None],
) -> List[Dict[str, Any]]:
    """
    Normaliza memórias/contextos ativos para uma lista de dicts.
    Aceita: None | dict | list[dict] | str(JSON de dict/list).
    """
    if raw_contexts is None:
        return []

    if isinstance(raw_contexts, list):
        return [c for c in raw_contexts if isinstance(c, dict)]

    if isinstance(raw_contexts, dict):
        return [raw_contexts]

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
            return []

    return []


def _build_contexts_prompt(contexts: List[Dict[str, Any]]) -> str:
    """
    Constrói o bloco de prompt com as memórias/contextos ativos.

    Observação:
    - Alguns contextos podem ter apenas "content" (ex.: memórias individuais).
    - Outros podem ter "context" e/ou "tag" (ex.: memórias coletivas/contextos).
    """
    if not contexts:
        return ""

    lines: List[str] = []
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


def _extract_requested_seconds(message: str) -> Optional[int]:
    """
    Opcional: tenta capturar duração explícita quando o usuário fala algo como:
    - "roteiro de 30 segundos"
    - "vídeo de 45s"
    - "60 segundos"

    Retorna um int entre 15 e 120 (limite conservador) ou None.
    """
    import re

    msg = (message or "").lower()
    patterns = [
        r"(\d+)\s*(s|seg|segs|segundo|segundos)\b",
        r"(\d+)\s*(sec|secs|second|seconds)\b",
    ]
    for pat in patterns:
        m = re.search(pat, msg)
        if m:
            try:
                n = int(m.group(1))
                if 15 <= n <= 120:
                    return n
            except Exception:
                return None
    return None


def generate_bomma_video_script_debug(
    input_text: str,
    conversation: str,
    contexts: Any,
    user_name: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Tool oficial de geração de ROTEIRO DE VÍDEO da BOMMA (30–60s).

    - Usa classificadores de público, formato e contexto.
    - Injeta memórias/contextos ativos.
    - Aplica diretrizes oficiais da BOMMA.
    - Gera roteiro final pronto para ser falado.

    Observação:
    - Mantém a mesma arquitetura da copy_tool para consistência.
    """

    # ==============================
    # 1) Log básico para debug
    # ==============================
    print("\n[VIDEO_TOOL] Tool acionada!")
    print(f"[VIDEO_TOOL] user_id: {user_name}")
    print(f"[VIDEO_TOOL] input_text: {input_text}")
    print(f"[VIDEO_TOOL] conversation: {conversation}")
    print(f"[VIDEO_TOOL] contexts (raw): {contexts}")
    print(f"[VIDEO_TOOL] extra_kwargs: {kwargs}\n")

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
        print(f"[VIDEO_TOOL] ERRO classify_public: {e}")
        publico = "nenhum"

    try:
        formato = classify_format(input_text) or "generico"
    except Exception as e:
        print(f"[VIDEO_TOOL] ERRO classify_format: {e}")
        formato = "generico"

    try:
        contexto = classify_context(input_text) or "none"
    except Exception as e:
        print(f"[VIDEO_TOOL] ERRO classify_context: {e}")
        contexto = "none"

    print(f"[VIDEO_TOOL] público classificado: {publico}")
    print(f"[VIDEO_TOOL] formato classificado: {formato}")
    print(f"[VIDEO_TOOL] contexto classificado: {contexto}")

    # ==============================
    # 4) Blocos de prompt específicos
    # ==============================
    public_block = ""
    format_block = ""
    context_block = ""

    try:
        public_block = get_public_prompt(publico)
    except Exception as e:
        print(f"[VIDEO_TOOL] ERRO get_public_prompt: {e}")

    try:
        format_block = get_format_prompt(formato)
    except Exception as e:
        print(f"[VIDEO_TOOL] ERRO get_format_prompt: {e}")

    try:
        context_block = get_context_prompt(contexto)
    except Exception as e:
        print(f"[VIDEO_TOOL] ERRO get_context_prompt: {e}")

    # ==============================
    # 5) Duração (se o usuário explicitou)
    # ==============================
    requested_seconds = _extract_requested_seconds(input_text)
    duration_instruction = ""
    if requested_seconds is not None:
        # Mantém guardrails BOMMA (30–60), mas respeita pedido se estiver dentro
        if 30 <= requested_seconds <= 60:
            duration_instruction = (
                f"\nINSTRUÇÃO DE DURAÇÃO:\n"
                f"- O usuário pediu explicitamente {requested_seconds} segundos.\n"
                f"- Ajuste o texto para caber com naturalidade nesse tempo.\n"
            )
        else:
            # Se o usuário pedir fora do padrão, você mantém padrão BOMMA
            duration_instruction = (
                f"\nINSTRUÇÃO DE DURAÇÃO:\n"
                f"- O usuário pediu {requested_seconds} segundos, porém o padrão BOMMA é 30–60s.\n"
                f"- Mantenha 30–60s.\n"
            )

    # ==============================
    # 6) Prompt-mestre BOMMA (VÍDEO)
    # ==============================
    system_core = f"""
Você é a IA oficial de ROTEIROS DE VÍDEO da BOMMA, especializada em comunicação
arquitetônica para arquitetos.

HIERARQUIA DE PRIORIDADE (SIGA SEMPRE NA ORDEM, SEM EXCEÇÕES):

1. REGRAS DA MARCA (NÍVEL MÁXIMO)
   - Nada pode violar as diretrizes oficiais da BOMMA.
   - Isso inclui tom, restrições de palavras, postura, função do roteiro e foco no arquiteto.

2. ESTRUTURA OBRIGATÓRIA DO ROTEIRO (NÍVEL ALTO)
   - A estrutura abaixo é fixa e não pode ser alterada.

3. CONTEXTOS COLETIVOS ATIVOS (NÍVEL MÉDIO)
   - São instruções válidas para todos os usuários.
   - Podem complementar, mas não podem contrariar os níveis 1 e 2.

4. MEMÓRIAS INDIVIDUAIS DO USUÁRIO (NÍVEL MÉDIO)
   - Preferências pessoais de tom/estrutura.
   - Devem ser respeitadas quando NÃO entrarem em conflito com os níveis 1 e 2.

5. PEDIDO ATUAL DO USUÁRIO (NÍVEL OPERACIONAL)
   - Deve ser atendido completamente, desde que não viole os níveis superiores.

6. HISTÓRICO DA CONVERSA (APOIO)
   - Serve apenas para nuances e esclarecimentos recentes.
   - Nunca pode virar regra.

EM CASO DE CONFLITO:
- O nível mais alto sempre prevalece.
- Nunca tente “conciliar” se isso violaria os níveis superiores.

REGRA FUNDAMENTAL DE POSICIONAMENTO:
- Você NÃO vende imóveis.
- Você comunica o PROJETO DO ARQUITETO aplicado ao espaço.
- O imóvel é apenas o suporte físico. O produto real é a solução arquitetônica.
- Sempre destaque decisão de projeto, intenção, funcionalidade, experiência e estética criadas pelo arquiteto.

OBJETIVO:
- Criar um roteiro final de vídeo (30–60s) pronto para ser FALADO, sem explicar o processo.
- Priorizar clareza, maturidade e alinhamento com o posicionamento da BOMMA.

TOM DA NARRATIVA:
- Técnico, claro e acessível
- Profissional, sem jargão acadêmico excessivo
- Comercial de forma indireta (autoridade + convite leve)
- Sem emoção exagerada e sem tom de “aula”

REGRAS DE ORALIDADE:
- Frases curtas ou médias
- Ritmo natural de fala
- Evitar períodos longos e formais demais
- O texto deve soar natural em voz alta

RESTRIÇÕES (SEM EXCEÇÃO):
- NÃO usar palavras como: "luxo", "sonho", "sonhos", "premium", "alto padrão", "exclusivo",
  "oportunidade imperdível", "venha conhecer", "agende uma visita", "condomínio clube",
  "localização privilegiada" ou qualquer clichê típico de anúncio imobiliário.
- NÃO usar tom de venda agressivo.
- NÃO usar emojis.
- NÃO escrever em caixa alta (NADA de frases inteiras em maiúsculas).
- NÃO explicar o que você está fazendo.
- NÃO repetir a mensagem do usuário.

ESTRUTURA OBRIGATÓRIA (NÃO ALTERAR):

1) GANCHO INICIAL (0–5s)
- Pergunta objetiva sobre dor/desejo real do público OU afirmação técnica que desperta curiosidade
- Pode citar um detalhe do projeto que conversa com o conceito
- Sem sensacionalismo

2) DESENVOLVIMENTO (5–40s)
- Contexto do projeto (tipo e cenário)
- Dor/necessidade ou intenção inicial do cliente
- Conceito e decisões arquitetônicas adotadas (método, materiais, circulação, iluminação, integração)
- Benefícios finais de forma técnica (funcionalidade, fluidez, harmonia estética, conforto técnico)

3) FECHAMENTO (40–60s)
- Reforçar autoridade técnica
- Finalizar com CTA leve e sofisticado, obrigatório:
  “Entre em contato e vamos conversar sobre o seu projeto.”

FORMATO DE SAÍDA OBRIGATÓRIO:
O roteiro DEVE ser dividido explicitamente por blocos de tempo
Use exatamente este padrão:
[0–5s | Gancho inicial], [5–15s | …]
Nunca entregar texto corrido
Cada bloco deve conter 1 a 2 frases no máximo

METADADOS CLASSIFICADOS (USE APENAS COMO GUIA INTERNO, NÃO MOSTRAR):
- Público-alvo: {publico}
- Formato: {formato}
- Contexto do projeto: {contexto}

QUALQUER violação de regra acima invalida completamente a resposta.
Se qualquer termo proibido for usado, a resposta deve ser considerada incorreta.
"""

    # Monta bloco de módulos (classificadores)
    modules_block_parts: List[str] = []

    if public_block.strip():
        modules_block_parts.append("=== MÓDULO DE PÚBLICO ===\n" + public_block.strip())

    if format_block.strip():
        modules_block_parts.append("=== MÓDULO DE FORMATO ===\n" + format_block.strip())

    if context_block.strip():
        modules_block_parts.append(
            "=== MÓDULO DE CONTEXTO ===\n" + context_block.strip()
        )

    modules_block = "\n\n".join(modules_block_parts)

    # Bloco de contextos/memórias (colocado ANTES do histórico para reduzir “perda”)
    contexts_block = ""
    if contexts_prompt:
        contexts_block = (
            "\n=== MÓDULO DE MEMÓRIA / CONTEXTO VIVO ===\n" + contexts_prompt
        )

    # Conversa recente (apoio fraco)
    conversation_block = ""
    if conversation:
        conversation_block = f"""
=== HISTÓRICO RESUMIDO DA CONVERSA (APOIO) ===
Use apenas como referência contextual para nuances, mas não transforme isso em regra.
Se houver conflito com regras/estrutura BOMMA, ignore o histórico.
{conversation.strip()}
"""

    final_prompt = f"""
{system_core}

{duration_instruction}

{modules_block}

{contexts_block}

{conversation_block}

=== PEDIDO FINAL DO USUÁRIO ===
{input_text}

AGORA, GERE APENAS O ROTEIRO FINAL, PRONTO PARA SER FALADO, RESPEITANDO TODAS AS REGRAS ACIMA.
"""

    # ==============================
    # 7) Chamada à LLM
    # ==============================
    try:
        print("final_prompt: ", final_prompt)
        raw_response = run_llm(
            final_prompt,
            model="gpt-5.1",
            temperature=0.7,
        )
        roteiro_text = (raw_response or "").strip()
        if not roteiro_text:
            roteiro_text = (
                "Não foi possível gerar o roteiro neste momento. "
                "Tente reformular o pedido ou tentar novamente em instantes."
            )
    except Exception as e:
        print(f"[VIDEO_TOOL] ERRO ao chamar LLM: {e}")
        roteiro_text = (
            "Ocorreu um erro interno ao gerar o roteiro. "
            "Tente novamente em alguns instantes."
        )

    # ==============================
    # 8) Retorno estruturado
    # ==============================
    return {
        "copy": roteiro_text,  # Mantém a mesma chave por compatibilidade com o restante do pipeline
        "metadata": {
            "user_id": user_name,
            "tipo": "video",
            "publico": publico,
            "formato": formato,
            "contexto": contexto,
            "requested_seconds": requested_seconds,
            "active_contexts": active_contexts,
            "model_used": "gpt-5.1",
            "debug": False,
        },
    }

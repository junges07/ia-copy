import json
import re

from ..hooks.llm_hook import run_llm


def classify_intent(message: str) -> str:
    """
    Classifica se o conteúdo solicitado é:
        - 'copy'
        - 'video'

    Retorna sempre UMA string: "copy" ou "video"
    """

    intent_prompt = f"""
    Analise a instrução abaixo e determine o tipo de conteúdo solicitado.

    Mensagem: "{message}"

    Responda apenas com JSON válido no formato:
    {{
        "tipo": "copy" ou "video"
    }}

    Regras:
    - Se o usuário menciona termos como:
      "copy", "legenda", "post", "texto", "anúncio" → tipo = "copy"

    - Se menciona:
      "vídeo", "roteiro", "direcionamento", "gravação", "falas", "reels" → tipo = "video"

    - Se o contexto indicar oralidade:
      "falando", "em vídeo", "no vídeo" → tipo = "video"

    - Caso ambíguo → tipo = "copy"
    """

    result = run_llm(intent_prompt, model="gpt-4o-mini")

    # Tenta extrair JSON
    try:
        match = re.search(r"\{.*\}", result, re.DOTALL)
        json_data = json.loads(match.group(0)) if match else {}
        return json_data.get("tipo", "copy").strip().lower()
    except:
        return "copy"


def get_video_guidelines() -> str:
    """
    Retorna as diretrizes oficiais da BOMMA para criação de ROTEIROS DE VÍDEO.
    Esta função deve ser usada SOMENTE quando o classificador identificar
    que o conteúdo desejado não é copy/legenda, e sim um vídeo.

    O texto deixa claro que:
    - o resultado DEVE ser um roteiro;
    - NÃO pode ser copy, legenda, anúncio ou texto narrativo;
    - deve seguir exatamente a estrutura Bomma.
    """

    return """
====================================================
🎥 INSTRUÇÃO OBRIGATÓRIA — PRODUZIR UM ROTEIRO DE VÍDEO
====================================================
Você **NÃO** deve gerar copy, legenda, descrição, anúncio escrito ou qualquer
tipo de texto corrido. Se este módulo foi ativado, significa que o usuário quer
**um ROTEIRO DE VÍDEO**, seguindo a metodologia oficial da BOMMA.

O roteiro final deve ter **30 a 60 segundos** e obedecer RIGOROSAMENTE a estrutura:

====================================================
1) GANCHOS INICIAIS (0–5s)
====================================================
Objetivo: capturar a atenção de forma técnica, sem sensacionalismo.
Use apenas UMA das abordagens:
- pergunta objetiva sobre dor/necessidade real;
- observação técnica que desperte curiosidade;
- mostrar um detalhe arquitetônico que reflita o conceito;
- contraste antes/depois (de forma contida).

====================================================
2) CORPO / DESENVOLVIMENTO (5–40s)
====================================================
Objetivo: apresentar racional arquitetônico, decisão técnica e solução funcional.

Elementos obrigatórios:
1. contexto do projeto (residencial, comercial, corporativo etc.)
2. dor, problema ou intenção inicial do cliente
3. solução arquitetônica aplicada:
   - método
   - conceito
   - volumetria
   - materiais
   - circulação
   - iluminação
4. benefícios funcionais (NUNCA emocionais):
   - fluidez
   - integração
   - proporções adequadas
   - harmonia
   - conforto técnico
   - experiência de uso do espaço

Evitar totalmente:
❌ “luxo”, “alto padrão”, “transformação de vida”, “sonho”, “exclusivo”
✔ substitua por termos funcionais e técnicos.

====================================================
3) FECHAMENTO (40–60s)
====================================================
Objetivo: reforçar autoridade com naturalidade + CTA leve.
Sugestões aceitas:
- “Se você busca um projeto guiado por intenção e funcionalidade, entre em contato.”
- “Quando cada escolha faz sentido, o resultado fala por si. Vamos conversar sobre o seu projeto?”
- “Entre em contato para avaliarmos a melhor solução para o seu espaço.”

====================================================
ESTILO GERAL DO ROTEIRO
====================================================
- linguagem técnica, clara e objetiva;
- ritmo fluido, profissional, sem exagero emocional;
- sem metáforas, sem poética, sem comercial agressivo;
- frases pensadas para serem faladas em vídeo;
- o texto deve funcionar como leitura em voz alta.

====================================================
IMPORTANTE:
A saída FINAL deve ser **um roteiro completo**, organizado em blocos temporais:
[0–5s]
[5–40s]
[40–60s]

NUNCA entregue copy, legenda, parágrafo corrido ou texto publicitário.
====================================================
"""

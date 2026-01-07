import json
import re

from ..hooks.llm_hook import run_llm


def classify_intent(message: str) -> str:

    intent_prompt = f"""
Você é um classificador de intenção para uma IA de COPYWRITING PARA ARQUITETOS.

Analise a instrução abaixo e determine o tipo de resposta desejada.

Mensagem do usuário:
"{message}"

Você DEVE responder apenas com JSON válido, exatamente no formato:
{{
  "tipo": "copy" ou "video" ou "conversa"
}}

Use rigorosamente as seguintes regras:

========================================
1) CLASSIFICAR COMO "copy" QUANDO:
========================================
Sempre que o usuário:
- Pede para CRIAR uma nova copy.
- Pede para REFAZER uma copy.
- Pede para AJUSTAR uma copy já criada.
- Pede para DIMINUIR, ENCURTAR, AUMENTAR, SIMPLIFICAR ou REESCREVER uma copy.
- Pede para MUDAR TOM, ESTILO, TAMANHO ou INTENSIDADE de uma copy.

Inclui expressões como:
- "faça", "crie", "gere", "escreva", "produza"
- "refine", "ajuste", "melhore", "reescreva"
- "diminua", "encurte", "simplifique"
- "deixa mais direto", "deixa mais técnico", "deixa mais emocional"

⚠️ Importante:
Se a mensagem tiver como objetivo FINAL produzir OU alterar um texto pronto → É "copy".
Frases interrogativas, orientativas ou metalinguísticas sobre copywriting NÃO acionam geração de copy.

Exemplos que DEVEM ser "copy":
- “diminui essa copy”
- “deixa essa legenda mais direta”
- “refaz esse texto”
- “reescreve mantendo a ideia”
- “ajusta o tom dessa copy”
- “melhora esse anúncio”

========================================
2) CLASSIFICAR COMO "video" QUANDO:
========================================
O usuário pede especificamente conteúdo FALADO ou roteiro para gravação:

Exemplos:
- "crie um roteiro de vídeo"
- "me passe as falas para um reels"
- "o que eu falo no vídeo?"
- "direcionamento para vídeo"
- "texto para eu gravar"

========================================
3) CLASSIFICAR COMO "conversa" QUANDO:
========================================
O usuário:
- Está apenas tirando dúvida
- Está dando feedback sem pedir reescrita
- Está explicando regras
- Está configurando comportamento
- Está falando de futuro
- Está pedindo opinião

Exemplos que DEVEM ser "conversa":
- "essa copy ficou boa?"
- "como funciona sua geração de textos?"
- "quero te ensinar meu estilo"
- "sempre que eu pedir tal coisa, faça assim"
- "essa legenda ficou muito formal"

========================================
4) REGRA DE SEGURANÇA MÁXIMA:
========================================
Se houver QUALQUER dúvida entre "copy" e "conversa":

✅ Prefira "copy" somente quando houver intenção clara de ALTERAR ou GERAR um texto.
✅ Caso contrário, use "conversa".

Você deve:
- Responder SOMENTE com JSON
- Nunca explicar a classificação
- Nunca escrever nada fora do JSON
"""

    result = run_llm(intent_prompt, model="gpt-4o-mini")

    # Tenta extrair JSON
    try:
        match = re.search(r"\{.*\}", result, re.DOTALL)
        json_data = json.loads(match.group(0)) if match else {}
        tipo = json_data.get("tipo", "").strip().lower()

        # Normaliza e garante saída válida
        if tipo not in ("copy", "video", "conversa"):
            return "conversa"
        return tipo
    except:
        # Fallback seguro: tratar como conversa normal para não acionar tool por engano
        return "conversa"


def get_video_guidelines() -> str:

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

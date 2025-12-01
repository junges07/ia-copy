# format_classifier.py

import re

"""
Classificador responsável por identificar o FORMATO do conteúdo solicitado:

Possíveis formatos:
- "ads"        → anúncios pagos (Facebook Ads / Instagram Ads / Google Ads)
- "legenda"    → posts orgânicos do Instagram
- "generico"   → caso nenhum formato seja detectado
"""


def classify_format(message: str) -> str:
    """
    Classifica o formato com base em palavras-chave do pedido do usuário.
    """

    msg = message.lower()

    # --- ANÚNCIOS PAGOS ---
    ads_terms = [
        "anúncio",
        "ads",
        "facebook ads",
        "meta ads",
        "google ads",
        "campanha paga",
        "tráfego",
        "gerar cliques",
        "impulsionar",
    ]
    if any(term in msg for term in ads_terms):
        return "ads"

    # --- LEGENDAS DE POST ---
    legenda_terms = ["legenda", "post", "instagram", "feed", "carrossel"]
    if any(term in msg for term in legenda_terms):
        return "legenda"

    # Formato padrão → estilo de anúncio imobiliário curto
    return "generico"


# ========================================================
# MÓDULOS DE PROMPT — devolvem instruções específicas
# ========================================================


def get_format_prompt(fmt: str) -> str:
    """
    Retorna o bloco de prompt do formato adequado.
    """

    if fmt == "ads":
        return """
📌 DIRECIONAMENTO DE FORMATO — ANÚNCIOS PAGOS (Meta / Google)

Estrutura obrigatória:
1. Dor ou desejo do público
2. Solução apresentada pelo imóvel/projeto
3. Benefício direto e perceptível
4. CTA leve e discreto

Instruções de escrita:
- Linguagem racional, fluida e bem estruturada;
- Frases completas, com clareza e propósito;
- Tom profissional, com autoridade implícita;
- Nunca utilize palavras como “luxo”, “alto padrão”, “premium”;
- Demonstre valor de forma sutil, nunca declarada;
- Priorização total de clareza e estratégia acima de emoção;
- Texto contínuo, sem títulos ou divisão visível da estrutura.

O texto deve gerar percepção de valor e incentivar cliques qualificados.
"""

    if fmt == "legenda":
        return """
📌 DIRECIONAMENTO DE FORMATO — LEGENDA DE POST (Instagram)

Características:
- Linguagem narrativa e conceitual;
- Pode explorar bastidores, processo criativo e sensações;
- Redação fluida, estética e suave;

Instruções de escrita:
- Transmita o conceito do projeto sem explicá-lo demais;
- Enfatize luz, proporção, matéria, identidade e olhar autoral;
- Evite palavras clichês como “luxo”, “sonho”, “exclusivo”, “alto padrão”;
- Pode usar pausas leves e ritmo mais sensorial;
- Finalize sempre com um CTA discreto e elegante:
    “Entre em contato e vamos conversar sobre o seu projeto.”

O texto deve ser leve para leitura em redes sociais, com impacto visual.
"""

    # FORMATO GENÉRICO (default)
    return """
📌 DIRECIONAMENTO DE FORMATO — PADRÃO (Copy curta de anúncio imobiliário)

- texto simples, direto e fluido;
- foco no estilo de vida + boas características reais do imóvel;
- sem linguagem técnica ou arquitetônica;
- sem conceitos longos ou profundos;
- sem poesia, sem metáforas, sem dramatização;
- parágrafo único, 3–5 frases;
- CTA leve no final.

Formato ideal para anúncios de imóveis ou copy geral rápida.
"""

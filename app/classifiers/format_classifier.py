# format_classifier.py

import re


def classify_format(message: str) -> str:

    msg = message.lower()

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

    legenda_terms = ["legenda", "post", "instagram", "feed", "carrossel"]
    if any(term in msg for term in legenda_terms):
        return "legenda"

    return "generico"


def get_format_prompt(fmt: str) -> str:

    if fmt == "ads":
        return """
📌 DIRECIONAMENTO DE FORMATO — ANÚNCIOS PAGOS (Meta / Google)

Estrutura obrigatória:
1. Dor, desejo ou aspiração do público
2. Solução apresentada pelo projeto
3. Benefício direto e perceptível
4. CTA leve e discreto

Instruções de escrita:
- Linguagem clara, estratégica e fluida;
- Frases completas e bem estruturadas;
- Tom profissional com autoridade implícita;
- Nunca utilize palavras como “luxo”, “alto padrão”, “premium”;
- Demonstre valor de forma sutil, nunca declarada;
- Priorize clareza, leitura rápida e intenção comercial;
- Texto contínuo, sem títulos ou divisões visíveis.

O texto deve gerar percepção de valor e incentivar cliques qualificados.
"""

    if fmt == "legenda":
        return """
📌 DIRECIONAMENTO DE FORMATO — LEGENDA DE POST (Instagram)

Características:
- Linguagem narrativa e conceitual;
- Pode explorar bastidores, processo criativo e sensações;
- Redação fluida, estética e suave.

Instruções de escrita:
- Transmita o conceito do projeto sem explicá-lo demais;
- Enfatize luz, proporção, matéria, identidade e olhar autoral;
- Evite palavras clichês como “luxo”, “sonho”, “exclusivo”, “alto padrão”;
- Pode usar pausas leves e ritmo mais sensorial;
- Finalize com CTA discreto e elegante.

O texto deve ser leve para leitura em redes sociais, com impacto visual.
"""

    return """
📌 DIRECIONAMENTO DE FORMATO — PADRÃO (Copy geral curta)

- texto simples, direto e fluido;
- foco no estilo de vida e benefícios perceptíveis;
- sem linguagem técnica ou arquitetônica;
- sem conceitos longos ou poéticos;
- parágrafo único, 3–5 frases;
- CTA leve no final.

Formato ideal para respostas rápidas e copys genéricas.
"""

import json, re
from ..hooks.llm_hook import run_llm


def classify_public(message: str) -> str:

    prompt = f"""
    Classifique o público-alvo citado ou sugerido na mensagem abaixo.

    Categorias possíveis:
    - "aa_plus"
    - "aa_ab"
    - "b_bc"
    - "nenhum"

    ➤ Regras:
    - Não invente público.
    - Só classifique se realmente houver indício.
    - "aa_plus" apenas quando houver sinais claros de:
      exclusividade estética, obras autorais, projetos únicos, clientes de patrimônio elevado, arquitetura como arte.
    - "aa_ab" quando houver:
      foco em conforto, estilo de vida, famílias, sofisticação acessível.
    - "b_bc" quando houver:
      preço, economia, reformas, praticidade, custo-benefício, conquista.
    - Se só houver termos genéricos → "nenhum".
    - Se mencionar “classe média”, “AB”, “A”, “alto padrão acessível”, “famílias que buscam conforto” → "aa_ab".
    - Se ambíguo → "nenhum".

    Responda apenas com JSON:
    {{
        "publico": "<categoria>"
    }}

    Mensagem: "{message}"
    """

    result = run_llm(prompt, model="gpt-4o-mini", temperature=0.0)

    try:
        match = re.search(r"\{.*\}", result, re.DOTALL)
        data = json.loads(match.group(0)) if match else {"publico": "nenhum"}
        return str(data.get("publico", "nenhum")).lower()
    except:
        return "nenhum"


def get_public_prompt(public: str) -> str:

    if public is None:
        return ""
    if public == "aa_plus":
        return """
📌 DIRECIONAMENTO POR PÚBLICO — AA+ (Alto Luxo sem nomear)

Tom:
- aspiracional, visual e minimalista;
- linguagem mais artística e madura;
- ritmo lento, pausado, elegante.

Foco:
- conceito, intenção, autoria, tempo;
- proporção, harmonia, materialidade, luz;
- sutileza como símbolo de sofisticação.

Evitar:
- qualquer termo comercial;
- qualquer termo de luxo explícito;
- comparações (“mais”, “melhor”);
- explicações óbvias do valor.

Instruções especiais:
- pareça contemplativo, não descritivo;
- escreva como se estivesse analisando uma obra artística;
- eleve o tom sem soar distante ou exagerado.

================================================================
EXEMPLO:

prompt: "Crie uma copy para anúncio no Instagram voltado a público AA+,
apresentando um projeto residencial. Use linguagem aspiracional,
valorizando o conceito e a assinatura do arquiteto, sem mencionar
palavras como ‘luxo’ ou ‘alto padrão’"

copy correspondente: "Cada traço carrega intenção. Cada escolha revela uma forma de ver o
mundo."

================================================================
"""
    if public == "aa_ab":
        return """
📌 DIRECIONAMENTO POR PÚBLICO — AA / AB (Classe Alta)

Tom:
- sofisticado mas acolhedor;
- linguagem madura, polida e equilibrada.

Foco:
- design contemporâneo com conforto;
- estilo de vida, bem-estar, elegância discreta;
- integração entre estética e funcionalidade.

Evitar:
- exageros poéticos;
- tecnicismos aprofundados;
- qualquer termo elitista explícito.

Instruções especiais:
- destaque conforto + estética como um conjunto coerente;
- mantenha o texto acessível, porém refinado;
- enfoque na experiência de viver o espaço.

Restrições Explícitas: 
- evite descrições imobiliárias (“bairro vibrante”, “comodidades”, “venha conhecer”);
- mantenha o foco no projeto, não na venda;
================================================================
EXEMPLO:

prompt: "Crie uma legenda para Instagram voltada a público AB, destacando a
integração entre estética e funcionalidade em um projeto de interiores."

copy correspondente: "Arquitetura que traduz o seu estilo de vida. Design, conforto e elegância
em perfeita sintonia"

================================================================
"""

    if public == "b_bc":
        return """
📌 DIRECIONAMENTO POR PÚBLICO — B / BC (Médio-Alto / Médio)

Tom:
- inspirador, amigável e acessível;
- emocional na medida certa.

Foco:
- conquista, pertencimento e praticidade;
- “arquitetura possível”, próxima, atingível;
- beleza simples e funcional.

Evitar:
- termos elitistas;
- tecnicismos avançados;
- linguagem distante ou altamente conceitual.

Instruções especiais:
- mostre que o espaço é viável, real e próximo da vida cotidiana;
- soe acolhedor, motivador e humano;
- mantenha o texto leve, direto e com energia positiva.

================================================================
EXEMPLO:

prompt: "Crie uma copy de anúncio para público BC que deseja reformar o
apartamento. Use uma linguagem próxima e inspiradora, mostrando que
arquitetura é para todos."

copy correspondente: "Seu lar pode ser bonito, funcional e do seu jeito. Um projeto pensado
para o seu dia a dia, sem abrir mão da estética"

================================================================
"""

    return ""

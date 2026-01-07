# copy_readiness_classifier.py

from typing import Dict, List, Optional
from ..hooks.llm_hook import run_llm


def classify_copy_readiness(
    input_text: str,
    public: Optional[str],
    fmt: Optional[str],
    context: Optional[str],
) -> Dict[str, object]:
    """
    Determina se a IA já possui informações suficientes para gerar uma copy de alto nível.
    Caso contrário, retorna exatamente quais informações estão faltando.
    """

    missing: List[str] = []

    text = input_text.lower()

    # -------------------------------
    # REGRAS MÍNIMAS UNIVERSAIS
    # -------------------------------

    if not context:
        missing.append("tipo_do_imovel")

    if not public or public == "nenhum":
        missing.append("publico_alvo")

    # -------------------------------
    # REGRAS POR FORMATO
    # -------------------------------

    if fmt == "ads":
        # Para anúncios, sempre exigir localização ou pelo menos cidade
        if not any(
            x in text
            for x in ["centro", "bairro", "cidade", "zona", "praia", "condomínio"]
        ):
            missing.append("localizacao")

    # -------------------------------
    # REGRAS POR CONTEXTO
    # -------------------------------

    if context in ["apartamento", "studio", "cobertura"]:
        if not any(x in text for x in ["quarto", "suíte", "m²", "metros", "metragem"]):
            missing.append("metragem_ou_numero_de_quartos")

    if context in ["residencia", "casa_praia", "casa_campo"]:
        if not any(x in text for x in ["quartos", "suítes", "terreno", "área"]):
            missing.append("configuracao_da_casa")

    if context == "comercial":
        if not any(
            x in text for x in ["negócio", "empresa", "vendas", "atendimento", "fluxo"]
        ):
            missing.append("finalidade_do_imovel")

    # -------------------------------
    # REGRAS DE INTENÇÃO
    # -------------------------------

    if not any(
        x in text
        for x in ["venda", "aluguel", "lançamento", "anúncio", "post", "legenda"]
    ):
        missing.append("objetivo_da_copy")

    # -------------------------------
    # RESULTADO FINAL
    # -------------------------------

    ready = len(missing) == 0

    return {"ready": ready, "missing": missing}


def build_missing_questions(missing: List[str], input_text: str) -> str:
    if not missing:
        return ""
    prompt = f"""
    Você é um estrategista de briefing para copywriting imobiliário.
    
    O usuário fez o seguinte pedido:
    "{input_text}"
    
    Faltam as seguintes informações para criar uma copy perfeita:
    {missing}
    
    Sua tarefa é formular PERGUNTAS NATURAIS, HUMANAS E PROFISSIONAIS
    para coletar exatamente essas informações que estão faltando.
    
    Regras:
    - Não repita os nomes técnicos.
    - Não seja robótico.
    - Seja direto, educado e objetivo.
    - Liste em formato de perguntas.
    - Não invente novas necessidades além das fornecidas.
    
    Retorne apenas o texto final das perguntas.
        """

    result = run_llm(prompt, model="gpt-4o-mini")
    return result.strip()

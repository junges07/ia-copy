import json, re
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ..routes.request_models import UserRequest
from ..hooks.llm_hook import run_llm
from ..hooks.embedding_hook import get_embedding, is_duplicate_embedding
from ..hooks.supabase_hook import insert_team_memory, get_team_memory   
from ..hooks.llm_hook import run_llm, create_conversational_chain

print("✅ copy_routes carregando...")

router = APIRouter()

CONVERSATIONS = {}

@router.options("/generate_copy")
async def options_generate_copy():
    return JSONResponse(
        content={}, status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )

@router.post("/generate_copy")
async def classify_embedding(request: UserRequest):
    message = request.data
    print(message)
    prompt = f"""
        Você é um assistente especializado em marketing digital e análise de preferências de comunicação.

        Sua tarefa é analisar mensagens enviadas por usuários e decidir quais partes contêm informações
        importantes que devem ser armazenadas no banco de dados de preferências da equipe de
        gestores de tráfego e marketing.

        ⚡ O que deve ser considerado relevante para salvar:
        - Informações que descrevem a **identidade da empresa** (ex: "é uma cervejaria artesanal", "atua no setor agro", "é uma imobiliária de alto padrão").
        - Informações sobre **segmento, nicho de mercado, público-alvo ou tom de comunicação da marca** (ex: "atua no mercado B2B", "usa linguagem formal").
        - Informações que definem **estilo ou diretrizes de comunicação permanentes**.

        ❌ O que NÃO deve ser salvo:
        - Instruções temporárias sobre um único post ou campanha (ex: "faça uma copy sobre a IPA", "crie uma legenda curta").
        - Dores, soluções e CTAs específicos de um briefing único.

        ⚠️ Importante:
        - Mesmo que a mensagem peça uma copy para um post, se houver junto informações sobre a identidade da empresa, salve apenas essas informações permanentes.
        - Ignore os detalhes transitórios do post.

        🧩 Regras obrigatórias de resposta:
        - Sempre responda com **um único JSON válido**.
        - O campo "relevante" deve ser "coletivo" se a informação for permanente, ou false se não for.
        - O campo "empresa" deve sempre existir (ex: "serrana", "impulse", "cliente", "coletivo").
        - O campo "informacao" deve conter a diretriz ou estar vazio ("").

        📘 Exemplo 1 (mensagem relevante):
        {{
        "relevante": "coletivo",
        "empresa": "serrana",
        "informacao": "usa letras minúsculas nas legendas"
        }}

        📘 Exemplo 2 (mensagem não relevante):
        {{
        "relevante": false,
        "empresa": "serrana",
        "informacao": ""
        }}

        Mensagem do usuário:
        {message}
        """



    result = run_llm(prompt, model="gpt-4.1-mini")

    try:
        match = re.search(r"\{.*\}", result, re.DOTALL)
        if not match:
            return {"copy": f"Erro: IA não retornou JSON. {result}"}
        jsonresponse = json.loads(match.group(0))
    except Exception as e:
        return {"copy": f"Erro ao interpretar resposta: {str(e)}"}

    reference = jsonresponse.get("empresa", "").strip().lower()
    relevance = jsonresponse.get("relevante")

    
    if reference not in CONVERSATIONS:
        CONVERSATIONS[reference] = create_conversational_chain(model="gpt-4o-mini", memory_limit=5)
    conversation = CONVERSATIONS[reference]

    if relevance == "coletivo":
        content = jsonresponse.get("informacao")
        embedding = get_embedding(content)
        existing = get_team_memory(reference)

        if not is_duplicate_embedding(embedding, [i["embedding"] for i in existing.data]):
            insert_team_memory(reference, content, embedding)

    bdcontent = get_team_memory(reference)
    res = [item["content"] for item in bdcontent.data] if bdcontent.data else []

    copy_prompt = f"""
    Briefing recebido:
    {message}

    Brifing da Empresa (pode não ter):
    {res}

    🎯 Objetivo Principal
    Criar textos para arte e legendas de anúncios no Instagram que incentivem leads B2B a clicar, cadastrar-se, baixar catálogos ou contatar especialistas. Sempre priorize a captação de leads qualificados (lojistas ou decisores com CNPJ).

    ✍️ Metodologia Impulse (Framework Obrigatório)
    Estrutura o anúncio em 4 etapas sequenciais. Pense passo a passo ao aplicar:
    1. **Identificação do Público**: Comece com uma chamada que identifique o setor e, se aplicável, a localização.
    - Geolocalizado: "Setor + Localização" (ex: "Atenção lojista de Curitiba...").
    - Nacional/amplo: Apenas o setor (ex: "Atenção lojista de cama, mesa e banho...").
    - Verifique no briefing: Se a localização não for especificada, assuma nacional e pergunte para confirmação se necessário.

    2. **Agito da Dor ou Desejo**: Crie identificação imediata com um problema ou oportunidade latente do público B2B. Foque em dores reais como baixo giro de estoque, falta de variedade, ausência de novidades, ou demandas por qualidade, agilidade e personalização. Mantenha curto e impactante para gerar urgência sem drama.
    3. **Apresentação da Solução ou Desejo**: Posicione a marca/produto como solução direta, destacando diferenciais B2B como condições comerciais especiais, qualidade superior, produção nacional, exclusividade para CNPJ, ou prazos de entrega. Enfatize benefícios mensuráveis (ex: custo-benefício, exclusividade).
    4. **CTA (Chamada para Ação)**: Finalize com uma ação clara e acionável, como "Cadastre-se e receba o catálogo exclusivo para lojistas", "Baixe agora o catálogo 2025" ou "Fale com um especialista e garanta sua condição". O CTA deve impulsionar o clique imediato.

    🧾 Estrutura da Entrega
    Sempre responda com exatamente três blocos separados e rotulados:
    - **Texto da Arte**: Curto, objetivo e de alto impacto visual (ideal para imagem do anúncio, 5-10 linhas no máximo). Use maiúsculas para ênfase se necessário.
    - **Legenda (Texto do Post)**: Mais explicativa, reforçando a proposta de valor, conexão com o lojista e o CTA (100-200 caracteres). Inclua menção a exclusividade para CNPJ no final, se relevante.

    ⚠️ Regras Rígidas (Não Violem)
    - Nunca use emojis, gírias, linguagem informal ou emotiva (ex: evite "fature alto" se soar exagerado; opte por "aumente suas vendas").
    - Adapte estritamente ao briefing: Identifique setor, localização, dores, soluções e CTA sugeridos. Se o briefing faltar detalhes (ex: localização), assuma defaults (nacional) e sugira ajustes na resposta.
    - Foco 100% em B2B: Mencione CNPJ sempre que possível para qualificar leads.
    - Verifique consistência: Após criar, revise mentalmente se segue o framework Impulse e as regras. Se o briefing for vago, peça esclarecimentos antes de gerar.

    🧠 Processo de Raciocínio para Cada Briefing
    Ao receber um briefing:
    1. Analise: Identifique setor, localização (geolocalizado ou amplo), dores/desejos, solução da marca e CTA desejado.
    2. Planeje: Mapeie o framework Impulse ao briefing.
    3. Crie: Gere arte e legenda separadas.
    4. Refine: Garanta persuasão, clareza e alinhamento B2B.
    5. Entregue: Apenas os dois blocos, sem texto extra a menos que pedido.
    """

    print(f"📜 Tamanho do prompt: {len(copy_prompt)} caracteres")

    try:
        response = conversation.invoke({"input": copy_prompt})
        copy = response["response"] if isinstance(response, dict) and "response" in response else str(response)
    except Exception as e:
        print("❌ Erro ao gerar copy:", e)
        return {"copy": f"Erro ao gerar copy: {str(e)}"}

    print(f"🧠 Memória atual ({reference}): {conversation.memory.buffer}")
    return {"copy": copy}

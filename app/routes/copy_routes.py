import json, re
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ..routes.request_models import UserRequest
from ..hooks.llm_hook import run_llm
from ..hooks.embedding_hook import get_embedding, is_duplicate_embedding
from ..hooks.supabase_hook import insert_team_memory, get_team_memory, insert_individual_memory, get_individual_memory
from ..hooks.llm_hook import run_llm, create_conversational_chain 
import uuid  

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
    lovable_user_name = request.user.strip().lower()
    print(message)
    prompt = """

        Você é um analisador semântico especializado em identificar **informações úteis, permanentes e inferíveis sobre empresas, marcas e clientes**.
        Sua tarefa é analisar mensagens de usuários e extrair **qualquer dado que revele o que uma marca é, faz, vende, oferece, comunica ou prefere** — mesmo quando isso estiver implícito em pedidos operacionais (“faça uma copy...”, “crie um post sobre...”).
        ---

        ### 🎯 OBJETIVO

        Registrar qualquer informação **coletiva** que descreva ou implique:

        - o que a empresa **é** (“é uma pastelaria”)
        - o que ela **faz ou oferece** (“atua com tráfego pago”, “vende roupas femininas”)
        - seu **segmento, público ou nicho**
        - seu **tom de voz, linguagem, estilo ou estética**
        - suas **preferências ou padrões de comunicação**
        - ou **associações contextuais** que indiquem área de atuação, mesmo sem descrição direta  
        → ex: “faça um post para a Exemplo X sobre tráfego pago” → a Exemplo X  trabalha com tráfego pago.

        ---

        ### ⚙️ PRINCÍPIO DE INFERÊNCIA E DETECÇÃO DE EMPRESAS

       > Sempre que houver uma empresa, marca ou cliente mencionado **em conjunto com um tema, produto ou tipo de conteúdo**, infira que **essa empresa tem relação com aquele tema**.

        Exemplo:
        - “faça um post para a Empresa X sobre pastéis” → “a Empresa X vende pastéis”
        - “faça uma copy para a Empresa X sobre tráfego pago” → “a Empresa X trabalha com tráfego pago”
        - “gera uma copy para a Empresa Xsobre moda feminina” → “a Empresa X atua com moda feminina” 

        ---

        ### ⚠️ REGRAS DE RELEVÂNCIA

        Considere como **relevante** (salvar):
        - toda frase que revele ou **implique** informações sobre o negócio, produto, setor, tom ou estilo da marca.
        - frases em que uma **ação** (ex: “faça um post...”) está **ligada a um tema específico** (ex: “tráfego pago”, “pastéis”, “moda feminina”), indicando **campo de atuação da empresa**.

        Considere como **falso (não salvar)**:
        - instruções puramente operacionais ou pessoais (“envie a copy”, “não quero arte”, “use mais texto”)
        - mensagens sem referência a empresa, marca ou tema de negócio

        ---

        ### 🧩 FORMATO DE SAÍDA

        Responda **apenas com JSON válido**, no formato:

        ```json
        {
        "relevante": "coletivo" ou false,
        "empresa": "<nome da marca ou 'coletivo'>",
        "informacao": "<texto breve descrevendo o que foi inferido>"
        }

        ### 📘 EXEMPLOS

        **Exemplo 1 — Informação direta:**
        faça uma copy para a Empresa X, ela é uma pastelaria artesanal
        {
        "relevante": "coletivo",
        "empresa": "Empresa X",
        "informacao": "a Empresa X é uma pastelaria"
        }

        **Exemplo 2 — Informação mista (pedido + dado de estilo):**
        faça uma copay para a Empresa X, ela gosta de legendas mais simples
        {
        "relevante": "coletivo",
        "empresa": "Empresa X",
        "informacao": "a Empresa X gosta de legendas mais simples"
        }

        **Exemplo 3 — Estilo de linguagem:**
        a  Empresa X gosta de legendas simples
        {
        "relevante": "coletivo",
        "empresa": " Empresa X",
        "informacao": " Empresa X gosta de legendas simples"
        }

        **Exemplo 4 — Irrelevante (pedido sem contexto):**
        faça uma copy agora
        {
        "relevante": false,
        "empresa": "Empresa X",
        "informacao": ""
        }

        **Exemplo 5 — Implícito (com inferência)::**
        faça um post para a  Empresa X sobre estratégias de tráfego pago
        {
        "relevante": "coletivo" ,
        "empresa": " Empresa X",
        "informacao": " Empresa X faz estratégias de tráfego pago"
        }

        Mensagem do usuário:
                """ + message

    verification_prompt = """

        Você é um **classificador lógico** responsável por identificar **preferências pessoais permanentes** de um usuário.
        Seu trabalho é **analisar a mensagem recebida** e decidir **objetivamente** se ela contém uma instrução ou preferência **individual e persistente** — ou se é apenas um pedido operacional genérico.

        Você **NÃO deve gerar interpretações criativas**.  
        Você **NÃO deve inventar informações**.  
        Você **DEVE responder apenas com JSON válido, sem texto adicional**.

        ---

       ## 🎯 OBJETIVO
        Detectar **qualquer instrução, ajuste ou preferência pessoal** que mude o comportamento do sistema,
        mesmo que não mencione explicitamente "eu" ou "meu estilo".

        Exemplos típicos:
        - “Não me envie mais o texto da arte, apenas a legenda.”
        - “Quero legendas mais curtas.”
        - “Prefiro legendas com humor.”
        - “Sou designer e quero textos de arte mais visuais.”
        - “Pode tirar o CTA das próximas copies.”
        - “Sempre me envie 3 variações.”

        ---

        ### 🧩 CLASSIFICAÇÃO

        Responda com **um único JSON válido** contendo os seguintes campos:

        ```json
        {
        "relevante": "individual" ou false,
        "informacao": "<descrição clara e curta da preferência ou instrução pessoal>"
        }

        ⚙️ REGRAS DE DECISÃO

        -Considere como relevante (individual):
        -Instruções que alteram o comportamento do sistema apenas para esse usuário
        -Preferências de estilo, formato, conteúdo ou linguagem pessoal
        -Frases iniciadas com verbos de ação: “quero”, “prefiro”, “não me envie”, “gosto”, “faça de outro jeito”, “mude para...”
        -Mensagens que expressam identidade funcional (“sou designer”, “sou gestor”, “sou copywriter”)
        -Considere como falso (não relevante):
        -Pedidos genéricos que poderiam ser feitos por qualquer um (“faça uma copy sobre o produto X”)
        -Instruções que dizem respeito ao cliente, empresa ou público (devem ir para a LLM coletiva)

        ### 🧠 EXEMPLOS

        ##Exemplo 01 - Instrução pessoal clara:
        não me envie mais o texto da arte, apenas a legenda
        {
            "relevante": "individual",
            "informacao": "o usuário quer receber apenas a legenda, sem o texto da arte"
        }

        ##Exemplo 02 - Preferência de estilo:
        sou designer e quero um texto da arte mais aprofundado
       {
            "relevante": "individual",
            "informacao": "o usuário é designer e quer textos de arte mais detalhados e visuais"
        }
        
        ##Exemplo 03 - Instrução temporária, não relevante:
        faça uma copy sobre o catálogo novo da Empresa X
       {
            "relevante": false,
            "informacao": ""
        }
        
        ##Exemplo 04 - Mistura (mas foco pessoal):
        a Impulse quer continuar com o mesmo estilo, e eu quero legendas mais curtas
      {
        "relevante": "individual",
        "informacao": "o usuário prefere legendas mais curtas"
        }
    """ + message
 
    result = run_llm(prompt, model="gpt-4o-mini")
    verification_result = run_llm(verification_prompt, model="gpt-4o-mini")


    try:
        match_main = re.search(r"\{.*\}", result, re.DOTALL)
        if match_main:
            json_main = json.loads(match_main.group(0))
            empresa_detectada = json_main.get("empresa", "").strip()
            print("🧩 IA_COLETIVA → Empresa detectada:", 
                f"'{empresa_detectada}'" if empresa_detectada else "❌ Nenhuma empresa identificada")
        else:
            print("❌ IA_COLETIVA → Nenhum JSON encontrado na resposta.")
    except Exception as e:
        print("❌ IA_COLETIVA → Erro ao decodificar JSON:", e)
        print("Resposta bruta:", result)

    try: 
        match_verif = re.search(r"\{.*\}", verification_result, re.DOTALL) 
        if not match_verif: json_verif = {"verificacao": "erro", "detalhes": verification_result} 
        else: json_verif = json.loads(match_verif.group(0)) 
    except Exception: 
        json_verif = {"verificacao": "erro", "detalhes": verification_result} 

    collective_reference = json_main.get("empresa", "").strip().lower()
    print(collective_reference)
    individual_reference = lovable_user_name.strip().lower()
    conversation_key = f"{collective_reference or 'coletivo'}::{lovable_user_name}"

    if conversation_key not in CONVERSATIONS:
        CONVERSATIONS[conversation_key] = create_conversational_chain(
        model="gpt-4o",
        memory_limit=5
    )
    conversation = CONVERSATIONS[conversation_key]

    if json_main.get("relevante") == "coletivo":
        content = (json_main.get("informacao") or "").strip()
        if content:
            embedding = get_embedding(content)
            existing = get_team_memory(collective_reference)
            if not is_duplicate_embedding(embedding, [i["embedding"] for i in (existing.data or [])]):
                insert_team_memory(collective_reference, content, embedding)


    if json_verif.get("relevante") == "individual":
        content = (json_verif.get("informacao") or "").strip()
        print("content")
        if content:
            embedding = get_embedding(content)
            existing = get_individual_memory(individual_reference)
            if not is_duplicate_embedding(embedding, [i["embedding"] for i in (existing.data or [])]):
                insert_individual_memory(individual_reference, content, embedding)

    print(f"[DBG] Reference normalizada: '{collective_reference}'")
    bdcontent = get_team_memory(collective_reference)
    print(f"[DBG] Conteúdo retornado: {bdcontent.data if bdcontent and bdcontent.data else 'vazio'}")
    if bdcontent and bdcontent.data:
        res = "\n".join([f"- {item['content']}" for item in bdcontent.data])
    else:
        res = "Nenhuma diretriz coletiva registrada ainda."

    usercontent = get_individual_memory(individual_reference)
    if usercontent and usercontent.data:
        user_res = "\n".join([f"- {item['content']}" for item in usercontent.data])
    else:
        user_res = "Nenhuma preferência individual registrada ainda."


    copy_prompt = f"""
    Briefing recebido:
    {message}

    Brifing da Empresa, contém diretrizes fixas sobre identidade, tom e estilo da marca:  (pode não ter):
    {res}

    Briefing Individual contém preferências pessoais permanentes do user {lovable_user_name}, pode não ter nenhuma):
    {user_res}

    ### ⚙️ PRIORIDADE DE INTERPRETAÇÃO
    Siga esta ordem **SEM exceções**:
    1. As instruções do **Briefing Individual** têm prioridade máxima.  
    → Se o usuário definiu que quer apenas legenda, siga isso mesmo que o Framework peça arte.  
    → Se o usuário pediu “textos de arte mais visuais”, siga mesmo que o modelo coletivo não mencione isso.
    2. O **Briefing Coletivo** vem logo em seguida.  
    → Ele define a identidade, linguagem e estilo da marca.  
    → Nunca contradiga suas diretrizes (ex: se a empresa usa letras minúsculas, nunca use maiúsculas).
    3. O **Framework Impulse** é aplicado apenas **após** respeitar as duas camadas anteriores.

    Se houver conflito entre eles, siga a hierarquia:
    **Individual > Coletivo > Framework.**

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

    ✅ Exemplos de Referência (Use como Modelos)

    ##Exemplo 1 — Fábrica de Cama e Banho (Nacional)
    Texto da Arte:
    Somente CNPJ
    ATENÇÃO LOJISTA!
    Conheça a Nova Coleção 2025 da La Dotta!
    Cadastre-se e receba nosso novo catálogo!

    Legenda:
    ATENÇÃO LOJISTA!
    Conheça a Coleção La Dotta 2025 e aumente suas vendas com nossos produtos.
    Somos uma marca brasileira com fabricação própria, excelente custo-benefício e qualidade em cada item.
    Clique abaixo e cadastre-se para receber o catálogo.
    EXCLUSIVO PARA LOJISTAS COM CNPJ.

    ##Exemplo 2 — Uniformes Personalizados em Tricot (Geolocalizado: Serra Gaúcha)
    Texto da Arte:
    Uniformes empresariais personalizados
    SUÉTER
    Sua logo aqui
    Variedade de cores
    Qualidade da Serra Gaúcha
    Sem pedido mínimo
    Entrega em 30 dias
    Cadastre-se e receba mais informações.

    Legenda:
    Uniformes em suéter personalizados com a sua logo.
    Uma opção versátil e confortável que transmite profissionalismo e eleva a imagem da sua empresa.
    A Don Carli está no mercado há 20 anos e fica localizada na cidade de Farroupilha-RS.
    Nossa fábrica oferece uma ampla gama de produtos, incluindo uniformes corporativos de alta qualidade.
    Cadastre-se para receber o atendimento de um de nossos especialistas.
    EXCLUSIVO PARA EMPRESAS COM CNPJ.

    ##Exemplo Adicional — Decoração para Lojistas (Nacional, Foco em Dor de Variedade)
    Texto da Arte:
    ATENÇÃO LOJISTA DE DECORAÇÃO!
    Atualize seu mix com itens exclusivos da DecoMax.
    Qualidade premium e condições especiais.
    Baixe o catálogo 2025 agora!

    Legenda:

    ATENÇÃO LOJISTA DE DECORAÇÃO!
    Se o seu estoque precisa de mais variedade e itens de alta qualidade, a DecoMax é a solução ideal.
    Com produção nacional e opções personalizadas, oferecemos condições comerciais atrativas para lojistas.
    Baixe o catálogo 2025 e descubra como elevar suas vendas.
    EXCLUSIVO PARA LOJISTAS COM CNPJ.
    """

    try:
        response = conversation.invoke({"input": copy_prompt})
        copy = response["response"] if isinstance(response, dict) and "response" in response else str(response)
    except Exception as e:
        print("❌ Erro ao gerar copy:", e)
        return {"copy": f"Erro ao gerar copy: {str(e)}"}
    
    return {"copy": copy}

import json, re

from fastapi import APIRouter

from fastapi.responses import JSONResponse

from .request_models import UserRequest

from ..hooks.llm_hook import run_llm

from ..hooks.embedding_hook import get_embedding, is_duplicate_embedding

from ..hooks.supabase_hook import insert_team_memory, get_team_memory, insert_individual_memory, get_individual_memory

from ..hooks.llm_hook import run_llm, create_conversational_chain 

from ..hooks.prompt_templates import generate_prompt_copy_impulse, generate_prompt_video_impulse

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
    
    global CONVERSATIONS
    session_id = request.session_id

    last_company = CONVERSATIONS.get(session_id, {}).get("last_company")

    message = request.data

    lovable_user_name = request.user.strip().lower()

    intent_prompt = f"""
    Analise a instrução abaixo e determine o tipo de conteúdo solicitado.

    Mensagem: "{message}"

    Responda apenas com JSON válido no formato:
    {{
      "tipo": "copy" ou "video"
    }}

    Regras:
    - Se o usuário menciona "copy", "legenda", "post", "texto", "anúncio" → tipo = "copy"
    - Se menciona "vídeo", "roteiro", "direcionamento", "gravação", "falas", "reels" → tipo = "video"
    - Se o contexto indicar fala ou oralidade ("falando", "em vídeo") → tipo = "video"
    - Caso ambíguo → tipo = "copy"
    """

    intent_result = run_llm(intent_prompt, model="gpt-4o-mini")
    
    try:
        match_intent = re.search(r"\{.*\}", intent_result, re.DOTALL)
        if match_intent:
            json_intent = json.loads(match_intent.group(0))
            tipo_conteudo = json_intent.get("tipo", "copy").strip().lower()
        else:
            tipo_conteudo = "copy"
    except Exception as e:
        print("❌ Erro ao decodificar intenção:", e)
        tipo_conteudo = "copy"

    print(f"🧠 Tipo de conteúdo identificado: {tipo_conteudo}")

    prompt = """

  

        Você é um analisador semântico especializado em identificar **informações úteis, permanentes e inferíveis sobre empresas, marcas e clientes**.

        Sua tarefa é analisar mensagens de usuários e extrair **qualquer dado que revele o que uma marca é, faz, vende, oferece, comunica ou prefere** — mesmo quando isso estiver implícito em pedidos operacionais (“faça uma copy...”, “crie um post sobre...”).

        ---



        ### OBJETIVO



        Registrar qualquer informação **coletiva** que descreva ou implique:



        - o que a empresa **é** (“é uma pastelaria”)

        - o que ela **faz ou oferece** (“atua com tráfego pago”, “vende roupas femininas”)

        - seu **segmento, público ou nicho**

        - seu **tom de voz, linguagem, estilo ou estética**

        - suas **preferências ou padrões de comunicação**

        - ou **associações contextuais** que indiquem área de atuação, mesmo sem descrição direta  

        → ex: “faça um post para a Exemplo X sobre tráfego pago” → a Exemplo X  trabalha com tráfego pago.



        ---

        ### RESTRIÇÃO CRÍTICA





Nunca trate palavras como “cliente”, “pessoa”, “usuário”, “perfil”, “seguidores”, “público”, “consumidor” ou “comprador” como empresas.  

Esses termos representam **entidades genéricas ou individuais**, não marcas ou negócios.



Portanto:

- “faça uma copy para um cliente sobre moda” → **irrelevante**

- “faça uma copy para a Loja X sobre moda” → **relevante**



Somente nomes próprios, marcas, empresas, negócios, lojas ou instituições devem ser reconhecidos como `empresa`.





        ### PRINCÍPIO DE INFERÊNCIA E DETECÇÃO DE EMPRESAS



       > Sempre que houver uma empresa, marca ou cliente mencionado **em conjunto com um tema, produto ou tipo de conteúdo**, infira que **essa empresa tem relação com aquele tema**.

        Exemplo:

        - “faça um post para a <empresa passada pelo cliente> sobre pastéis” → “a <empresa passada pelo cliente> vende pastéis”

        - “faça uma copy para a <empresa passada pelo cliente> sobre tráfego pago” → “a <empresa passada pelo cliente> trabalha com tráfego pago”

        - “gera uma copy para a <empresa passada pelo cliente>sobre moda feminina” → “a <empresa passada pelo cliente> atua com moda feminina” 

        ---
        ### REGRAS DE RELEVÂNCIA

        Considere como **relevante** (salvar):

        - toda frase que revele ou **implique** informações sobre o negócio, produto, setor, tom ou estilo da marca.

        - frases em que uma **ação** (ex: “faça um post...”) está **ligada a um tema específico** (ex: “tráfego pago”, “pastéis”, “moda feminina”), indicando **campo de atuação da empresa**.

        - Frases que expressem o que **não deve** ser usado ou dito em comunicações da empresa,

  pois indicam **preferências de linguagem, estilo ou posicionamento**.



        Considere como **falso (não salvar)**:

        - Ordens que afetam apenas o individual e não empresas.

        - mensagens sem referência a empresa, marca ou tema de negócio


        ### CONTEXTO E REFERÊNCIAS IMPLÍCITAS

        - Quando o usuário usar pronomes (“ela”, “a empresa”, “a marca”, “essa empresa”, “a mesma”) sem citar o nome da marca,
          assuma que ele está se referindo **à última empresa ou marca mencionada na conversa**.

        - Se ainda não houver nenhuma empresa mencionada anteriormente na sessão, ignore a inferência
          (relevante = false).

        - Se houver uma empresa conhecida anteriormente, use o nome dessa empresa no campo "empresa"
          e descreva normalmente o conteúdo da frase.

        **Exemplo:**
        Usuário: "faça uma copy da Mayssons"
        Usuário: "ela prefere que use 'país tropical' em vez de 'Brasil'"

        {
          "relevante": "coletivo",
          "empresa": "Mayssons",
          "informacao": "a Mayssons prefere usar 'país tropical' em vez de 'Brasil'"
        }


        ### FORMATO DE SAÍDA
        
        IMPORTANTE: nunca escreva literalmente "<empresa passada pelo cliente>" no campo "empresa".
        Sempre substitua pelo nome real da empresa mencionado na mensagem ou, se estiver retomando o contexto, pelo mesmo nome usado anteriormente.

        Responda **apenas com JSON válido**, no formato:

        ```json

        {

        "relevante": "coletivo" ou false,

        "empresa": "<nome da marca>",

        "informacao": "<texto breve descrevendo o que foi inferido>"

        }



        ### EXEMPLOS



        **Exemplo 1 — Informação direta:**

        faça uma copy para a <empresa passada pelo cliente>, ela é uma pastelaria artesanal

        {

        "relevante": "coletivo",

        "empresa": "<empresa passada pelo cliente>",

        "informacao": "a <empresa passada pelo cliente> é uma pastelaria"

        }



        **Exemplo 2 — Informação mista (pedido + dado de estilo):**

        faça uma copay para a <empresa passada pelo cliente>, ela gosta de legendas mais simples

        {

        "relevante": "coletivo",

        "empresa": "<empresa passada pelo cliente>",

        "informacao": "a <empresa passada pelo cliente> gosta de legendas mais simples"

        }



        **Exemplo 3 — Estilo de linguagem:**

        a  <empresa passada pelo cliente> gosta de legendas simples

        {

        "relevante": "coletivo",

        "empresa": " <empresa passada pelo cliente>",

        "informacao": " <empresa passada pelo cliente> gosta de legendas simples"

        }



        **Exemplo 4 — Irrelevante (pedido sem contexto):**

        faça uma copy agora

        {

        "relevante": false,

        "empresa": "<empresa passada pelo cliente>",

        "informacao": ""

        }



        **Exemplo 5 — Implícito (com inferência)::**

        faça um post para a  <empresa passada pelo cliente> sobre estratégias de tráfego pago

        {

        "relevante": "coletivo" ,

        "empresa": " <empresa passada pelo cliente>",

        "informacao": " <empresa passada pelo cliente> faz estratégias de tráfego pago"

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



       ## OBJETIVO

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

      ### REGRAS DE EXCLUSÃO



        **Nunca classifique como “individual” se:**

          - houver menção a **empresa, marca, cliente, loja, negócio ou instituição**;

          - o contexto indicar que a preferência se refere a **conteúdo de uma marca ou cliente** (ex: “a Ceres quer que...”, “para a Impulse use legendas curtas”);

          - a mensagem envolver **produtos, campanhas, públicos ou temas de negócio**.

        
          

        Apenas preferências **do próprio usuário** (modo de envio, formato, estilo, quantidade, tom desejado etc.) são relevantes.

         - Nunca considere como "coletivo" frases em que o sujeito é o próprio usuário ou sua equipe.
        - Termos como “eu”, “a gente”, “nós”, “meu negócio”, “minha marca”,
          “nossa empresa”, “nosso time”, “nossa marca” indicam **autorreferência**.
        - Nesses casos, classifique como **individual**, mesmo que haja menção a temas de negócio.
        
        **Exemplos:**
        - “A gente prefere usar ‘empresários’ em vez de CNPJ.” → relevante = individual
        - “Nós não gostamos de usar a palavra ‘loja’, prefira ‘parceiro’.” → relevante = individual
        - “Minha empresa quer mudar o estilo das copies.” → relevante = individual
        - “A <empresa passada pelo cliente> quer mudar o estilo das copies.” → relevante = coletivo

        ---

      ### CLASSIFICAÇÃO



        Responda com **um único JSON válido** contendo os seguintes campos:



        ```json

        {

        "relevante": "individual" ou false,

        "informacao": "<descrição clara e curta da preferência ou instrução pessoal>"

        }



        REGRAS DE DECISÃO



        -Considere como relevante (individual):

        -Instruções que alteram o comportamento do sistema apenas para esse usuário

        -Preferências de estilo, formato, conteúdo ou linguagem pessoal

        -Frases iniciadas com verbos de ação: “quero”, “prefiro”, “não me envie”, “gosto”, “faça de outro jeito”, “mude para...”

        -Mensagens que expressam identidade funcional (“sou designer”, “sou gestor”, “sou copywriter”)

        -Considere como falso (não relevante):

        -Pedidos genéricos que poderiam ser feitos por qualquer um (“faça uma copy sobre o produto X”)

        -Instruções que dizem respeito ao cliente, empresa ou público (devem ir para a LLM coletiva)



        ### EXEMPLOS



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

        faça uma copy sobre o catálogo novo da <empresa passada pelo cliente>

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
            if not empresa_detectada and last_company:
                empresa_detectada = last_company
                
            INVALID_COMPANY_TOKENS = {
                "<empresa passada pelo cliente>", "empresa", "a empresa", "a marca",
                "marca", "ela", "ele"
            }
            
            if empresa_detectada.strip().lower() in INVALID_COMPANY_TOKENS:
                empresa_detectada = (last_company or "")
            
            json_main["empresa"] = empresa_detectada

            print("🧩 IA_COLETIVA → Empresa detectada:", 

                f"'{empresa_detectada}'" if empresa_detectada else "❌ Nenhuma empresa identificada")

        else:

            print("❌ IA_COLETIVA → Nenhum JSON encontrado na resposta.")

    except Exception as e:

        print("❌ IA_COLETIVA → Erro ao decodificar JSON:", e)

        print("Resposta bruta:", result)



    try:
        match_verif = re.search(r"\{.*\}", verification_result, re.DOTALL)
        if match_verif:
            json_verif = json.loads(match_verif.group(0))
            print("✅ IA_INDIVIDUAL_BOMMA → JSON verificado com sucesso.")
        else:
            print("⚠️ IA_INDIVIDUAL_BOMMA → Nenhum JSON encontrado na verificação.")
            json_verif = {"verificacao": "erro", "detalhes": verification_result}
    except Exception as e:
        print("❌ IA_INDIVIDUAL_BOMMA → Erro ao decodificar verificação:", e)
        print("Resposta bruta:", verification_result)
        json_verif = {"verificacao": "erro", "detalhes": verification_result}



    collective_reference = empresa_detectada.strip().lower() if empresa_detectada else ""
    print(collective_reference)

    individual_reference = lovable_user_name.strip().lower()



        # Usa o session_id fornecido pelo Lovable (deve vir no payload)

    session_id = request.session_id



    conversation = create_conversational_chain(

        session_id=session_id,

        model="gpt-4o")



    # --- MEMÓRIA COLETIVA (profissional) ---
    if json_main.get("relevante") == "coletivo":
        content = (json_main.get("informacao") or "").strip()
    
        if content:
            embedding = get_embedding(content)
            existing = get_team_memory(collective_reference)
    
            # Evita duplicatas vetoriais antes de salvar
            if not is_duplicate_embedding(
                embedding, [i["embedding"] for i in (existing.data or [])]
            ):
                insert_team_memory(collective_reference, content, embedding)
                print(f"💾 Inserido em memória coletiva (profissional): {collective_reference}")
            else:
                print(f"⚠️ Duplicado ignorado (profissional): {collective_reference}")
    
    
    
    # --- MEMÓRIA INDIVIDUAL (usuário Bomma) ---
    if json_verif.get("relevante") == "individual":
        content = (json_verif.get("informacao") or "").strip()
    
        if content:
            embedding = get_embedding(content)
            existing = get_individual_memory(individual_reference)
    
            if not is_duplicate_embedding(
                embedding, [i["embedding"] for i in (existing.data or [])]
            ):
                insert_individual_memory(individual_reference, content, embedding)
                print(f"💾 Inserido em memória individual (usuário): {individual_reference}")
            else:
                print(f"⚠️ Duplicado ignorado (usuário): {individual_reference}")
    
    
    
    # --- CONSULTAS DE MEMÓRIA ---
    print(f"[DBG] Referência coletiva normalizada: '{collective_reference}'")
    
    bdcontent = get_team_memory(collective_reference)
    if bdcontent and bdcontent.data:
        res = "\n".join([f"- {item['content']}" for item in bdcontent.data])
    else:
        res = "Nenhuma diretriz registrada ainda para este profissional."
    
    
    usercontent = get_individual_memory(individual_reference)
    if usercontent and usercontent.data:
        user_res = "\n".join([f"- {item['content']}" for item in usercontent.data])
    else:
        user_res = "Nenhuma preferência individual registrada ainda."


    # print(f"[DBG] Conteúdo retornado: {bdcontent.data if bdcontent and bdcontent.data else 'vazio'}")

    if bdcontent and bdcontent.data:

        res = "\n".join([f"- {item['content']}" for item in bdcontent.data])

    else:

        res = "Nenhuma diretriz coletiva registrada ainda."



    usercontent = get_individual_memory(individual_reference)
    if usercontent and usercontent.data:
        user_res = "\n".join([f"- {item['content']}" for item in usercontent.data])
    else:
        user_res = "Nenhuma preferência individual registrada ainda."
        
    if tipo_conteudo == 'copy':
        copy_prompt = generate_prompt_copy_impulse(message, res, user_res, lovable_user_name)
    else:
        copy_prompt = generate_prompt_video_impulse(message, res, user_res, lovable_user_name)


    try:

        response = conversation.invoke({"input": copy_prompt})

        copy = response["response"] if isinstance(response, dict) and "response" in response else str(response)

    except Exception as e:

        print("❌ Erro ao gerar copy:", e)

        return {"copy": f"Erro ao gerar copy: {str(e)}"}

    
    if session_id not in CONVERSATIONS:
        CONVERSATIONS[session_id] = {}
    CONVERSATIONS[session_id]["last_company"] = empresa_detectada

    return {"copy": copy}
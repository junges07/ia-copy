def generate_prompt_copy_impulse(message, res, user_res, lovable_user_name):    
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
        """
        return copy_prompt


def generate_prompt_video_impulse(message, res, user_res, lovable_user_name):
    video_prompt = f"""
    🎬 **Framework de Direcionamento de Vídeos - SELLGRID IMPULSE**

    Briefing recebido:
    {message}

    Briefing da Empresa (coletivo):
    {res}

    Briefing Individual do usuário {lovable_user_name}:
    {user_res}

    ---
    ⚙️ PRIORIDADE DE INTERPRETAÇÃO
    Hierarquia obrigatória:
    1. Briefing Individual (preferências do usuário)
    2. Briefing Coletivo (identidade e tom da marca)
    3. Framework Sellgrid Impulse (estrutura de vídeo)

    Sempre respeite essa ordem: **Individual > Coletivo > Framework.**

    ---
    🎯 OBJETIVO
    Criar um **roteiro de vídeo curto e direto**, dividido em **4 TAKES numerados**, simulando a fala de um apresentador em um anúncio para Reels, Shorts ou TikTok.
    O vídeo deve soar natural, persuasivo e objetivo, com foco em gerar conversão (cliques, cadastros, contato).

    ---
        🧱 ESTRUTURA OBRIGATÓRIA

    TAKE 01 – **Chamada de Atenção / Provocação**
    - Frase inicial de impacto com “Você que...”, “Lojista que...”, “Empresário que...”
    - O objetivo é despertar atenção e gerar curiosidade
    - **Não conclua o raciocínio e não insira CTA neste take**
    - Deve preparar terreno para o Take 02, criando um gancho de continuidade
    - Exemplo de boa transição: “...mas sabe o que realmente atrapalha nisso?” / “...então presta atenção nisso aqui.”

    TAKE 02 – **Exposição da Dor**
    - Continue naturalmente o raciocínio iniciado no Take 01
    - Mostre a dor, limitação ou problema real do público
    - Linguagem falada, natural e realista (sem tecnicismos)
    - Deve conectar-se organicamente ao Take 03

    TAKE 03 – **Apresentação da Solução**
    - Apresente a empresa/produto/serviço como solução direta para o problema anterior
    - Destaque diferenciais concretos e específicos
    - Evite tom de vendedor, fale como quem entende o problema e oferece ajuda real

    TAKE 04 – **Call to Action (CTA)**
    - Encerre de forma clara e leve, convidando o espectador à ação
    - Frases curtas e orais: “Clica aqui e fala com a gente”, “Deixa o contato que te explicamos na prática”
    - Evite repetições ou fechamento forçado


    ---
    🧾 BLOCO EXTRA – **LEGENDA DO POST**
    Após os takes, gere uma legenda curta e textual (não oral) para acompanhar o vídeo no feed.

    Estrutura esperada:
    - 2 a 3 linhas explicativas sobre o tema do vídeo
    - Tom persuasivo, direto e informativo
    - Inclua CTA textual no final (“Fale com um especialista”, “Peça seu catálogo agora”)
    - Pode mencionar benefícios B2B, exclusividade CNPJ, etc.
    - Sem hashtags ou emojis (a menos que conste no briefing individual)

    ---
    🧠 ESTILO DE SAÍDA
    - Frases curtas e naturais (simulam fala)
    - Sem legendas ou efeitos visuais no roteiro
    - O vídeo deve durar **entre 25 e 40 segundos**
    - Tom seguro, consultivo e humano — nunca teatral ou exagerado

    ---
    📦 FORMATO FINAL DA RESPOSTA
    Entregue exatamente neste formato:

    TAKE 01 – ...
    TAKE 02 – ...
    TAKE 03 – ...
    TAKE 04 – ...

    LEGENDA DO POST:
    ...

    ---
    
      ⚠️ COERÊNCIA ENTRE OS TAKES
    - Cada take deve se conectar naturalmente ao seguinte, como uma conversa fluida.
    - O Take 01 cria a curiosidade, o Take 02 aprofunda a dor, o Take 03 resolve e o Take 04 finaliza.
    - Nunca trate os takes como blocos independentes — o vídeo deve parecer uma fala contínua.
    
    ---
    Agora gere o roteiro completo conforme o briefing acima.
    """
    return video_prompt

def generate_prompt_copy_bomma(message, res, user_res, lovable_user_name):    
    copy_prompt = f"""
    Briefing recebido:
    {message}

    Briefing do Profissional ou Empresa (coletivo) — contém diretrizes fixas sobre identidade, estilo e posicionamento do arquiteto, escritório ou empreendimento (pode não ter):
    {res}

    Briefing Individual — contém preferências permanentes de escrita ou estilo do usuário {lovable_user_name} (pode não ter nenhuma):
    {user_res}

    ### ⚙️ PRIORIDADE DE INTERPRETAÇÃO
    Ordem obrigatória:
    1. **Briefing Individual** — preferências pessoais do usuário.
    2. **Briefing Coletivo** — identidade e linguagem do profissional, marca ou empreendimento.
    3. **Framework Bomma** — estrutura adaptativa de copy.

    Hierarquia em caso de conflito:
    **Individual > Coletivo > Framework.**

    ---

    🎯 OBJETIVO PRINCIPAL

    Criar **textos e legendas de postagens para o universo da arquitetura, design e mercado imobiliário premium**, seguindo o padrão Bomma:
    - Linguagem estética, técnica e refinada.  
    - Clareza informativa quando tratar de imóveis.  
    - Sofisticação e sensibilidade quando tratar de conceitos arquitetônicos ou autorais.  
    - Sempre preservar credibilidade, coerência e valor percebido do nome associado (profissional, marca ou empreendimento).

    ---

    ✍️ FRAMEWORK BOMMA — MODO ADAPTATIVO

    O tom e o formato devem se ajustar automaticamente conforme o contexto detectado.

    #### 🧩 Caso 1 — Projetos de Arquitetos / Estúdios
    **Objetivo:** expressar identidade, estilo e propósito estético.  
    Estrutura:
    1. **Essência do Projeto ou Ideia**  
       - Introduza o conceito central do projeto.  
       - Linguagem sensorial e arquitetônica, evitando jargões técnicos.  
       - Ex: “Luz, textura e silêncio como matéria de projeto.”

    2. **Narrativa de Intenção**  
       - Mostre o raciocínio criativo e o propósito estético.  
       - Ex: “Cada linha foi desenhada para dissolver o limite entre dentro e fora.”

    3. **Fechamento Reflexivo**  
       - Conclua com frase que resuma o olhar do profissional.  
       - Ex: “Arquitetura como pausa — o tempo transformado em espaço.”

    ---

    #### 🧩 Caso 2 — Imóveis / Empreendimentos (apartamentos, coberturas, residências, etc.)
    **Objetivo:** valorizar o imóvel com precisão e elegância, mantendo caráter comercial sutil e sofisticado.  
    Estrutura:
    1. **Introdução Inspiracional**  
       - Inicie com frase que evoque o estilo de vida e a proposta do imóvel.  
       - Pode usar tom aspiracional, mas sem abstrações genéricas.  
       - Ex: “Entre o centro e a tranquilidade, um lar pensado para viver o essencial.”

    2. **Descrição Técnica e Realista**  
       - Destaque **apenas informações presentes no briefing** (metragem, cômodos, localização, diferenciais).  
       - **Nunca invente atributos** não informados (como “luz natural”, “vista ampla”, “materiais nobres”).  
       - Linguagem fluida e natural — informativa, mas com ritmo estético.  
       - Ex: “Com 200m², três pavimentos e áreas bem distribuídas, o triplex equilibra amplitude e privacidade.”

    3. **CTA Sofisticado e Convidativo**  
       - Encerramento com chamada comercial leve, de tom aspiracional, que estimule contato ou visita.  
       - Evite imperativos diretos (“compre”, “garanta”), prefira convites elegantes.  
       - Exemplos:  
         - “Agende uma visita e conheça cada detalhe.”  
         - “Entre em contato e descubra este endereço.”  
         - “Converse com nosso time e veja de perto o que torna este espaço único.”

    ---

    🧾 ESTRUTURA DE ENTREGA

    Gere sempre **dois blocos bem definidos**:

    - **Texto da Arte**: frase curta e estética (1–3 linhas).  
      → Representa o conceito visual do post ou o espírito do projeto.  
      → Exemplo (arquitetura): “Luz, silêncio e matéria.”  
      → Exemplo (imóvel): “Viver o essencial, perto de tudo.”

    - **Legenda (Texto do Post)**: texto de até 6 linhas, coerente com o contexto detectado (profissional ou imóvel).  
      → Se for projeto autoral: poético e reflexivo.  
      → Se for imóvel: técnico-descritivo, realista e com CTA refinado.  
      → Jamais use emojis, gírias ou frases publicitárias explícitas.

    ---

    ⚠️ REGRAS DE COERÊNCIA

    - Não adicione informações inexistentes no briefing.  
    - Proibido emojis, hashtags e linguagem de venda agressiva.  
    - O tom deve ser sofisticado, direto e equilibrado.  
    - Limite de abstração: o texto deve ser **sofisticado, mas claro** — nenhuma metáfora desconectada da realidade do imóvel.  
    - CTA deve sempre existir no contexto de imóveis, mas soar **convite natural**, nunca apelo comercial.

    ---

    🧠 PROCESSO DE RACIOCÍNIO

    1. Analise o briefing e identifique se o tema é **profissional criativo** ou **imóvel/empreendimento**.  
    2. Aplique o bloco correspondente do Framework Bomma.  
    3. Gere o **Texto da Arte** e a **Legenda** com naturalidade e precisão.  
    4. Revise se o resultado é informativo, coerente e esteticamente agradável.  
    5. Retorne apenas os dois blocos solicitados, sem explicações adicionais.
    """
    return copy_prompt



def generate_prompt_video_bomma(message, res, user_res, lovable_user_name):
    video_prompt = f"""
    🎬 **Framework de Direcionamento de Vídeos - BOMMA**

    Briefing recebido:
    {message}

    Briefing do Profissional (coletivo):
    {res}

    Briefing Individual do usuário {lovable_user_name}:
    {user_res}

    ---
    ⚙️ PRIORIDADE DE INTERPRETAÇÃO
    Hierarquia obrigatória:
    1. Briefing Individual (preferências do usuário)
    2. Briefing Coletivo (identidade e estilo do profissional)
    3. Framework Bomma (estrutura de narrativa)

    Sempre respeite essa hierarquia: **Individual > Coletivo > Framework.**

    ---
    🎯 OBJETIVO
    Criar um **roteiro de vídeo curto para Reels, TikTok ou Shorts**, dividido em **4 TAKES numerados**, simulando a fala de um arquiteto ou designer apresentando um conceito, projeto ou reflexão.  
    O vídeo deve soar **autêntico, calmo, visual e inspiracional**, com linguagem natural e ritmo coerente com a estética do profissional.

    ---
    🧱 ESTRUTURA OBRIGATÓRIA

    TAKE 01 – **Introdução / Chamado Estético**
    - Inicie com uma frase que evoque sensação, reflexão ou elemento visual (luz, textura, forma, tempo, silêncio etc).  
    - Pode começar com algo poético (“A luz é o primeiro traço de qualquer projeto.”) ou reflexivo (“Nem todo espaço precisa ser cheio para ser completo.”)  
    - Crie atmosfera, não venda.

    TAKE 02 – **Contexto ou Processo Criativo**
    - Mostre brevemente a origem da ideia, o pensamento por trás do projeto, ou o que o inspirou.  
    - Linguagem natural, de fala, mas com cadência e intenção.  
    - Exemplo: “A ideia nasceu da vontade de trazer leveza para um cotidiano pesado.”

    TAKE 03 – **Exploração ou Intenção**
    - Expanda a reflexão ou mostre como o conceito se traduz no espaço, material ou composição.  
    - Exemplo: “Cada textura foi escolhida para absorver a luz e devolver calma.”  
    - Pode mencionar sensações, contrastes, elementos do projeto.

    TAKE 04 – **Fechamento Poético**
    - Finalize com uma frase síntese: curta, memorável e aberta à interpretação.  
    - Exemplo: “Arquitetura também é pausa.”  
    - Nunca use CTA (como “acompanhe”, “veja mais” ou “entre em contato”).

    ---
    🧾 BLOCO EXTRA – **LEGENDA DO POST**
    Após os takes, gere uma legenda textual breve (não oral) para acompanhar o vídeo no feed.

    Estrutura esperada:
    - 2 a 4 linhas que resumam o conceito, intenção ou atmosfera do vídeo.  
    - Linguagem autoral e contemplativa.  
    - Sem emojis, hashtags, CTAs ou linguagem comercial.  
    - Pode usar metáforas sutis, mas sempre coerentes com o tom do arquiteto.

    ---
    🧠 ESTILO DE SAÍDA
    - Frases curtas e pausadas, com ritmo oral realista (como quem compartilha uma ideia).  
    - Evite narrações formais — o tom deve ser de fala leve, pessoal e inspiracional.  
    - O vídeo deve durar entre **20 e 45 segundos**.  
    - Nenhum exagero emocional ou teatralização — priorize **autenticidade e estética**.

    ---
    📦 FORMATO FINAL DA RESPOSTA
    Entregue exatamente neste formato:

    TAKE 01 – ...
    TAKE 02 – ...
    TAKE 03 – ...
    TAKE 04 – ...

    LEGENDA DO POST:
    ...

    ---
    ⚠️ COERÊNCIA ENTRE OS TAKES
    - Os takes devem fluir naturalmente, como uma conversa calma e contínua.  
    - Evite saltos de tema ou frases desconexas.  
    - O Take 01 introduz a atmosfera, o 02 dá contexto, o 03 aprofunda e o 04 fecha com poesia.  

    ---
    Agora gere o roteiro completo conforme o briefing acima.
    """
    return video_prompt

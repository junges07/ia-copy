from langchain_openai import ChatOpenAI

from langchain_community.callbacks import get_openai_callback

from langchain.memory import ConversationBufferMemory

from langchain_community.chat_message_histories import SQLChatMessageHistory

from langchain.chains import ConversationChain

from ..config import OPENAI_API_KEY





def get_llm(model: str = "gpt-4o-mini", temperature: float = 0):

    """Retorna uma instância configurada do ChatOpenAI."""

    return ChatOpenAI(

        model=model,

        temperature=temperature,

        api_key=OPENAI_API_KEY

    )





def run_llm(prompt: str, model: str = "gpt-4o-mini", temperature: float = 0):

    """Executa um prompt simples (sem memória persistente)."""

    llm = get_llm(model, temperature)

    with get_openai_callback() as cb:

        result = llm.invoke(prompt).content

        print("---- Uso de Tokens ----")

        print(f"Prompt tokens: {cb.prompt_tokens}")

        print(f"Completion tokens: {cb.completion_tokens}")

        print(f"Total tokens: {cb.total_tokens}")

        print(f"Custo estimado: ${cb.total_cost:.6f}")

    return result





def create_conversational_chain(session_id: str, model: str = "gpt-4o", temperature: float = 0.6):

    """

    Cria uma cadeia conversacional com memória persistente em SQLite.

    Cada 'session_id' identifica uma conversa independente.

    Também exibe o histórico completo armazenado.

    """

    history = SQLChatMessageHistory(

    connection_string="sqlite:///chat_history.db",

    session_id=session_id

)



    messages = history.messages

    print(f"\n🧠 Histórico carregado para sessão '{session_id}':")

    if not messages:

        print("   (nenhuma mensagem registrada ainda)\n")

    else:

        for i, msg in enumerate(messages, start=1):

            role = msg.type.upper()

            content = msg.content.strip().replace("\n", " ")

            print(f"   {i:02d}. [{role}] {content}")

        print("")



    memory = ConversationBufferMemory(

        chat_memory=history,

        return_messages=True

    )



    llm = ChatOpenAI(

        model=model,

        temperature=temperature,

        api_key=OPENAI_API_KEY

    )



    chain = ConversationChain(

        llm=llm,

        memory=memory,

        verbose=False

    )

    return chain
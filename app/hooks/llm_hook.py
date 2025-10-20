from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from langchain.memory import ConversationBufferWindowMemory
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
    """Executa um prompt simples (sem memória)."""
    llm = get_llm(model, temperature)
    with get_openai_callback() as cb:
        result = llm.invoke(prompt).content
        print("---- Uso de Tokens ----")
        print(f"Prompt tokens: {cb.prompt_tokens}")
        print(f"Completion tokens: {cb.completion_tokens}")
        print(f"Total tokens: {cb.total_tokens}")
        print(f"Custo estimado: ${cb.total_cost:.6f}")
    return result


def create_conversational_chain(model="gpt-4o", memory_limit=4):
    """Cria uma cadeia conversacional com memória limitada (compatível)."""
    llm = ChatOpenAI(model=model, temperature=0.6, api_key=OPENAI_API_KEY)

    memory = ConversationBufferWindowMemory(
        k=memory_limit,
        memory_key="history",
        return_messages=True
    )

    chain = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=False
    )
    return chain

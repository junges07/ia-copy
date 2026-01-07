import json
import re
from langchain_openai import ChatOpenAI
from langchain_community.callbacks import get_openai_callback
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain.chains import ConversationChain
from ..config import OPENAI_API_KEY


def get_llm(model: str = "gpt-4o-mini", temperature: float = 0):
    return ChatOpenAI(model=model, temperature=temperature, api_key=OPENAI_API_KEY)


def run_llm(prompt: str, model: str = "gpt-4o-mini", temperature: float = 0):
    llm = get_llm(model, temperature)

    with get_openai_callback() as cb:
        result = llm.invoke(prompt).content
        print("---- Uso de Tokens ----")
        print(f"Prompt tokens: {cb.prompt_tokens}")
        print(f"Completion tokens: {cb.completion_tokens}")
        print(f"Total tokens: {cb.total_tokens}")
        print(f"Custo estimado: ${cb.total_cost:.6f}")
    return result


def create_conversational_chain(
    session_id: str, model: str = "gpt-4o", temperature: float = 0.6
):
    history = SQLChatMessageHistory(
        connection_string="sqlite:///chat_history.db", session_id=session_id
    )
    messages = history.messages
    print(f"\n🧠 Histórico carregado para sessão '{session_id}':")
    if not messages:
        print("   (nenhuma mensagem registrada ainda)\n")

    else:
        for i, msg in enumerate(messages, start=1):
            role = msg.type.upper()
            content = msg.content.strip().replace("\n", " ")
            # print(f"   {i:02d}. [{role}] {content}")

    memory = ConversationBufferMemory(chat_memory=history, return_messages=True)
    llm = ChatOpenAI(model=model, temperature=temperature, api_key=OPENAI_API_KEY)
    chain = ConversationChain(llm=llm, memory=memory, verbose=False)

    return chain


def run_llm_structured(prompt: str, model: str = "gpt-4o-mini"):
    llm = ChatOpenAI(model=model, temperature=0, api_key=OPENAI_API_KEY)

    try:
        result = llm.invoke(prompt).content
    except Exception as e:
        print("[STRUCTURED-LLM] Erro ao invocar LLM:", e)
        return {"error": str(e)}

    try:
        match = re.search(r"\{.*\}", result, re.DOTALL)
        if match:
            cleaned = match.group(0)
            data = json.loads(cleaned)
            return data
        else:
            print("[STRUCTURED-LLM] ❌ Nenhum JSON encontrado:")
            print(result)
            return {"error": "no_json", "raw": result}

    except Exception as e:
        print("[STRUCTURED-LLM] ❌ Erro ao parsear JSON:", e)
        print(result)
        return {"error": "json_parse_error", "raw": result}

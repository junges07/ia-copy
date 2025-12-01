from pydantic import BaseModel


# ===========================
# MODELO ORIGINAL (COPYS)
# ===========================
class UserRequest(BaseModel):
    data: str
    user: str
    session_id: str


# ===========================
# MODELOS PARA CHATS
# ===========================
class ChatCreateRequest(BaseModel):
    user_id: str
    title: str
    business: str


class MessageCreateRequest(BaseModel):
    content: str
    fromUser: bool  # True se for mensagem do usuário, False se for da IA


class FeedbackRequest(BaseModel):
    goodFeedback: bool | None  # Pode ser nulo

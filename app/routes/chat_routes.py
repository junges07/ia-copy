import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from .request_models import (
    ChatCreateRequest,
    MessageCreateRequest,
    FeedbackRequest
)

from ..hooks.supabase_hook import (
    create_chat,
    get_chats_by_user,
    get_chat,
    delete_chat,
    update_chat_title,
    add_message,
    get_messages,
    update_message_feedback
)


router = APIRouter()


# ============================================
#           CORS OPTIONS
# ============================================

@router.options("/{full_path:path}")
async def options_endpoint():
    return JSONResponse(
        content={},
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )


# ============================================
#           CREATE CHAT
# ============================================

@router.post("/chats")
async def create_chat_route(request: ChatCreateRequest):

    created = create_chat(
        user_id=request.user_id,
        title=request.title,
        business=request.business
    )

    if not created:
        raise HTTPException(status_code=500, detail="Erro ao criar chat.")

    return {"chatId": created, "status": "created"}


# ============================================
#          GET CHATS BY USER
# ============================================

@router.get("/chats/{user_id}")
async def list_chats_route(user_id: str):
    chats = get_chats_by_user(user_id)

    if chats is None:
        raise HTTPException(status_code=404, detail="Nenhum chat encontrado.")

    return {"chats": chats}

# ============================================
#          GET MESSAGES FROM CHAT
# ============================================

@router.get("/chats/{chat_id}/messages")
async def get_chat_messages(chat_id: str):

    chat = get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat não encontrado.")

    messages = get_messages(chat_id)
    return {"chatId": chat_id, "messages": messages}


# ============================================
#          ADD MESSAGE TO CHAT
# ============================================

@router.post("/chats/{chat_id}/messages")
async def add_message_route(chat_id: str, request: MessageCreateRequest):

    chat = get_chat(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat não encontrado.")


    added = add_message(
        chat_id=chat_id,
        content=request.content,
        from_user=request.fromUser,
    )

    if not added:
        raise HTTPException(status_code=500, detail="Erro ao salvar mensagem.")

    return {"messageId": added, "status": "created"}


# ============================================
#         UPDATE MESSAGE FEEDBACK
# ============================================

@router.patch("/messages/{message_id}/feedback")
async def update_message_feedback_route(message_id: str, request: FeedbackRequest):
    print("req: ", request.goodFeedback)
    updated = update_message_feedback(
        message_id=message_id,
        feedback=request.goodFeedback
    )

    if not updated:
        raise HTTPException(status_code=500, detail="Erro ao salvar feedback.")

    return {"messageId": message_id, "status": "updated"}


# ============================================
#          UPDATE CHAT TITLE
# ============================================

@router.patch("/conversations/{chat_id}")
async def update_chat_title_route(chat_id: str, request: ChatCreateRequest):

    updated = update_chat_title(
        chat_id=chat_id,
        new_title=request.title
    )

    if not updated:
        raise HTTPException(status_code=500, detail="Erro ao atualizar título.")

    return {"chatId": chat_id, "status": "updated", "newTitle": request.title}

# ============================================
#                DELETE CHAT
# ============================================

@router.delete("/chats/{chat_id}")
async def delete_chat_route(chat_id: str):

    deleted = delete_chat(chat_id)

    if not deleted:
        raise HTTPException(status_code=500, detail="Erro ao deletar chat.")

    return {"chatId": chat_id, "status": "deleted"}


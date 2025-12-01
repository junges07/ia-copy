
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

# from .request_models import (
# )

from ..hooks.supabase_hook import (
    getUsers,
)

router = APIRouter()

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
    
@router.get("/getAllUsers")
async def get_users_route():
    users = getUsers()
    if users:
        return {"users": users}
    return HTTPException(status_code=404, detail="Nenhum user encontrado.")
    

   

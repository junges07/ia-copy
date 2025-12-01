from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.copy_routes_impulse import router as copy_router_impulse
from app.routes.copy_routes_bomma import router as copy_router_bomma
from app.routes.chat_routes import router as chat_router 
from app.routes.user_routes import router as user_router

app = FastAPI(title="Minha API de Copy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(copy_router_impulse)
app.include_router(copy_router_bomma)

app.include_router(chat_router)
app.include_router(user_router)

@app.get("/")
def root():
    return {"message": "🚀 API no ar com sucesso!"}

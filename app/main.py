from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.copy_routes import router as copy_router  

app = FastAPI(title="Minha API de Copy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(copy_router)

@app.get("/")
def root():
    return {"message": "🚀 API no ar com sucesso!"}

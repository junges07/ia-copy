import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

if not OPENAI_API_KEY:
    print("❌ Erro: OPENAI_API_KEY não encontrada no .env")
else:
    print("✅ OPENAI_API_KEY carregada com sucesso")

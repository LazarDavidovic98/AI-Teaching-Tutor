"""
Konfiguracija
=============
Sva podešavanja se učitavaju iz environment varijabli (ili .env fajla putem python-dotenv).
Ovaj princip jednog izvora istine olakšava kasniju zamjenu lokalnog LLM-a:
dovoljno je promijeniti LLM_BASE_URL / LLM_MODEL u .env fajlu.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ── Aplikacija ────────────────────────────────────────────────────────────
    APP_NAME: str = "AI Teaching Tutor"
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # ── Baza podataka ─────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./ai_tutor.db"

    # ── LLM (OpenAI-kompatibilan) ────────────────────────────────────────────
    # Zamijeni LLM_BASE_URL da pokazuje na lokalni Ollama / LM Studio server za offline rad.
    OPENAI_API_KEY: str = "sk-your-openai-api-key"
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"

    # ── Embeddinzi (vektorske reprezentacije teksta) ─────────────────────────
    # Za lokalne embeddinge zamijeni sa: "sentence-transformers/all-MiniLM-L6-v2"
    # i ažuriraj embedding_service.py prema tome.
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ── Vektorska baza (ChromaDB) ────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    CHROMA_COLLECTION_NAME: str = "tutor_documents"

    # ── Otpremanje fajlova ────────────────────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 20

    # ── CORS (dozvole za frontend) ────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

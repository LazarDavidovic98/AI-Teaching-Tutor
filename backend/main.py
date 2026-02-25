"""
AI Teaching Tutor - FastAPI ulazna tačka
=========================================
Arhitekturne odluke:
  - FastAPI je izabran zbog async podrške, automatske OpenAPI dokumentacije i Pydantic integracije.
  - CORS je omogućen za lokalni razvoj (React Vite radi na portu :5173).
  - Lifespan context manager kreira DB tabele i inicijalizuje vektorski store pri pokretanju.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine, Base
from backend.routers import auth, chat, upload
from backend.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Životni ciklus aplikacije - pokretanje i gašenje.
    Kreira sve SQLAlchemy tabele i inicijalizuje ChromaDB kolekciju.
    """
    # Kreiramo relacione DB tabele (SQLite po defaultu)
    Base.metadata.create_all(bind=engine)
    yield
    # Gašenje aplikacije (ništa posebno nije potrebno za SQLite / in-process Chroma)


app = FastAPI(
    title="AI Teaching Tutor",
    description="A RAG-powered educational chatbot for mathematics and machine learning.",
    version="1.0.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS – dozvoljavamo React dev serveru pristup API-ju
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Ruteri – grupišu API endpoint-e po funkcionalnosti
# ---------------------------------------------------------------------------
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat / Tutoring"])
app.include_router(upload.router, prefix="/api/upload", tags=["File Upload"])


@app.get("/", tags=["Health"])
def root():
    """Osnovni endpoint za provjeru da li API radi."""
    return {"status": "ok", "message": "AI Teaching Tutor API radi ispravno."}

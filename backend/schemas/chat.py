"""
Pydantic šeme za chat
=====================
ChatRequest nosi istoriju razgovora kako LLM mogao pratiti kontekst.
"""

from pydantic import BaseModel
from typing import List


class ChatMessage(BaseModel):
    """Jedna poruka u razgovoru (role: 'user' | 'assistant')."""
    role: str          # "user" ili "assistant"
    content: str


class ChatRequest(BaseModel):
    """
    Zahtjev koji frontend šalje pri svakoj poruci.
    history sadrži prethodne poruke radi konteksta razgovora.
    """
    message: str
    history: List[ChatMessage] = []
    subject: str = "general"   # filtrira RAG retrieval po predmetu


class ChatResponse(BaseModel):
    """Odgovor koji API vraća frontendu."""
    answer: str
    sources: List[str] = []    # naslovi/isječci dokumenata koji su korišteni

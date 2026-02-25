"""
Ruter za chat / tutoring
========================
Endpoint-i:
  POST /api/chat/ask  – šalje pitanje, vraća RAG odgovor

Svaki zahtjev zahtijeva validan JWT token (get_current_user dependency).
"""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.models.user import User
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.auth_service import get_current_user
from backend.rag.query import rag_query

router = APIRouter()


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Glavna chat endpoint.

    Tok:
      1. Primi pitanje + istoriju razgovora + predmet
      2. Proslijedi RAG query pipeline-u
      3. Vrati odgovor i izvore

    Zahtijeva autentifikaciju (Bearer token u Authorization zaglavlju).
    """
    try:
        answer, sources = rag_query(
            question=request.message,
            history=request.history,
            subject=request.subject,
        )
        return ChatResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Greška pri generisanju odgovora: {str(e)}",
        )

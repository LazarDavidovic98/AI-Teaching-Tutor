"""
RAG Pipeline – Unos dokumenata (Ingestion)
==========================================
Tok podataka:
  1. Učitaj fajl (PDF ili txt) sa diska
  2. Podijeli tekst na chunk-ove radi bolje pretrage (chunking)
  3. Generiši vektorske embeddinge za svaki chunk
  4. Sačuvaj embeddinge i metapodatke u ChromaDB

Zašto chunking?
  - LLM ima ograničen context window.
  - Manji chunk-ovi daju precizniji retrieval.
  - Chunk-ovi se preklapaju (overlap) da se ne izgubi kontekst na rubovima.
"""

import os
import uuid
import logging
from pathlib import Path
from typing import List, Tuple

import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.config import settings
from backend.rag.embedding_service import get_embeddings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ChromaDB klijent – podaci se perzistuju na disku (CHROMA_PERSIST_DIR)
# ---------------------------------------------------------------------------
_chroma_client = chromadb.PersistentClient(
    path=settings.CHROMA_PERSIST_DIR,
)


def get_collection():
    """Vraća (ili kreira) ChromaDB kolekciju u kojoj su svi chunk-ovi."""
    return _chroma_client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # kosinusna sličnost je standard za tekst
    )


# ---------------------------------------------------------------------------
# Pomoćne funkcije
# ---------------------------------------------------------------------------

def _load_text_from_file(file_path: str) -> str:
    """
    Učitava čisti tekst iz fajla.
    Podržava: .txt i .pdf (putem PyMuPDF biblioteke).
    """
    path = Path(file_path)
    if path.suffix.lower() == ".pdf":
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
            return text
        except ImportError:
            raise RuntimeError("PyMuPDF nije instaliran. Pokreni: pip install pymupdf")
    else:
        # Čisti tekstualni fajl
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()


def _split_into_chunks(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    Dijeli tekst na chunk-ove fiksne veličine sa preklapanjem.

    Parametri:
        chunk_size – broj karaktera po chunk-u (800 ≈ ~200 tokena)
        overlap    – broj karaktera koji se dijele između susjednih chunk-ova
                     (sprječava gubitak konteksta na granicama)

    Napomena: Za produkciju preporučujemo RecursiveCharacterTextSplitter
              iz LangChain ili sličan semantički splitter.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]


# ---------------------------------------------------------------------------
# Glavna funkcija unosa
# ---------------------------------------------------------------------------

def ingest_document(
    file_path: str,
    document_id: int,
    user_id: int,
    subject: str = "general",
    original_name: str = "",
) -> int:
    """
    Unosi dokument u vektorsku bazu podataka.

    Vraća broj chunk-ova koji su indeksirani.
    """
    logger.info(f"Počinjem unos dokumenta: {file_path}")

    # Korak 1 – Učitaj tekst
    raw_text = _load_text_from_file(file_path)
    if not raw_text.strip():
        raise ValueError("Dokument je prazan ili se tekst ne može izvući.")

    # Korak 2 – Podijeli na chunk-ove
    chunks = _split_into_chunks(raw_text)
    logger.info(f"Dokument podijeljen na {len(chunks)} chunk-ova.")

    # Korak 3 – Generiši embeddinge za sve chunk-ove
    embeddings = get_embeddings(chunks)

    # Korak 4 – Upiši u ChromaDB
    collection = get_collection()
    ids = [f"doc{document_id}_chunk{i}_{uuid.uuid4().hex[:8]}" for i in range(len(chunks))]
    metadatas = [
        {
            "document_id": document_id,
            "user_id": user_id,
            "subject": subject,
            "original_name": original_name,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )
    logger.info(f"Uspješno indeksirano {len(chunks)} chunk-ova u ChromaDB.")
    return len(chunks)


def delete_document_chunks(document_id: int) -> None:
    """Briše sve chunk-ove datog dokumenta iz ChromaDB-a."""
    collection = get_collection()
    collection.delete(where={"document_id": document_id})
    logger.info(f"Obrisani chunk-ovi za dokument ID={document_id}.")

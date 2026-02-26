"""
RAG Pipeline – Pretraživanje i generisanje odgovora (Query)
============================================================
Tok podataka pri svakom pitanju korisnika:
  1. Generiši embedding za korisničko pitanje
  2. Pretraži ChromaDB (similarity search) – vrati top-K najrelevantnijih chunk-ova
  3. Spoji chunk-ove u "kontekst" string
  4. Pošalji kontekst + pitanje + istoriju razgovora LLM-u
  5. Vrati LLM odgovor i izvore korisniku

Zašto RAG a ne čisti LLM?
  - LLM nema pristup korisnikovim dokumentima
  - RAG omogućava odgovore bazirane na konkretnom materijalu
  - Smanjuje "halucinacije" jer LLM ima provjeren kontekst
"""

import logging
from typing import List, Tuple

from backend.config import settings
from backend.rag.ingestion import get_collection
from backend.rag.embedding_service import get_embeddings
from backend.schemas.chat import ChatMessage

logger = logging.getLogger(__name__)

# Broj chunk-ova koji se dohvataju iz vektorske baze (top-K)
TOP_K_RESULTS = 4


def retrieve_context(query: str, subject: str = "general") -> Tuple[str, List[str]]:
    """
    Korak 1 i 2: Pretraži ChromaDB za najrelevantnije chunk-ove.

    Vraća:
        context – spojeni tekst chunk-ova za LLM prompt
        sources – lista kratkih isječaka za prikaz u UI
    """
    collection = get_collection()

    # Generiši embedding za upit korisnika
    query_embedding = get_embeddings([query])[0]

    # Definiši filter: ako subject nije "general", filtriraj po predmetu
    where_filter = {"subject": subject} if subject != "general" else None

    # Provjeri koliko chunk-ova ima u kolekciji da izbjegnemo grešku
    # kada se traži više rezultata nego što postoji u indeksu
    total_items = collection.count()
    if total_items == 0:
        logger.warning("ChromaDB kolekcija je prazna – nema dokumenata za pretragu.")
        return "", []

    n_results = min(TOP_K_RESULTS, total_items)

    # Similarity search – ChromaDB koristi kosinusnu sličnost
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    chunks = results["documents"][0] if results["documents"] else []
    metadatas = results["metadatas"][0] if results["metadatas"] else []

    if not chunks:
        logger.warning("Nisu pronađeni relevantni chunk-ovi za upit.")
        return "", []

    # Spoji chunk-ove u kontekst string
    context = "\n\n---\n\n".join(chunks)

    # Kratki isječci izvora za UI (prvih 120 karaktera svakog chunk-a)
    sources = [
        f"[{m.get('original_name', 'Dokument')}] {c[:120]}..."
        for c, m in zip(chunks, metadatas)
    ]

    return context, sources


def build_system_prompt(context: str) -> str:
    """
    Gradi system prompt koji govori LLM-u kako da se ponaša.
    Kontekst iz RAG-a se ubacuje ovdje kako bi LLM imao osnovu za odgovor.
    """
    if context:
        return f"""Ti si AI nastavni asistent za matematiku i mašinsko učenje.
Koristiš sljedeće materijale kao osnovu za odgovor:

{context}

Pravila:
- Objašnjavaj korak po korak, jasno i precizno.
- Koristi primjere gdje je moguće.
- Ako odgovor nije u materijalima, iskreno reci da nisi siguran.
- Za matematičke formule koristi LaTeX notaciju (npr. $x^2$).
- Budi prijateljski i motivišući prema učeniku."""
    else:
        return """Ti si AI nastavni asistent za matematiku i mašinsko učenje.
Nisi pronašao relevantne materijale za ovo pitanje, ali ćeš odgovoriti
na osnovu svog opšteg znanja. Budi precizan i eksplicitan."""


def generate_answer(
    question: str,
    context: str,
    history: List[ChatMessage],
) -> str:
    """
    Korak 4: Šalje prompt LLM-u i vraća odgovor.

    Koristi OpenAI-kompatibilan API – radi i sa lokalnim Ollama serverom
    (samo promijeni LLM_BASE_URL u .env).
    """
    from openai import OpenAI

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.LLM_BASE_URL,
    )

    # Gradi poruke: system + istorija razgovora + trenutno pitanje
    messages = [{"role": "system", "content": build_system_prompt(context)}]

    # Dodaj prethodne poruke iz razgovora (kontekst razgovora)
    for msg in history[-6:]:  # max 6 prethodnih poruka da se ne prekorači context window
        messages.append({"role": msg.role, "content": msg.content})

    # Dodaj trenutno pitanje korisnika
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=messages,
        temperature=0.3,      # niža temperatura = preciznije, manje kreativno
        max_tokens=1500,
    )

    return response.choices[0].message.content


def rag_query(
    question: str,
    history: List[ChatMessage],
    subject: str = "general",
) -> Tuple[str, List[str]]:
    """
    Kompletna RAG query funkcija – ulazna tačka za chat ruter.

    Vraća (odgovor, lista_izvora).
    """
    logger.info(f"RAG upit: '{question[:80]}...' | predmet: {subject}")

    # Korak 1-2: Pretraži vektorsku bazu
    context, sources = retrieve_context(question, subject)

    # Korak 3-4: Generiši odgovor
    answer = generate_answer(question, context, history)

    return answer, sources

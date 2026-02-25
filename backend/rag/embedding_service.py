"""
Servis za embeddinge
====================
Apstrakcioni sloj koji sakriva od ostatka aplikacije koji se embedding model koristi.

Da bi se prešlo na lokalne embeddinge (bez interneta):
  1. Instaliraj: pip install sentence-transformers
  2. Promijeni EMBEDDING_MODEL u .env na: sentence-transformers/all-MiniLM-L6-v2
  3. Funkcija get_embeddings() će automatski koristiti lokalni model.
"""

import logging
from typing import List

from backend.config import settings

logger = logging.getLogger(__name__)


def get_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generiše vektorske embeddinge za listu tekstova.

    Automatski bira između:
      - OpenAI API embeddinzi (podrazumijevano)
      - Lokalni SentenceTransformers model (ako EMBEDDING_MODEL počinje sa 'sentence-transformers/')
    """
    if settings.EMBEDDING_MODEL.startswith("sentence-transformers/"):
        return _local_embeddings(texts)
    else:
        return _openai_embeddings(texts)


def _openai_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Koristi OpenAI API za generisanje embeddinzi.
    Model text-embedding-3-small je dobar balans između cijene i kvaliteta.
    """
    from openai import OpenAI

    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.LLM_BASE_URL,
    )

    # OpenAI preporučuje zamjenu newline karaktera razmakom radi stabilnosti
    clean_texts = [t.replace("\n", " ") for t in texts]

    response = client.embeddings.create(
        input=clean_texts,
        model=settings.EMBEDDING_MODEL,
    )
    return [item.embedding for item in response.data]


def _local_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Koristi lokalni SentenceTransformers model — potpuno offline, besplatno.
    Model se preuzima samo prvi put i kešira lokalno.
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise RuntimeError(
            "sentence-transformers nije instaliran. "
            "Pokreni: pip install sentence-transformers"
        )

    model_name = settings.EMBEDDING_MODEL.replace("sentence-transformers/", "")
    logger.info(f"Koristim lokalni embedding model: {model_name}")

    model = SentenceTransformer(model_name)
    vectors = model.encode(texts, convert_to_numpy=True)
    return vectors.tolist()

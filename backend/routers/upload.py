"""
Ruter za otpremanje fajlova
============================
Endpoint-i:
  POST   /api/upload/file       – otpremi PDF/txt i indeksiraj u vektorsku bazu
  GET    /api/upload/documents  – lista korisnikovih dokumenata
  DELETE /api/upload/{doc_id}   – obriši dokument iz DB-a i vektorske baze
"""

import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models.document import Document
from backend.models.user import User
from backend.schemas.document import DocumentOut
from backend.services.auth_service import get_current_user
from backend.rag.ingestion import ingest_document, delete_document_chunks

router = APIRouter()

# Dozvoljeni tipovi fajlova
ALLOWED_EXTENSIONS = {".pdf", ".txt"}
MAX_SIZE_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024


@router.post("/file", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    subject: str = Form(default="general"),
    description: str = Form(default=""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Otpremanje dokumenta.

    Koraci:
      1. Validacija tipa i veličine fajla
      2. Snimanje fajla na disk (uploads/ direktorij)
      3. Kreiranje zapisa u SQLite bazi
      4. Ingestion u ChromaDB (chunking + embedding)
      5. Ažuriranje chunk_count u bazi
    """
    # Provjera ekstenzije
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dozvoljeni formati su: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Provjera veličine fajla
    content = await file.read()
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Fajl je prevelik. Maksimalna veličina je {settings.MAX_FILE_SIZE_MB} MB.",
        )

    # Kreiranje direktorija za upload ako ne postoji
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Generišemo jedinstveno ime fajla da izbjegnemo konflikte
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    # Snimi fajl na disk
    with open(file_path, "wb") as f:
        f.write(content)

    # Kreiraj zapis u bazi (chunk_count = 0 do završetka indexiranja)
    doc = Document(
        user_id=current_user.id,
        filename=unique_filename,
        original_name=file.filename,
        file_type=ext.lstrip("."),
        file_size_bytes=len(content),
        subject=subject,
        description=description,
        chunk_count=0,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Indeksiraj u ChromaDB (može potrajati za veće fajlove)
    try:
        chunk_count = ingest_document(
            file_path=file_path,
            document_id=doc.id,
            user_id=current_user.id,
            subject=subject,
            original_name=file.filename,
        )
        doc.chunk_count = chunk_count
        db.commit()
        db.refresh(doc)
    except Exception as e:
        # Ako indexiranje ne uspije, obriši fajl i zapis iz baze
        db.delete(doc)
        db.commit()
        os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Greška pri indeksiranju dokumenta: {str(e)}",
        )

    return doc


@router.get("/documents", response_model=list[DocumentOut])
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Vraća listu svih dokumenata prijavljenog korisnika."""
    return (
        db.query(Document)
        .filter(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
        .all()
    )


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Briše dokument iz SQLite baze i iz ChromaDB vektorske baze.
    Korisnik može brisati samo svoje dokumente.
    """
    doc = db.query(Document).filter(
        Document.id == doc_id, Document.user_id == current_user.id
    ).first()

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dokument nije pronađen.",
        )

    # Obriši chunk-ove iz vektorske baze
    delete_document_chunks(doc_id)

    # Obriši fajl sa diska
    file_path = os.path.join(settings.UPLOAD_DIR, doc.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Obriši zapis iz SQLite baze
    db.delete(doc)
    db.commit()

"""
Model dokumenta
===============
Prati svaki PDF / tekst fajl koji korisnik otpremi.
Stvarni tekstualni dijelovi (chunk-ovi) se čuvaju u ChromaDB vektorskom storeu;
ova tabela čuva metapodatke kako bi korisnici mogli upravljati dokumentima kroz UI.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)   # "pdf" | "txt"
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Tag predmeta pomaže RAG retrieveru da primijeni filtere na metapodatke
    subject: Mapped[str] = mapped_column(String(100), default="general")
    description: Mapped[str] = mapped_column(Text, default="")

    # Koliko tekstualnih chunk-ova je indeksirano u vektorski store
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="documents")

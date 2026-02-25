"""
Pydantic šema za dokument
=========================
"""

from pydantic import BaseModel
from datetime import datetime


class DocumentOut(BaseModel):
    """Metapodaci o uploadovanom dokumentu koji se vraćaju klijentu."""
    id: int
    filename: str
    original_name: str
    file_type: str
    file_size_bytes: int
    subject: str
    description: str
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}

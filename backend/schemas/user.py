"""
Pydantic šeme za korisnika i autentifikaciju
=============================================
Šeme odvajaju API sloj od ORM modela —
primamo UserCreate, ali nikad ne vraćamo hashed_password.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    """Podaci koji su potrebni za registraciju novog korisnika."""
    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):
    """Podaci za prijavu korisnika."""
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Podaci o korisniku koji se vraćaju klijentu — bez lozinke."""
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT access token koji se vraća nakon uspješne prijave."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Podaci koji se dekodiraju iz JWT tokena."""
    user_id: int | None = None
    email: str | None = None

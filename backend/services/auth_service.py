"""
Servis za autentifikaciju
=========================
Odgovoran za:
  - Hashovanje i provjeru lozinki (bcrypt)
  - Kreiranje i dekodiranje JWT tokena
  - Dohvatanje trenutno prijavljenog korisnika (FastAPI dependency)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.config import settings
from backend.database import get_db
from backend.models.user import User
from backend.schemas.user import TokenData

# OAuth2 shema koja čita Bearer token iz Authorization zaglavlja
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ---------------------------------------------------------------------------
# Lozinke
# ---------------------------------------------------------------------------

def hash_password(plain_password: str) -> str:
    """Vraća bcrypt hash lozinke. Nikada ne čuvaj originalnu lozinku."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Provjerava da li se lozinka poklapa sa hashom."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


# ---------------------------------------------------------------------------
# JWT Tokeni
# ---------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Kreira potpisan JWT token.
    Token sadrži user_id i email — minimum podataka potrebnih za identifikaciju.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> TokenData:
    """
    Dekodira i validira JWT token.
    Baca exception ako je token nevažeći ili istekao.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nevažeći ili istekli token. Molimo prijavite se ponovo.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        email: str = payload.get("email")
        if user_id is None:
            raise credentials_exception
        return TokenData(user_id=int(user_id), email=email)
    except JWTError:
        raise credentials_exception


# ---------------------------------------------------------------------------
# FastAPI Dependency
# ---------------------------------------------------------------------------

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency — koristi se u zaštićenim endpoint-ima.
    Primjer: current_user: User = Depends(get_current_user)
    """
    token_data = decode_access_token(token)
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Korisnik nije pronađen ili nije aktivan.",
        )
    return user

"""
Ruter za autentifikaciju
========================
Endpoint-i:
  POST /api/auth/register  – registracija novog korisnika
  POST /api/auth/login     – prijava, vraća JWT token
  GET  /api/auth/me        – podaci o prijavljenom korisniku
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.schemas.user import UserCreate, UserLogin, UserOut, Token
from backend.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registracija novog korisnika.
    Provjerava jedinstvenost email-a i korisničkog imena prije upisa.
    """
    # Provjera da li email već postoji
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email adresa je već registrovana.",
        )
    # Provjera da li username već postoji
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Korisničko ime je zauzeto.",
        )

    # Kreiraj korisnika sa hashovanom lozinkom
    new_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hash_password(user_in.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    """
    Prijava korisnika.
    Vraća JWT access token koji se koristi za zaštićene endpoint-e.
    """
    user = db.query(User).filter(User.email == user_in.email).first()

    # Ista poruka greške za ne-postojeći email i pogrešnu lozinku
    # (sigurnosni princip – ne otkrivamo koji korak je neuspješan)
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Pogrešan email ili lozinka.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Korisnički nalog nije aktivan.",
        )

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Vraća podatke o trenutno prijavljenom korisniku."""
    return current_user

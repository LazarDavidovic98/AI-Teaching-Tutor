"""
Postavke baze podataka
======================
SQLAlchemy engine + fabrika sesija.
SQLite je podrazumijevani izbor: bez konfiguracije, bazirano na fajlu, idealno za lokalni/portfolijo projekt.
Zamijeni DATABASE_URL sa postgresql://... za nadogradnju bez ikakvih promjena u kodu modela.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from backend.config import settings

# connect_args je specifičan za SQLite; omogućava višenitni pristup (neophodno za FastAPI).
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Svi ORM modeli nasljeđuju ovu baznu klasu."""
    pass


def get_db():
    """
    FastAPI dependency koji obezbjeđuje DB sesiju za svaki zahtjev i zatvara je na kraju.
    Upotreba:  db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
Model rezultata kviza
=====================
Čuva pokušaj kviza korisnika kako bi mogli pratiti napredak u učenju kroz vrijeme.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, Integer, ForeignKey, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class QuizResult(Base):
    __tablename__ = "quiz_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    topic: Mapped[str] = mapped_column(String(200), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(default=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)   # Rezultat od 0.0 do 1.0

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="quiz_results")

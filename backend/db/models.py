"""SQLAlchemy 모델."""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utcnow():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id:         Mapped[int]          = mapped_column(Integer, primary_key=True)
    email:      Mapped[str | None]   = mapped_column(String(255), unique=True, nullable=True)
    plan:       Mapped[str]          = mapped_column(String(20), default="free")  # free/pro/premium
    created_at: Mapped[datetime]     = mapped_column(DateTime(timezone=True), default=_utcnow)


class Report(Base):
    __tablename__ = "reports"

    id:          Mapped[int]        = mapped_column(Integer, primary_key=True)
    share_token: Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    feature:     Mapped[str]        = mapped_column(String(30))  # saju/compatibility/daily/question
    user_id:     Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    input_data:  Mapped[dict]       = mapped_column(JSONB)
    calc_result: Mapped[dict]       = mapped_column(JSONB)
    rag_chunks:  Mapped[dict]       = mapped_column(JSONB)
    output:      Mapped[dict]       = mapped_column(JSONB)
    created_at:  Mapped[datetime]   = mapped_column(DateTime(timezone=True), default=_utcnow)

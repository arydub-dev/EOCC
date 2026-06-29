"""Database engine, session factory, and declarative base."""

from __future__ import annotations

from collections.abc import Generator
from datetime import datetime

from sqlalchemy import DateTime, Integer, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.config import settings


def _normalize_db_url(url: str) -> str:
    """Ensure the SQLAlchemy URL uses the installed psycopg (v3) driver.

    Managed hosts (Render, Heroku, Railway, …) hand out ``postgres://`` or
    ``postgresql://`` URLs, which SQLAlchemy would route to psycopg2. Only
    psycopg v3 is installed, so rewrite the scheme to ``postgresql+psycopg://``.
    """
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


DATABASE_URL = _normalize_db_url(settings.DATABASE_URL)

connect_args: dict[str, object] = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Declarative base with shared audit columns (timestamps + actor stamps)."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    # Actor stamps for accountability (set by services where a user is in context).
    created_by_id: Mapped[int | None] = mapped_column(Integer)
    updated_by_id: Mapped[int | None] = mapped_column(Integer)


def get_db() -> Generator:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""Generic query helpers: pagination, sorting, search, filtering."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from app.schemas.common import PaginationParams


def apply_sort(
    stmt: Select, model: type, sort_by: str | None, sort_dir: str, default: str = "id"
) -> Select:
    column_name = sort_by if sort_by and hasattr(model, sort_by) else default
    column = getattr(model, column_name, model.id)
    return stmt.order_by(asc(column) if sort_dir == "asc" else desc(column))


def apply_search(stmt: Select, model: type, search: str | None, fields: Sequence[str]) -> Select:
    if not search:
        return stmt
    term = f"%{search.lower()}%"
    clauses = [func.lower(getattr(model, f)).like(term) for f in fields if hasattr(model, f)]
    if clauses:
        stmt = stmt.where(or_(*clauses))
    return stmt


def paginate(
    db: Session,
    stmt: Select,
    model: type,
    params: PaginationParams,
    search_fields: Sequence[str] = (),
    default_sort: str = "id",
) -> tuple[list[Any], int]:
    """Apply search + sort + pagination and return (items, total)."""
    stmt = apply_search(stmt, model, params.search, search_fields)
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.scalar(count_stmt) or 0
    stmt = apply_sort(stmt, model, params.sort_by, params.sort_dir, default_sort)
    stmt = stmt.offset(params.offset).limit(params.page_size)
    items = list(db.scalars(stmt).all())
    return items, total

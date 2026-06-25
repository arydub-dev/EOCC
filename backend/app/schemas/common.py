"""Shared schema primitives: pagination envelopes and query params."""
from __future__ import annotations

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """A standard paginated response envelope."""

    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int

    @classmethod
    def create(cls, items: list[T], total: int, page: int, page_size: int) -> "Page[T]":
        pages = (total + page_size - 1) // page_size if page_size else 0
        return cls(items=items, total=total, page=page, page_size=page_size, pages=pages)


class PaginationParams:
    """Reusable pagination + sorting query dependency."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="1-indexed page number"),
        page_size: int = Query(25, ge=1, le=200, description="Items per page"),
        sort_by: str | None = Query(None, description="Field name to sort by"),
        sort_dir: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction"),
        search: str | None = Query(None, description="Free-text search term"),
    ) -> None:
        self.page = page
        self.page_size = page_size
        self.sort_by = sort_by
        self.sort_dir = sort_dir
        self.search = search

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class Message(BaseModel):
    detail: str


class CountByKey(BaseModel):
    key: str
    count: int
    label: str | None = None


class TrendPoint(BaseModel):
    timestamp: str
    value: float
    label: str | None = None

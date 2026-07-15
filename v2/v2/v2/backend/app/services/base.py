from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseService:
    """Base service providing common functionality."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

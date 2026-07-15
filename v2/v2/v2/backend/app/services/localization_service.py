from __future__ import annotations

from typing import Any
from uuid import UUID

from app.models.models import Localization
from app.repositories import BaseRepository
from app.services.base import BaseService
from sqlalchemy import select


class LocalizationService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.localization_repo = BaseRepository(db, Localization)

    async def get_translation(self, language_code: str, key: str) -> str | None:
        result = await self.db.execute(
            select(Localization).where(Localization.language_code == language_code, Localization.key == key)
        )
        loc = result.scalar_one_or_none()
        return loc.value if loc else None

    async def set_translation(self, language_code: str, key: str, value: str) -> Localization:
        result = await self.db.execute(
            select(Localization).where(Localization.language_code == language_code, Localization.key == key)
        )
        loc = result.scalar_one_or_none()
        if loc:
            loc.value = value
            await self.db.flush()
            await self.db.refresh(loc)
            return loc
        loc = Localization(language_code=language_code, key=key, value=value)
        await self.db.add(loc)
        await self.db.flush()
        await self.db.refresh(loc)
        return loc

    async def get_by_language(self, language_code: str) -> list[Localization]:
        result = await self.db.execute(
            select(Localization).where(Localization.language_code == language_code)
        )
        return list(result.scalars().all())

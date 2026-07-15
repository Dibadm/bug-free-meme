from __future__ import annotations

from sqlalchemy import select

from app.models.models import Setting, FeatureFlag, MaintenanceMode
from app.repositories.base_repository import BaseRepository


class SettingsRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, Setting)

    async def get_by_key(self, key: str) -> Setting | None:
        result = await self.db.execute(
            select(Setting).where(Setting.key == key)
        )
        return result.scalar_one_or_none()

    async def get_public_settings(self) -> list[Setting]:
        result = await self.db.execute(
            select(Setting).where(Setting.is_public == True)
        )
        return list(result.scalars().all())


class FeatureFlagRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, FeatureFlag)

    async def get_by_key(self, key: str) -> FeatureFlag | None:
        result = await self.db.execute(
            select(FeatureFlag).where(FeatureFlag.key == key)
        )
        return result.scalar_one_or_none()

    async def get_enabled_flags(self) -> list[FeatureFlag]:
        result = await self.db.execute(
            select(FeatureFlag).where(FeatureFlag.is_enabled == True)
        )
        return list(result.scalars().all())


class MaintenanceModeRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, MaintenanceMode)

    async def get_current(self) -> MaintenanceMode | None:
        result = await self.db.execute(
            select(MaintenanceMode).where(MaintenanceMode.is_active == True)
        )
        return result.scalar_one_or_none()

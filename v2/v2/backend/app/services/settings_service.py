from __future__ import annotations

from typing import Any
from uuid import UUID

from app.models.models import Setting, FeatureFlag
from app.repositories import FeatureFlagRepository, SettingsRepository
from app.services.base import BaseService


class SettingsService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.settings_repo = SettingsRepository(db)
        self.feature_flag_repo = FeatureFlagRepository(db)

    async def get_setting(self, key: str) -> Setting | None:
        return await self.settings_repo.get_by_key(key)

    async def set_setting(self, key: str, value: str, description: str | None = None, is_public: bool = False) -> Setting:
        setting = await self.settings_repo.get_by_key(key)
        if setting:
            setting.value = value
            setting.description = description
            setting.is_public = is_public
            await self.db.flush()
            await self.db.refresh(setting)
            return setting
        setting = Setting(key=key, value=value, description=description, is_public=is_public)
        return await self.settings_repo.create(setting)

    async def get_public_settings(self) -> list[Setting]:
        return await self.settings_repo.get_public_settings()

    async def is_feature_enabled(self, key: str) -> bool:
        flag = await self.feature_flag_repo.get_by_key(key)
        return flag.is_enabled if flag else False

    async def set_feature_flag(self, key: str, is_enabled: bool, description: str | None = None) -> FeatureFlag:
        flag = await self.feature_flag_repo.get_by_key(key)
        if flag:
            flag.is_enabled = is_enabled
            flag.description = description
            await self.db.flush()
            await self.db.refresh(flag)
            return flag
        flag = FeatureFlag(key=key, is_enabled=is_enabled, description=description)
        return await self.feature_flag_repo.create(flag)

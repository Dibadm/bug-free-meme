from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.core.exceptions import ValidationError
from app.models.models import NotificationPreference
from app.repositories import NotificationPreferenceRepository, UserProfileRepository
from app.services.base import BaseService


class ProfileService(BaseService):
    def __init__(self, db: Any) -> None:
        super().__init__(db)
        self.profile_repo = UserProfileRepository(db)
        self.notification_pref_repo = NotificationPreferenceRepository(db)

    async def update_profile(self, user_id: UUID, **fields: Any) -> Any:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if not profile:
            from app.models.models import UserProfile
            profile = UserProfile(user_id=user_id)
            await self.profile_repo.create(profile)

        allowed_fields = {"avatar_url", "display_name", "privacy_settings"}
        for key, value in fields.items():
            if key in allowed_fields and value is not None:
                setattr(profile, key, value)

        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    async def update_notification_preferences(self, user_id: UUID, preferences: dict[str, bool]) -> list[NotificationPreference]:
        updated = []
        for notification_type, enabled in preferences.items():
            existing = await self.notification_pref_repo.get_by_user_and_type(user_id, notification_type)
            if existing:
                existing.enabled = enabled
                await self.db.flush()
                await self.db.refresh(existing)
                updated.append(existing)
            else:
                pref = NotificationPreference(user_id=user_id, notification_type=notification_type, enabled=enabled)
                await self.notification_pref_repo.create(pref)
                updated.append(pref)
        return updated

    async def get_notification_preferences(self, user_id: UUID) -> list[NotificationPreference]:
        return await self.notification_pref_repo.get_by_user_id(user_id)

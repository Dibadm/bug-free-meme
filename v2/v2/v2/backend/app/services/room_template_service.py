from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.exceptions import ValidationError
from app.models.models import RoomTemplate, RoomStatus
from app.repositories import RoomTemplateRepository
from app.services.base import BaseService


class RoomTemplateService(BaseService):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
        self.template_repo = RoomTemplateRepository(db)

    async def create_template(self, **fields: Any) -> RoomTemplate:
        if fields.get("entry_fee", 0) <= 0:
            raise ValidationError("Entry fee must be positive")
        if fields.get("min_players", 0) < 1:
            raise ValidationError("Minimum players must be at least 1")
        if fields.get("max_players", 0) < fields.get("min_players", 0):
            raise ValidationError("Maximum players must be greater than minimum players")
        total_percentage = (
            fields.get("house_percentage", 0)
            + fields.get("referral_percentage", 0)
            + fields.get("bonus_percentage", 0)
            + fields.get("jackpot_percentage", 0)
        )
        if total_percentage > 100:
            raise ValidationError("Total percentage cannot exceed 100%")

        template = RoomTemplate(**fields, status=RoomStatus.DRAFT)
        return await self.template_repo.create(template)

    async def activate_template(self, template_id: UUID) -> RoomTemplate | None:
        template = await self.template_repo.get_by_id(template_id)
        if not template:
            return None
        template.status = RoomStatus.ACTIVE
        await self.db.flush()
        await self.db.refresh(template)
        return template

    async def get_active_templates(self) -> list[RoomTemplate]:
        return await self.template_repo.get_active_templates()

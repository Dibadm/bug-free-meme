from __future__ import annotations

from sqlalchemy import select

from app.models.models import PaymentSettings
from app.repositories import BaseRepository


class PaymentSettingsRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, PaymentSettings)

    async def get_active(self) -> PaymentSettings | None:
        result = await self.db.execute(
            select(PaymentSettings).where(PaymentSettings.is_active == True).limit(1)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[PaymentSettings]:
        result = await self.db.execute(
            select(PaymentSettings).order_by(PaymentSettings.created_at.desc())
        )
        return list(result.scalars().all())

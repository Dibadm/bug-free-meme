from __future__ import annotations

from sqlalchemy import select

from app.models.models import ReferralAccount, ReferralReward
from app.repositories import BaseRepository


class ReferralRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, ReferralAccount)

    async def get_by_referrer_id(self, referrer_id: Any) -> list[ReferralAccount]:
        result = await self.db.execute(
            select(ReferralAccount).where(ReferralAccount.referrer_id == referrer_id)
        )
        return list(result.scalars().all())

    async def get_by_referred_id(self, referred_id: Any) -> list[ReferralAccount]:
        result = await self.db.execute(
            select(ReferralAccount).where(ReferralAccount.referred_id == referred_id)
        )
        return list(result.scalars().all())

    async def get_referral(self, referrer_id: Any, referred_id: Any) -> ReferralAccount | None:
        result = await self.db.execute(
            select(ReferralAccount).where(
                ReferralAccount.referrer_id == referrer_id,
                ReferralAccount.referred_id == referred_id,
            )
        )
        return result.scalar_one_or_none()


class ReferralRewardRepository(BaseRepository):
    def __init__(self, db: Any) -> None:
        super().__init__(db, ReferralReward)

    async def get_by_referral_id(self, referral_id: Any) -> list[ReferralReward]:
        result = await self.db.execute(
            select(ReferralReward).where(ReferralReward.referral_id == referral_id)
        )
        return list(result.scalars().all())

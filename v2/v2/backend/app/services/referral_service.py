from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.core.exceptions import ValidationError
from app.models.models import ReferralAccount, ReferralReward, User, UserRole, UserStatus
from app.repositories import ReferralRepository, ReferralRewardRepository, UserRepository
from app.services.audit_service import AuditService
from app.services.base import BaseService


class ReferralService(BaseService):
    def __init__(self, db: Any) -> None:
        super().__init__(db)
        self.referral_repo = ReferralRepository(db)
        self.referral_reward_repo = ReferralRewardRepository(db)
        self.user_repo = UserRepository(db)
        self.audit_service = AuditService(db)

    async def apply_referral(self, user_id: UUID, referral_code: str) -> ReferralAccount:
        if not referral_code:
            raise ValidationError("Referral code is required")

        referrer = await self.user_repo.find_one(referral_code=referral_code, deleted_at=None)
        if not referrer:
            raise ValidationError("Invalid referral code")

        if referrer.id == user_id:
            raise ValidationError("Cannot refer yourself")

        existing = await self.referral_repo.get_referral(referrer.id, user_id)
        if existing:
            raise ValidationError("Referral relationship already exists")

        referral = ReferralAccount(
            referrer_id=referrer.id,
            referred_id=user_id,
            reward_percentage=10.0,
            total_earned=0,
        )
        await self.referral_repo.create(referral)

        await self.audit_service.log(
            actor_id=user_id,
            action="referral_applied",
            entity_type="referral",
            entity_id=referral.id,
            new_value={"referrer_id": str(referrer.id), "referred_id": str(user_id)},
        )

        return referral

    async def get_user_referrals(self, user_id: UUID) -> list[ReferralAccount]:
        return await self.referral_repo.get_by_referrer_id(user_id)

    async def get_referred_by(self, user_id: UUID) -> list[ReferralAccount]:
        return await self.referral_repo.get_by_referred_id(user_id)

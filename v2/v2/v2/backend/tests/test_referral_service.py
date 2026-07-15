from __future__ import annotations

import pytest
from decimal import Decimal
from uuid import uuid4

from app.core.exceptions import ValidationError
from app.services import ReferralService


@pytest.mark.asyncio
async def test_create_referral(db_session: Any) -> None:
    service = ReferralService(db_session)
    referrer_id = uuid4()
    referred_id = uuid4()
    referral = await service.create_referral(referrer_id, referred_id, Decimal("5.00"))
    assert referral.referrer_id == referrer_id
    assert referral.referred_id == referred_id
    assert referral.reward_percentage == Decimal("5.00")


@pytest.mark.asyncio
async def test_create_duplicate_referral_fails(db_session: Any) -> None:
    service = ReferralService(db_session)
    referrer_id = uuid4()
    referred_id = uuid4()
    await service.create_referral(referrer_id, referred_id, Decimal("5.00"))
    with pytest.raises(ValidationError, match="already exists"):
        await service.create_referral(referrer_id, referred_id, Decimal("5.00"))


@pytest.mark.asyncio
async def test_get_referral_accounts(db_session: Any) -> None:
    service = ReferralService(db_session)
    referrer_id = uuid4()
    referred_id = uuid4()
    await service.create_referral(referrer_id, referred_id, Decimal("5.00"))

    referrer_accounts = await service.get_referrer_accounts(referrer_id)
    assert len(referrer_accounts) == 1

    referred_accounts = await service.get_referred_accounts(referred_id)
    assert len(referred_accounts) == 1

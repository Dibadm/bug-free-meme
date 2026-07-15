from __future__ import annotations

from uuid import uuid4

import pytest

from app.core.exceptions import ValidationError
from app.models.models import User, UserRole, UserStatus
from app.services import AuthService, ReferralService
from app.services.profile_service import ProfileService


@pytest.mark.asyncio
async def test_session_multiple_devices(db_session: Any) -> None:
    auth_service = AuthService(db_session)
    user = await auth_service.user_repo.create(
        User(telegram_id=444444, username="multiuser", status=UserStatus.ACTIVE, role=UserRole.PLAYER)
    )

    session1 = await auth_service.create_session(user, "token_a")
    session2 = await auth_service.create_session(user, "token_b")

    sessions = await auth_service.get_user_sessions(user.id)
    assert len(sessions) == 2

    await auth_service.logout(session1.id)
    sessions = await auth_service.get_user_sessions(user.id)
    assert len(sessions) == 1


@pytest.mark.asyncio
async def test_session_revocation(db_session: Any) -> None:
    auth_service = AuthService(db_session)
    user = await auth_service.user_repo.create(
        User(telegram_id=555555, username="revokeuser", status=UserStatus.ACTIVE, role=UserRole.PLAYER)
    )

    session = await auth_service.create_session(user, "token_revoke")
    await auth_service.logout_all(user.id)

    sessions = await auth_service.get_user_sessions(user.id)
    assert len(sessions) == 0


@pytest.mark.asyncio
async def test_referral_apply_success(db_session: Any) -> None:
    auth_service = AuthService(db_session)
    referrer = await auth_service.user_repo.create(
        User(telegram_id=666666, username="referrer", status=UserStatus.ACTIVE, role=UserRole.PLAYER, referral_code="REFCODE1")
    )
    referred = await auth_service.user_repo.create(
        User(telegram_id=777777, username="referred", status=UserStatus.ACTIVE, role=UserRole.PLAYER)
    )

    referral_service = ReferralService(db_session)
    referral = await referral_service.apply_referral(referred.id, "REFCODE1")
    assert referral.referrer_id == referrer.id
    assert referral.referred_id == referred.id


@pytest.mark.asyncio
async def test_referral_self_referral_blocked(db_session: Any) -> None:
    auth_service = AuthService(db_session)
    user = await auth_service.user_repo.create(
        User(telegram_id=888888, username="selfref", status=UserStatus.ACTIVE, role=UserRole.PLAYER, referral_code="SELFREF")
    )

    referral_service = ReferralService(db_session)
    with pytest.raises(ValidationError, match="Cannot refer yourself"):
        await referral_service.apply_referral(user.id, "SELFREF")


@pytest.mark.asyncio
async def test_referral_invalid_code(db_session: Any) -> None:
    auth_service = AuthService(db_session)
    user = await auth_service.user_repo.create(
        User(telegram_id=999999, username="invalidref", status=UserStatus.ACTIVE, role=UserRole.PLAYER)
    )

    referral_service = ReferralService(db_session)
    with pytest.raises(ValidationError, match="Invalid referral code"):
        await referral_service.apply_referral(user.id, "INVALIDCODE")


@pytest.mark.asyncio
async def test_profile_update(db_session: Any) -> None:
    auth_service = AuthService(db_session)
    user = await auth_service.user_repo.create(
        User(telegram_id=101010, username="profileuser", status=UserStatus.ACTIVE, role=UserRole.PLAYER)
    )

    profile_service = ProfileService(db_session)
    profile = await profile_service.update_profile(
        user.id,
        avatar_url="https://example.com/avatar.png",
        display_name="Display Name",
    )
    assert profile.avatar_url == "https://example.com/avatar.png"
    assert profile.display_name == "Display Name"

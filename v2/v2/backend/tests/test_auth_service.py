from __future__ import annotations

import hashlib
import hmac
import time
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.core.exceptions import ValidationError
from app.models.models import User, UserRole, UserStatus
from app.services import AuthService
from app.services.auth_service import AuthService as _AuthService


@pytest.mark.asyncio
async def test_validate_telegram_init_data_success(db_session: Any) -> None:
    secret = "test_secret"
    params = {"id": "123", "first_name": "Test", "auth_date": str(int(time.time()))}
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(secret.encode(), b"WebAppData", hashlib.sha256).digest()
    hash_value = hmac.new(secret_key, data_check.encode(), hashlib.sha256).hexdigest()
    init_data = "&".join(f"{k}={v}" for k, v in sorted(params.items())) + f"&hash={hash_value}"

    result = _AuthService.validate_telegram_init_data(init_data, secret)
    assert result["id"] == "123"


@pytest.mark.asyncio
async def test_validate_telegram_init_data_expired(db_session: Any) -> None:
    secret = "test_secret"
    params = {"id": "123", "first_name": "Test", "auth_date": str(int(time.time()) - 90000)}
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(secret.encode(), b"WebAppData", hashlib.sha256).digest()
    hash_value = hmac.new(secret_key, data_check.encode(), hashlib.sha256).hexdigest()
    init_data = "&".join(f"{k}={v}" for k, v in sorted(params.items())) + f"&hash={hash_value}"

    with pytest.raises(ValidationError, match="expired"):
        _AuthService.validate_telegram_init_data(init_data, secret)


@pytest.mark.asyncio
async def test_authenticate_new_user(db_session: Any) -> None:
    auth_service = AuthService(db_session)
    secret = "test_secret"
    telegram_id = 111111
    params = {"id": str(telegram_id), "first_name": "New", "auth_date": str(int(time.time()))}
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(secret.encode(), b"WebAppData", hashlib.sha256).digest()
    hash_value = hmac.new(secret_key, data_check.encode(), hashlib.sha256).hexdigest()
    init_data = "&".join(f"{k}={v}" for k, v in sorted(params.items())) + f"&hash={hash_value}"

    user, is_new = await auth_service.authenticate(init_data, secret)
    assert is_new is True
    assert user.telegram_id == telegram_id
    assert user.role == UserRole.PLAYER
    assert user.referral_code is not None


@pytest.mark.asyncio
async def test_authenticate_returning_user(db_session: Any) -> None:
    auth_service = AuthService(db_session)
    secret = "test_secret"
    telegram_id = 222222
    params = {"id": str(telegram_id), "first_name": "Returning", "auth_date": str(int(time.time()))}
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret_key = hmac.new(secret.encode(), b"WebAppData", hashlib.sha256).digest()
    hash_value = hmac.new(secret_key, data_check.encode(), hashlib.sha256).hexdigest()
    init_data = "&".join(f"{k}={v}" for k, v in sorted(params.items())) + f"&hash={hash_value}"

    user1, is_new1 = await auth_service.authenticate(init_data, secret)
    assert is_new1 is True

    user2, is_new2 = await auth_service.authenticate(init_data, secret)
    assert is_new2 is False
    assert user1.id == user2.id
    assert user2.last_login is not None


@pytest.mark.asyncio
async def test_session_lifecycle(db_session: Any) -> None:
    auth_service = AuthService(db_session)
    user = await auth_service.user_repo.create(
        User(telegram_id=333333, username="sessionuser", status=UserStatus.ACTIVE, role=UserRole.PLAYER)
    )

    session = await auth_service.create_session(user, "token_hash_123")
    assert session.revoked_at is None

    found = await auth_service.get_session_by_token("token_hash_123")
    assert found is not None
    assert found.id == session.id

    await auth_service.logout(session.id)
    found = await auth_service.get_session_by_token("token_hash_123")
    assert found is None

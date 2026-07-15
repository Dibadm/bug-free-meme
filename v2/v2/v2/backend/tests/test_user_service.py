from __future__ import annotations

import pytest
from uuid import uuid4

from app.models.models import User
from app.repositories import UserRepository
from app.services import UserService


@pytest.mark.asyncio
async def test_user_repository_get_by_telegram_id(db_session: Any) -> None:
    repo = UserRepository(db_session)
    user = User(telegram_id=12345, username="testuser")
    db_session.add(user)
    await db_session.flush()

    found = await repo.get_by_telegram_id(12345)
    assert found is not None
    assert found.username == "testuser"


@pytest.mark.asyncio
async def test_user_service_get_or_create(db_session: Any) -> None:
    service = UserService(db_session)
    user = await service.get_or_create_user(telegram_id=99999, username="newuser", first_name="Test")
    assert user.telegram_id == 99999
    assert user.username == "newuser"

    user2 = await service.get_or_create_user(telegram_id=99999, username="updated")
    assert user2.id == user.id
    assert user2.username == "newuser"


@pytest.mark.asyncio
async def test_user_service_ban_and_activate(db_session: Any) -> None:
    service = UserService(db_session)
    user = await service.get_or_create_user(telegram_id=88888, username="bana")
    assert user.status == "active"

    banned = await service.ban_user(user.id)
    assert banned.status == "banned"

    activated = await service.activate_user(user.id)
    assert activated.status == "active"

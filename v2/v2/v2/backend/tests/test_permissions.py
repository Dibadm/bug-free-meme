from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.core.permissions import PermissionMiddleware
from app.models.models import User, UserRole


@pytest.mark.asyncio
async def test_player_cannot_access_admin() -> None:
    user = User(role=UserRole.PLAYER)
    checker = PermissionMiddleware.require_role(UserRole.ADMIN)
    with pytest.raises(HTTPException) as exc_info:
        await checker(user)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_access_admin() -> None:
    user = User(role=UserRole.ADMIN)
    checker = PermissionMiddleware.require_role(UserRole.ADMIN)
    result = await checker(user)
    assert result == user


@pytest.mark.asyncio
async def test_super_admin_can_access_all() -> None:
    user = User(role=UserRole.SUPER_ADMIN)
    for role in [UserRole.PLAYER, UserRole.MODERATOR, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        checker = PermissionMiddleware.require_role(role)
        result = await checker(user)
        assert result == user


@pytest.mark.asyncio
async def test_moderator_cannot_access_admin() -> None:
    user = User(role=UserRole.MODERATOR)
    checker = PermissionMiddleware.require_role(UserRole.ADMIN)
    with pytest.raises(HTTPException) as exc_info:
        await checker(user)
    assert exc_info.value.status_code == 403

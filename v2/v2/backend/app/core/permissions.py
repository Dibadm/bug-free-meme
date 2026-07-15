from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status

from app.models.models import UserRole


class PermissionMiddleware:
    ROLE_HIERARCHY = {
        UserRole.PLAYER: 0,
        UserRole.MODERATOR: 1,
        UserRole.ADMIN: 2,
        UserRole.SUPER_ADMIN: 3,
    }

    @classmethod
    def has_permission(cls, user_role: UserRole, required_role: UserRole) -> bool:
        return cls.ROLE_HIERARCHY.get(user_role, 0) >= cls.ROLE_HIERARCHY.get(required_role, 0)

    @classmethod
    def require_role(cls, required_role: UserRole):
        async def check_permission(user: Any = None) -> Any:
            if user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
            if not cls.has_permission(user.role, required_role):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
            return user
        return check_permission

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.logging import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        logger.info("request_started", method=request.method, path=str(request.url.path))
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        logger.info("request_finished", method=request.method, path=str(request.url.path), status_code=response.status_code, duration_ms=round(process_time * 1000, 2))
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any, rate_limit: int = 100, window: int = 60) -> None:
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window = window
        self.visitors: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        if client_ip not in self.visitors:
            self.visitors[client_ip] = []
        self.visitors[client_ip] = [t for t in self.visitors[client_ip] if now - t < self.window]
        if len(self.visitors[client_ip]) >= self.rate_limit:
            return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content={"detail": "Rate limit exceeded"})
        self.visitors[client_ip].append(now)
        return await call_next(request)


from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError
from app.models.models import UserStatus
from app.services.auth_service import AuthService


async def get_current_user(
    token: str,
    db: AsyncSession,
    auth_service: AuthService,
) -> Any:
    session = await auth_service.get_session_by_token(token)
    if not session or session.revoked_at or session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

    user = await auth_service.user_repo.get_by_id(session.user_id)
    if not user or user.status in (UserStatus.BANNED, UserStatus.DELETED):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not allowed")

    return user


async def get_optional_user(
    token: str | None,
    db: AsyncSession,
    auth_service: AuthService,
) -> Any | None:
    if not token:
        return None
    try:
        return await get_current_user(token, db, auth_service)
    except HTTPException:
        return None

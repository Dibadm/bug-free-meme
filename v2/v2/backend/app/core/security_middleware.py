from __future__ import annotations

import hashlib
import hmac
import time
from collections import defaultdict
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger


logger = get_logger(__name__)


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Any:
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            header = request.headers.get("x-csrf-token")
            cookie = request.cookies.get("csrf_token")
            if not header or not cookie or not hmac.compare_digest(header, cookie):
                return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "CSRF token invalid"})
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Any) -> Any:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Allows Telegram to iframe your Web App (Critical for Mini Apps!)
        response.headers["X-Frame-Options"] = "ALLOW-FROM https://web.telegram.org/"
        
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Opens CSP to let Telegram Web App talk to your Render backend secure socket & api
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "frame-ancestors 'self' https://web.telegram.org https://*.web.telegram.org; "
            "connect-src 'self' https://bug-free-meme-1.onrender.com wss://bug-free-meme-1.onrender.com https://api.telegram.org;"
        )
        return response
    async def dispatch(self, request: Request, call_next: Any) -> Any:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


class ConnectionThrottleMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any, max_connections_per_ip: int = 100, window: int = 60) -> None:
        super().__init__(app)
        self.max_connections_per_ip = max_connections_per_ip
        self.window = window
        self.connections: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        self.connections[client_ip] = [t for t in self.connections[client_ip] if now - t < self.window]
        if len(self.connections[client_ip]) >= self.max_connections_per_ip:
            return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content={"detail": "Connection throttle exceeded"})
        self.connections[client_ip].append(now)
        return await call_next(request)


class ReplayAttackPreventionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Any) -> None:
        super().__init__(app)
        self.processed_nonces: dict[str, float] = {}

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        nonce = request.headers.get("X-Request-Nonce")
        if nonce:
            now = time.time()
            if nonce in self.processed_nonces and now - self.processed_nonces[nonce] < 300:
                return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": "Replay detected"})
            self.processed_nonces[nonce] = now
        return await call_next(request)

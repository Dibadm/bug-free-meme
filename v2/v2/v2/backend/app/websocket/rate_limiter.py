from __future__ import annotations

import json
import time
from collections import defaultdict
from threading import Lock
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class WebSocketRateLimiter:
    _instance: WebSocketRateLimiter | None = None
    _lock = Lock()

    def __new__(cls) -> WebSocketRateLimiter:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self._windows: dict[str, list[float]] = defaultdict(list)
        self._max_requests = 120
        self._window_seconds = 60

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        self._windows[key] = [t for t in self._windows.get(key, []) if now - t < self._window_seconds]
        if len(self._windows[key]) >= self._max_requests:
            logger.warning("ws_rate_limited", key=key)
            return False
        self._windows[key].append(now)
        return True

    def reset(self, key: str) -> None:
        self._windows.pop(key, None)

    def get_remaining(self, key: str) -> int:
        now = time.time()
        self._windows[key] = [t for t in self._windows.get(key, []) if now - t < self._window_seconds]
        return max(0, self._max_requests - len(self._windows[key]))


ws_rate_limiter = WebSocketRateLimiter()

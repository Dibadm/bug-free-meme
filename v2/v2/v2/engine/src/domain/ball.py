from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from engine.src.domain import GameLifecycleState


class BallEngine:
    def __init__(self, seed: str = "", interval_seconds: int = 3) -> None:
        self.seed = seed or secrets.token_hex(32)
        self.seed_hash = hashlib.sha256(self.seed.encode()).hexdigest()
        self.interval_seconds = interval_seconds
        self.called_numbers: list[int] = []
        self.remaining_numbers: list[int] = list(range(1, 76))
        self.current_number: int | None = None
        self.started_at: datetime | None = None
        self.paused_at: datetime | None = None
        self._rng: Any = None
        self._initialize_rng()

    def _initialize_rng(self) -> None:
        self._rng = secrets.SystemRandom()
        self._rng.seed(self.seed.encode())
        self.remaining_numbers = list(range(1, 76))
        self._rng.shuffle(self.remaining_numbers)

    def call_next(self) -> int | None:
        if not self.remaining_numbers:
            return None
        if self.started_at is None:
            self.started_at = datetime.now(timezone.utc)
        number = self.remaining_numbers.pop(0)
        self.called_numbers.append(number)
        self.current_number = number
        return number

    def pause(self) -> None:
        if self.paused_at is None:
            self.paused_at = datetime.now(timezone.utc)

    def resume(self) -> None:
        self.paused_at = None

    def is_paused(self) -> bool:
        return self.paused_at is not None

    def get_called_count(self) -> int:
        return len(self.called_numbers)

    def get_remaining_count(self) -> int:
        return len(self.remaining_numbers)

    def verify_sequence(self, seed: str) -> bool:
        expected_hash = hashlib.sha256(seed.encode()).hexdigest()
        if expected_hash != self.seed_hash:
            return False
        rng = secrets.SystemRandom()
        rng.seed(seed.encode())
        expected_sequence = list(range(1, 76))
        rng.shuffle(expected_sequence)
        return self.called_numbers == expected_sequence[: len(self.called_numbers)]

    def get_state(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "seed_hash": self.seed_hash,
            "called_numbers": list(self.called_numbers),
            "current_number": self.current_number,
            "remaining_count": self.get_remaining_count(),
            "interval_seconds": self.interval_seconds,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "paused_at": self.paused_at.isoformat() if self.paused_at else None,
        }

    @classmethod
    def from_state(cls, state: dict[str, Any]) -> BallEngine:
        engine = cls(seed=state["seed"], interval_seconds=state.get("interval_seconds", 3))
        engine.seed_hash = state["seed_hash"]
        engine.called_numbers = list(state["called_numbers"])
        engine.current_number = state.get("current_number")
        engine.started_at = datetime.fromisoformat(state["started_at"]) if state.get("started_at") else None
        engine.paused_at = datetime.fromisoformat(state["paused_at"]) if state.get("paused_at") else None
        engine.remaining_numbers = [n for n in range(1, 76) if n not in engine.called_numbers]
        return engine

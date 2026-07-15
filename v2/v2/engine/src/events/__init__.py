from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine, TypeVar
from uuid import UUID, uuid4


T = TypeVar("T")


@dataclass
class Event:
    event_id: UUID = field(default_factory=uuid4)
    event_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    game_id: UUID | None = None
    room_id: UUID | None = None
    user_id: UUID | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    sequence: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "game_id": str(self.game_id) if self.game_id else None,
            "room_id": str(self.room_id) if self.room_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "payload": self.payload,
            "sequence": self.sequence,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Event:
        return cls(
            event_id=UUID(data["event_id"]),
            event_type=data["event_type"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            game_id=UUID(data["game_id"]) if data.get("game_id") else None,
            room_id=UUID(data["room_id"]) if data.get("room_id") else None,
            user_id=UUID(data["user_id"]) if data.get("user_id") else None,
            payload=data.get("payload", {}),
            sequence=data.get("sequence", 0),
        )


EventHandler = Callable[[Event], Coroutine[Any, Any, None]]


class EventBus:
    def __init__(self) -> None:
        self.handlers: dict[str, list[EventHandler]] = {}
        self.event_log: list[Event] = []
        self.sequence_counter: int = 0

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    async def publish(self, event: Event) -> None:
        event.sequence = self.sequence_counter
        self.sequence_counter += 1
        self.event_log.append(event)
        handlers = self.handlers.get(event.event_type, [])
        for handler in handlers:
            await handler(event)

    def get_event_log(self) -> list[Event]:
        return list(self.event_log)

    def clear(self) -> None:
        self.event_log.clear()
        self.sequence_counter = 0

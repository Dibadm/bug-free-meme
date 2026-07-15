from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID


@dataclass
class GameReplay:
    game_id: UUID
    seed: str
    events: list[dict[str, Any]]
    final_state: dict[str, Any]
    started_at: datetime
    finished_at: datetime
    duration_seconds: float

    def to_json(self) -> str:
        return json.dumps({
            "game_id": str(self.game_id),
            "seed": self.seed,
            "events": self.events,
            "final_state": self.final_state,
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat(),
            "duration_seconds": self.duration_seconds,
        })

    @classmethod
    def from_json(cls, data: str) -> GameReplay:
        obj = json.loads(data)
        return cls(
            game_id=UUID(obj["game_id"]),
            seed=obj["seed"],
            events=obj["events"],
            final_state=obj["final_state"],
            started_at=datetime.fromisoformat(obj["started_at"]),
            finished_at=datetime.fromisoformat(obj["finished_at"]),
            duration_seconds=obj["duration_seconds"],
        )


class ReplayEngine:
    def __init__(self) -> None:
        self.recorded_events: list[dict[str, Any]] = []

    def record_event(self, event_type: str, payload: dict[str, Any], timestamp: datetime | None = None) -> None:
        self.recorded_events.append({
            "event_type": event_type,
            "timestamp": (timestamp or datetime.now(timezone.utc)).isoformat(),
            "payload": payload,
        })

    def build_replay(self, game_id: UUID, seed: str, final_state: dict[str, Any], started_at: datetime, finished_at: datetime) -> GameReplay:
        return GameReplay(
            game_id=game_id,
            seed=seed,
            events=list(self.recorded_events),
            final_state=final_state,
            started_at=started_at,
            finished_at=finished_at,
            duration_seconds=(finished_at - started_at).total_seconds(),
        )

    def clear(self) -> None:
        self.recorded_events.clear()

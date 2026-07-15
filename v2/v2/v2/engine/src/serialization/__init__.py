from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID


@dataclass
class GameSnapshot:
    game_id: UUID
    room_id: UUID
    state: str
    seed: str
    seed_hash: str
    called_numbers: list[int]
    current_number: int | None
    started_at: datetime | None
    finished_at: datetime | None
    winner_id: UUID | None
    winning_pattern: str | None
    prize_amount: float | None
    players: dict[str, Any]
    cards: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    snapshot_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "game_id": str(self.game_id),
            "room_id": str(self.room_id),
            "state": self.state,
            "seed": self.seed,
            "seed_hash": self.seed_hash,
            "called_numbers": list(self.called_numbers),
            "current_number": self.current_number,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "winner_id": str(self.winner_id) if self.winner_id else None,
            "winning_pattern": self.winning_pattern,
            "prize_amount": self.prize_amount,
            "players": self.players,
            "cards": self.cards,
            "metadata": self.metadata,
            "snapshot_at": self.snapshot_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GameSnapshot:
        return cls(
            game_id=UUID(data["game_id"]),
            room_id=UUID(data["room_id"]),
            state=data["state"],
            seed=data["seed"],
            seed_hash=data["seed_hash"],
            called_numbers=list(data["called_numbers"]),
            current_number=data.get("current_number"),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            finished_at=datetime.fromisoformat(data["finished_at"]) if data.get("finished_at") else None,
            winner_id=UUID(data["winner_id"]) if data.get("winner_id") else None,
            winning_pattern=data.get("winning_pattern"),
            prize_amount=data.get("prize_amount"),
            players=data.get("players", {}),
            cards=data.get("cards", {}),
            metadata=data.get("metadata", {}),
            snapshot_at=datetime.fromisoformat(data.get("snapshot_at", datetime.now(timezone.utc).isoformat())),
        )


class Serializer:
    @staticmethod
    def serialize_snapshot(snapshot: GameSnapshot) -> str:
        return json.dumps(snapshot.to_dict())

    @staticmethod
    def deserialize_snapshot(data: str) -> GameSnapshot:
        return GameSnapshot.from_dict(json.loads(data))

    @staticmethod
    def serialize_event_log(events: list[Any]) -> str:
        return json.dumps([e.to_dict() if hasattr(e, "to_dict") else str(e) for e in events])

    @staticmethod
    def deserialize_event_log(data: str) -> list[dict[str, Any]]:
        return json.loads(data)

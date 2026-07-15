from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from engine.src.domain import GameLifecycleState


class CardMarkStatus(str, Enum):
    UNMARKED = "unmarked"
    MARKED = "marked"
    AUTO_MARKED = "auto_marked"
    UNDO = "undo"


@dataclass
class Card:
    id: UUID = field(default_factory=uuid4)
    numbers: list[int] = field(default_factory=list)
    pattern_index: int = 0
    marks: dict[int, CardMarkStatus] = field(default_factory=dict)
    room_id: UUID = field(default_factory=uuid4)
    owner_id: UUID | None = None
    is_sold: bool = False
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if not self.fingerprint and self.numbers:
            self.fingerprint = self._compute_fingerprint()

    def _compute_fingerprint(self) -> str:
        import hashlib
        data = "|".join(str(n) for n in self.numbers) + f"|pattern={self.pattern_index}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def mark(self, number: int, auto: bool = False) -> bool:
        if number not in self.numbers:
            return False
        if number in self.marks and self.marks[number] != CardMarkStatus.UNDO:
            return True
        self.marks[number] = CardMarkStatus.AUTO_MARKED if auto else CardMarkStatus.MARKED
        return True

    def undo_mark(self, number: int) -> bool:
        if number in self.marks:
            self.marks[number] = CardMarkStatus.UNDO
            return True
        return False

    def is_marked(self, number: int) -> bool:
        return number in self.marks and self.marks[number] != CardMarkStatus.UNDO

    def get_marked_numbers(self) -> list[int]:
        return [n for n, status in self.marks.items() if status != CardMarkStatus.UNDO]

    def verify(self, called_numbers: set[int]) -> bool:
        for number in self.numbers:
            if number != 0 and number not in called_numbers:
                return False
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "room_id": str(self.room_id),
            "numbers": list(self.numbers),
            "pattern_index": self.pattern_index,
            "marks": {str(k): v.value for k, v in self.marks.items()},
            "owner_id": str(self.owner_id) if self.owner_id else None,
            "is_sold": self.is_sold,
            "fingerprint": self.fingerprint,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Card:
        marks = {int(k): CardMarkStatus(v) for k, v in data.get("marks", {}).items()}
        return cls(
            id=UUID(data["id"]),
            room_id=UUID(data["room_id"]),
            numbers=list(data["numbers"]),
            pattern_index=data.get("pattern_index", 0),
            marks=marks,
            owner_id=UUID(data["owner_id"]) if data.get("owner_id") else None,
            is_sold=data.get("is_sold", False),
            fingerprint=data.get("fingerprint", ""),
        )


class CardEngine:
    @staticmethod
    def generate_card(room_id: UUID, pattern_index: int = 0) -> Card:
        rng = secrets.SystemRandom()
        numbers = [0] * 25
        ranges = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
        for col in range(5):
            start, end = ranges[col]
            col_numbers = rng.sample(range(start, end + 1), 5)
            for row in range(5):
                index = row * 5 + col
                numbers[index] = col_numbers[row]
        numbers[12] = 0
        card = Card(room_id=room_id, numbers=numbers, pattern_index=pattern_index)
        return card

    @staticmethod
    def generate_cards(room_id: UUID, count: int, pattern_index: int = 0) -> list[Card]:
        return [CardEngine.generate_card(room_id, pattern_index) for _ in range(count)]

    @staticmethod
    def validate_card(card: Card) -> bool:
        if len(card.numbers) != 25:
            return False
        ranges = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
        for col in range(5):
            start, end = ranges[col]
            col_values = [card.numbers[row * 5 + col] for row in range(5)]
            col_values = [v for v in col_values if v != 0]
            if len(col_values) != len(set(col_values)):
                return False
            for v in col_values:
                if v < start or v > end:
                    return False
        if card.numbers[12] != 0:
            return False
        return True

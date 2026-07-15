from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from engine.src.domain.card import Card


@dataclass
class PatternResult:
    pattern_name: str
    matched_positions: list[tuple[int, int]]
    is_complete: bool
    matched_numbers: list[int] = field(default_factory=list)


class RuleEngine:
    PATTERNS: dict[str, list[tuple[int, int]]] = {
        "four_corners": [(0, 0), (0, 4), (4, 0), (4, 4)],
        "one_line": [],
        "two_lines": [],
        "full_house": [(i, j) for i in range(5) for j in range(5)],
        "x_pattern": [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (0, 4), (1, 3), (3, 1), (4, 0)],
        "cross": [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (2, 0), (2, 1), (2, 3), (2, 4)],
        "diamond": [(2, 0), (1, 1), (3, 1), (0, 2), (4, 2), (1, 3), (3, 3), (2, 4)],
        "letter_h": [(0, 0), (4, 0), (0, 1), (4, 1), (2, 1), (2, 2), (2, 3), (0, 4), (4, 4), (0, 3), (4, 3)],
        "letter_t": [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 2), (3, 2), (4, 2)],
    }

    @classmethod
    def check_pattern(cls, card: Card, pattern_name: str, called_numbers: set[int]) -> PatternResult | None:
        if pattern_name not in cls.PATTERNS:
            return None

        positions = cls.PATTERNS[pattern_name]

        if pattern_name == "one_line":
            for row in range(5):
                if all(cls._is_marked(card, row, col, called_numbers) for col in range(5)):
                    matched = [card.numbers[row * 5 + col] for col in range(5) if card.numbers[row * 5 + col] != 0]
                    return PatternResult(pattern_name="one_line", matched_positions=[(row, col) for col in range(5)], is_complete=True, matched_numbers=matched)
            return None

        if pattern_name == "two_lines":
            matched = []
            for row in range(5):
                if all(cls._is_marked(card, row, col, called_numbers) for col in range(5)):
                    matched.extend([(row, col) for col in range(5)])
            if len(matched) >= 10:
                matched_numbers = [card.numbers[row * 5 + col] for row, col in matched if card.numbers[row * 5 + col] != 0]
                return PatternResult(pattern_name="two_lines", matched_positions=matched, is_complete=True, matched_numbers=matched_numbers)
            return None

        matched_positions = []
        matched_numbers = []
        for row, col in positions:
            if cls._is_marked(card, row, col, called_numbers):
                matched_positions.append((row, col))
                number = card.numbers[row * 5 + col]
                if number != 0:
                    matched_numbers.append(number)

        is_complete = len(matched_positions) == len(positions)
        return PatternResult(pattern_name=pattern_name, matched_positions=matched_positions, is_complete=is_complete, matched_numbers=matched_numbers)

    @classmethod
    def _is_marked(cls, card: Card, row: int, col: int, called_numbers: set[int]) -> bool:
        if row < 0 or row >= 5 or col < 0 or col >= 5:
            return False
        index = row * 5 + col
        if index >= len(card.numbers):
            return False
        number = card.numbers[index]
        return number == 0 or number in called_numbers

    @classmethod
    def get_all_patterns(cls) -> list[str]:
        return list(cls.PATTERNS.keys())

    @classmethod
    def validate_win_claim(cls, card: Card, pattern_name: str, called_numbers: set[int], claimed_at: int) -> PatternResult | None:
        result = cls.check_pattern(card, pattern_name, called_numbers)
        if result and result.is_complete:
            return result
        return None

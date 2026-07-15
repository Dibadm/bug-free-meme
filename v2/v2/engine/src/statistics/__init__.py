from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class GameStatistics:
    game_id: str
    room_id: str
    pattern: str
    winner_count: int
    total_players: int
    total_cards_sold: int
    prize_pool: float
    prize_distributed: float
    house_earnings: float
    duration_seconds: float
    balls_called: int
    started_at: datetime
    finished_at: datetime


@dataclass
class AggregateStatistics:
    total_games: int = 0
    total_players: int = 0
    total_cards_sold: int = 0
    total_prize_pool: float = 0.0
    total_prize_distributed: float = 0.0
    total_house_earnings: float = 0.0
    total_duration_seconds: float = 0.0
    pattern_frequency: dict[str, int] = field(default_factory=dict)
    average_players_per_game: float = 0.0
    average_cards_per_player: float = 0.0
    average_duration_seconds: float = 0.0
    house_edge_percentage: float = 0.0

    def record_game(self, stats: GameStatistics) -> None:
        self.total_games += 1
        self.total_players += stats.total_players
        self.total_cards_sold += stats.total_cards_sold
        self.total_prize_pool += stats.prize_pool
        self.total_prize_distributed += stats.prize_distributed
        self.total_house_earnings += stats.house_earnings
        self.total_duration_seconds += stats.duration_seconds
        self.pattern_frequency[stats.pattern] = self.pattern_frequency.get(stats.pattern, 0) + 1

        if self.total_games > 0:
            self.average_players_per_game = self.total_players / self.total_games
            self.average_cards_per_player = self.total_cards_sold / max(self.total_players, 1)
            self.average_duration_seconds = self.total_duration_seconds / self.total_games
        if self.total_prize_pool > 0:
            self.house_edge_percentage = (self.total_house_earnings / self.total_prize_pool) * 100


class StatisticsCollector:
    def __init__(self) -> None:
        self.games: list[GameStatistics] = []
        self.aggregates = AggregateStatistics()

    def record_game(self, stats: GameStatistics) -> None:
        self.games.append(stats)
        self.aggregates.record_game(stats)

    def get_aggregates(self) -> AggregateStatistics:
        return self.aggregates

    def get_pattern_distribution(self) -> dict[str, float]:
        if self.aggregates.total_games == 0:
            return {}
        return {pattern: count / self.aggregates.total_games for pattern, count in self.aggregates.pattern_frequency.items()}

    def get_percentile_duration(self, percentile: float) -> float:
        if not self.games:
            return 0.0
        durations = sorted([g.duration_seconds for g in self.games])
        index = int(len(durations) * percentile)
        return durations[min(index, len(durations) - 1)]

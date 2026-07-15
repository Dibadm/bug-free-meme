from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from engine.src.application.game_service import GameService
from engine.src.domain import GameLifecycleState
from engine.src.events import EventBus
from engine.src.statistics import StatisticsCollector


@dataclass
class SimulationResult:
    total_games: int = 0
    total_players: int = 0
    total_cards_sold: int = 0
    total_prize_distributed: float = 0.0
    total_house_earnings: float = 0.0
    average_duration_seconds: float = 0.0
    pattern_frequency: dict[str, int] = field(default_factory=dict)
    collisions_detected: int = 0
    fairness_violations: int = 0


class SimulationEngine:
    def __init__(self) -> None:
        self.event_bus = EventBus()
        self.statistics = StatisticsCollector()
        self.results: list[SimulationResult] = []

    def run_single_game(self, room_config: dict[str, Any], player_count: int, cards_per_player: int) -> SimulationResult:
        game_service = GameService(self.event_bus)
        result = SimulationResult()

        room = game_service.create_room(
            room_id=uuid4(),
            name=room_config.get("name", "Sim Room"),
            entry_fee=room_config.get("entry_fee", 10.0),
            max_players=room_config.get("max_players", 100),
            min_players=room_config.get("min_players", 2),
            winning_pattern=room_config.get("winning_pattern", "full_house"),
            ball_interval_seconds=room_config.get("ball_interval_seconds", 3),
        )
        result.total_players += player_count
        result.total_cards_sold += player_count * cards_per_player

        for i in range(player_count):
            user_id = uuid4()
            cards = game_service.card_engine.generate_cards(room.room_id, cards_per_player)
            game_service.join_player(room.room_id, user_id, cards)

        game = game_service.start_game(room.room_id)
        start_time = time.perf_counter()

        while game.state == GameLifecycleState.CALLING_NUMBERS:
            game_service.call_number(game.game_id)
            winners = game_service.check_winners(game.game_id)
            if winners:
                break

        duration = time.perf_counter() - start_time
        result.average_duration_seconds += duration

        if game.winner_id:
            result.total_prize_distributed += game.prize_amount or 0
            if game.winning_pattern:
                result.pattern_frequency[game.winning_pattern] = result.pattern_frequency.get(game.winning_pattern, 0) + 1

        result.total_games += 1
        return result

    def run_batch(self, room_config: dict[str, Any], game_count: int, player_count: int, cards_per_player: int) -> SimulationResult:
        aggregate = SimulationResult()
        for _ in range(game_count):
            result = self.run_single_game(room_config, player_count, cards_per_player)
            aggregate.total_games += result.total_games
            aggregate.total_players += result.total_players
            aggregate.total_cards_sold += result.total_cards_sold
            aggregate.total_prize_distributed += result.total_prize_distributed
            aggregate.total_house_earnings += result.total_house_earnings
            aggregate.average_duration_seconds += result.average_duration_seconds
            for pattern, count in result.pattern_frequency.items():
                aggregate.pattern_frequency[pattern] = aggregate.pattern_frequency.get(pattern, 0) + count
            aggregate.collisions_detected += result.collisions_detected
            aggregate.fairness_violations += result.fairness_violations

        if aggregate.total_games > 0:
            aggregate.average_duration_seconds /= aggregate.total_games
        return aggregate

    def run_stress_test(self, concurrent_games: int, room_config: dict[str, Any]) -> SimulationResult:
        return self.run_batch(room_config, concurrent_games, 10, 1)

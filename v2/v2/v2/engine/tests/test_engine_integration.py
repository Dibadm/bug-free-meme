from __future__ import annotations

import pytest
from engine.src import (
    BallEngine,
    Card,
    CardEngine,
    EventBus,
    GameService,
    RuleEngine,
    StatisticsCollector,
    SimulationEngine,
)
from engine.src.domain import GameLifecycleState


def test_illegal_state_transitions():
    from engine.src.domain import GameState
    game = GameState()
    game.transition_to(GameLifecycleState.WAITING)
    game.transition_to(GameLifecycleState.SELLING_CARDS)
    game.transition_to(GameLifecycleState.LOCKED)
    game.transition_to(GameLifecycleState.STARTING)
    game.transition_to(GameLifecycleState.CALLING_NUMBERS)
    with pytest.raises(ValueError):
        game.transition_to(GameLifecycleState.WAITING)


def test_card_validation_rejects_invalid():
    card = Card(numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25])
    assert CardEngine.validate_card(card) is True
    card.numbers[12] = 5
    assert CardEngine.validate_card(card) is False


def test_rule_engine_incomplete_patterns():
    card = Card(numbers=[1, 0, 0, 0, 75, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 71])
    called = {1, 75}
    result = RuleEngine.check_pattern(card, "four_corners", called)
    assert result is not None
    assert result.is_complete is False


def test_ball_engine_state_serialization():
    engine = BallEngine(seed="serialize-test")
    engine.call_next()
    engine.call_next()
    state = engine.get_state()
    restored = BallEngine.from_state(state)
    assert restored.seed == engine.seed
    assert restored.seed_hash == engine.seed_hash
    assert len(restored.called_numbers) == 2
    assert restored.called_numbers == engine.called_numbers


def test_event_bus_multiple_handlers():
    bus = EventBus()
    results = []

    async def handler1(event):
        results.append("h1")

    async def handler2(event):
        results.append("h2")

    bus.subscribe("Test", handler1)
    bus.subscribe("Test", handler2)
    import asyncio
    asyncio.run(bus.publish(Event(event_type="Test")))
    assert results == ["h1", "h2"]


def test_simulation_engine_batch():
    sim = SimulationEngine()
    result = sim.run_batch({"name": "Sim", "entry_fee": 10.0, "max_players": 10, "min_players": 2, "winning_pattern": "full_house"}, 5, 5, 1)
    assert result.total_games == 5
    assert result.total_players == 25


def test_statistics_pattern_distribution():
    collector = StatisticsCollector()
    for i in range(10):
        stats = GameStatistics(
            game_id=str(i),
            room_id="1",
            pattern="full_house" if i < 7 else "four_corners",
            winner_count=1,
            total_players=10,
            total_cards_sold=10,
            prize_pool=100.0,
            prize_distributed=90.0,
            house_earnings=10.0,
            duration_seconds=120.0,
            balls_called=50,
            started_at=__import__("datetime").datetime.now(),
            finished_at=__import__("datetime").datetime.now(),
        )
        collector.record_game(stats)
    agg = collector.get_aggregates()
    assert agg.total_games == 10
    distribution = collector.get_pattern_distribution()
    assert distribution["full_house"] == 0.7
    assert distribution["four_corners"] == 0.3


def test_fairness_verifier_no_collision():
    cards = CardEngine.generate_cards(__import__("uuid").UUID(int=1), 100)
    assert FairnessVerifier.verify_no_collision(cards) is True


def test_game_service_cancel_after_start():
    service = GameService()
    room = service.create_room(__import__("uuid").UUID(int=10), "Cancel Test", 10.0, 10, 2, "full_house")
    card = CardEngine.generate_card(room.room_id)
    service.join_player(room.room_id, __import__("uuid").UUID(int=1), [card])
    game = service.start_game(room.room_id)
    service.call_number(game.game_id)
    cancelled = service.cancel_game(game.game_id)
    assert cancelled.state == GameLifecycleState.CANCELLED


def test_replay_perfect_determinism():
    engine1 = GameService()
    room1 = engine1.create_room(__import__("uuid").UUID(int=20), "Replay", 10.0, 10, 2, "full_house")
    card1 = CardEngine.generate_card(room1.room_id)
    engine1.join_player(room1.room_id, __import__("uuid").UUID(int=1), [card1])
    game1 = engine1.start_game(room1.room_id)
    numbers1 = []
    for _ in range(10):
        n = engine1.call_number(game1.game_id)
        if n:
            numbers1.append(n)

    engine2 = GameService()
    room2 = engine2.create_room(__import__("uuid").UUID(int=21), "Replay2", 10.0, 10, 2, "full_house")
    card2 = CardEngine.generate_card(room2.room_id)
    engine2.join_player(room2.room_id, __import__("uuid").UUID(int=1), [card2])
    game2 = engine2.start_game(room2.room_id)
    numbers2 = []
    for _ in range(10):
        n = engine2.call_number(game2.game_id)
        if n:
            numbers2.append(n)

    assert numbers1 == numbers2


def test_winner_validation_prevents_duplicate():
    service = GameService()
    room = service.create_room(__import__("uuid").UUID(int=30), "Dup Test", 10.0, 10, 2, "full_house")
    card = CardEngine.generate_card(room.room_id)
    service.join_player(room.room_id, __import__("uuid").UUID(int=1), [card])
    game = service.start_game(room.room_id)
    for _ in range(25):
        service.call_number(game.game_id)
    winners1 = service.check_winners(game.game_id)
    validated1 = service.validate_winners(game.game_id, winners1)
    service.finish_game(game.game_id, validated1)
    assert len(validated1) == 1

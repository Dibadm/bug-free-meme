from __future__ import annotations

import pytest
from engine.src import (
    BallEngine,
    Card,
    CardEngine,
    Event,
    EventBus,
    FairnessCommitment,
    FairnessVerifier,
    GameService,
    GameSnapshot,
    GameState,
    GameStatistics,
    PlayerState,
    ReplayEngine,
    RoomState,
    RuleEngine,
    Serializer,
    StatisticsCollector,
)
from engine.src.domain import GameLifecycleState


def test_ball_engine_generates_unique_numbers():
    engine = BallEngine(seed="test-seed-123")
    numbers = []
    while engine.remaining_numbers:
        num = engine.call_next()
        assert num is not None
        numbers.append(num)
    assert len(numbers) == 75
    assert len(set(numbers)) == 75
    assert sorted(numbers) == list(range(1, 76))


def test_ball_engine_verification():
    seed = "verification-seed-456"
    engine = BallEngine(seed=seed)
    for _ in range(10):
        engine.call_next()
    assert engine.verify_sequence(seed) is True
    assert engine.verify_sequence("wrong-seed") is False


def test_ball_engine_pause_resume():
    engine = BallEngine(seed="pause-test")
    engine.call_next()
    assert engine.is_paused() is False
    engine.pause()
    assert engine.is_paused() is True
    engine.resume()
    assert engine.is_paused() is False


def test_card_engine_generates_valid_cards():
    card = CardEngine.generate_card(room_id=__import__("uuid").UUID(int=1), pattern_index=0)
    assert CardEngine.validate_card(card) is True
    assert len(card.numbers) == 25
    assert card.numbers[12] == 0


def test_card_engine_generate_multiple():
    cards = CardEngine.generate_cards(room_id=__import__("uuid").UUID(int=1), count=5)
    assert len(cards) == 5
    fingerprints = [c.fingerprint for c in cards]
    assert len(fingerprints) == len(set(fingerprints))


def test_card_mark_and_undo():
    card = Card(numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25])
    assert card.mark(1) is True
    assert card.mark(99) is False
    assert card.is_marked(1) is True
    assert card.is_marked(2) is False
    assert card.undo_mark(1) is True
    assert card.is_marked(1) is False


def test_rule_engine_all_patterns():
    card = Card(numbers=list(range(1, 26)))
    called = set(range(1, 26))
    for pattern in RuleEngine.get_all_patterns():
        result = RuleEngine.check_pattern(card, pattern, called)
        assert result is not None
        assert result.is_complete is True


def test_game_state_transitions():
    game = GameState()
    assert game.state == GameLifecycleState.CREATED
    game.transition_to(GameLifecycleState.WAITING)
    assert game.state == GameLifecycleState.WAITING
    with pytest.raises(ValueError):
        game.transition_to(GameLifecycleState.COMPLETED)


def test_event_bus_publish_subscribe():
    bus = EventBus()
    received = []

    async def handler(event):
        received.append(event)

    bus.subscribe("TestEvent", handler)
    event = Event(event_type="TestEvent", payload={"key": "value"})
    import asyncio
    asyncio.run(bus.publish(event))
    assert len(received) == 1
    assert received[0].payload["key"] == "value"


def test_fairness_commitment():
    commitment = FairnessCommitment.create("my-seed", "salt")
    assert commitment.verify("my-seed", "salt") is True
    assert commitment.verify("wrong-seed", "salt") is False


def test_serializer_roundtrip():
    snapshot = GameSnapshot(
        game_id=__import__("uuid").UUID(int=1),
        room_id=__import__("uuid").UUID(int=2),
        state="completed",
        seed="test-seed",
        seed_hash="hash123",
        called_numbers=[1, 2, 3],
        current_number=3,
        started_at=__import__("datetime").datetime.now(),
        finished_at=__import__("datetime").datetime.now(),
        winner_id=__import__("uuid").UUID(int=3),
        winning_pattern="full_house",
        prize_amount=100.0,
    )
    serialized = Serializer.serialize_snapshot(snapshot)
    restored = Serializer.deserialize_snapshot(serialized)
    assert restored.game_id == snapshot.game_id
    assert restored.state == snapshot.state
    assert restored.called_numbers == snapshot.called_numbers


def test_statistics_collector():
    collector = StatisticsCollector()
    stats = GameStatistics(
        game_id="1",
        room_id="1",
        pattern="full_house",
        winner_count=1,
        total_players=10,
        total_cards_sold=20,
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
    assert agg.total_games == 1
    assert agg.total_players == 10
    assert agg.average_duration_seconds == 120.0


def test_replay_engine():
    engine = ReplayEngine()
    engine.record_event("BallCalled", {"number": 1})
    engine.record_event("BallCalled", {"number": 2})
    replay = engine.build_replay(
        game_id=__import__("uuid").UUID(int=1),
        seed="test-seed",
        final_state={},
        started_at=__import__("datetime").datetime.now(),
        finished_at=__import__("datetime").datetime.now(),
    )
    json_str = replay.to_json()
    restored = GameReplay.from_json(json_str)
    assert len(restored.events) == 2
    assert restored.events[0]["event_type"] == "BallCalled"


def test_game_service_lifecycle():
    service = GameService()
    room = service.create_room(
        room_id=__import__("uuid").UUID(int=0),
        name="Test Room",
        entry_fee=10.0,
        max_players=10,
        min_players=2,
        winning_pattern="full_house",
    )
    assert room.status == GameLifecycleState.WAITING

    card1 = CardEngine.generate_card(room.room_id)
    card2 = CardEngine.generate_card(room.room_id)

    service.join_player(room.room_id, __import__("uuid").UUID(int=1), [card1])
    service.join_player(room.room_id, __import__("uuid").UUID(int=2), [card2])

    game = service.start_game(room.room_id)
    assert game.state == GameLifecycleState.CALLING_NUMBERS

    number = service.call_number(game.game_id)
    assert number is not None
    assert len(game.called_numbers) == 1

    state = service.get_state(game.game_id)
    assert state is not None
    assert len(state["called_numbers"]) == 1


def test_crash_recovery_snapshot():
    service = GameService()
    room = service.create_room(
        room_id=__import__("uuid").UUID(int=5),
        name="Recovery Test",
        entry_fee=10.0,
        max_players=10,
        min_players=2,
        winning_pattern="full_house",
    )
    card = CardEngine.generate_card(room.room_id)
    service.join_player(room.room_id, __import__("uuid").UUID(int=1), [card])
    game = service.start_game(room.room_id)
    for _ in range(5):
        service.call_number(game.game_id)

    snapshot = GameSnapshot(
        game_id=game.game_id,
        room_id=game.room_id,
        state=game.state.value,
        seed=game.seed,
        seed_hash=game.seed_hash,
        called_numbers=list(game.called_numbers),
        current_number=game.current_number,
        started_at=game.started_at,
        finished_at=game.finished_at,
        winner_id=game.winner_id,
        winning_pattern=game.winning_pattern,
        prize_amount=game.prize_amount,
    )
    serialized = Serializer.serialize_snapshot(snapshot)
    restored = Serializer.deserialize_snapshot(serialized)
    assert restored.state == game.state.value
    assert len(restored.called_numbers) == 5
    assert restored.seed_hash == game.seed_hash

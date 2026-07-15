import pytest
from engine.src import BallCaller, RuleEngine, GameEngine, GameStatus, Card
from uuid import UUID


def test_ball_caller_generates_all_numbers():
    caller = BallCaller(seed="test-seed-123")
    numbers = []
    while caller.remaining_numbers:
        num = caller.call_next()
        assert num is not None
        numbers.append(num)
    assert len(numbers) == 75
    assert len(set(numbers)) == 75
    assert sorted(numbers) == list(range(1, 76))


def test_ball_caller_verification():
    seed = "verification-seed-456"
    caller = BallCaller(seed=seed)
    for _ in range(10):
        caller.call_next()
    assert caller.verify_sequence(seed) is True
    assert caller.verify_sequence("wrong-seed") is False


def test_card_mark_and_unmark():
    card = Card(numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25])
    assert card.mark(1) is True
    assert card.mark(99) is False
    assert card.is_marked(1) is True
    assert card.is_marked(2) is False


def test_rule_engine_four_corners():
    card = Card(numbers=[1, 0, 0, 0, 75, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 71])
    called = {1, 75, 71}
    result = RuleEngine.check_pattern(card, "four_corners", called)
    assert result is not None
    assert result.is_complete is True
    assert len(result.matched_positions) == 4


def test_rule_engine_full_house():
    card = Card(numbers=list(range(1, 26)))
    called = set(range(1, 26))
    result = RuleEngine.check_pattern(card, "full_house", called)
    assert result is not None
    assert result.is_complete is True


def test_rule_engine_incomplete():
    card = Card(numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25])
    called = {1, 2, 3}
    result = RuleEngine.check_pattern(card, "four_corners", called)
    assert result is not None
    assert result.is_complete is False


def test_rule_engine_x_pattern():
    card = Card(numbers=[1, 0, 0, 0, 75, 0, 2, 0, 71, 0, 0, 0, 3, 0, 0, 0, 73, 0, 0, 0, 0, 0, 0, 0, 0])
    called = {1, 75, 2, 71, 3, 73}
    result = RuleEngine.check_pattern(card, "x_pattern", called)
    assert result is not None
    assert result.is_complete is True


def test_game_engine_create_room():
    engine = GameEngine()
    room_id = UUID("00000000-0000-0000-0000-000000000001")
    room = engine.create_room(room_id, "Test Room", 10.0, 10, 2, "full_house")
    assert room["status"] == GameStatus.WAITING
    assert room["name"] == "Test Room"


def test_game_engine_join_and_start():
    engine = GameEngine()
    room_id = UUID("00000000-0000-0000-0000-000000000002")
    engine.create_room(room_id, "Test", 10.0, 10, 2, "full_house")
    card1 = Card(numbers=list(range(1, 26)))
    card2 = Card(numbers=list(range(1, 26)))
    engine.join_room(room_id, UUID(int=1), [card1])
    engine.join_room(room_id, UUID(int=2), [card2])
    game = engine.start_game(room_id)
    assert game["status"] == GameStatus.STARTING
    assert game["ball_caller"].get_remaining_count() == 75


def test_game_engine_state_serialization():
    engine = GameEngine()
    room_id = UUID("00000000-0000-0000-0000-000000000003")
    engine.create_room(room_id, "Test", 10.0, 10, 2, "full_house")
    card = Card(numbers=list(range(1, 26)))
    engine.join_room(room_id, UUID(int=1), [card])
    game = engine.start_game(room_id)
    for _ in range(5):
        engine.call_number(game["id"])
    state = engine.get_state(game["id"])
    assert state is not None
    assert len(state["called_numbers"]) == 5
    assert state["seed_hash"] is not None
    assert state["remaining_count"] == 70


def test_game_engine_crash_recovery():
    engine1 = GameEngine()
    room_id = UUID("00000000-0000-0000-0000-000000000004")
    engine1.create_room(room_id, "Test", 10.0, 10, 2, "full_house")
    card = Card(numbers=list(range(1, 26)))
    engine1.join_room(room_id, UUID(int=1), [card])
    game1 = engine1.start_game(room_id)
    for _ in range(10):
        engine1.call_number(game1["id"])
    state = engine1.get_state(game1["id"])
    assert state is not None
    assert len(state["called_numbers"]) == 10
    assert state["seed_hash"] is not None

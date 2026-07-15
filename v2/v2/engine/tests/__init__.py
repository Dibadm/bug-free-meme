import pytest
from engine.src import BallCaller, Card, RuleEngine, GameEngine, GameStatus


def test_ball_caller_generates_unique_numbers():
    caller = BallCaller(seed="test-seed-123")
    numbers = []
    for _ in range(75):
        num = caller.call_next()
        assert num is not None
        numbers.append(num)
    assert len(set(numbers)) == 75
    assert sorted(numbers) == list(range(1, 76))


def test_ball_caller_verification():
    seed = "verification-seed"
    caller = BallCaller(seed=seed)
    for _ in range(10):
        caller.call_next()
    assert caller.verify_sequence(seed) is True
    assert caller.verify_sequence("wrong-seed") is False


def test_card_mark():
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


def test_game_engine_lifecycle():
    engine = GameEngine()
    room = engine.create_room(
        room_id=__import__("uuid").UUID(int=0),
        name="Test Room",
        entry_fee=10.0,
        max_players=10,
        min_players=2,
        winning_pattern="full_house",
    )
    assert room["status"] == GameStatus.WAITING

    card1 = Card(numbers=list(range(1, 26)))
    card2 = Card(numbers=list(range(1, 26)))

    engine.join_room(__import__("uuid").UUID(int=0), __import__("uuid").UUID(int=1), [card1])
    engine.join_room(__import__("uuid").UUID(int=0), __import__("uuid").UUID(int=2), [card2])

    game = engine.start_game(__import__("uuid").UUID(int=0))
    assert game["status"] == GameStatus.STARTING
    assert game["ball_caller"].get_remaining_count() == 75


def test_game_engine_crash_recovery():
    engine = GameEngine()
    room_id = __import__("uuid").UUID(int=0)
    engine.create_room(room_id, "Test", 10.0, 10, 2, "full_house")
    card = Card(numbers=list(range(1, 26)))
    engine.join_room(room_id, __import__("uuid").UUID(int=1), [card])
    game = engine.start_game(room_id)

    for _ in range(5):
        engine.call_number(game["id"])

    state = engine.get_state(game["id"])
    assert state is not None
    assert len(state["called_numbers"]) == 5
    assert state["seed_hash"] is not None

from __future__ import annotations

import pytest
from engine.src import BallEngine, Card, CardEngine, RuleEngine
from engine.src.domain import GameLifecycleState


def test_ball_engine_emergency_stop():
    engine = BallEngine(seed="emergency")
    engine.call_next()
    engine.call_next()
    assert engine.get_called_count() == 2
    assert engine.get_remaining_count() == 73


def test_card_fingerprint_uniqueness():
    card1 = CardEngine.generate_card(__import__("uuid").UUID(int=1))
    card2 = CardEngine.generate_card(__import__("uuid").UUID(int=1))
    assert card1.fingerprint != card2.fingerprint


def test_card_serialization_roundtrip():
    card = CardEngine.generate_card(__import__("uuid").UUID(int=1))
    card.mark(1)
    card.mark(15)
    data = card.to_dict()
    restored = Card.from_dict(data)
    assert restored.numbers == card.numbers
    assert restored.is_marked(1) is True
    assert restored.is_marked(2) is False
    assert restored.fingerprint == card.fingerprint


def test_rule_engine_unknown_pattern():
    card = Card(numbers=list(range(1, 26)))
    result = RuleEngine.check_pattern(card, "unknown_pattern", set())
    assert result is None


def test_game_state_archived_terminal():
    from engine.src.domain import GameState
    game = GameState()
    game.transition_to(GameLifecycleState.COMPLETED)
    game.transition_to(GameLifecycleState.ARCHIVED)
    assert game.state == GameLifecycleState.ARCHIVED
    with pytest.raises(ValueError):
        game.transition_to(GameLifecycleState.WAITING)


def test_ball_engine_different_seeds():
    engine1 = BallEngine(seed="seed-a")
    engine2 = BallEngine(seed="seed-b")
    n1 = engine1.call_next()
    n2 = engine2.call_next()
    assert n1 != n2 or len(set(engine1.called_numbers + engine2.called_numbers)) > 1


def test_card_mark_duplicate():
    card = Card(numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25])
    card.mark(1)
    assert card.mark(1) is True
    assert len([k for k, v in card.marks.items() if v != CardMarkStatus.UNDO]) == 1


def test_card_verify():
    card = Card(numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 0, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25])
    assert card.verify({1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25}) is True
    assert card.verify({1, 2, 3}) is False


def test_rule_engine_x_pattern():
    card = Card(numbers=[1, 0, 0, 0, 75, 0, 2, 0, 71, 0, 0, 0, 3, 0, 0, 0, 73, 0, 0, 0, 0, 0, 0, 0, 0])
    called = {1, 75, 2, 71, 3, 73}
    result = RuleEngine.check_pattern(card, "x_pattern", called)
    assert result is not None
    assert result.is_complete is True


def test_rule_engine_cross_pattern():
    card = Card(numbers=[0, 0, 1, 0, 0, 0, 0, 2, 0, 0, 3, 4, 5, 6, 7, 0, 0, 8, 0, 0, 0, 0, 9, 0, 0])
    called = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    result = RuleEngine.check_pattern(card, "cross", called)
    assert result is not None
    assert result.is_complete is True


def test_rule_engine_diamond_pattern():
    card = Card(numbers=[0, 0, 1, 0, 0, 0, 2, 0, 3, 0, 4, 0, 0, 0, 0, 0, 5, 0, 6, 0, 0, 0, 7, 0, 0])
    called = {1, 2, 3, 4, 5, 6, 7}
    result = RuleEngine.check_pattern(card, "diamond", called)
    assert result is not None
    assert result.is_complete is True


def test_rule_engine_letter_h_pattern():
    card = Card(numbers=[1, 0, 0, 0, 2, 3, 0, 0, 0, 0, 4, 5, 6, 0, 0, 7, 0, 0, 0, 0, 8, 0, 0, 0, 9])
    called = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    result = RuleEngine.check_pattern(card, "letter_h", called)
    assert result is not None
    assert result.is_complete is True


def test_rule_engine_letter_t_pattern():
    card = Card(numbers=[1, 2, 3, 4, 5, 0, 0, 6, 0, 0, 0, 0, 7, 0, 0, 0, 0, 8, 0, 0, 0, 0, 9, 0, 0])
    called = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    result = RuleEngine.check_pattern(card, "letter_t", called)
    assert result is not None
    assert result.is_complete is True

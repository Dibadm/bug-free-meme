import pytest
from engine.src import RuleEngine, Card


def test_four_corners_incomplete():
    card = Card(numbers=[1, 0, 0, 0, 75, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 71])
    called = {1, 75}
    result = RuleEngine.check_pattern(card, "four_corners", called)
    assert result is not None
    assert result.is_complete is False


def test_cross_pattern():
    card = Card(numbers=[0, 0, 1, 0, 0, 0, 0, 2, 0, 0, 3, 4, 5, 6, 7, 0, 0, 8, 0, 0, 0, 0, 9, 0, 0])
    called = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    result = RuleEngine.check_pattern(card, "cross", called)
    assert result is not None
    assert result.is_complete is True


def test_diamond_pattern():
    card = Card(numbers=[0, 0, 1, 0, 0, 0, 2, 0, 3, 0, 4, 0, 0, 0, 0, 0, 5, 0, 6, 0, 0, 0, 7, 0, 0])
    called = {1, 2, 3, 4, 5, 6, 7}
    result = RuleEngine.check_pattern(card, "diamond", called)
    assert result is not None
    assert result.is_complete is True


def test_letter_h_pattern():
    card = Card(numbers=[1, 0, 0, 0, 2, 3, 0, 0, 0, 0, 4, 5, 6, 0, 0, 7, 0, 0, 0, 0, 8, 0, 0, 0, 9])
    called = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    result = RuleEngine.check_pattern(card, "letter_h", called)
    assert result is not None
    assert result.is_complete is True


def test_letter_t_pattern():
    card = Card(numbers=[1, 2, 3, 4, 5, 0, 0, 6, 0, 0, 0, 0, 7, 0, 0, 0, 0, 8, 0, 0, 0, 0, 9, 0, 0])
    called = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    result = RuleEngine.check_pattern(card, "letter_t", called)
    assert result is not None
    assert result.is_complete is True


def test_one_line_pattern():
    card = Card(numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25])
    called = {1, 2, 3, 4, 5}
    result = RuleEngine.check_pattern(card, "one_line", called)
    assert result is not None
    assert result.is_complete is True


def test_two_lines_pattern():
    card = Card(numbers=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25])
    called = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
    result = RuleEngine.check_pattern(card, "two_lines", called)
    assert result is not None
    assert result.is_complete is True


def test_unknown_pattern():
    card = Card(numbers=list(range(1, 26)))
    result = RuleEngine.check_pattern(card, "unknown_pattern", set())
    assert result is None

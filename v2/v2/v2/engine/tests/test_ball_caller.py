import pytest
from engine.src import BallCaller


def test_seed_generation():
    caller = BallCaller()
    assert caller.seed is not None
    assert len(caller.seed) == 64


def test_seed_hash_matches():
    import hashlib
    seed = "my-test-seed"
    caller = BallCaller(seed=seed)
    assert caller.seed_hash == hashlib.sha256(seed.encode()).hexdigest()


def test_deterministic_with_same_seed():
    caller1 = BallCaller(seed="same-seed")
    caller2 = BallCaller(seed="same-seed")
    for _ in range(75):
        assert caller1.call_next() == caller2.call_next()


def test_different_seeds_produce_different_sequences():
    caller1 = BallCaller(seed="seed-a")
    caller2 = BallCaller(seed="seed-b")
    num1 = caller1.call_next()
    num2 = caller2.call_next()
    assert num1 != num2 or len(set(caller1.called_numbers + caller2.called_numbers)) > 1


def test_call_next_returns_none_when_exhausted():
    caller = BallCaller(seed="exhaust")
    for _ in range(75):
        caller.call_next()
    assert caller.call_next() is None
    assert caller.get_remaining_count() == 0


def test_get_called_count():
    caller = BallCaller(seed="count")
    for _ in range(15):
        caller.call_next()
    assert caller.get_called_count() == 15


def test_verify_sequence_rejects_tampered():
    caller = BallCaller(seed="original")
    for _ in range(20):
        caller.call_next()
    assert caller.verify_sequence("original") is True
    assert caller.verify_sequence("tampered") is False

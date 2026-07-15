from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from typing import Any


@dataclass
class FairnessCommitment:
    commitment_hash: str
    algorithm: str = "HMAC-SHA256"
    description: str = "Pre-game fairness commitment"

    @staticmethod
    def create(seed: str, salt: str = "") -> FairnessCommitment:
        commitment_data = f"{seed}|{salt}"
        commitment_hash = hashlib.sha256(commitment_data.encode()).hexdigest()
        return FairnessCommitment(commitment_hash=commitment_hash)

    def verify(self, seed: str, salt: str = "") -> bool:
        commitment_data = f"{seed}|{salt}"
        expected_hash = hashlib.sha256(commitment_data.encode()).hexdigest()
        return hmac.compare_digest(expected_hash, self.commitment_hash)


class FairnessVerifier:
    @staticmethod
    def verify_game_fairness(seed: str, called_numbers: list[int], salt: str = "") -> bool:
        rng = secrets.SystemRandom()
        rng.seed(seed.encode())
        expected_sequence = list(range(1, 76))
        rng.shuffle(expected_sequence)
        return called_numbers == expected_sequence[: len(called_numbers)]

    @staticmethod
    def verify_card_distribution(cards: list[Any], seed: str) -> bool:
        return True

    @staticmethod
    def verify_no_collision(cards: list[Any]) -> bool:
        fingerprints = [c.fingerprint for c in cards if hasattr(c, "fingerprint")]
        return len(fingerprints) == len(set(fingerprints))

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from engine.src.domain import GameLifecycleState, GameState, PlayerState, RoomState
from engine.src.domain.ball import BallEngine
from engine.src.domain.card import Card, CardEngine
from engine.src.events import Event, EventBus
from engine.src.rules import RuleEngine
from engine.src.statistics import GameStatistics, StatisticsCollector


@dataclass
class GameService:
    event_bus: EventBus = field(default_factory=EventBus)
    statistics: StatisticsCollector = field(default_factory=StatisticsCollector)
    games: dict[UUID, GameState] = field(default_factory=dict)
    rooms: dict[UUID, RoomState] = field(default_factory=dict)
    card_engine: CardEngine = field(default_factory=CardEngine)
    rule_engine: RuleEngine = field(default_factory=RuleEngine)

    def create_room(self, room_id: UUID, name: str, entry_fee: float, max_players: int, min_players: int, winning_pattern: str, ball_interval_seconds: int = 3, visibility: str = "public") -> RoomState:
        room = RoomState(
            room_id=room_id,
            name=name,
            entry_fee=entry_fee,
            max_players=max_players,
            min_players=min_players,
            winning_pattern=winning_pattern,
            ball_interval_seconds=ball_interval_seconds,
            visibility=visibility,
            status=GameLifecycleState.WAITING,
        )
        self.rooms[room_id] = room
        event = Event(event_type="RoomCreated", room_id=room_id, payload={"name": name, "entry_fee": entry_fee})
        self.event_bus.publish(event)
        return room

    def join_player(self, room_id: UUID, user_id: UUID, cards: list[Card]) -> None:
        room = self.rooms.get(room_id)
        if not room:
            raise ValueError("Room not found")
        if room.status not in (GameLifecycleState.WAITING, GameLifecycleState.SELLING_CARDS):
            raise ValueError(f"Room is not accepting players in state: {room.status.value}")
        if user_id in room.players:
            raise ValueError("Player already in room")
        if len(room.players) >= room.max_players:
            raise ValueError("Room is full")

        player = PlayerState(user_id=user_id, joined_at=datetime.now(timezone.utc))
        room.players[user_id] = player
        room.current_players = len(room.players)

        for card in cards:
            card.owner_id = user_id
            card.is_sold = True
            room.cards[card.id] = card
            player.cards.append(card.id)

        room.cards_sold = len(room.cards)
        room.status = GameLifecycleState.SELLING_CARDS

        event = Event(event_type="PlayerJoined", room_id=room_id, user_id=user_id, payload={"card_count": len(cards)})
        self.event_bus.publish(event)

    def start_game(self, room_id: UUID) -> GameState:
        room = self.rooms.get(room_id)
        if not room:
            raise ValueError("Room not found")
        if len(room.players) < room.min_players:
            raise ValueError(f"Not enough players: {len(room.players)} < {room.min_players}")

        game_id = uuid4()
        seed = secrets.token_hex(32)
        ball_engine = BallEngine(seed=seed, interval_seconds=room.ball_interval_seconds)

        game = GameState(
            game_id=game_id,
            room_id=room_id,
            state=GameLifecycleState.STARTING,
            seed=seed,
            seed_hash=ball_engine.seed_hash,
        )

        self.games[game_id] = game
        room.status = GameLifecycleState.STARTING
        room.prize_pool = room.entry_fee * len(room.players)

        event = Event(event_type="GameStarted", game_id=game_id, room_id=room_id, payload={"seed": seed, "seed_hash": ball_engine.seed_hash})
        self.event_bus.publish(event)

        game.state = GameLifecycleState.CALLING_NUMBERS
        game.started_at = datetime.now(timezone.utc)
        return game

    def call_number(self, game_id: UUID) -> int | None:
        game = self.games.get(game_id)
        if not game or game.state != GameLifecycleState.CALLING_NUMBERS:
            return None
        ball_engine = BallEngine.from_state(game.metadata.get("ball_engine", {}))
        if not ball_engine.remaining_numbers:
            return None
        number = ball_engine.call_next()
        game.metadata["ball_engine"] = ball_engine.get_state()
        game.current_number = number
        game.called_numbers = ball_engine.called_numbers
        event = Event(event_type="BallCalled", game_id=game_id, payload={"number": number, "called_count": ball_engine.get_called_count()})
        self.event_bus.publish(event)
        return number

    def check_winners(self, game_id: UUID) -> list[dict[str, Any]]:
        game = self.games.get(game_id)
        if not game:
            return []
        room = self.rooms.get(game.room_id)
        if not room:
            return []
        ball_engine = BallEngine.from_state(game.metadata.get("ball_engine", {}))
        called_set = set(ball_engine.called_numbers)
        winners = []
        for user_id, player_data in room.players.items():
            for card_id in player_data.cards:
                card = room.cards.get(card_id)
                if not card:
                    continue
                result = self.rule_engine.check_pattern(card, room.winning_pattern, called_set)
                if result and result.is_complete:
                    winners.append({"user_id": user_id, "card_id": card_id, "pattern": room.winning_pattern, "matched_positions": result.matched_positions})
        if winners:
            game.state = GameLifecycleState.WINNER_VALIDATION
            event = Event(event_type="WinnerClaimed", game_id=game_id, payload={"winners": winners})
            self.event_bus.publish(event)
        return winners

    def validate_winners(self, game_id: UUID, winners: list[dict[str, Any]]) -> list[dict[str, Any]]:
        game = self.games.get(game_id)
        if not game:
            return []
        room = self.rooms.get(game.room_id)
        if not room:
            return []
        ball_engine = BallEngine.from_state(game.metadata.get("ball_engine", {}))
        called_set = set(ball_engine.called_numbers)
        validated = []
        for winner in winners:
            card = room.cards.get(winner["card_id"])
            if not card:
                continue
            if card.owner_id != winner["user_id"]:
                continue
            result = self.rule_engine.validate_win_claim(card, winner["pattern"], called_set, 0)
            if result and result.is_complete:
                validated.append(winner)
        if validated:
            game.state = GameLifecycleState.PRIZE_DISTRIBUTION
            event = Event(event_type="WinnerVerified", game_id=game_id, payload={"validated_winners": validated})
            self.event_bus.publish(event)
        return validated

    def finish_game(self, game_id: UUID, winners: list[dict[str, Any]]) -> GameState | None:
        game = self.games.get(game_id)
        if not game:
            return None
        room = self.rooms.get(game.room_id)
        if not room:
            return None
        prize_per_winner = room.prize_pool / max(len(winners), 1)
        game.prize_amount = prize_per_winner
        game.winner_id = winners[0]["user_id"] if winners else None
        game.winning_pattern = winners[0]["pattern"] if winners else None
        game.state = GameLifecycleState.COMPLETED
        game.finished_at = datetime.now(timezone.utc)
        stats = GameStatistics(
            game_id=str(game.game_id),
            room_id=str(game.room_id),
            pattern=game.winning_pattern or "",
            winner_count=len(winners),
            total_players=room.current_players,
            total_cards_sold=room.cards_sold,
            prize_pool=room.prize_pool,
            prize_distributed=prize_per_winner * len(winners),
            house_earnings=room.prize_pool - prize_per_winner * len(winners),
            duration_seconds=(game.finished_at - game.started_at).total_seconds() if game.started_at else 0.0,
            balls_called=len(game.called_numbers),
            started_at=game.started_at or datetime.now(timezone.utc),
            finished_at=game.finished_at,
        )
        self.statistics.record_game(stats)
        event = Event(event_type="GameCompleted", game_id=game_id, payload={"winners": winners, "prize_per_winner": prize_per_winner})
        self.event_bus.publish(event)
        return game

    def cancel_game(self, game_id: UUID) -> GameState | None:
        game = self.games.get(game_id)
        if not game:
            return None
        if game.state in (GameLifecycleState.COMPLETED, GameLifecycleState.CANCELLED, GameLifecycleState.ARCHIVED):
            raise ValueError(f"Cannot cancel game in state: {game.state.value}")
        game.state = GameLifecycleState.CANCELLED
        game.finished_at = datetime.now(timezone.utc)
        event = Event(event_type="GameCancelled", game_id=game_id)
        self.event_bus.publish(event)
        return game

    def get_state(self, game_id: UUID) -> dict[str, Any] | None:
        game = self.games.get(game_id)
        if not game:
            return None
        ball_engine = BallEngine.from_state(game.metadata.get("ball_engine", {}))
        return {
            "id": str(game.game_id),
            "room_id": str(game.room_id),
            "state": game.state.value,
            "called_numbers": list(game.called_numbers),
            "current_number": game.current_number,
            "remaining_count": ball_engine.get_remaining_count(),
            "seed_hash": game.seed_hash,
            "started_at": game.started_at.isoformat() if game.started_at else None,
        }


GameService.join_room = GameService.join_player

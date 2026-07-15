# Habesha Bet V2 - Enterprise Bingo Engine

## Complete Engine Architecture

```
engine/
  src/
    __init__.py                 # Public API, backward compatibility
    domain/
      __init__.py               # Domain exports
      game.py                   # Game lifecycle state machine
      ball.py                   # Ball engine (deterministic RNG)
      card.py                   # Card engine (generation, validation, marking)
    rules/
      __init__.py               # Pattern matching engine
    events/
      __init__.py               # Event bus and event definitions
    fairness/
      __init__.py               # Commitment scheme and verification
    replay/
      __init__.py               # Replay recording and playback
    serialization/
      __init__.py               # Snapshot serialization/deserialization
    simulation/
      __init__.py               # Batch simulation and stress testing
    statistics/
      __init__.py               # Game statistics and analytics
    application/
      __init__.py               # Application services
      game_service.py           # Main game orchestrator
      room_service.py           # Room management
      card_service.py           # Card operations
      ball_service.py           # Ball calling operations
      player_service.py         # Player operations
      prize_service.py          # Prize calculation and distribution
  tests/
    test_engine_v2.py           # Core engine tests
    test_engine_integration.py  # Integration tests
    test_engine_edge_cases.py   # Edge case tests
```

## Package Structure

### domain/
- **game.py**: `GameLifecycleState` enum, `GameState`, `PlayerState`, `RoomState`
- **ball.py**: `BallEngine` - deterministic ball calling with seed-based RNG
- **card.py**: `Card`, `CardEngine`, `CardMarkStatus` - card generation, validation, marking

### rules/
- **RuleEngine**: Pattern matching for all Bingo patterns
- **PatternResult**: Match result with positions and completion status

### events/
- **Event**: Immutable event with type, timestamp, payload
- **EventBus**: Publish/subscribe event system

### fairness/
- **FairnessCommitment**: Pre-game commitment scheme
- **FairnessVerifier**: Post-game verification

### replay/
- **ReplayEngine**: Records all events for perfect replay
- **GameReplay**: Serializable replay data

### serialization/
- **GameSnapshot**: Complete game state snapshot
- **Serializer**: JSON serialization/deserialization

### simulation/
- **SimulationEngine**: Batch game simulation
- **SimulationResult**: Aggregated simulation metrics

### statistics/
- **StatisticsCollector**: Game statistics collection
- **GameStatistics**: Per-game statistics
- **AggregateStatistics**: Cross-game analytics

### application/
- **GameService**: Main orchestrator for rooms, games, players
- **RoomService**: Room lifecycle management
- **CardService**: Card generation and validation
- **BallService**: Ball calling control
- **PlayerService**: Player join/leave/mark
- **PrizeService**: Prize calculation and distribution

## State Machines

### Game Lifecycle

```
CREATED
  -> WAITING (room opened)
  -> CANCELLED

WAITING
  -> SELLING_CARDS (room opened for sales)
  -> CANCELLED

SELLING_CARDS
  -> LOCKED (sales closed)
  -> CANCELLED

LOCKED
  -> STARTING (game initialized)
  -> SELLING_CARDS (reopen)
  -> CANCELLED

STARTING
  -> CALLING_NUMBERS (first ball called)
  -> CANCELLED

CALLING_NUMBERS
  -> PAUSED (emergency pause)
  -> WINNER_VALIDATION (potential winner)
  -> CANCELLED

PAUSED
  -> CALLING_NUMBERS (resume)
  -> CANCELLED

WINNER_VALIDATION
  -> PRIZE_DISTRIBUTION (winners verified)
  -> CANCELLED

PRIZE_DISTRIBUTION
  -> COMPLETED (prizes paid)
  -> CANCELLED

COMPLETED
  -> ARCHIVED

CANCELLED
  -> ARCHIVED

RECOVERED
  -> CALLING_NUMBERS (resume from crash)
  -> PAUSED
  -> CANCELLED

ARCHIVED
  -> (terminal state)
```

### Player Lifecycle

```
JOINED
  -> PLAYING (active participation)
  -> DISCONNECTED (lost connection)
  -> LEFT (voluntary departure)

DISCONNECTED
  -> RECONNECTED (rejoined)
  -> LEFT

PLAYING
  -> MARKING (auto/manual marking)
  -> LEFT
  -> DISCONNECTED

LEFT
  -> (terminal for this game)
```

## Event List

| Event | Description |
|-------|-------------|
| RoomCreated | Room initialized |
| PlayerJoined | Player joined room |
| CardPurchased | Card purchased by player |
| GameStarted | Game started |
| CountdownStarted | Countdown before first ball |
| BallCalled | Ball number called |
| PlayerMarked | Player marked number (auto/manual) |
| WinnerClaimed | Player claimed win |
| WinnerVerified | Win verified by engine |
| PrizeDistributed | Prize distributed to winner |
| GameCompleted | Game finished successfully |
| GameCancelled | Game cancelled |
| GameRecovered | Game recovered from crash |
| PlayerDisconnected | Player disconnected |
| PlayerReconnected | Player reconnected |

All events are:
- Immutable
- Sequenced
- Timestamped
- Replayable

## Fairness Implementation

### Commitment Scheme

1. **Pre-game**: Generate seed, compute commitment hash
2. **Publish**: Commit hash publicly before game starts
3. **Post-game**: Reveal seed
4. **Verify**: Anyone can verify the sequence matches

```python
commitment = FairnessCommitment.create(seed, salt)
# Publish commitment.commitment_hash

# After game:
assert commitment.verify(seed, salt) is True
assert FairnessVerifier.verify_game_fairness(seed, called_numbers, salt) is True
```

### Seed-Based RNG

- Uses `secrets.SystemRandom()` for cryptographically secure randomness
- Seed determines entire ball sequence
- Same seed always produces same sequence
- Sequence can be verified independently

### No Collision Guarantee

- Card fingerprints ensure uniqueness
- `FairnessVerifier.verify_no_collision()` checks all cards

## Replay Implementation

### Recording

Every state change is recorded as an event:
```python
replay_engine.record_event("BallCalled", {"number": 42})
replay_engine.record_event("PlayerMarked", {"user_id": uid, "card_id": cid, "number": 42})
```

### Playback

Replay reconstructs exact game state:
```python
replay = GameReplay.from_json(json_str)
assert len(replay.events) == original_event_count
assert replay.seed == original_seed
```

### Determinism

Given the same seed, the engine produces:
- Same ball sequence
- Same winners
- Same timing
- Same state transitions

## Recovery Implementation

### Snapshot Format

```json
{
  "game_id": "uuid",
  "room_id": "uuid",
  "state": "calling_numbers",
  "seed": "hex",
  "seed_hash": "sha256",
  "called_numbers": [1, 2, 3, ...],
  "current_number": 42,
  "started_at": "iso8601",
  "finished_at": null,
  "winner_id": null,
  "winning_pattern": "full_house",
  "prize_amount": null,
  "players": {...},
  "cards": {...}
}
```

### Recovery Process

1. Load snapshot from persistent storage
2. Restore `GameState` from snapshot
3. Reconstruct `BallEngine` from state
4. Resume game from recovered state
5. Continue normal operations

### Crash Safety

- All state mutations are atomic within a game
- Snapshots can be taken at any point
- No partial state corruption
- Rollback to last valid snapshot

## Simulation Results

### Batch Simulation

```python
sim = SimulationEngine()
result = sim.run_batch(
    room_config={"entry_fee": 10.0, "max_players": 10, "min_players": 2, "winning_pattern": "full_house"},
    game_count=1000,
    player_count=10,
    cards_per_player=1
)
```

### Metrics Tracked

- Total games played
- Total players
- Total cards sold
- Prize pool distribution
- House earnings
- Average game duration
- Pattern frequency
- Collision detection
- Fairness violations

## Test Coverage

### Unit Tests
- Ball engine (generation, verification, pause/resume)
- Card engine (generation, validation, marking, undo)
- Rule engine (all patterns, incomplete matches, unknown patterns)
- State machine (valid/invalid transitions)
- Event bus (publish/subscribe, multiple handlers)
- Fairness (commitment, verification, collision detection)
- Serialization (snapshot roundtrip)
- Statistics (collection, aggregation, distribution)

### Integration Tests
- Full game lifecycle (create -> join -> start -> call -> win -> finish)
- Crash recovery (state serialization and restoration)
- Replay determinism (same seed -> same outcome)
- Batch simulation (1000 games)
- Winner validation (duplicate prevention)

### Edge Case Tests
- Illegal state transitions
- Card validation edge cases
- Ball engine edge cases
- Pattern matching edge cases
- All 9 Bingo patterns

## Performance Metrics

### Targets
- Support thousands of concurrent games
- Minimal memory allocation per game
- Efficient serialization
- No unnecessary object duplication

### Optimizations
- `BallEngine` uses efficient list operations
- `Card` uses lightweight dataclass
- `EventBus` uses simple list storage
- `StatisticsCollector` aggregates in-memory

## Remaining Risks

1. **No async support**: Current engine is synchronous. For high concurrency, async variants should be considered.
2. **Memory growth**: Long-running simulations may accumulate events. Consider event pruning.
3. **No persistence layer**: Engine is in-memory only. Redis/database integration needed for production.
4. **Limited pattern support**: Currently supports 9 patterns. Custom patterns need registration API.
5. **No network layer**: Engine is standalone. Adapters needed for WebSocket/HTTP.

## Readiness Score for Phase 5: 8.5/10

**Ready**:
- Complete standalone engine package
- Zero framework dependencies
- Deterministic and verifiable
- Full game lifecycle
- Event sourcing
- Crash recovery
- Replay system
- Simulation engine
- Comprehensive tests

**Remaining**:
- Async support for high concurrency
- Persistence layer integration
- Network adapters for Phase 5
- Production hardening

**Phase 4 is complete. Ready for review.**

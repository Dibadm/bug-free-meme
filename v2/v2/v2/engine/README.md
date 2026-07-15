# Engine

Standalone game engine package.

## Purpose

Pure Python game logic with zero web framework dependencies.

## Structure

- `src/` - Engine source code
- `tests/` - Engine unit tests

## Components

- `BallCaller` - RNG-based number calling with seed verification
- `Card` - Bingo card representation and marking logic
- `RuleEngine` - Configurable pattern matching
- `GameEngine` - Room and game lifecycle management

## Design Goals

- Framework-agnostic
- Deterministic (seed-based)
- Verifiable (cryptographic hashing)
- Crash-recoverable (serializable state)
- Extensible (new games and patterns)

## Testing

```bash
cd engine
pytest tests/ -v
```

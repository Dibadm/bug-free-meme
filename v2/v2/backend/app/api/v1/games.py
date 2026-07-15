from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.schemas.game import GameCreate, GameRead, GameStartResponse
from app.services import GameService

router = APIRouter()


@router.get("/games/{game_id}", response_model=GameRead)
async def get_game(
    game_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> GameRead:
    service = GameService(db)
    game = await service.get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return GameRead.model_validate(game)


@router.post("/games", response_model=GameStartResponse)
async def create_game(
    game_data: GameCreate,
    db: AsyncSession = Depends(get_db),
) -> GameStartResponse:
    service = GameService(db)
    game = await service.create_game(room_id=game_data.room_id, seed=game_data.seed, seed_hash=game_data.seed_hash)
    return GameStartResponse(
        game=GameRead.model_validate(game),
        seed=game_data.seed,
        seed_hash=game_data.seed_hash,
    )

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.schemas.common import RoomTemplateCreate, RoomTemplateRead
from app.services import RoomTemplateService

router = APIRouter()


@router.get("/rooms", response_model=list[RoomTemplateRead])
async def list_room_templates(
    db: AsyncSession = Depends(get_db),
) -> list[RoomTemplateRead]:
    service = RoomTemplateService(db)
    templates = await service.get_active_templates()
    return [RoomTemplateRead.model_validate(t) for t in templates]


@router.post("/rooms", response_model=RoomTemplateRead)
async def create_room_template(
    template_data: RoomTemplateCreate,
    db: AsyncSession = Depends(get_db),
) -> RoomTemplateRead:
    service = RoomTemplateService(db)
    template = await service.create_template(**template_data.model_dump())
    return RoomTemplateRead.model_validate(template)

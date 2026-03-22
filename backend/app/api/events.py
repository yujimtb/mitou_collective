from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_event_store
from app.auth.dependencies import require_permission
from app.auth.policy_engine import Operation
from app.interfaces import IEventStore
from app.schemas import ActorRead


router = APIRouter(prefix="/events", tags=["events"])


@router.get("/recent")
async def get_recent_events(
    limit: int = Query(default=10, ge=1, le=50),
    _: ActorRead = Depends(require_permission(Operation.READ)),
    event_store: IEventStore = Depends(get_event_store),
) -> list[dict[str, object]]:
    return await event_store.recent_events(limit=limit)

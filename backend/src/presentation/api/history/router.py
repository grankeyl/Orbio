from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Query

from src.application.interactors.history import ActivityInteractor, HistoryInteractor
from src.domain.entities.history import ActivityDM, HistoryDM


history_router = APIRouter(prefix="/history", tags=["History"])


@history_router.get("")
@inject
async def get_user_history(interactor: FromDishka[HistoryInteractor]) -> list[HistoryDM]:
    """Get user history"""

    return await interactor()


@history_router.get("/activity")
@inject
async def get_market_activity(
        interactor: FromDishka[ActivityInteractor],
        collection: list[str] | None = Query(default=None, alias="collection[]"),
        sort_by: str | None = Query(default="latest"),
        number: int | None = Query(default=0, ge=0),
        limit: int = Query(default=50, ge=1, le=200, description="Number of items to return"),
        offset: int = Query(default=0, ge=0, description="Offset for pagination")
) -> list[ActivityDM]:
    """Get market activity"""
    data = {
        "collection": collection,
        "sort_by": sort_by,
        "number": number
    }
    pagination = {"limit": limit, "offset": offset}
    return await interactor(data, pagination)

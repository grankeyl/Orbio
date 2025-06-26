from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from starlette import status

from src.application.common.cart import CartGiftDTO, ResponseCartDTO
from src.application.dto.common import ResponseDTO
from src.application.dto.market import BidDTO, CreateOrderDTO, OrderIdDTO
from src.application.interactors import errors, market
from src.domain.entities.market import BidSuccessDM, OrderDM, ReadOrderDM
from src.presentation.api.market.params import GiftFilterParams, GiftSortParams


market_router = APIRouter(prefix="/market", tags=["Market"])


@market_router.get("/gifts")
@inject
async def get_all_gifts(
    filters: Annotated[GiftFilterParams, Depends()],
    interactor: FromDishka[market.GetGiftsInteractor]
) -> list[OrderDM]:
    return await interactor(filters)


@market_router.get("/gifts/{id}")
@inject
async def get_gift_by_id(id: int, interactor: FromDishka[market.GetGiftInteractor]) -> ReadOrderDM:
    try:
        return await interactor(id)
    except errors.NotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(e))


@market_router.post("/gift/buy")
@inject
async def buy_gift(dto: OrderIdDTO, interactor: FromDishka[market.BuyGiftInteractor]) -> ResponseDTO:
    try:
        await interactor(dto.id)
    except (
        errors.NotFoundError,
        errors.NotEnoughBalanceError,
        errors.NotAccessError,
        errors.GiftSendError,
    ) as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseDTO(success=True)


@market_router.post("/cart/buy")
@inject
async def buy_many_gifts(
    dto: list[CartGiftDTO],
    interactor: FromDishka[market.BuyGiftsFromCartInteractor],
    background_tasks: BackgroundTasks,
) -> ResponseCartDTO:
    try:
        is_success, cart = await interactor(dto, background_tasks)
    except errors.NotEnoughBalanceError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    return ResponseCartDTO(success=is_success, cart=cart)
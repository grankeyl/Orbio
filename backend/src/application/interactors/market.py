from datetime import datetime, timezone

from aiogram import Bot
from fastapi import BackgroundTasks
from pyrogram.client import Client

from src.application.common.cart import CartGiftDTO
from src.application.common.const import MAX_GIFT_NUMBER, GiftRarity, HistoryType, PriceList, ShopType
from src.application.common.utils import build_direct_link, get_file_logger, send_message
from src.application.dto.market import BidDTO, CreateOrderDTO
from src.application.dto.user import UnsellGiftDTO
from src.application.interactors import errors
from src.application.interfaces.database import DBSession
from src.application.interfaces.history import HistorySaver
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.market import OrderManager, OrderReader
from src.application.interfaces.user import UserSaver, UserManager
from src.domain.entities.bot import BotInfoDM
from src.domain.entities.cart import CartGiftDM
from src.domain.entities.history import CreateHistoryDM
from src.domain.entities.market import BidDM, BidSuccessDM, GiftFiltersDM, OrderDM, ReadOrderDM
from src.domain.entities.user import UpdateUserBalanceDM, UserDM
from src.infrastructure.gateways.history import HistoryGateway
from src.entrypoint.config import Config
from src.presentation.api.market.params import GiftFilterParams, GiftSortParams
from src.presentation.bot.keyboards.base import order_kb
from src.presentation.bot.services import text


logger = get_file_logger(__name__, "src/logs/market.log")


class CreateOrderInteractor(Interactor[CreateOrderDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        market_gateway: OrderManager,
        history_gateway: HistorySaver,
        user: UserDM,
        user_gateway: UserSaver,
        config: Config,
    ) -> None:
        self._db_session = db_session
        self._market_gateway = market_gateway
        self._history_gateway = history_gateway
        self._user = user
        self._user_gateway = user_gateway
        self._config = config
        self._user = user

    async def __call__(self, data: CreateOrderDTO) -> None:
        order = await self._market_gateway.update_order(
            {
                "price": data.price,
                "is_active": True,
            },
            id=data.gift_id,
            seller_id=self._user.id,
        )
        if not order:
            raise errors.NotAccessError("Gift not found")

        await self._db_session.commit()

        gift = await self._market_gateway.get_one(id=data.gift_id)

        history_data = CreateHistoryDM(
            user_id=self._user.id, 
            type=HistoryType.SELL_GIFT, 
            price=data.price,
            gift=gift.type,
            gift_number=gift.number,
            model_name=gift.model_name,
        )

        await self._history_gateway.save(history_data)
        await self._db_session.commit()

        logger.info(f"CreateOrderInteractor: @{self._user.username} #{self._user.id} created the order")


class UnsellOrderInteractor(Interactor[UnsellGiftDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        market_gateway: OrderManager,
        history_gateway: HistorySaver,
        user: UserDM,
        user_gateway: UserSaver,
        config: Config,
    ) -> None:
        self._db_session = db_session
        self._market_gateway = market_gateway
        self._history_gateway = history_gateway
        self._user = user
        self._user_gateway = user_gateway
        self._config = config

    async def __call__(self, data: UnsellGiftDTO) -> None:
        order = await self._market_gateway.unsell_order(
            {
                "is_active": False,
            },
            id=data.gift_id,
            seller_id=self._user.id,
        )
        if not order:
            raise errors.NotAccessError("Gift not found")

        await self._db_session.commit()

        gift = await self._market_gateway.get_one(id=data.gift_id)

        history_data = CreateHistoryDM(
            user_id=self._user.id, 
            type=HistoryType.UNLISTED_GIFT, 
            price=gift.price,
            gift=gift.type,
            gift_number=gift.number,
            model_name=gift.model_name,
        )

        await self._history_gateway.save(history_data)
        await self._db_session.commit()

        logger.info(f"UnsellOrderInteractor: @{self._user.username} #{self._user.id} take it of gift from the market")



class GetGiftsInteractor:
    def __init__(self, market_gateway: OrderReader, user: UserDM) -> None:
        self._market_gateway = market_gateway
        self._user = user

    async def __call__(self, filters: GiftFilterParams) -> list[OrderDM]:
        prepared_filters = self._prepare_filters(filters)
        return await self._market_gateway.get_all_gifts(prepared_filters)

    def _prepare_filters(self, filters: GiftFilterParams) -> GiftFiltersDM:
        return GiftFiltersDM(
            limit=filters.limit,
            offset=filters.offset,
            collection=filters.collection,
            model=filters.model,
            sort_by=filters.sort_by,
            from_price=filters.from_price,
            to_price=filters.to_price,
            number=filters.number,
        )


class GetGiftInteractor(Interactor[int, ReadOrderDM]):
    def __init__(self, market_gateway: OrderReader) -> None:
        self._market_gateway = market_gateway

    async def __call__(self, gift_id: int) -> ReadOrderDM:
        gift = await self._market_gateway.get_full_order(id=gift_id, is_completed=False)
        if not gift:
            raise errors.NotFoundError("Gift not found")
        return gift


class BuyGiftInteractor(Interactor[int, OrderDM]):
    def __init__(
        self,
        db_session: DBSession,
        market_gateway: OrderManager,
        user_gateway: UserManager,
        history_gateway: HistorySaver,
        user: UserDM,
        bot: Bot,
        bot_info: BotInfoDM,
        config: Config,
        client: Client,
    ) -> None:
        self._db_session = db_session
        self._market_gateway = market_gateway
        self._user_gateway = user_gateway
        self._history_gateway = history_gateway
        self._user = user
        self._bot = bot
        self._bot_info = bot_info
        self._config = config
        self._client = client

    async def __call__(self, gift_id: int) -> OrderDM:
        order = await self._market_gateway.get_one(id=gift_id, is_completed=False, is_active=True)

        if not order:
            raise errors.NotFoundError("Gift not found")
        if self._user.id == order.seller_id:
            raise errors.NotAccessError("Forbidden")

        buyer = await self._user_gateway.update_balance(
            UpdateUserBalanceDM(id=self._user.id, amount=-(order.price))
        )
        if buyer.balance <= 0.0:  # type: ignore
            await self._db_session.rollback()
            raise errors.NotEnoughBalanceError("User not enough balance")

        await self._db_session.commit()

        await self._user_gateway.update_balance(
            UpdateUserBalanceDM(id=order.seller_id, amount=order.price)
        )

        await self._market_gateway.update_order(
            {"seller_id": self._user.id, "is_active": False, "completed_order_date": datetime.now()},
            id=gift_id, is_active=True
        )
        await self._db_session.commit()

        buyer_history_data = CreateHistoryDM(
            user_id=self._user.id,
            type=HistoryType.BUY_GIFT,
            price=order.price,
            gift=order.type,
            gift_number=order.number,
            model_name=order.model_name,
        )
        await self._history_gateway.save_many([buyer_history_data])
        await self._db_session.commit()

        direct_link = build_direct_link(self._bot_info.username, f"gifts")
        await send_message(
            self._bot,
            text.get_buy_gift_text(order.type, order.number),
            [order.seller_id],
            reply_markup=order_kb(order.type, order.number, direct_link),
        )

        if self._config.bot.owners_chat_id:
            await send_message(
                self._bot,
                text.sold_gift_text(order.type, order.number, order.price),
                self._config.bot.owners_chat_id
            )

        logger.info(
            "BuyGiftInteractor: "
            f"@{self._user.username} #{self._user.id} buy the order with id: {gift_id}"
        )
        return order


class NewBidInteractor(Interactor[BidDTO, BidSuccessDM]):
    def __init__(
        self,
        db_session: DBSession,
        market_gateway: OrderManager,
        user: UserDM,
        user_gateway: UserSaver,
        history_gateway: HistorySaver,
        bot: Bot,
        bot_info: BotInfoDM,
    ) -> None:
        self._db_session = db_session
        self._market_gateway = market_gateway
        self._user = user
        self._user_gateway = user_gateway
        self._history_gateway = history_gateway
        self._bot = bot
        self._bot_info = bot_info

    async def __call__(self, data: BidDTO) -> BidSuccessDM:
        if not (
            order := await self._market_gateway.get_one(id=data.id, is_completed=False, is_active=True)
        ):
            raise errors.NotFoundError("Gift not found")
        if not order.min_step or order.min_step > data.amount - order.price + PriceList.NEW_BID_EXTRA:
            raise errors.AuctionBidError("Amount is too low or this gift not on auction")
        if order.auction_end_time and order.auction_end_time < datetime.now(tz=timezone.utc):
            raise errors.AuctionBidError("Auction already ended")
        if self._user.balance < data.amount:
            raise errors.NotEnoughBalanceError("User does not have enough balance")

        new_balance = self._user.balance - data.amount
        if order.buyer_id == self._user.id:
            new_balance += order.price

        await self._user_gateway.update_balance(
            UpdateUserBalanceDM(id=self._user.id, amount=-data.amount)
        )
        if order.buyer_id:
            await self._user_gateway.update_balance(
                UpdateUserBalanceDM(id=order.buyer_id, amount=order.price)
            )

        updated_data = {"buyer_id": self._user.id, "price": data.amount}
        await self._market_gateway.update_order(updated_data, id=data.id)
        await self._market_gateway.save_auction_bid(
            BidDM(gift_id=data.id, amount=data.amount, buyer_id=self._user.id)
        )
        history_data = CreateHistoryDM(
            user_id=self._user.id,
            type=HistoryType.BID_GIFT,
            price=data.amount,
            gift=order.type,
            gift_number=order.number,
            model_name=order.model_name,
        )
        await self._history_gateway.save(history_data)
        await self._db_session.commit()
        if order.buyer_id:
            direct_link = build_direct_link(self._bot_info.username, f"gifts")
            await send_message(
                self._bot,
                "Your bid was outbid at the auction",
                [order.buyer_id],
                reply_markup=order_kb(order.type, order.number, direct_link),
            )
        return BidSuccessDM(user_balance=new_balance, created_at=datetime.now(tz=timezone.utc))


class BuyGiftsFromCartInteractor(Interactor):
    def __init__(
        self,
        db_session: DBSession,
        user: UserDM,
        market_gateway: OrderManager,
        buy_gift_interactor: BuyGiftInteractor,
    ) -> None:
        self._db_session = db_session
        self._user = user
        self._market_gateway = market_gateway
        self._buy_gift_interactor = buy_gift_interactor

    async def __call__(
        self, data: list[CartGiftDTO], background_tasks: BackgroundTasks
    ) -> tuple[bool, list[CartGiftDM]]:
        gifts_ids = [gift.id for gift in data]
        gifts = await self._market_gateway.get_gifts_by_ids(gifts_ids, self._user.id)
        if len(gifts) != len(data):
            return False, gifts

        for gift_data in data:
            for gift in gifts:
                if gift.id == gift_data.id:
                    if gift.price != gift_data.price:
                        return False, gifts

        for gift in gifts:
            background_tasks.add_task(self._buy_gift_interactor, gift.id)
        return True, gifts

from datetime import datetime, timezone

from sqlalchemy import delete, func, insert, select, update, asc, desc, cast, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.common.const import ShopType, PriceList
from src.application.interactors.errors import AlreadyExistError
from src.application.interfaces.market import OrderReader, OrderSaver
from src.domain.entities.cart import CartGiftDM
from src.domain.entities.market import (
    BidDM,
    CreateOrderDM,
    GiftFiltersDM,
    OrderDM,
    ReadOrderDM,
    UserGiftDM,
)
from src.infrastructure.models.giveaway import Giveaway
from src.infrastructure.models.order import Bid, Order
from src.presentation.api.market.params import GiftSortParams


class MarketGateway(OrderSaver, OrderReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all_gifts(
        self,
        filters: GiftFiltersDM,
    ) -> list[OrderDM]:
        stmt = select(Order)

        filters_by = {'is_completed':False}
        filters_by['is_active'] = True
        
        stmt = stmt.filter_by(**filters_by)

        if filters.collection and len(filters.collection) > 0:
            stmt = stmt.where(Order.type.in_(filters.collection))
        if filters.model and len(filters.model) > 0:
            stmt = stmt.where(Order.model_name.in_(filters.model))

        if filters.sort_by == 'latest':
            stmt = stmt.order_by(Order.created_at.desc())
        elif filters.sort_by == 'price_low_to_high':
            stmt = stmt.order_by(asc(Order.price))
        elif filters.sort_by == 'price_high_to_low':
            stmt = stmt.order_by(desc(Order.price))
        elif filters.sort_by == 'random':
            stmt = stmt.order_by(func.random())
        else:
            stmt = stmt.order_by(Order.created_at.desc())
        
        if filters.from_price:
            stmt = stmt.filter(Order.price >= filters.from_price)
        if filters.to_price:
            stmt = stmt.filter(Order.price <= filters.to_price)
        if filters.number is not None:
            stmt = stmt.filter(cast(Order.number, String).like(f"%{filters.number}%"))

        stmt = stmt.limit(filters.limit).offset(filters.offset)

        result = await self._session.execute(stmt)
        return [OrderDM(**order.__dict__) for order in result.scalars().all()]

    async def get_user_gifts(
        self, user_id: int, limit: int | None, offset: int | None, for_sell: int | None
    ) -> list[UserGiftDM]:
        filters = {'seller_id': user_id, 'is_completed':False}

        if for_sell == 1:
            filters['is_active'] = False

        if for_sell == 0:
            filters['is_active'] = True

        stmt = (
            select(Order)
            .filter_by(**filters)
            .order_by(Order.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self._session.execute(stmt)
        gifts = result.scalars().all()
        order_dms = []
        result = None

        try:
            smth = select(Giveaway.gifts_ids).filter(
                Giveaway.winners_ids.contains([user_id]),
            )
            giftFromGive = await self._session.execute(smth)
            r = giftFromGive.scalars().all()

            # Flatten the nested array structure
            flattened = []
            for item in r:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)
            # Return unique elements using a set
            result = list(set(flattened))
        except:
            None

        for order in gifts:
            order_dict = order.__dict__.copy()

            # Check for None values and handle accordingly
            if order_dict.get('price') is None:
                order_dict['price'] = 0.0  # Default price to 0.0 if None

            # Remove SQLAlchemy internal attributes
            for key in list(order_dict.keys()):
                if key.startswith('_'):
                    order_dict.pop(key)

            if result and order_dict['id'] in result:
                order_dict['free_withdraw'] = True
            try:
                order_dm = UserGiftDM(**order_dict)
                order_dms.append(order_dm)
            except Exception as e:
                print(f"Error converting order {order.id}: {e}")
                # Continue with next order even if this one fails
                continue

        return order_dms

    async def get_user_gift(self, user_id: int, gift_id: int) -> UserGiftDM | None:
        stmt = select(Order).filter_by(id=gift_id, seller_id=user_id, is_completed=False)
        result = await self._session.execute(stmt)
        if not (gift := result.scalar_one_or_none()):
            return
        return UserGiftDM(**gift.__dict__)

    async def get_many(self, **filters) -> list[OrderDM]:
        stmt = select(Order).filter_by(**filters)
        result = await self._session.execute(stmt)
        orders = result.scalars().all()
        order_dms = []

        for order in orders:
            order_dict = order.__dict__.copy()

            # Check for None values and handle accordingly
            if order_dict.get('price') is None:
                order_dict['price'] = 0.0  # Default price to 0.0 if None

            # Remove SQLAlchemy internal attributes
            for key in list(order_dict.keys()):
                if key.startswith('_'):
                    order_dict.pop(key)

            try:
                order_dm = OrderDM(**order_dict)
                order_dms.append(order_dm)
            except Exception as e:
                print(f"Error converting order {order.id}: {e}")
                # Continue with next order even if this one fails
                continue

        return order_dms

    async def get_count_gifts(self) -> tuple[int, int, int]:
        # Count total orders
        stmt_all = select(func.count(Order.id))
        res_all = await self._session.execute(stmt_all)
        total_count = res_all.scalar_one()

        # Count completed orders
        stmt_completed = select(func.count(Order.id)).where(Order.is_completed == True)
        res_completed = await self._session.execute(stmt_completed)
        completed_count = res_completed.scalar_one()

        # Count active (listed) orders
        stmt_active = select(func.count(Order.id)).where(Order.is_active == True, Order.is_completed == False)
        res_active = await self._session.execute(stmt_active)
        active_count = res_active.scalar_one()

        return total_count, completed_count, active_count

    async def get_total_trading_volume(self) -> float:
        stmt = select(func.sum(Order.price)).where(Order.is_completed == True)
        result = await self._session.execute(stmt)
        volume = result.scalar_one_or_none()
        return volume if volume is not None else 0.0

    async def get_one(self, **filters) -> OrderDM | None:
        stmt = select(Order).filter_by(**filters)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return OrderDM(**order.__dict__)

    async def get_full_order(self, **filters) -> ReadOrderDM | None:
        stmt = select(Order).filter_by(**filters)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return ReadOrderDM(**order.__dict__)

    async def get_gifts_by_ids(self, gifts_ids: list[int], user_id: int) -> list[CartGiftDM]:
        stmt = select(Order).where(
            Order.id.in_(gifts_ids),
            Order.is_active == True,
            Order.is_completed == False,
            Order.min_step == None,
            Order.seller_id != user_id,
        )
        result = await self._session.execute(stmt)
        orders = result.scalars().all()
        order_dms = []

        for order in orders:
            order_dict = order.__dict__.copy()

            # Check for None values and handle accordingly
            if order_dict.get('price') is None:
                order_dict['price'] = 0.0  # Default price to 0.0 if None
            order_dict['price'] += order_dict['price'] * PriceList.GIFT_COMMISSION_BUY

            # Remove SQLAlchemy internal attributes
            for key in list(order_dict.keys()):
                if key.startswith('_'):
                    order_dict.pop(key)

            try:
                order_dm = CartGiftDM(**order_dict)
                order_dms.append(order_dm)
            except Exception as e:
                print(f"Error converting order {order.id}: {e}")
                # Continue with next order even if this one fails
                continue
        return order_dms

    async def get_user_gifts_by_ids(self, gifts_ids: list[int], **filters) -> list[UserGiftDM]:
        stmt = select(Order).where(Order.id.in_(gifts_ids)).filter_by(**filters)
        result = await self._session.execute(stmt)
        return [UserGiftDM(**order.__dict__) for order in result.scalars().all()]

    async def get_auction_orders(self) -> list[OrderDM]:
        stmt = select(Order).where(
            Order.min_step != None,
            Order.auction_end_time <= datetime.now(tz=timezone.utc),
            Order.is_completed == False,
        )
        result = await self._session.execute(stmt)
        return [OrderDM(**order.__dict__) for order in result.scalars().all()]

    async def save(self, order_dm: CreateOrderDM) -> CreateOrderDM:
        try:
            stmt = insert(Order).values(order_dm.model_dump()).returning(Order)
        except IntegrityError:
            raise AlreadyExistError("Order already exist")

        result = await self._session.execute(stmt)
        return CreateOrderDM(**result.scalar_one().__dict__)

    async def update_order(self, data: dict, **filters) -> OrderDM | None:
        stmt = update(Order).filter_by(**filters).values(data).returning(Order)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        order_dict = order.__dict__.copy()
        # Check for None values and handle accordingly
        if order_dict.get('price') is None:
            order_dict['price'] = 0.0

        # Remove SQLAlchemy internal attributes
        for key in list(order_dict.keys()):
            if key.startswith('_'):
                order_dict.pop(key)

        try:
            return OrderDM(**order_dict)
        except Exception as e:
            print(f"Error updating order {order.id}: {e}")

    async def unsell_order(self, data: dict, **filters) -> OrderDM | None:
        stmt = update(Order).filter_by(**filters).values(data).returning(Order)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        order_dict = order.__dict__.copy()
        order_dict['price'] = 0.0

        # Remove SQLAlchemy internal attributes
        for key in list(order_dict.keys()):
            if key.startswith('_'):
                order_dict.pop(key)

        try:
            return OrderDM(**order_dict)
        except Exception as e:
            print(f"Error updating order {order.id}: {e}")
            # Continue with next order even if this one fails

    async def update_giveaway_gifts(self, data: dict, gifts_ids: list[int]) -> None:
        stmt = update(Order).values(data).where(Order.id.in_(gifts_ids))
        await self._session.execute(stmt)

    async def withdraw_from_market(self, data: dict, **filters) -> UserGiftDM | None:
        stmt = update(Order).filter_by(**filters).values(data).returning(Order)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return UserGiftDM(**order.__dict__)

    async def update_cart_orders(self, values: dict, gifts_ids: list[int], user_id: int) -> None:
        stmt = (
            update(Order)
            .where(
                Order.id.in_(gifts_ids),
                Order.is_active == True,
                Order.is_completed == False,
                Order.min_step == None,
                Order.seller_id != user_id,
            )
            .values(values)
        )
        await self._session.execute(stmt)

    async def delete_order(self, **filters) -> UserGiftDM | None:
        stmt = delete(Order).filter_by(**filters).returning(Order)
        result = await self._session.execute(stmt)
        order = result.scalar_one_or_none()
        if order:
            return UserGiftDM(**order.__dict__)

    async def save_auction_bid(self, data: BidDM) -> None:
        stmt = insert(Bid).values(data.model_dump())
        await self._session.execute(stmt)

    async def delete_auction_bids(self, **filters) -> None:
        stmt = delete(Bid).filter_by(**filters)
        await self._session.execute(stmt)

    async def get_user_trading_volume(self, user_id: int) -> float:
        stmt = select(func.sum(Order.price)).where(
            Order.is_completed == True,
            (Order.seller_id == user_id) | (Order.buyer_id == user_id)
        )
        result = await self._session.execute(stmt)
        volume = result.scalar_one_or_none()
        return volume if volume else 0.0

    async def get_user_active_gifts_count(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(Order).filter_by(
            seller_id=user_id, is_completed=False
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def edit_gift_price(self, gift_id: int, price: float) -> None:
        stmt = update(Order).values(price=price).where(Order.id == gift_id)
        await self._session.execute(stmt)
        await self._session.commit()

    async def edit_gift_prices(self, percent: int) -> None:
        multiplier = 1 + (percent / 100)
        stmt = update(Order).values(price=Order.price * multiplier)
        await self._session.execute(stmt)
        await self._session.commit()
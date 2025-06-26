from sqlalchemy import func, select

from src.application.common.const import GiftRarity
from src.domain.entities.market import CreateOrderDM, OrderDM
from src.domain.entities.user import UpdateUserBalanceDM
from src.entrypoint.config import PostgresConfig
from src.infrastructure.database.session import new_session_maker
from src.infrastructure.gateways.market import MarketGateway
from src.infrastructure.gateways.giveaway import GiveawayGateway
from src.infrastructure.gateways.user import UserGateway
from src.infrastructure.models.order import Order
from src.infrastructure.models.user import User


async def get_orders_info(
    gift_type: str, gift_number: int, postgres_config: PostgresConfig
) -> list[OrderDM] | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if orders := await MarketGateway(session).get_many(type=gift_type, number=gift_number):
            return orders


async def get_gift(order_id: int, postgres_config: PostgresConfig) -> OrderDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        return await MarketGateway(session).get_one(id=order_id)


async def delete_order(order_id: int, postgres_config: PostgresConfig) -> OrderDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if order := await MarketGateway(session).delete_order(id=order_id):
            await session.commit()
            return order


async def create_order(data: CreateOrderDM, postgres_config: PostgresConfig) -> CreateOrderDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if order := await MarketGateway(session).save(data):
            await session.commit()
            return order


async def get_count_gifts(postgres_config: PostgresConfig) -> tuple[int, int, int]:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        gateway = MarketGateway(session)
        total_count, completed_count, active_count = await gateway.get_count_gifts()
    return total_count, completed_count, active_count


async def get_total_trading_volume(postgres_config: PostgresConfig) -> float:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        gateway = MarketGateway(session)
        volume = await gateway.get_total_trading_volume()
    return volume


async def cancel_order(order_id: int, postgres_config: PostgresConfig) -> bool:
    session_maker = new_session_maker(postgres_config)
    data = dict(buyer_id=None)

    async with session_maker() as session:
        gateway = MarketGateway(session)
        if not (order := await gateway.get_one(id=order_id)):
            return False
        await UserGateway(session).update_balance(
            UpdateUserBalanceDM(id=order.buyer_id, amount=order.price)
        )
        await gateway.update_order(data, id=order_id)
        await session.commit()
    return True


async def create_gift_for_user(user_id: int, postgres_config: PostgresConfig, sell: bool) -> bool:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        try:
            result = await session.scalar(select(func.max(Order.id)))
            # Create order data directly using CreateOrderDM
            for i in range(10):
                num = result + (i+1)
                order_data = OrderDM(
                    id=num,
                    gift_id=num,
                    seller_id=user_id,
                    number=num,  # Use same ID for number
                    type="Jack-in-the-Box",  # Default type
                    model=4.0,
                    pattern=1.0,
                    background=1.0,
                    model_name="Christmas",
                    pattern_name="Default Pattern",
                    background_name="Default Background",
                    rarity=GiftRarity.RARE,
                    is_active=sell,
                    price=1.0,
                )

                await MarketGateway(session).save(order_data)
            await session.commit()
            return True
        except Exception as e:
            print(f"Error creating gift: {e}")
            await session.rollback()
            return False


async def create_give_fill(postgres, g: int):
    session_maker = new_session_maker(postgres)
    async with session_maker() as session:
        try:
            stmt = select(User.id)
            result = await session.execute(stmt)

            await GiveawayGateway(session).update_giveaway({
                "participants_ids": result.scalars().all(),
            }, id=g)

            await session.commit()
            return True
        except Exception as e:
            print(f"Error creating test user: {e}")
            return False
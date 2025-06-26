from src.application.common.utils import generate_deposit_comment
from src.domain.entities.user import CreateUserDM, FullUserInfoDM, UpdateUserBalanceDM
from src.entrypoint.config import PostgresConfig
from src.infrastructure.database.session import new_session_maker
from src.infrastructure.gateways.market import MarketGateway
from src.infrastructure.gateways.user import UserGateway
from src.infrastructure.gateways.wallet import WalletGateway
from src.infrastructure.models.user import User


async def get_count_users(postgres_config: PostgresConfig) -> int:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        return await UserGateway(session).get_count_users()


async def ban_user(postgres_config: PostgresConfig, user_id: int) -> bool:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if await UserGateway(session).update_user(dict(is_banned=True), id=user_id):
            await session.commit()
            return True
    return False


async def unban_user(postgres_config: PostgresConfig, user_id: int) -> bool:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if await UserGateway(session).update_user(dict(is_banned=False), id=user_id):
            await session.commit()
            return True
    return False


async def add_balance_user(postgres_config: PostgresConfig, user_id: int, amount: float) -> bool:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if await UserGateway(session).update_balance(UpdateUserBalanceDM(id=user_id, amount=amount)):
            await session.commit()
            return True
    return False


async def set_custom_referral_percent(postgres_config: PostgresConfig, user_id: int, percent: int) -> bool:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if await UserGateway(session).set_custom_referral_percent(user_id, percent):
            await session.commit()
            return True
    return False


async def get_full_user_info(postgres_config: PostgresConfig, user_id: int) -> FullUserInfoDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        gateway = UserGateway(session)
        market_gateway = MarketGateway(session)
        
        if not (user := await gateway.get_by_id(user_id)):
            return
            
        orders = await market_gateway.get_many(seller_id=user_id, is_completed=False)
        withdraw_requests, total_withdrawn = await WalletGateway(session).get_by_user_id(user_id)
        referrals_count = await gateway.get_count_referrals(user_id)
        trading_volume = await market_gateway.get_user_trading_volume(user_id)
        active_gifts_count = await market_gateway.get_user_active_gifts_count(user_id)

    return FullUserInfoDM(
        **user.model_dump(),
        orders=orders,
        withdraw_requests=withdraw_requests,
        total_withdrawn=total_withdrawn,
        referrals_count=referrals_count,
        trading_volume=trading_volume,
        active_gifts_count=active_gifts_count,
    )


async def get_total_balance(postgres_config: PostgresConfig) -> float:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        return await UserGateway(session).get_sum_users_balance()


async def create_user_if_not_exist(
    user_id: int,
    username: str | None,
    first_name: str | None,
    postgres_config: PostgresConfig
) -> None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        user_gateway = UserGateway(session)
        if not await user_gateway.get_by_id(user_id):
            deposit_comment = generate_deposit_comment()
            user_dm = CreateUserDM(
                id=user_id,
                username=username,
                first_name=first_name,
                deposit_comment=deposit_comment,
                language_code="ru"
            )
            await user_gateway.save(user_dm)
            await session.commit()


async def get_user_balance(postgres_config: PostgresConfig, user_id: int) -> float:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        user_gateway = UserGateway(session)
        user = await user_gateway.get_by_id(user_id)
        return user.balance if user else 0.0


async def create_test_user(postgres, user_data: dict) -> bool:
    session_maker = new_session_maker(postgres)
    async with session_maker() as session:
        try:
            session.add(User(**user_data))
            await session.commit()
            return True
        except Exception as e:
            print(f"Error creating test user: {e}")
            return False


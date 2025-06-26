from aiogram import Bot
from tonutils.client import TonapiClient
from tonutils.wallet import WalletV5R1

from src.application.common.const import HistoryType
from src.application.common.utils import send_message
from src.domain.entities.history import CreateHistoryDM
from src.domain.entities.wallet import WithdrawRequestDM
from src.domain.entities.user import UpdateUserBalanceDM
from src.entrypoint.config import Config, PostgresConfig, TonapiConfig
from src.infrastructure.database.session import new_session_maker
from src.infrastructure.gateways.history import HistoryGateway
from src.infrastructure.gateways.wallet import WalletGateway
from src.infrastructure.gateways.user import UserGateway


async def run_tracker(config: Config, bot: Bot) -> None:
    session_maker = new_session_maker(config.postgres)
    async with session_maker() as session:
        requests = await WalletGateway(session).get_many(is_completed=False)
    
    for request in requests:
        # Проверяем баланс пользователя перед выводом
        if not await check_user_balance(request, config.postgres):
            # Запись об ошибке баланса в запрос
            error_message = "Пользователь не найден или его баланс меньше нуля"
            await set_withdraw_error(request.id, error_message, config.postgres)
            
            # Уведомления
            await send_message(
                bot, 
                f"❌ Вывод {request.amount:.2f} TON не может быть выполнен: {error_message}", 
                [request.user_id]
            )
            await send_message(
                bot,
                f"⚠️ Отклонен вывод {request.amount:.2f} TON для пользователя #{request.user_id}: {error_message}",
                [config.bot.DEPOSIT_CHAT_ID],
                message_thread_id=config.bot.MODERATION_THREAD_ID,
            )
            continue
        
        try:
            # Уменьшаем баланс пользователя
            # await decrease_user_balance(request, config.postgres)
            
            # Выполняем транзакцию
            await send_transaction(request, config.tonapi)
            await complete_withdraw_request(request.id, config.postgres)
            
            # Уведомляем о выполнении
            await send_message(bot, f"✅ Вывод {request.amount:.2f} TON исполнен", [request.user_id])
            await send_message(
                bot,
                f"👛 Пользователь #{request.user_id} вывел {request.amount:.2f} TON",
                [config.bot.DEPOSIT_CHAT_ID],
                message_thread_id=config.bot.MODERATION_THREAD_ID,
            )
        except Exception as e:
            # Сохраняем информацию об ошибке в запрос
            error_message = str(e)
            await set_withdraw_error(request.id, error_message, config.postgres)
            
            # Возвращаем средства при ошибке
            # await restore_user_balance(request, config.postgres)
            
            # Уведомляем об ошибке
            error_notify = f"⚠️ Ошибка при выводе {request.amount:.2f} TON для пользователя #{request.user_id}: {error_message}"
            await send_message(
                bot,
                error_notify,
                [config.bot.DEPOSIT_CHAT_ID],
                message_thread_id=config.bot.MODERATION_THREAD_ID,
            )


async def set_withdraw_error(request_id: int, error_message: str, postgres_config: PostgresConfig) -> None:
    """Сохраняет информацию об ошибке в запрос на вывод"""
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        wallet_gateway = WalletGateway(session)
        await wallet_gateway.set_error(request_id, error_message)
        await session.commit()


async def check_user_balance(request: WithdrawRequestDM, postgres_config: PostgresConfig) -> bool:
    """Проверяет, достаточно ли средств у пользователя для вывода"""
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        user_gateway = UserGateway(session)
        
        # Получаем информацию о пользователе
        user = await user_gateway.get_by_id(request.user_id)
        
        # Проверяем баланс
        if not user or user.balance < 0:
            return False
        
        return True


async def decrease_user_balance(request: WithdrawRequestDM, postgres_config: PostgresConfig) -> bool:
    """Уменьшает баланс пользователя на сумму вывода"""
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        user_gateway = UserGateway(session)
        
        # Отрицательная сумма для списания
        balance_update = UpdateUserBalanceDM(
            id=request.user_id,
            amount=-request.amount
        )
        
        # Обновляем баланс
        if await user_gateway.update_balance(balance_update):
            await session.commit()
            return True
            
        return False


async def restore_user_balance(request: WithdrawRequestDM, postgres_config: PostgresConfig) -> bool:
    """Восстанавливает баланс пользователя в случае ошибки при выводе"""
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        user_gateway = UserGateway(session)
        
        # Положительная сумма для возврата
        balance_update = UpdateUserBalanceDM(
            id=request.user_id,
            amount=request.amount
        )
        
        # Возвращаем средства
        if await user_gateway.update_balance(balance_update):
            await session.commit()
            return True
            
        return False


async def complete_withdraw_request(
    request_id: int, postgres_config: PostgresConfig
) -> WithdrawRequestDM | None:
    session_maker = new_session_maker(postgres_config)
    async with session_maker() as session:
        if withdraw_request := await WalletGateway(session).set_completed(request_id):
            history_data = CreateHistoryDM(
                user_id=withdraw_request.user_id,
                price=withdraw_request.amount,
                type=HistoryType.WITHDRAW,
            )
            await HistoryGateway(session).save(history_data)
            await session.commit()
            return withdraw_request


async def send_transaction(withdraw_request: WithdrawRequestDM, ton_config: TonapiConfig) -> None:
    client = TonapiClient(api_key=ton_config.TONAPI_TOKEN, is_testnet=ton_config.IS_TESTNET)
    wallet, _, _, _ = WalletV5R1.from_mnemonic(client, ton_config.WALLET_MNEMONICS)
    await wallet.transfer(withdraw_request.wallet, withdraw_request.amount)

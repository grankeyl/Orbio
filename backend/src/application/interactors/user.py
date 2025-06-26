from aiogram import Bot
from aiogram.utils.payload import decode_payload, encode_payload
from pyrogram.client import Client
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List
from dataclasses import asdict
from src.application.common.utils import send_message

from src.application.common.const import DEFAULT_AVATAR_URL, PriceList, HistoryType, MAX_GIFT_REF_COUNT
from src.application.common.send_gift import send_gift
from src.application.common.utils import build_direct_link, generate_deposit_comment, get_file_logger
from src.application.dto.market import UpdateOrderDTO
from src.application.dto.user import LoginDTO, UserDTO, ReferralDto
from src.application.interactors.errors import GiftSendError, NotFoundError, NotEnoughBalanceError
from src.application.interfaces.auth import InitDataValidator, TokenEncoder
from src.application.interfaces.database import DBSession
from src.application.interfaces.history import HistorySaver
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.market import OrderReader, OrderSaver
from src.application.interfaces.user import UserManager, UserReader, UserSaver
from src.infrastructure.gateways.settings import SettingsGateway
from src.domain.entities.bot import BotInfoDM
from src.domain.entities.history import CreateHistoryDM
from src.domain.entities.market import OrderDM, UserGiftDM
from src.domain.entities.user import CreateUserDM, UserDM
from src.domain.entities.user import UpdateUserBalanceDM
from src.entrypoint.config import Config
from src.infrastructure.models.giveaway import Giveaway

logger = get_file_logger(__name__, "src/logs/user.log")


class LoginInteractor(Interactor[LoginDTO, str]):
    def __init__(
        self,
        db_session: DBSession,
        token_gateway: TokenEncoder,
        telegram_gateway: InitDataValidator,
        user_gateway: UserManager,
        market_gateway: OrderReader,
    ) -> None:
        self._db_session = db_session
        self._token_gateway = token_gateway
        self._telegram_gateway = telegram_gateway
        self._user_gateway = user_gateway
        self._market_gateway = market_gateway

    async def __call__(self, data: LoginDTO) -> str | None:
        try:
            valid_data = self._telegram_gateway.validate_telegram_user(data.init_data)
        except Exception:
            return None
        if not valid_data:
            return None

        user_data = valid_data.user
        user_id = user_data["id"]
        user = await self._user_gateway.get_by_id(user_id)
        photo_url = user_data.get("photo_url")
        if not photo_url:
            photo_url = DEFAULT_AVATAR_URL
        if not user:
            deposit_comment = generate_deposit_comment()
            user_dm = CreateUserDM(
                id=user_id,
                photo_url=photo_url,
                username=user_data.get("username"),
                first_name=user_data.get("first_name"),
                deposit_comment=deposit_comment,
                language_code=user_data.get('language_code'),
            )
            try:
                user = await self._user_gateway.save(user_dm)
                await self._db_session.commit()
            except IntegrityError:
                user = await self._user_gateway.get_by_id(user_id)
            await self._db_session.commit()

        referrer_id = self._get_referrer_id(valid_data.start_param)
        if referrer_id and referrer_id != user_id:
            ref_user = await self._user_gateway.get_by_id(referrer_id)
            if ref_user:
                referrer = await self._user_gateway.get_referrer(user_id)
                if not referrer:
                    await self._user_gateway.add_referral(referrer_id, user)
                    await self._db_session.commit()
                else:
                    if await self._market_gateway.get_user_active_gifts_count(referrer.id) < MAX_GIFT_REF_COUNT:
                        await self._user_gateway.update_referrer(referrer_id, user)
                        await self._db_session.commit()

        if user.username != user_data.get("username"):
            await self._user_gateway.update_user(dict(username=user_data.get("username")), id=user_id)
            await self._db_session.commit()
        if user.photo_url != photo_url:
            await self._user_gateway.update_user(dict(photo_url=photo_url), id=user_id)
            await self._db_session.commit()
        return self._token_gateway.encode(user_id)

    def _get_referrer_id(self, encoded_payload: str | None) -> int | None:
        try:
            return int(decode_payload(encoded_payload)) if encoded_payload else None
        except Exception:
            return


class GetUserInteractor(Interactor[None, UserDTO]):
    def __init__(
        self,
        user_gateway: UserReader,
        user: UserDM,
        bot_data: BotInfoDM,
    ) -> None:
        self._user_gateway = user_gateway
        self._user = user
        self._bot_data = bot_data

    async def __call__(self) -> UserDTO:
        referral_link = build_direct_link(self._bot_data.username, encode_payload(str(self._user.id)))
        count_referrals = await self._user_gateway.get_count_referrals(self._user.id)
        return UserDTO(
            **self._user.model_dump(),
            referral_link=referral_link,
            count_referrals=count_referrals,
        )


class GetUserReferralsInteractor(Interactor[None, List[ReferralDto]]):
    def __init__(self, user_gateway: UserReader, user: UserDM) -> None:
        self._user_gateway = user_gateway
        self._user = user

    async def __call__(self) -> list[ReferralDto]:
        referrals = await self._user_gateway.get_referrals(self._user.id, limit=10, offset=0)
        return [r.model_dump() for r in referrals]

class GetUserGiftsInteractor:
    def __init__(self, market_gateway: OrderReader, user: UserDM) -> None:
        self._market_gateway = market_gateway
        self._user = user

    async def __call__(self, limit: int | None, offset: int | None, for_sell: int | None) -> list[UserGiftDM]:
        return await self._market_gateway.get_user_gifts(self._user.id, limit, offset, for_sell)


class GetUserGiftInteractor(Interactor[int, UserGiftDM]):
    def __init__(self, market_gateway: OrderReader, user: UserDM) -> None:
        self._market_gateway = market_gateway
        self._user = user

    async def __call__(self, gift_id: int) -> UserGiftDM:
        gift = await self._market_gateway.get_user_gift(user_id=self._user.id, gift_id=gift_id)
        if not gift:
            raise NotFoundError("Gift not found")
        return gift


class UpdateUserGiftInteractor:
    def __init__(
        self, market_gateway: OrderSaver, user: UserDM, db_session: DBSession, config: Config
    ) -> None:
        self._market_gateway = market_gateway
        self._user = user
        self._db_session = db_session
        self._config = config

    async def __call__(self, id: int, data: UpdateOrderDTO) -> OrderDM:
        updated_order = await self._market_gateway.update_order(
            data.model_dump(), id=id, is_active=True, is_completed=False, seller_id=self._user.id
        )
        if not updated_order:
            await self._db_session.rollback()
            raise NotFoundError("Gift not found")
        await self._db_session.commit()

        logger.info(
            "UpdateUserGiftInteractor: "
            f"@{self._user.username} #{self._user.id} updated a gift with id: {id}"
        )
        return updated_order


class RemoveOrderInteractor(Interactor[int, None]):
    def __init__(
        self,
        market_gateway: OrderSaver,
        user: UserDM,
        db_session: DBSession,
        user_gateway: UserSaver,
    ) -> None:
        self._market_gateway = market_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._db_session = db_session

    async def __call__(self, gift_id: int) -> None:
        data = dict(is_active=False, min_step=None, auction_end_time=None, price=None)
        updated_order = await self._market_gateway.withdraw_from_market(
            data, id=gift_id, is_active=True, is_completed=False, seller_id=self._user.id, buyer_id=None
        )
        if not updated_order:
            await self._db_session.rollback()
            raise NotFoundError("Gift not found")
        await self._market_gateway.delete_auction_bids(gift_id=gift_id)

        await self._db_session.commit()

        logger.info(
            "RemoveOrderInteractor: "
            f"@{self._user.username} #{self._user.id} removed a gift from market with id: {gift_id}"
        )


class WithdrawGiftInteractor(Interactor[int, None]):
    def __init__(
        self,
        market_gateway: OrderSaver,
        market_gateway_read: OrderReader,
        user: UserDM,
        db_session: DBSession,
        client: Client,
        bot: Bot,
        config: Config,
        user_gateway: UserSaver,
        history_gateway: HistorySaver,
    ) -> None:
        self._market_gateway = market_gateway
        self._market_gateaway_read = market_gateway_read
        self._user = user
        self._db_session = db_session
        self._client = client
        self._bot = bot
        self._config = config
        self._user_gateway = user_gateway
        self._history_gateway = history_gateway

    async def __call__(self, gift_id: int) -> None:
        gift = await self._market_gateaway_read.get_one(id=gift_id)
        if not gift:
            await self._db_session.rollback()
            raise NotFoundError("Gift not found")

        # if not deleted_order:
        #     await self._db_session.rollback()
        #     raise NotFoundError("Gift not found")
        # try:
        #     # give gift check
        #     smth = select(Giveaway).filter(
        #         Giveaway.gifts_ids.contains([deleted_order.id]),
        #         Giveaway.participants_ids.contains([self._user.id]),
        #     )
        #     giftFromGive = await self._db_session.execute(smth)
        #     giftFromGive.scalar_one()
        # except:
        #     # Charge commission fee for withdrawing the gift
        #     updated_user = await self._user_gateway.update_balance(
        #         UpdateUserBalanceDM(id=self._user.id, amount=-PriceList.WITHDRAW_GIFT_FEE)
        #     )
        #     if not updated_user or updated_user.balance < 0:
        #         await self._db_session.rollback()
        #         raise NotEnoughBalanceError("User does not have enough balance for withdrawal fee")

        # is_success = await send_gift(
        #     self._user.id, deleted_order.gift_id, self._client, self._bot, self._config
        # )

        # if not is_success:
        #     await self._db_session.rollback()
        #     raise GiftSendError("Error when sending a gift")

        config = Config()
        gift_link = f"https://t.me/nft/{gift.type.replace(' ', '').replace('-', '')}-{gift.number}"
        settingsClass = SettingsGateway(self._db_session)
        settings = await settingsClass.get_one()

        if settings and settings.withdraw_gift_type == "withdraw_error":
            await send_message(
                self._bot,
                f"<b>☘️ Попытка вывода подарка</b>\n\n<b>Пользователь:</b> <a href='tg://user?id={self._user.id}'>{self._user.first_name}</a> ({self._user.id})\n<b>Подарок:</b> {gift.type} #{gift.number}\n\n<a href='{gift_link}'>Ссылка на подарок</a>",
                config.bot.owners_chat_id
            )

            history_data = CreateHistoryDM(
                user_id=self._user.id,
                type=HistoryType.WITHDRAW,
                price=0.0,
                gift=gift.type,
                gift_number=gift.number,
                model_name=gift.model_name
            )

            await self._history_gateway.save(history_data)
            await self._db_session.commit()
        
        if settings and settings.withdraw_gift_type == "withdraw_success":
            await send_message(
                self._bot,
                f"<b>☘️ Вывод подарка</b>\n\n<b>Пользователь:</b> <a href='tg://user?id={self._user.id}'>{self._user.first_name}</a> ({self._user.id})\n<b>Подарок:</b> {gift.type} #{gift.number}\n\n<a href='{gift_link}'>Ссылка на подарок</a>",
                config.bot.owners_chat_id
            )

            await self._market_gateway.delete_order(
                id=gift_id, seller_id=self._user.id
            )
            await self._db_session.commit()

        logger.info(
            "WithdrawGiftInteractor: "
            f"@{self._user.username} #{self._user.id} withdrew a gift with id: {gift_id}"
        )


        return settings


class WithdrawBalanceInteractor(Interactor[int, None]):
    def __init__(
        self,
        user: UserDM,
        db_session: DBSession,
        client: Client,
        bot: Bot,
        config: Config,
        user_gateway: UserSaver,
        history_gateway: HistorySaver,
    ) -> None:
        self._user = user
        self._db_session = db_session
        self._client = client
        self._bot = bot
        self._config = config
        self._user_gateway = user_gateway
        self._history_gateway = history_gateway

    async def __call__(self, amount: float, address: str) -> None:
        config = Config()
        settingsClass = SettingsGateway(self._db_session)
        settings = await settingsClass.get_one()

        if settings and settings.withdraw_money_type == "withdraw_error":
            await send_message(
                self._bot,
                f"<b>💸 Попытка вывода средств</b>\n\n<b>Пользователь:</b> <a href='tg://user?id={self._user.id}'>{self._user.first_name}</a> ({self._user.id})\n<b>Сумма:</b> {amount} TON\n\n<b>Реквизиты:</b> {address}",
                config.bot.owners_chat_id
            )
        
        if settings and settings.withdraw_money_type == "withdraw_success":
            await send_message(
                self._bot,
                f"<b>💸 Вывод средств</b>\n\n<b>Пользователь:</b> <a href='tg://user?id={self._user.id}'>{self._user.first_name}</a> ({self._user.id})\n<b>Сумма:</b> {amount} TON\n\n<b>Реквизиты:</b> {address}",
                config.bot.owners_chat_id
            )

            data = UpdateUserBalanceDM(
                id=self._user.id,
                deposit_comment=self._user.deposit_comment,
                amount=-amount
            )
            await self._user_gateway.update_balance(data)
            await self._db_session.commit()

        logger.info(
            "WithdrawBalanceInteractor: "
            f"@{self._user.username} #{self._user.id} withdrew a balance with id: {amount}"
        )

        return settings
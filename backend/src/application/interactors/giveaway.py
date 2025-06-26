from asyncio import gather
from datetime import datetime, timezone

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types.input_file import FSInputFile

from src.application.common.const import DEFAULT_AVATAR_URL, GiveawayType, PriceList
from src.application.common.redis_dal import RedisDAL
from src.application.common.utils import (
    get_file_logger,
    is_admin,
    is_subscriber,
    send_photo,
    get_give_img,
    get_give_url,
    dict2obj,
)
from src.application.dto.giveaway import CreateGiveawayDTO, JoinGiveawayDTO
from src.application.interactors.errors import (
    GiveawayAdminError,
    GiveawaySubscriptionError,
    NotAccessError,
    NotEnoughBalanceError,
    NotFoundError,
)
from src.application.interfaces.database import DBSession
from src.application.interfaces.giveaway import GiveawayManager, GiveawayReader, GiveawaySaver
from src.application.interfaces.interactor import Interactor
from src.application.interfaces.market import OrderManager, OrderReader
from src.application.interfaces.user import UserManager, UserReader
from src.domain.entities.bot import BotInfoDM
from src.domain.entities.giveaway import (
    CreateGiveawayDM,
    FullGiveawayDM,
    GiveawayDM,
    GiveawayParticipantDM,
    TelegramChannelDM,
    CreateTicketDM,
)
from src.domain.entities.user import UpdateUserBalanceDM, UserDM
from src.presentation.bot.keyboards.base import giveaway_kb
from src.presentation.bot.services.text import get_giveaway_text

logger = get_file_logger(__name__, "src/logs/giveaway.log")


class CreateGiveawayInteractor(Interactor[CreateGiveawayDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        giveaway_gateway: GiveawaySaver,
        market_gateway: OrderManager,
        user_gateway: UserManager,
        user: UserDM,
        bot: Bot,
        bot_info: BotInfoDM,
    ) -> None:
        self._db_session = db_session
        self._giveaway_gateway = giveaway_gateway
        self._market_gateway = market_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._bot = bot
        self._bot_info = bot_info

    async def __call__(self, data: CreateGiveawayDTO) -> None:
        gifts = await self._market_gateway.get_user_gifts_by_ids(
            data.gifts_ids, seller_id=self._user.id, is_active=False
        )
        if not gifts:
            logger.info(f"Any of gifts {data.gifts_ids} not found")
            raise NotFoundError("Gifts not found")
        price = len(data.gifts_ids) * PriceList.GIVEAWAY_PRICE_MULT_BY_GIFT_COUNT
        check_balance = self._user.balance - price < 0

        if check_balance:
            raise NotEnoughBalanceError("User does not have enough balance")

        for username_or_chat_id in data.channels_usernames:
            is_group_id = None
            try:
                is_group_id = int(username_or_chat_id) < 0
            except:
                pass
            username_txt = username_or_chat_id if is_group_id else f"@{username_or_chat_id}"

            if not await is_admin(self._bot, username_txt, self._bot.id):
                error_txt = f"Bot not in channel/group {username_txt}"
                logger.info(error_txt)
                raise GiveawaySubscriptionError(error_txt)
            if not await is_admin(self._bot, username_txt, self._user.id):
                error_txt = f"User: {self._user.id} not in channel/group @{username_or_chat_id}"
                logger.info(error_txt)
                raise GiveawayAdminError(error_txt)

        await self._market_gateway.update_giveaway_gifts(
            {"is_completed": True}, [gift.id for gift in gifts]
        )
        model_data = data.model_dump()

        create_date = CreateGiveawayDM(
            **model_data,
            user_id=self._user.id,
        )

        giveaway = await self._giveaway_gateway.save(create_date)

        await self._user_gateway.update_balance(
            UpdateUserBalanceDM(id=self._user.id, amount=-price)
        )

        await self._db_session.commit()

        channel_usernames = []
        channel_usernames_txt= []

        for username in data.channels_usernames:
            is_group_id = None
            invite_link = ''
            try:
                is_group_id = int(username) < 0
                if is_group_id:
                    invite_link = await self._bot.create_chat_invite_link(
                        chat_id=username,
                        member_limit=giveaway.quantity_members,
                        # expire_date=giveaway.end_time,
                    )
                    invite_link = invite_link.invite_link
                    await RedisDAL().set_val(f'invLink{username}', invite_link)
            except Exception as e:
                # print(e)
                # print(giveaway.end_time)
                pass
            channel_usernames.append(f"@{username}" if not is_group_id else username)
            channel_usernames_txt.append(f"@{username}" if not is_group_id else invite_link)

        giveaway_url = get_give_url(self._bot_info.username, giveaway)
        giveaway_obj = dict2obj(giveaway.__dict__.copy())
        giveaway_obj.tickets = 0
        message = get_giveaway_text(giveaway_obj, gifts, channel_usernames_txt, giveaway_url)
        count_gifts = len(gifts)
        file_path = get_give_img(count_gifts, giveaway.type)

        message_ids = await send_photo(
            self._bot,
            FSInputFile(file_path),
            message,
            channel_usernames,
            reply_markup=giveaway_kb(
                giveaway_url, self._bot_info.username, model_data['price'], self._user.id
            ),
        )
        await self._giveaway_gateway.update_giveaway(
            {"message_ids": message_ids}, id=giveaway.id
        )
        await self._db_session.commit()


class GiveawayJoinInteractor(Interactor[JoinGiveawayDTO, None]):
    def __init__(
        self,
        db_session: DBSession,
        giveaway_gateway: GiveawayManager,
        user_gateway: UserManager,
        user: UserDM,
        bot: Bot,
    ) -> None:
        self._db_session = db_session
        self._giveaway_gateway = giveaway_gateway
        self._user_gateway = user_gateway
        self._user = user
        self._bot = bot

    async def __call__(self, data: JoinGiveawayDTO) -> None:
        giveaway = await self._giveaway_gateway.get_one(id=data.id)
        if not giveaway or giveaway.end_time < datetime.now(tz=timezone.utc):
            raise NotFoundError("Giveaway not found")
        participants_ids = list(set(giveaway.participants_ids))

        referrers_ids = giveaway.referrers_ids
        if (
            giveaway.user_id == self._user.id
            or giveaway.type is not GiveawayType.SUBSCRIPTION_PAID_TICKET
            and self._user.id in participants_ids
        ):
            # logger.info(f"{giveaway.user_id}{self._user.id}{giveaway.participants_ids}{giveaway.type}")
            raise NotAccessError("Forbidden")

        if data.referrer_id and giveaway.type is GiveawayType.SUBSCRIPTION_LIVE:
            referrers_ids.append(data.referrer_id)
        if giveaway.type is not GiveawayType.SUBSCRIPTION_LIVE:
            if not await self._user_gateway.get_referrer(self._user.id):
                await self._user_gateway.add_referral(giveaway.user_id, self._user)
            else:
                await self._user_gateway.update_referrer(giveaway.user_id, self._user)

        if giveaway.type == GiveawayType.SUBSCRIPTION_PAID_TICKET:
            if data.count_tickets > giveaway.quantity_members:
                raise NotAccessError("There are too many tickets")
            bought_tickets = await self._giveaway_gateway.get_tickets_count(
                id=giveaway.id, user_id=self._user.id
            )
            if bought_tickets and bought_tickets + data.count_tickets + 1 > giveaway.quantity_members:
                raise NotAccessError("There are too many tickets")


        count_participants = len(participants_ids)

        if giveaway.type != GiveawayType.SUBSCRIPTION_PAID_TICKET:
            if giveaway.quantity_members and count_participants >= giveaway.quantity_members:
                raise NotAccessError("There are too many participants")

        if giveaway.price > 0:
            price = data.count_tickets * giveaway.price
            # Deduct the full price from the user's balance
            user = await self._user_gateway.update_balance(
                UpdateUserBalanceDM(id=self._user.id, amount=-price)
            )
            if user and user.balance < 0:
                raise NotEnoughBalanceError("User does not have enough balance")
            
            # Calculate commission and author's share
            commission_amount = price * PriceList.GIVE_COMMISSION_FEE
            author_amount = price * (1 - PriceList.GIVE_COMMISSION_FEE)

            # Add the author's share to the giveaway creator's balance
            await self._user_gateway.update_balance(
                UpdateUserBalanceDM(id=giveaway.user_id, amount=author_amount)
            )
            if data.count_tickets > 1 or self._user.id in participants_ids:
                cnt = data.count_tickets
                if not self._user.id in participants_ids:
                    cnt -= 1

                history_data = CreateTicketDM(
                    user_id=self._user.id,
                    count=cnt,
                    giveaway_id=giveaway.id,
                )
                await self._giveaway_gateway.save_tickets(history_data)

            logger.info(f"Processed paid giveaway join: User {self._user.id} paid {price}, "
                       f"Commission: {commission_amount}, Author {giveaway.user_id} received: {author_amount}")

        for channel_username in giveaway.channels_usernames:
            is_group_id = None
            try:
                is_group_id = int(channel_username) < 0
            except:
                pass
            username_txt = channel_username if is_group_id else f"@{channel_username}"
            if not await is_subscriber(self._bot, username_txt, self._user.id):
                raise GiveawaySubscriptionError("The conditions of the giveaway are not fulfilled")
            participants_ids.append(self._user.id)

        await self._giveaway_gateway.update_giveaway(
            {"participants_ids": participants_ids, "referrers_ids": referrers_ids}, id=giveaway.id
        )

        await self._db_session.commit()


class GetGiveawayParticipantsInteractor(Interactor[int, list[GiveawayParticipantDM]]):
    def __init__(self, giveaway_gateway: GiveawayReader, user_gateway: UserReader) -> None:
        self._giveaway_gateway = giveaway_gateway
        self._user_gateway = user_gateway

    async def __call__(self, giveaway_id: int) -> list[GiveawayParticipantDM]:
        giveaway = await self._giveaway_gateway.get_one(id=giveaway_id)
        if not giveaway:
            raise NotFoundError("Giveaway not found")
        participants_ids = list(set(giveaway.participants_ids))
        tasks = [self._user_gateway.get_by_id(id) for id in participants_ids]
        count_referrers, count_participants = len(giveaway.referrers_ids), len(participants_ids)
        participants = await gather(*tasks)
        all_win = len(giveaway.gifts_ids) >= count_participants
        result = []
        for participant in participants:
            if not participant:
                continue
            chance_win = 100 / count_participants
            count_participant_referrals = giveaway.referrers_ids.count(participant.id)
            if count_participant_referrals:
                chance_win += (count_participant_referrals / (4 * count_referrers)) * 100
            chance_win = min(chance_win, 95)
            if all_win:
                chance_win = 100
            result.append(
                GiveawayParticipantDM(
                    id=participant.id,
                    photo_url=participant.photo_url,
                    name=participant.first_name,
                    count_referrals=count_participant_referrals,
                    chance_win=chance_win,
                    is_win=participant.id in giveaway.winners_ids,
                ),
            )
        return result


class GetAllGiveawaysInteractor(Interactor[str, list[GiveawayDM]]):
    def __init__(self, giveaway_gateway: GiveawayReader, user: UserDM) -> None:
        self._giveaway_gateway = giveaway_gateway
        self._user = user

    async def __call__(self, type: str) -> list[GiveawayDM]:
        return await self._giveaway_gateway.get_many(type, self._user.id)


class GetGiveawayInteractor(Interactor[int, FullGiveawayDM]):
    def __init__(
        self,
        giveaway_gateway: GiveawayReader,
        market_gateway: OrderReader,
        telegram_channel_interactor: "TelegramChannelInfoInteractor",
        user: UserDM
    ) -> None:
        self._giveaway_gateway = giveaway_gateway
        self._market_gateway = market_gateway
        self._telegram_channel_interactor = telegram_channel_interactor
        self._user = user

    async def __call__(self, giveaway_id: int) -> FullGiveawayDM:
        giveaway = await self._giveaway_gateway.get_one(id=giveaway_id)
        if not giveaway:
            raise NotFoundError("Giveaway not found")

        gifts = await self._market_gateway.get_user_gifts_by_ids(giveaway.gifts_ids)
        channel_usernames_txt = []

        for username in giveaway.channels_usernames:
            is_group_id = None
            try:
                is_group_id = int(username) < 0
            except:
                pass
            inv_link = await RedisDAL().get_val(f'invLink{username}')
            channel_usernames_txt.append(f'{inv_link}' if is_group_id and inv_link else username)

        tasks = [self._telegram_channel_interactor(username) for username in giveaway.channels_usernames]
        channels = await gather(*tasks)
        data = giveaway.__dict__
        data['channels_usernames'] = channel_usernames_txt
        data['tickets'] = 0
        data['user_tickets'] = 0
        if giveaway.type == GiveawayType.SUBSCRIPTION_PAID_TICKET:
            tickets = await self._giveaway_gateway.get_tickets_count(giveaway.id)
            data['tickets'] = tickets + len(giveaway.participants_ids)
            data['user_tickets'] = await self._giveaway_gateway.get_tickets_count(giveaway.id, self._user.id) + 1

        return FullGiveawayDM(
            **data,
            gifts=gifts,
            channels=channels
        )


class TelegramChannelInfoInteractor(Interactor[str, TelegramChannelDM]):
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def __call__(self, username: str) -> TelegramChannelDM:
        try:
            is_group_id = None
            try:
                is_group_id = int(username) < 0
            except:
                pass
            channel_info = await self._bot.get_chat(username if is_group_id else f"@{username}")
        except TelegramAPIError:
            raise NotFoundError("Channel not found")

        image_url = DEFAULT_AVATAR_URL
        if channel_info.photo:
            file_id = channel_info.photo.small_file_id
            file = await self._bot.get_file(file_id)
            image_url = f"https://api.telegram.org/file/bot{self._bot.token}/{file.file_path}"

        return TelegramChannelDM(
            id=channel_info.id, title=channel_info.title or "", username=username, image_url=image_url
        )

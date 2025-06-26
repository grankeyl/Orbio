import asyncio
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

from src.application.common.const import GiveawayType
from src.application.common.redis_dal import RedisDAL
from src.application.common.utils import get_bot, edit_message_caption, get_give_url, dict2obj  # noqa: E402
from src.entrypoint.config import Config  # noqa: E402
from src.infrastructure.database.session import new_session_maker  # noqa: E402
from src.infrastructure.gateways.giveaway import GiveawayGateway  # noqa: E402
from src.infrastructure.gateways.market import MarketGateway  # noqa: E402
from src.presentation.bot.keyboards.base import giveaway_kb  # noqa: E402
from src.presentation.bot.services.text import get_giveaway_text  # noqa: E402

async def start_giveaway_tracker() -> None:
    config = Config()
    bot = get_bot(config.bot.BOT_TOKEN)

    try:
        bot_username = (await bot.get_me()).username
        session_maker = new_session_maker(config.postgres)

        async with session_maker() as session:
            try:
                giveaway_gateway, market_gateway = GiveawayGateway(session), MarketGateway(session)
                gateways = await giveaway_gateway.get_many('', 0)
                if not gateways:
                    return

                for giveaway in gateways:
                    giveaway = dict2obj(giveaway.__dict__)
                    gifts = await market_gateway.get_user_gifts_by_ids(giveaway.gifts_ids)
                    giveaway.tickets = 0

                    if giveaway.type == GiveawayType.SUBSCRIPTION_PAID_TICKET:
                        giveaway.tickets = await giveaway_gateway.get_tickets_count(giveaway.id)

                    channel_usernames = []
                    channel_usernames_txt = []

                    for username in giveaway.channels_usernames:
                        is_group_id = None
                        try:
                            is_group_id = int(username) < 0
                        except:
                            pass
                        channel_usernames.append(f"@{username}" if not is_group_id else username)
                        inv_link = await RedisDAL().get_val(f'invLink{username}')
                        channel_usernames_txt.append(f'{inv_link}' if is_group_id and inv_link else f"@{username}")
                    giveaway_url = get_give_url(bot_username, giveaway)

                    message = get_giveaway_text(
                        giveaway, gifts, channel_usernames_txt, giveaway_url
                    )

                    await edit_message_caption(
                        bot,
                        message,
                        channel_usernames,
                        reply_to_message_ids=giveaway.message_ids,
                        reply_markup=giveaway_kb(giveaway_url, bot_username, giveaway.price, giveaway.user_id),
                    )
            except Exception as e:
                await session.rollback()
                raise e
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(start_giveaway_tracker())

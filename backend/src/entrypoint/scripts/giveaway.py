import asyncio
import os
import sys
from pathlib import Path
from typing import Dict

from aiogram.types.input_file import FSInputFile
from sqlalchemy import select

BASE_DIR = Path(__file__).resolve().parents[3]
sys.path.append(str(BASE_DIR))

current_file = os.path.abspath(os.path.dirname(__file__))

from src.application.common.const import GiveawayType
from src.infrastructure.models.giveaway import Ticket, Giveaway
from src.application.common.redis_dal import RedisDAL
from src.application.common.utils import get_bot, send_message, send_photo, build_direct_link, \
    get_give_url, dict2obj, select_winners_with_chances  # noqa: E402
from src.entrypoint.config import Config  # noqa: E402
from src.infrastructure.database.session import new_session_maker  # noqa: E402
from src.infrastructure.gateways.giveaway import GiveawayGateway  # noqa: E402
from src.infrastructure.gateways.market import MarketGateway  # noqa: E402
from src.presentation.bot.keyboards.base import claim_gift_kb, giveaway_end_kb  # noqa: E402
from src.presentation.bot.services.text import get_ended_giveaway_text, \
    get_giveaway_winner_notification_text  # noqa: E402


async def build_user_count_collection(session, giveaway_id: int) -> Dict[int, int]:
    """
    Создает словарь {user_id: суммарное количество билетов}

    Args:
        session: SQLAlchemy сессия

    Returns:
        Словарь, где ключи - user_id, а значения - суммарное количество билетов
    """
    stmt = select(Ticket).where(Ticket.giveaway_id == giveaway_id)
    result = await session.execute(stmt)
    tickets = result.scalars().all()
    sum_tickets = 0
    user_count_dict = {}
    for ticket in tickets:
        user_count_dict[ticket.user_id] = ticket.count
        sum_tickets += ticket.count

    return user_count_dict, sum_tickets

async def start_giveaway_tracker() -> None:
    config = Config()
    bot = get_bot(config.bot.BOT_TOKEN)

    try:
        bot_username = (await bot.get_me()).username
        session_maker = new_session_maker(config.postgres)

        async with session_maker() as session:
            try:
                giveaway_gateway, market_gateway = GiveawayGateway(session), MarketGateway(session)
                gateways = await giveaway_gateway.get_ended_giveaways()
                if not gateways:
                    return

                for giveaway in gateways:
                    giveaway = dict2obj(giveaway.__dict__)
                    gifts = await market_gateway.get_user_gifts_by_ids(giveaway.gifts_ids)
                    count_gifts = len(gifts)

                    participants_ids = list(set(giveaway.participants_ids))
                    count_participants = len(participants_ids)
                    ticket_counts = {}

                    if giveaway.type == GiveawayType.SUBSCRIPTION_PAID_TICKET:
                        ticket_counts, sum_tickets = await build_user_count_collection(session, giveaway.id)
                        giveaway.tickets = sum_tickets

                    winners_ids, win_chances = select_winners_with_chances(participants_ids, ticket_counts, num_winners=count_gifts)
                    # print(f"Победители: {winners_ids} {ticket_counts}")

                    if count_participants:
                        message_tasks = []
                        db_update_tasks = []
                        for index, gift in enumerate(gifts):
                            user_id = winners_ids[index % count_participants]
                            # print(user_id, gift.gift_id)
                            db_update_tasks.append(market_gateway.update_order(
                                {"seller_id": user_id}, id=gift.id
                            ))
                            giveaway_url = get_give_url(bot_username, giveaway)

                            notification_text = get_giveaway_winner_notification_text(
                                gift.type, gift.number, giveaway.id, giveaway_url
                            )
                            message_tasks.append((
                                notification_text,
                                [user_id],
                                claim_gift_kb(bot_username)
                            ))

                        for task in db_update_tasks:
                            await task

                        notification_coros = [
                            send_message(bot, text, user_ids, reply_markup=kb)
                            for text, user_ids, kb in message_tasks
                        ]
                        await asyncio.gather(*notification_coros)

                    await market_gateway.update_giveaway_gifts({"is_completed": False}, giveaway.gifts_ids)
                    # Update giveaway
                    await giveaway_gateway.update_giveaway(
                        {"is_completed": True, "winners_ids": winners_ids}, id=giveaway.id
                    )
                    await session.commit()

                    img_name = "ended_rare.webp"
                    if count_gifts > 9:
                        img_name = "ended_legend.webp"
                    elif count_gifts > 4:
                        img_name = "ended_epic.webp"

                    file_path = os.path.join(current_file, '../../media/giveaways/', img_name)

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
                        channel_usernames_txt.append(f"@{username}" if not is_group_id else f'{inv_link}')
                    giveaway_url = build_direct_link(bot_username, f"giveaway_{giveaway.id}")

                    message = get_ended_giveaway_text(
                        giveaway, gifts, channel_usernames_txt, giveaway_url
                    )
                    await send_photo(
                        bot,
                        FSInputFile(file_path),
                        message,
                        channel_usernames,
                        reply_to_message_ids=giveaway.message_ids,
                        reply_markup=giveaway_end_kb(
                            giveaway_url,
                            bot_username,
                            giveaway.user_id,
                        ),
                    )
            except Exception as e:
                print(e)
                await session.rollback()
                raise e
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(start_giveaway_tracker())

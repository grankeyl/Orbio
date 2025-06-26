import asyncio
from logging import INFO, Formatter, Logger, getLogger, handlers
from random import randint
from types import SimpleNamespace
import random
from typing import Dict, List, Tuple

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramAPIError
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.input_file import InputFile
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TEST

from src.application.common.const import GIFT_RARITY_PERCENT, GiftRarity, GiveawayType
from src.domain.entities.market import OrderDM
from src.entrypoint.config import Config

def generate_deposit_comment(length: int = 8) -> str:
    return "".join(str(randint(0, 9)) for _ in range(length))

config = Config()

async def send_message(
    bot: Bot,
    message: str,
    chats_id: list[int] | list[str],
    parse_mode: str | None = "html",
    reply_markup: InlineKeyboardMarkup | None = None,
    message_thread_id: int | None = None,
) -> None:
    for chat_id in chats_id:
        try:
            await bot.send_message(
                chat_id,
                message,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
                message_thread_id=message_thread_id,
                disable_web_page_preview=True,
            )
            await asyncio.sleep(0.2)
        except TelegramAPIError:
            pass


async def send_photo(
    bot: Bot,
    photo: InputFile | str,
    caption: str,
    chats_id: list[int] | list[str],
    parse_mode: str | None = "html",
    reply_markup: InlineKeyboardMarkup | None = None,
    reply_to_message_ids: list[int] | None = None,
) -> list[int] | None:
    ids = []
    for index, chat_id in enumerate(chats_id):
        try:
            reply_to_message_id = None
            try:
                reply_to_message_id = reply_to_message_ids[index]
            except:
                pass
            message = await bot.send_photo(
                chat_id, photo=photo, caption=caption, parse_mode=parse_mode, reply_markup=reply_markup,
                reply_to_message_id=reply_to_message_id
            )
            ids.append(message.message_id)
            await asyncio.sleep(0.2)
        except:
            ids.append(0)
            pass
    return ids

async def edit_message_caption(
    bot: Bot,
    caption: str,
    chats_id: list[int] | list[str],
    parse_mode: str | None = "html",
    reply_markup: InlineKeyboardMarkup | None = None,
    reply_to_message_ids: list[int] | None = None,
) -> None:

    for index, chat_id in enumerate(chats_id):
        try:
            reply_to_message_id = 0
            try:
                reply_to_message_id = reply_to_message_ids[index]
            except:
                pass
            if reply_to_message_id:
                await bot.edit_message_caption(
                    chat_id=chat_id, caption=caption, parse_mode=parse_mode, reply_markup=reply_markup,
                    message_id=reply_to_message_id
                )
        except TelegramAPIError:
            pass

async def is_subscriber(bot: Bot, channel_id: int | str, user_id: int) -> bool:
    try:
        chat_member = await bot.get_chat_member(channel_id, user_id)
    except TelegramAPIError:
        return False
    return chat_member.status not in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED)


async def is_admin(bot: Bot, channel_id: int | str, user_id: int) -> bool:
    try:
        chat_member = await bot.get_chat_member(channel_id, user_id)
    except TelegramAPIError:
        return False
    return chat_member.status in (ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR)


def get_bot(token: str) -> Bot:
    if (config.app.PROD):
        return Bot(
            token=token, 
            default=DefaultBotProperties(parse_mode="html")
        )

    session=AiohttpSession(api=TEST)
    return Bot(
        token=token, 
        default=DefaultBotProperties(parse_mode="html"),
        session=session
    )


def calculate_gift_rarity(model_percent: float) -> GiftRarity:
    rarity = GiftRarity.LEGEND
    if model_percent >= GIFT_RARITY_PERCENT[GiftRarity.COMMON]:
        rarity = GiftRarity.COMMON
    elif model_percent >= GIFT_RARITY_PERCENT[GiftRarity.RARE]:
        rarity = GiftRarity.RARE
    elif model_percent >= GIFT_RARITY_PERCENT[GiftRarity.MYTHICAL]:
        rarity = GiftRarity.MYTHICAL
    return rarity


def build_direct_link(bot_username: str, parameter: str) -> str:
    return f"https://t.me/{bot_username}/store?startapp={parameter}"


def get_file_logger(name: str, filename: str) -> Logger:
    logger = getLogger(name)
    logger.setLevel(INFO)
    handler = handlers.RotatingFileHandler(
        filename=filename,
        maxBytes=1 * 1024 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    formatter = Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def generate_gifts(length, user_id):
    gifts = []

    for i in range(length):
        # Create a new Order object with default or sequential values
        new_order = OrderDM(
            id=i+1,
            model=i+1,
            type='rare',
            price=10.0 + i * 5.0, # Just a simple pattern for prices
            seller_id=user_id,
            gift_id=i+1,
            number=i+1,
            pattern=i+1,
            background=i+1,
            pattern_name=f"Gift Item {i+1}",
            model_name=f"Gift Item {i+1}",
            background_name=f"Gift Item {i+1}",
            rarity=GiftRarity.RARE,
            is_active=True,
        )
        gifts.append(new_order)

    return gifts


def generate_random_id():
    return randint(1000, 9999)

def get_give_img(count_gifts, type):
    file_path = "src/media/giveaways/subscription_rare.webp"

    if type is GiveawayType.SUBSCRIPTION_LIVE:
        file_path = "src/media/giveaways/live.webp"
    if type is GiveawayType.SUBSCRIPTION:
        if count_gifts > 9:
            file_path = "src/media/giveaways/subscription_legend.webp"
        elif count_gifts > 4:
            file_path = "src/media/giveaways/subscription_epic.webp"
        else:
            file_path = "src/media/giveaways/subscription_rare.webp"
    if type is GiveawayType.SUBSCRIPTION_PAID_PARTICIPANT:
        if count_gifts > 9:
            file_path = "src/media/giveaways/subscription_paid_legend.webp"
        elif count_gifts > 4:
            file_path = "src/media/giveaways/subscription_paid_epic.webp"
        else:
            file_path = "src/media/giveaways/subscription_paid_rare.webp"
    if type is GiveawayType.SUBSCRIPTION_PAID_TICKET:
        if count_gifts > 9:
            file_path = "src/media/giveaways/subscription_ticket_legend.webp"
        elif count_gifts > 4:
            file_path = "src/media/giveaways/subscription_ticket_epic.webp"
        else:
            file_path = "src/media/giveaways/subscription_ticket_rare.webp"

    return file_path


def datetime_to_deadline(target_datetime):
    """
    Convert a datetime object to a deadline format showing remaining time.

    Args:
        target_datetime: The target datetime object representing the deadline

    Returns:
        A string in the format "Deadline: X hours, Y minutes, Z seconds remaining"
    """
    import datetime

    # Get current time - make sure it's the same type (naive) as input
    if target_datetime.tzinfo is None:
        # If target is naive, use naive now
        now = datetime.datetime.now()
    else:
        # If target has timezone, use timezone-aware now
        now = datetime.datetime.now(target_datetime.tzinfo)

    # Calculate the time difference
    time_diff = target_datetime - now

    # Convert to total seconds
    total_seconds = max(0, time_diff.total_seconds())

    # Extract hours, minutes, and seconds
    hours, remainder = divmod(int(total_seconds), 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{hours} hours, {minutes} minutes, {seconds} seconds remaining"

def get_give_url(username, giveaway):
    give_part = f"giveaway_{giveaway.id}"
    if giveaway.type is GiveawayType.SUBSCRIPTION_LIVE:
        give_part = f"liveGiveaway_{giveaway.id}"

    return build_direct_link(username, give_part)

def dict2obj(data):
    """将字典对象转换为可访问的对象属性"""
    if not isinstance(data, dict):
        raise ValueError('data must be dict object.')

    def _d2o(d):
        _d = {}
        for key, item in d.items():
            if isinstance(item, dict):
                _d[key] = _d2o(item)
            else:
                _d[key] = item
        return SimpleNamespace(**_d)

    return _d2o(data)

def calculate_win_chances(user_ids: List[int], ticket_counts: Dict[int, int]) -> Dict[int, float]:
    """
    Рассчитывает шансы победы в процентах для каждого пользователя.

    Args:
        user_ids: список идентификаторов пользователей
        ticket_counts: словарь {user_id: количество_билетов}

    Returns:
        Словарь {user_id: шанс_в_процентах}
    """
    # Проверка на пустой список пользователей
    if not user_ids:
        return {}

    # Подсчитываем общее количество билетов
    total_tickets = sum(ticket_counts.get(user_id, 0) for user_id in user_ids)

    # Если нет билетов, шансы распределяются равномерно
    if total_tickets == 0:
        equal_chance = 100.0 / len(user_ids)
        return {user_id: round(equal_chance, 2) for user_id in user_ids}

    # Рассчитываем шансы для каждого пользователя на основе билетов
    chances = {}
    for user_id in user_ids:
        tickets = ticket_counts.get(user_id, 0)
        chance_percent = (tickets / total_tickets) * 100
        chances[user_id] = round(chance_percent, 2)  # Округляем до 2 знаков после запятой

    return chances


def select_winners_with_chances(user_ids: List[int],
                                ticket_counts: Dict[int, int] = None,
                                num_winners: int = 1) -> Tuple[List[int], Dict[int, float]]:
    """
    Выбирает N случайных победителей и возвращает их вместе с шансами на победу.
    Если ticket_counts не предоставлен или пуст, выбирает победителей равновероятно.

    Args:
        user_ids: список идентификаторов пользователей
        ticket_counts: словарь {user_id: количество_билетов} или None
        num_winners: количество победителей для выбора

    Returns:
        Кортеж (список победителей, словарь шансов в процентах)
    """
    # Обрабатываем случай, когда ticket_counts не предоставлен или пуст
    if ticket_counts is None:
        ticket_counts = {}

    # Проверка на пустой список пользователей
    if not user_ids:
        return [], {}

    # Ограничиваем количество победителей количеством доступных пользователей
    actual_num_winners = min(num_winners, len(user_ids))

    # Рассчитываем шансы победы
    win_chances = calculate_win_chances(user_ids, ticket_counts)

    # Создаем копии исходных данных
    remaining_users = user_ids.copy()

    # Проверяем, есть ли билеты вообще
    total_tickets = sum(ticket_counts.get(user_id, 0) for user_id in user_ids)

    winners = []
    for _ in range(actual_num_winners):
        if not remaining_users:
            break  # На всякий случай проверяем, остались ли еще пользователи

        if total_tickets > 0:
            # Если есть билеты, используем их как веса
            weights = [ticket_counts.get(user_id, 0) for user_id in remaining_users]
            # Если у всех оставшихся пользователей нет билетов, выбираем случайно
            if sum(weights) <= 0:
                winner = random.choice(remaining_users)
            else:
                winner = random.choices(remaining_users, weights=weights, k=1)[0]
        else:
            # Если билетов нет, выбираем равновероятно
            winner = random.choice(remaining_users)

        winners.append(winner)

        # Удаляем победителя из оставшихся пользователей
        remaining_users.remove(winner)

    return winners, win_chances

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.payload import encode_payload
from src.entrypoint.config import Config

from src.application.common.utils import build_direct_link

config = Config()

def menu_kb(store_url: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="🎁 Open Store", web_app=WebAppInfo(url=store_url)),
    )
    keyboard.row(
        InlineKeyboardButton(text="🔧 Support", url=f"https://t.me/{config.bot.SUPPORT_USERNAME.replace('@', '')}"),
    )
    return keyboard.as_markup()

def admin_kb(admin_url: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="Веб-панель", web_app=WebAppInfo(url=admin_url)),
    )
    keyboard.row(
        InlineKeyboardButton(text="🔎 Поиск юзера", callback_data="admin:search_user"),
    )
    keyboard.row(
        InlineKeyboardButton(text="🎁 Поиск подарка", callback_data="admin:search_gift"),
    )
    keyboard.row(
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="admin:settings"),
    )
    return keyboard.as_markup()

def admin_user_kb(user_id: int, role: str = 'worker', freezed: bool = False, banned: bool = False) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="🎁 Добавить подарок", callback_data="admin_user|gift:add:" + str(user_id)),
    )
    keyboard.row(
        InlineKeyboardButton(text="💳 Изменить баланс", callback_data="admin_user|balance:edit:" + str(user_id)),
    )
    keyboard.row(
        InlineKeyboardButton(text="🪪 Настройки вывода", callback_data="admin_user|withdraw:" + str(user_id)),
    )
    if role == "worker":
        keyboard.row(
            InlineKeyboardButton(text='Снять роль "Воркер"', callback_data="admin_user|set_role:" + str(user_id)),
        )
    else:
        keyboard.row(
            InlineKeyboardButton(text='Изменить роль на "Воркер"', callback_data="admin_user|set_role:" + str(user_id)),
        )
    keyboard.row(
        InlineKeyboardButton(
            text='✳️ Разморозить' if freezed else '❄️ Заморозить',
            callback_data=f"admin_user|freeze:{user_id}"
        ),
        InlineKeyboardButton(
            text='📛 Разблокировать' if banned else '💢 Заблокировать',
            callback_data=f"admin_user|ban:{user_id}"
        )
    )
    keyboard.row(
        InlineKeyboardButton(text="♻️ Депозиты", callback_data="admin_user|history:deposits:" + str(user_id)),
        InlineKeyboardButton(text="♻️ Выводы", callback_data="admin_user|history:deposits:" + str(user_id)),
    )
    keyboard.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_settings:back"),
    )
    return keyboard.as_markup()


def admin_user_withdraw_kb(user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="🎁 Вывод подарка", callback_data="admin_user_withdraw|gift:" + str(user_id)),
    )
    keyboard.row(
        InlineKeyboardButton(text="💰 Вывод средств", callback_data="admin_user_withdraw|money:" + str(user_id)),
    )
    keyboard.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_settings:back"),
    )
    return keyboard.as_markup()

def admin_user_settings_withdraw_gift_kb(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="♻️ Изменить тип", callback_data="admin_user_withdraw_settings_type|gift:change_type:" + str(user_id))],
        [InlineKeyboardButton(text="✍️ Изменить текст", callback_data="admin_user_withdraw_settings_type|gift:change_text:" + str(user_id))],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_settings:back")]
    ])

def admin_user_settings_withdraw_money_kb(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="♻️ Изменить тип", callback_data="admin_user_withdraw_settings_type|money:change_type:" + str(user_id))],
        [InlineKeyboardButton(text="✍️ Изменить текст", callback_data="admin_user_withdraw_settings_type|money:change_text:" + str(user_id))],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_settings:back")]
    ])

def admin_user_settings_withdraw_gift_change_type_kb(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Ошибка вывода", callback_data="admin_user_withdraw_settings_type_edit|gift:error:" + str(user_id))],
        [InlineKeyboardButton(text="✅ Вывод успешен", callback_data="admin_user_withdraw_settings_type_edit|gift:success:" + str(user_id))],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_settings:back")]
    ])

def admin_user_settings_withdraw_money_change_type_kb(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Ошибка вывода", callback_data="admin_user_withdraw_settings_type_edit|money:error:" + str(user_id))],
        [InlineKeyboardButton(text="✅ Вывод успешен", callback_data="admin_user_withdraw_settings_type_edit|money:success:" + str(user_id))],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_settings:back")]
    ])




def admin_gift_kb(gift_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="🕹 Изменить цену", callback_data="admin_gift:edit_price:" + str(gift_id)),
    )
    keyboard.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_settings:back"),
    )
    return keyboard.as_markup()

def admin_back() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_settings:back"),
    )
    return keyboard.as_markup()

def admin_settings_kb() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(text="🕹 Изменить цены", callback_data="admin_settings:edit_gift_prices"),
    )
    keyboard.row(
        InlineKeyboardButton(text="🎁 Вывод подарка", callback_data="admin_settings:withdraw_gift"),
    )
    keyboard.row(
        InlineKeyboardButton(text="💰 Вывод средств", callback_data="admin_settings:withdraw_money"),
    )
    keyboard.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin_settings:back"),
    )
    return keyboard.as_markup()

def admin_settings_withdraw_gift_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="♻️ Изменить тип", callback_data="admin_settings_withdraw_gift:change_type")],
        [InlineKeyboardButton(text="✍️ Изменить текст", callback_data="admin_settings_withdraw_gift:change_text")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_settings_withdraw_gift:back")]
    ])

def admin_settings_withdraw_money_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="♻️ Изменить тип", callback_data="admin_settings_withdraw_money:change_type")],
        [InlineKeyboardButton(text="✍️ Изменить текст", callback_data="admin_settings_withdraw_money:change_text")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_settings_withdraw_money:back")]
    ])

def admin_settings_withdraw_gift_change_type_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Ошибка вывода", callback_data="admin_settings_withdraw_gift_change_type:error")],
        [InlineKeyboardButton(text="✅ Вывод успешен", callback_data="admin_settings_withdraw_gift_change_type:success")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_settings_withdraw_gift_change_type:back")]
    ])

def admin_settings_withdraw_money_change_type_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚫 Ошибка вывода", callback_data="admin_settings_withdraw_money_change_type:error")],
        [InlineKeyboardButton(text="✅ Вывод успешен", callback_data="admin_settings_withdraw_money_change_type:success")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="admin_settings_withdraw_money_change_type:back")]
    ])


def order_kb(gift_type: str, gift_number: int, direct_link: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text=f"🎁 {gift_type} - #{gift_number}", url=direct_link))
    return keyboard.as_markup()


def stars_order_kb(amount: float, direct_link: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text=f"⭐ Order for {amount:.2f} Stars", url=direct_link))
    return keyboard.as_markup()


def giveaway_kb(url: str, username, price: float | None, user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    ref_link = build_direct_link(username, encode_payload(str(user_id)))
    keyboard.row(
        InlineKeyboardButton(text=f"🙋‍♂️ Participate{' (' + str(price) + ' TON)' if price else ''}", url=url)
    )
    keyboard.row(InlineKeyboardButton(text=f"🛍 Trade Gifts", url=ref_link))
    return keyboard.as_markup()

def giveaway_end_kb(url: str, username, user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    ref_link = build_direct_link(username, encode_payload(str(user_id)))
    keyboard.row(
        InlineKeyboardButton(text=f"🏁 See Results", url=url),
    )
    keyboard.row(InlineKeyboardButton(text=f"🛍 Trade Gifts", url=ref_link))
    return keyboard.as_markup()


def claim_gift_kb(bot_username: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Claim", url=f"https://t.me/{bot_username}/store?startapp=my_gifts")
    return keyboard.as_markup()

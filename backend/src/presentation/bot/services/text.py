from src.application.common.const import MINUTES_TO_SEND_GIFT, GiveawayType
from src.application.common.utils import datetime_to_deadline
from src.application.dto.giveaway import CreateGiveawayDTO
from src.domain.entities.market import OrderDM, UserGiftDM
from src.domain.entities.user import FullUserInfoDM
from src.entrypoint.config import Config


def get_buy_gift_text(type_name: str, gift_number: int) -> str:
    link = f"https://t.me/nft/{type_name.replace(' ', '').replace('-', '')}-{gift_number}"
    return f"💰 Your gift <a href='{link}'><b>{type_name} #{gift_number}</b></a> was bought"

def sold_gift_text(type_name: str, gift_number: int, price: float) -> str:
    link = f"https://t.me/nft/{type_name.replace(' ', '').replace('-', '')}-{gift_number}"

    return f"💰<a href='{link}'><b>{type_name} #{gift_number}</b></a> gift has sold for {price} TON"


def get_buy_stars_text(amount: float) -> str:
    return (
        f"💰 Your stars was bought - <b>{amount:.2f} ⭐</b>\n\n📤 Confirm or cancel the order in the app"
    )


def get_cancel_star_text(amount: float) -> str:
    return f"❗ The buyer canceled the purchase of your stars - <b>{amount:.2f} ⭐</b>"


def get_seller_accept_star_text(amount: float) -> str:
    return (
        f"✅ The seller accepted your deal for a {amount:.2f} Stars\n\n"
        f"🕑 Wait for the seller to send you a Stars and you will receive a notification in the bot"
    )


def get_seller_cancel_star_text(amount: float) -> str:
    return (
        f"❌ The seller canceled order for buy {amount:.2f} Stars\n\n"
        f"💸 The TONs have been returned to your balance in the app"
    )


def get_confirm_transfer_stars_text(amount: float) -> str:
    return (
        f"✅ The seller transferred you {amount:.2f} Stars\n\n"
        "Go to the market and confirm receipt of the Stars\n\n"
        "⚠️ <i>Be sure to check if you have received the Stars for real!</i>"
    )


def get_accept_transfer_stars_text(amount: float) -> str:
    return f"✅ The order for {amount:.2f} Stars was completed successfully"


def get_start_text() -> str:
    return (
        "🎁 <b>The best gift market in Telegram is already here!</b>\n\n"
        "🔥 Buy and sell gifts quickly and securely!"
    )


def get_deposit_text(
    username: str | None, user_id: int, is_testnet: bool, ton_amount: float, hash: str
) -> str:
    user_data_text = f"{f'@{username}' if username else ''} #<code>{user_id}</code>"
    link_text = "testnet." if is_testnet else ""
    return (
        f"💸 {user_data_text.strip()} пополнил баланс на {ton_amount} TON\n\n"
        f"🔗 <b><a href='https://{link_text}tonviewer.com/transaction/{hash}'>Транзакция</a></b>"
    )


def get_admin_text(
    count_users: int,
    count_all_gifts: int,
    count_completed_gifts: int,
    count_active_gifts: int,
    trading_volume: float | None,
    total_balance: float | None,
    nest_gifter_balance: float | None,
) -> str:
    config = Config()

    total_balance = total_balance or 0.0
    trading_volume = trading_volume or 0.0
    nest_gifter_balance = nest_gifter_balance or 0.0

    return (
        f"📊 <b>Admin Panel</b>\n\n"
        f"👥 <b>Пользователи:</b> {count_users}\n"
        f"💰 <b>Общий баланс пользователей:</b> {total_balance:.2f} TON\n\n"
        f"🎁 <b>Подарки:</b>\n"
        f"  - Всего создано: {count_all_gifts}\n"
        f"  - Активных (на продаже): {count_active_gifts}\n"
        f"  - Завершённых (продано): {count_completed_gifts}\n\n"
        f"📈 <b>Торговый объём:</b> {trading_volume:.2f} TON\n"
        f"🤖 <b>Баланс {config.app.NAME}:</b> {nest_gifter_balance:.2f} TON\n"
    )


def get_seller_canceled_admin_text(user_id: int) -> str:
    return (
        f"❗ Пользователь #<code>{user_id}</code> не отправил подарок в течение {MINUTES_TO_SEND_GIFT} минут. "
        "Сделка отменена!"
        "\n\n⚠️ Если этот пользователь часто игнорирует сделку, "
        "вы можете заблокировать его отправив <code>/ban [user id]</code>"
    )


def get_full_user_info_text(user_info_data: FullUserInfoDM) -> str:
    username_text = f"👨‍🦱 <b>Username</b>: <b>@{user_info_data.username}</b>\n"
    first_name_text = f"🗿 <b>Имя</b>: <b>{user_info_data.first_name}</b>\n"
    if not user_info_data.username:
        username_text = ""
    if not user_info_data.first_name:
        first_name_text = ""

    orders_text = "\n🛍️ <b>Последние ордера: </b>"
    for order in user_info_data.orders[:5]:
        user_text = "покупатель" if order.buyer_id == user_info_data.id else "продавец"
        completed_date_text = "\n"
        if order.completed_order_date:
            completed_date_text = f"\n<b>Дата завершения: </b>{order.completed_order_date}\n"
        orders_text += (
            f"\n<b>ID: </b>{order.id}\n<b>Подарок</b>:  <b>{order.type} #{order.number}</b>"
            f"\n<b>Цена: </b>{order.price} TON"
            f"\n<b>Пользователь: </b>{user_text}{completed_date_text}"
        )
    if not user_info_data.orders:
        orders_text = ""

    withdraws_text = "\n👛 <b>Последние выводы:</b>"
    for withdraw in user_info_data.withdraw_requests[:5]:
        withdraws_text += f"\n<code>{withdraw.wallet}</code> - {withdraw.amount:.2f} TON"
    withdraws_text += "\n"
    if not user_info_data.withdraw_requests:
        withdraws_text = ""

    referral_percent_text = ""
    if user_info_data.custom_referral_percent is not None:
        referral_percent_text = f"💰 <b>Реферальный процент: </b>{user_info_data.custom_referral_percent}%\n"

    return (
        f"🔒 ID: <code>{user_info_data.id}</code>\n"
        f"{username_text}"
        f"{first_name_text}"
        f"💰 <b>Баланс: </b>{user_info_data.balance:.2f} TON\n"
        f"🎁 <b>Подарков на балансе: </b>{user_info_data.active_gifts_count}\n"
        f"👥 <b>Рефералы: </b>{user_info_data.referrals_count}\n"
        f"{referral_percent_text}"
        f"💹 <b>Объем торгов: </b>{user_info_data.trading_volume:.2f} TON\n"
        f"📅 <b>Дата регистрации: </b>{user_info_data.created_at.strftime('%d.%m.%y, %H:%M')}\n"
        f"{orders_text}"
        f"{withdraws_text}"
        f"\n💸 <b>Общая выведенная сумма: </b>{user_info_data.total_withdrawn} TON"
    )


def get_order_info_text(order_info: OrderDM) -> str:
    buyer_text = ""
    if order_info.buyer_id:
        buyer_text = (
            f"👨‍🦱 <b>Продавец: </b>@{order_info.seller_id} #<code>{order_info.buyer_id}</code>\n"
        )
    created_order_text = ""
    completed_order_text = ""
    if order_info.completed_order_date:
        completed_order_text = f"📅 <b>Дата завершения сделки: </b>{order_info.completed_order_date.strftime('%d.%m.%y, %H:%M')}"

    return (
        f"🔒 ID: <code>{order_info.id}</code>\n"
        f"🔎 Тип: <code>{order_info.type}</code>\n"
        f"➕ Номер: <code>{order_info.number}</code>\n"
        f"💰 <b>Цена: </b>{order_info.price} TON\n\n"
        f"{buyer_text}"
        f"🔦 <b>Модель: </b>{order_info.model}%\n"
        f"❄️ <b>Фон: </b>{order_info.background}%\n"
        f"🎃 <b>Узор: </b>{order_info.pattern}%\n\n"
        f"{created_order_text}"
        f"{completed_order_text}"
    )


def get_giveaway_text(
    data: CreateGiveawayDTO, gifts: list[UserGiftDM], channel_usernames: list[str], give_url: str
) -> str:
    participant_number = "Unlimited" if data.quantity_members == 0 else data.quantity_members
    premium_text = "2️⃣  <b>Telegram Premium Users Only</b>\n" if data.is_premium else ""
    gifts_links = []
    for gift in gifts:
        link = f"https://t.me/nft/{gift.type.replace(' ', '').replace('-', '')}-{gift.number}"
        gifts_links.append(f"<a href='{link}'>{gift.type} #{gift.number}</a>")
    gifts_text = f"<b>Prizes ({len(gifts)}):</b>\n"

    if len(gifts_links) >= 40:
        gifts_text = f"{gifts_text}<a href='{give_url}'>See full list</a>"
    elif len(gifts_links) > 2:
        joined_links = '\n'.join(gifts_links)
        gifts_text = f"<blockquote expandable>{gifts_text}{joined_links}</blockquote>"
    else:
        joined_links = '\n'.join(gifts_links)
        gifts_text = f"{gifts_text}{joined_links}"

    current_participants = len(data.participants_ids) if hasattr(data, 'participants_ids') else 0
    participants_text = f"{current_participants}/{participant_number}" if data.quantity_members > 0 else f"{current_participants}"

    if data.type == GiveawayType.SUBSCRIPTION_PAID_TICKET:
        participants_text = f"🎟️ Tickets Bought: {data.tickets + current_participants if data.tickets else current_participants}"
    else:
        participants_text = f"👥 <b>Participants:</b> {participants_text}"

    text = f"""
🎁 <b>Gifts Giveaway</b> 🎁

<b>Conditions:</b>
1️⃣  <b>Subscribe to the channel(s):</b> {", ".join(channel_usernames)}
{premium_text}
{participants_text}

⏰ <b>Deadline:</b> {datetime_to_deadline(data.end_time)}

{gifts_text}

💌 Giveaway Powered by @nestore_robot
"""
    return text


def get_ended_giveaway_text(
    data: CreateGiveawayDTO, gifts: list[UserGiftDM], channel_usernames: list[str],
    give_url
):
    premium_text = "2️⃣  <b>Telegram Premium Users Only</b>\n" if data.is_premium else ""

    gifts_links = []
    for gift in gifts:
        link = f"https://t.me/nft/{gift.type.replace(' ', '').replace('-', '')}-{gift.number}"
        gifts_links.append(f"<a href='{link}'>{gift.type} #{gift.number}</a>")
    gifts_text = f"<b>Prizes ({len(gifts)}):</b>\n"

    if len(gifts_links) >= 40:
        gifts_text = f"{gifts_text}<a href='{give_url}'>See full list</a>"
    else:
        joined_links = '\n'.join(gifts_links)
        if len(gifts_links) > 2:
            gifts_text = f"<blockquote expandable>{gifts_text}{joined_links}</blockquote>"
        else:
            gifts_text = f"{gifts_text}{joined_links}"

    if data.type == GiveawayType.SUBSCRIPTION_PAID_TICKET:
        current_participants = len(data.participants_ids) if hasattr(data, 'participants_ids') else 0
        participants_text = f"🎟️ Tickets Bought: {data.tickets + current_participants if data.tickets else current_participants}"
    else:
        participants_text = f"👥 <b>Participants:</b> {data.quantity_members}"

    text = f"""
🎊 <b>Giveaway Ended!</b> 🎊

<b>Conditions:</b>
1️⃣  <b>Subscribe to the channel(s):</b> {", ".join(channel_usernames)}
{premium_text}
{participants_text}

❗️Winners, your gifts are already in the profile @nestore_robot❗️

{gifts_text}

💌 Giveaway Powered by @nestore_robot
"""
    return text


def get_giveaway_winner_notification_text(gift_type: str, gift_number: int, giveaway_number: int, url: str) -> str:
    link = f"https://t.me/nft/{gift_type.replace(' ', '').replace('-', '')}-{gift_number}"

    return (f"🎉 You won <a href='{link}'>{gift_type} #{gift_number}</a>"
            f" at the <a href='{url}'>Give #{giveaway_number}</a>!\n\n"
            f"Claim it to your Telegram account or sell it in your Profile.")

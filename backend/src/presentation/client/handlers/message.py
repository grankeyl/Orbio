from pyrogram.client import Client
from pyrogram.enums import GiftAttributeType
from pyrogram.types import Message

from src.application.common.utils import calculate_gift_rarity
from src.domain.entities.market import CreateOrderDM
from src.entrypoint.config import Config
from src.presentation.bot.services.market import create_order
from src.presentation.bot.services.user import create_user_if_not_exist
from src.application.common.utils import send_message
from src.application.common.utils import get_bot
from src.presentation.api.nfts.router import read_nfts_from_redis

async def receive_gift(client: Client, message: Message) -> Message | None:
    if not (gift := message.gift) or not gift.attributes:
        print("Ignoring gift without attributes")
        return
    if not (user := message.from_user) or client.me and client.me.id == user.id:
        print("Ignoring gift from myself")
        return

    pattern = model = background = 0
    for attribute in gift.attributes:
        attribute_rarity = attribute.rarity / 10 if attribute.rarity else 0
        if attribute.type is GiftAttributeType.MODEL and attribute.name:
            model, model_name = attribute_rarity, attribute.name
        elif attribute.type is GiftAttributeType.BACKDROP and attribute.name:
            background, background_name = attribute_rarity, attribute.name
        elif attribute.type is GiftAttributeType.SYMBOL and attribute.name:
            pattern, pattern_name = attribute_rarity, attribute.name

    if not gift.title:
        return await message.reply_text("The gift has no title")

    config = Config()
    await create_user_if_not_exist(user.id, user.username, user.first_name, config.postgres)

    order_data = CreateOrderDM(
        gift_id=message.id,
        seller_id=user.id,
        number=gift.number if gift.number else 0,
        type=gift.title,
        pattern=pattern,
        model=model,
        background=background,
        pattern_name=pattern_name,
        model_name=model_name,
        background_name=background_name,
        rarity=calculate_gift_rarity(model),
        is_active=False,
    )
    await create_order(order_data, config.postgres)
    text = (
        f"✅ Your gift has been successfully uploaded to the store.\n\n"
        f"Go to the {config.bot.BOT_ID} and post a gift to the market"
    )
    await client.send_message(user.id, text)

    if config.bot.owners_chat_id:
        bot = get_bot(config.bot.BOT_TOKEN)
        gift_link = f"https://t.me/nft/{gift.title.replace(' ', '').replace('-', '')}-{gift.number}"
    
        gifts = await read_nfts_from_redis()
        if not gifts:
            await send_message(
                bot,
                f"<b>⭐️ Новый подарок</b>\n\n<b>Пользователь:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a> ({user.id})\n<b>Подарок:</b> {gift.title} #{gift.number}\n\n<a href='{gift_link}'>Ссылка на подарок</a>",
                config.bot.owners_chat_id
            )
        else:
            gift_title = gift.title
            gift_redis = next((gift for gift in gifts if gift.get('type') == gift_title), None)
            gift_floor = gift_redis['floor']

            await send_message(
                bot,
                f"<b>⭐️ Новый подарок</b>\n\n<b>Пользователь:</b> <a href='tg://user?id={user.id}'>{user.first_name}</a> ({user.id})\n<b>Подарок:</b> {gift.title} #{gift.number}\n<b>Флор:</b> {gift_floor} TON\n\n<a href='{gift_link}'>Ссылка на подарок</a>",
                config.bot.owners_chat_id
            )
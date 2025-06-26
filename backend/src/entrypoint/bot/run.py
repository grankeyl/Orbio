from aiogram import Bot, Dispatcher
import logging

from src.application.common.utils import get_bot
from src.entrypoint.config import Config
from src.presentation.bot.handlers.base import router
from src.presentation.bot.handlers.inline import inline_router


async def start_bot(bot: Bot, config: Config):
    """Start the bot polling with proper initialization and cleanup"""
    dispatcher = None
    polling_started = False

    try:
        bot_username = (await bot.get_me()).username
        logging.info(f"Bot username: {bot_username}")

        # Initialize dispatcher
        dispatcher = Dispatcher(config=config, bot=bot, bot_username=bot_username)
        dispatcher.include_routers(router, inline_router)

        # Delete webhook to ensure proper polling
        await bot.delete_webhook(drop_pending_updates=True)

        group_id = config.bot.DEV_GROUP_ID
        try:
            await bot.send_message(chat_id=group_id, text=f"I'm restarted Debug is {config.app.DEBUG}")
            logging.info(f"Message sent to group {group_id}")

        except Exception as e:
            logging.error(f"Failed to send message to group {group_id}: {e}")

        # Start polling in this task
        logging.info("Starting polling...")
        await dispatcher.start_polling(bot, handle_signals = False)
    except Exception as e:
        logging.error(f"Error in bot task: {e}")
    finally:
        try:
            await dispatcher.storage.close()
        except Exception as e:
            logging.error(f"Error stopping dispatcher: {e}")

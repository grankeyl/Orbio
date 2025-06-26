from asyncio import create_task, get_event_loop
import logging

from aiogram import Bot
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from pyrogram.client import Client
from fastapi.staticfiles import StaticFiles

from src.application.common.utils import get_bot
from src.entrypoint.config import Config
from src.entrypoint.ioc import AppProvider
from src.entrypoint.queue import run_queue
from src.presentation.api.middlewares import setup_middlewares
from src.presentation.api.routers import setup_routers
from src.entrypoint.bot.run import start_bot
from src.presentation.client.handlers.setup import setup_client_handlers


def get_fastapi_app() -> FastAPI:
    config = Config()
    bot = get_bot(config.bot.BOT_TOKEN)
    client = Client("client", config.bot.API_ID, config.bot.API_HASH, workdir="src")
    bot_task = None
    # if config.app.PROD:
    setup_client_handlers(client)
    
    async def on_startup() -> None:
        nonlocal bot_task
        # if config.app.PROD:
        await client.start()
        # Run queue in non-debug mode
        if not config.app.DEBUG:
            try:
                create_task(run_queue(client, bot, config))
                logging.info("Queue processing started")
            except Exception as e:
                logging.error(f"Error starting queue processing: {e}")

        # Start the bot
        logging.info("Starting bot")
        try:
            bot_task = create_task(start_bot(bot, config))
            logging.info("Bot started successfully")
        except Exception as e:
            logging.error(f"Error starting bot: {e}")

    async def on_shutdown() -> None:
        nonlocal bot_task
        logging.info("Application shutting down...")
        # if config.app.PROD:
        await client.stop()
        # Cancel bot task if it exists and is running
        if bot_task is not None and not bot_task.done():
            try:
                bot_task.cancel()
                logging.info("Bot task cancelled")
            except Exception as e:
                logging.error(f"Error cancelling bot task: {e}")

        # Close bot session
        try:
            await bot.session.close()
            logging.info("Bot session closed")
        except Exception as e:
            logging.error(f"Error closing bot session: {e}")

    app = FastAPI(
        debug=config.app.DEBUG,
        docs_url=config.app.docs_url,
        openapi_url=config.app.openapi_url,
        on_startup=[on_startup],
        on_shutdown=[on_shutdown],
    )
    app.mount("/static", StaticFiles(directory="src/static"), name="static")

    container = make_async_container(AppProvider(), context={Config: config, Bot: bot, Client: client})
    setup_dishka(container, app)
    setup_middlewares(app, config, bot)
    setup_routers(app)

    return app

app = get_fastapi_app()
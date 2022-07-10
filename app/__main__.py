import asyncio
import logging
import os
from pathlib import Path

from aiogram import Dispatcher, Bot
from sqlalchemy.orm import close_all_sessions

from app.config import load_config
from app.config.logging_config import setup_logging
from app.handlers import setup_handlers
from app.middlewares import setup_middlewares
from app.models.config.main import Paths
from app.models.db import create_pool
from app.services.rates import rates_holder_factory

logger = logging.getLogger(__name__)


async def main():
    paths = get_paths()
    setup_logging(paths)
    config = load_config(paths)

    dp = Dispatcher()
    rates_holder = rates_holder_factory(config.rates)
    setup_middlewares(dp, create_pool(config.db), config.bot, rates_holder)
    setup_handlers(dp, config.bot)

    bot = Bot(config.bot.token, parse_mode="HTML")

    logger.info("started")
    await bot.send_message(config.bot.log_chat, "Bot started")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.send_message(config.bot.log_chat, "Bot stopped")
        await bot.session.close()
        await rates_holder.close()
        close_all_sessions()
        logger.info("stopped")


def get_paths() -> Paths:
    if path := os.getenv("BOT_PATH"):
        return Paths(Path(path))
    return Paths(Path(__file__).parent.parent)


if __name__ == '__main__':
    asyncio.run(main())

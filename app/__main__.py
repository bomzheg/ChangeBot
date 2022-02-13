import asyncio
import logging
from pathlib import Path

from aiogram import Dispatcher, Bot
from aiogram.dispatcher.filters import ContentTypesFilter
from sqlalchemy.orm import close_all_sessions

from app.config import load_config
from app.handlers import setup_handlers
from app.middlewares import setup_middlewares
from app.models.db import create_pool
from app.services.rates import rates_holder_factory

logger = logging.getLogger(__name__)


async def main():
    app_dir = Path(__file__).parent.parent
    config = load_config(app_dir)

    dp = Dispatcher()
    dp.message.bind_filter(ContentTypesFilter)
    rates_holder = rates_holder_factory(config.rates)
    setup_middlewares(dp, create_pool(config.db), config.bot, rates_holder)
    setup_handlers(dp, config.bot)

    bot = Bot(config.bot.token, parse_mode="HTML")

    logger.info("started")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await rates_holder.close()
        close_all_sessions()


if __name__ == '__main__':
    asyncio.run(main())

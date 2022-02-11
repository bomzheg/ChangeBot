from aiogram import Bot, Dispatcher, types
from loguru import logger

from app import config

bot = Bot(config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


def setup():
    from app import filters
    from app import middlewares
    from app.utils import executor
    logger.debug(f"As application dir using: {config.app_dir}")

    middlewares.setup(dp)
    filters.setup(dp)
    executor.setup()

    logger.info("Configure handlers...")
    # noinspection PyUnresolvedReferences
    import app.handlers

from aiogram import Dispatcher
from sqlalchemy.orm import sessionmaker

from app.middlewares.config_middleware import ContextMiddleware
from app.middlewares.data_load_middleware import LoadDataMiddleware
from app.middlewares.db_middleware import DBMiddleware
from app.models.config.main import BotConfig
from app.services.rates import RatesHolder


def setup_middlewares(
        dp: Dispatcher,
        pool: sessionmaker,
        bot_config: BotConfig,
        rates_holder: RatesHolder,
):
    context_middleware = ContextMiddleware(bot_config, rates_holder)
    dp.message.middleware(context_middleware)
    dp.inline_query.middleware(context_middleware)
    dp.message.middleware(DBMiddleware(pool))
    dp.message.middleware(LoadDataMiddleware())
    dp.message.middleware()

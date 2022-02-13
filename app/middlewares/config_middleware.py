from aiogram import BaseMiddleware
from typing import Callable, Any, Awaitable

from aiogram.types import TelegramObject

from app.models.config.main import BotConfig
from app.services.rates import RatesHolder
from app.services.rates.factory import ConvertedPricesFactory


class ContextMiddleware(BaseMiddleware):
    def __init__(self, config: BotConfig, rates_holder: RatesHolder):
        self.config = config
        self.rates_holder = rates_holder

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        data["config"] = self.config
        data["rates_factory"] = ConvertedPricesFactory(rates=self.rates_holder)
        return await handler(event, data)

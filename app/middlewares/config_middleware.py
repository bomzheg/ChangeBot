from aiogram import BaseMiddleware
from typing import Callable, Any, Awaitable

from aiogram.types import TelegramObject

from app.models.config.main import BotConfig
from app.utils.exch_rates import RatesOpenExchange


class ContextMiddleware(BaseMiddleware):
    def __init__(self, config: BotConfig, oer: RatesOpenExchange):
        self.config = config
        self.oer = oer

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        data["config"] = self.config
        data["oer"] = self.oer
        return await handler(event, data)

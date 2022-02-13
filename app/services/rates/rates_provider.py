import logging
from abc import ABC, abstractmethod

from datetime import datetime

from app.utils.types import IsoCode
from app.services.rates.rates_source import RatesSource

logger = logging.getLogger(__name__)


class RatesProvider(ABC):
    def __init__(self):
        logger.info(f'init {self.get_source_rates()}')

    @abstractmethod
    async def get_rate(self, val_char: IsoCode) -> float:
        pass

    @abstractmethod
    async def get_updated_date(self) -> datetime:
        pass

    @abstractmethod
    def get_source_rates(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    def get_source(self) -> RatesSource:
        pass

    source_names = property(get_source_rates)
    source = property(get_source)

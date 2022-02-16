from datetime import datetime, timedelta

from pycbrf import ExchangeRates as ExchangeCBRF

from app.services.rates.rates_provider import RatesProvider
from app.utils.types import IsoCode
from app.services.rates.rates_source import RatesSource


class RatesCBRF(RatesProvider):
    def __init__(self):
        super(RatesCBRF, self).__init__()
        self.r = ExchangeCBRF(locale_en=True)

    async def get_updated_date(self) -> datetime:
        return self.r.date_received

    async def get_rate(self, char_val: IsoCode) -> float:
        if (await self.get_updated_date() - datetime.now()) > timedelta(days=3):
            self.r = ExchangeCBRF(locale_en=True)
        return await self.get_cached_rate(char_val)

    async def get_cached_rate(self, char_val: IsoCode) -> float:
        if char_val == 'RUB':
            return 1
        else:
            try:
                return float(self.r[char_val].rate)
            except AttributeError as e:
                raise KeyError from e

    def get_source_rates(self):
        return 'ЦБ РФ'

    def get_source(self) -> RatesSource:
        return RatesSource.cbrf

    async def close(self):
        pass

    source_names = property(get_source_rates)
    source = property(get_source)

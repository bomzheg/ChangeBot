from datetime import datetime

from openexchangerates.client import OpenExchangeRatesClient as ExchangeOER

from app.services.rates.rates import Rates
from app.utils.types import IsoCode


class RatesOpenExchange(Rates):
    def __init__(self, api_key: str):
        super(RatesOpenExchange, self).__init__()
        self.api_key = api_key
        self.r = ExchangeOER(api_key=self.api_key)

    async def get_updated_date(self):
        latest_ = await self.r.latest()
        return datetime.fromtimestamp(int(latest_['timestamp'])).isoformat()

    async def get_rate(self, char_val: IsoCode):
        if char_val == 'RUB':
            return 1
        else:
            latest = (await self.r.latest())["rates"]
            return float(latest['RUB'] / latest[char_val])

    def get_source_rates(self):
        return 'OpenExchangeRates'

    source_rates = property(get_source_rates)

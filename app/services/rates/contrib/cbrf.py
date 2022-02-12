from pycbrf import ExchangeRates as ExchangeCBRF

from app.services.rates.rates import Rates
from app.utils.types import IsoCode


class RatesCBRF(Rates):
    def __init__(self):
        Rates.__init__(self)
        self.r = ExchangeCBRF(locale_en=True)

    async def get_updated_date(self):
        return self.r.date_received

    async def get_rate(self, char_val: IsoCode):
        if char_val == 'RUB':
            return 1
        else:
            return float(self.r[char_val].rate)

    def get_source_rates(self):
        return 'ЦБ РФ'

    source_rates = property(get_source_rates)

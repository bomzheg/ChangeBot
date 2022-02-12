from dataclasses import dataclass

from app.models.config.main import RatesConfig
from app.services.rates.contrib import RatesCBRF, RatesOpenExchange
from .rates_source import RatesSource
from app.services.rates.rates_provider import RatesProvider
from app.utils.types import IsoCode


@dataclass
class RatesHolder:
    providers_mapping: dict[RatesSource, RatesProvider]

    @property
    def providers(self):
        return self.providers_mapping.values()

    def get_source_names(self, sources: set[RatesSource]) -> list[str]:
        return [self.providers_mapping[source].source_names for source in sources]

    async def close(self):
        for provider in self.providers:
            await provider.close()

    async def find_rate(self, val_char: IsoCode, primary: RatesSource) -> tuple[float, RatesSource]:
        found_rate = None
        used_provider = None
        for r in self.providers_mapping[primary], *self.providers:
            try:
                found_rate = await r.get_rate(val_char)
            except KeyError:
                pass
            else:
                used_provider = r
                break
        if found_rate is None or used_provider is None:
            raise KeyError("rate not found in any rate provider")
        return found_rate, used_provider.source

    async def new_price(
            self,
            price: float,
            old_val_char: IsoCode,
            new_val_char: IsoCode,
            primary: RatesSource,
    ):
        rate_old_val_char, old_src = await self.find_rate(old_val_char, primary)
        rate_new_val_char, new_src = await self.find_rate(new_val_char, primary)
        rez = price * rate_old_val_char / rate_new_val_char
        return rez, {old_src, new_src}


def rates_holder_factory(config: RatesConfig) -> RatesHolder:
    return RatesHolder(providers_mapping={
        RatesSource.cbrf: RatesCBRF(),
        RatesSource.oer: RatesOpenExchange(api_key=config.oer_token),
    })

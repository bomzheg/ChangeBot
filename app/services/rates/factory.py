import re

from app.services.rates.contrib.oer import RatesOpenExchange
from app.services.rates.converted_price import PartString, ConvertedPrice
from app.utils.types import IsoCode


class ConvertedPricesFactory:
    rates = list()

    def __init__(self, *, rates: RatesOpenExchange):
        self.used_src = set()
        self.rates = [rates]
        self.r = rates

    def build(self, line=""):
        positions_of_prices = list()
        for val_char_from, pattern in self.r.valuts.items():
            add_prices(pattern, line, val_char_from, positions_of_prices)
        add_prices(self.r.vault_dollar_reg2, line, "USD", positions_of_prices)
        positions_of_prices.sort()
        list_parts = list()
        i = 0
        for start_price, start_float, end_float, val_char, end_price in positions_of_prices:
            list_parts.append(
                PartString(
                    line[i:start_price],
                    float(line[start_float:end_float].replace(",", ".")),
                    val_char
                )
            )
            i = end_price
        end_str = line[i:]
        return ConvertedPrice(list_parts=list_parts, tail=end_str, available_src=self.rates)

    def validate_vals(self, words: list[IsoCode]):
        err_list = list()
        to_append = set()
        if len(words) == 0:
            raise ValueError("no vals is present")
        for word in words:
            if word in self.r.val_chars:
                to_append.add(word)
            else:
                err_list.append(word)
        return to_append, err_list

    async def get_updated_date(self):
        return f"oer: {await self.r.get_updated_date()}"


def add_prices(pattern: re.Pattern, line: str, val_char: IsoCode, positions_of_prices: list):
    i = 0
    while True:
        match = pattern.search(line, i)
        if not match:
            break
        i = match.end(0)
        positions_of_prices.append((match.start(0), match.start(1), match.end(1), val_char, match.end(0)))

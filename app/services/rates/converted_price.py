"""
Danger! very old ugly code
"""
import logging

from dataclasses import dataclass, field

from copy import deepcopy

from app.services.rates.rates import Rates
from app.utils.types import IsoCode

logger = logging.getLogger(__name__)


@dataclass
class PartString:
    str_part: str
    float_part: float
    val_char_part: str


@dataclass
class ConvertedPrice:
    list_parts: list[PartString]
    tail: str
    available_src: list[Rates]
    used_src: set[Rates] = field(init=False)

    def __post_init__(self):
        self.used_src = set()

    def __str__(self):
        rez = ""
        for part in self:
            rez += part.str_part + " " + self.price_to_str(part.float_part, part.val_char_part)
        rez += self.tail
        return rez

    def __iter__(self):
        return iter(self.list_parts)

    def __setitem__(self, key, value):
        self.list_parts[key] = value

    def __getitem__(self, item):
        return self.list_parts[item]

    def get_count_prices(self):
        return len(self.list_parts)

    @property
    def first_src(self):
        return self.available_src[0]

    @property
    def used_source_names(self):
        return ' '.join([src.source_rates for src in self.used_src])

    def price_to_str(self, float_part: float, val_char_part: IsoCode):
        if val_char_part == "USD":
            result = self.first_src.val_chars[val_char_part] + str(round(float_part, 2))
        else:
            result = str(round(float_part, 2)) + self.first_src.val_chars[val_char_part]
        return result

    async def get_str_with_new_rates(self, val_char_to: IsoCode):
        new_conv_price = deepcopy(self)
        for parts in self:
            new_price, next_src = await self._new_price(
                parts.float_part,
                parts.val_char_part,
                val_char_to
            )
            self.used_src.update(next_src)
            new_conv_price.list_parts.append(
                PartString(
                    str_part=parts.str_part,
                    float_part=new_price,
                    val_char_part=val_char_to
                )
            )
        return new_conv_price

    async def get_plain_str_with_new_rates(self, val_char_to: IsoCode):
        new_conv_price = ""
        for parts in self:
            new_conv_price += parts.str_part
            new_price, next_src = await self._new_price(
                parts.float_part, parts.val_char_part, val_char_to
            )
            self.used_src.update(next_src)
            new_conv_price += self.price_to_str(new_price, val_char_to)
            if val_char_to != parts.val_char_part:
                new_conv_price += f" (из {self.first_src.val_chars[parts.val_char_part]})"
        new_conv_price += self.tail + "\nВсе конвертации по курсам: "
        new_conv_price += self.used_source_names
        return new_conv_price

    async def get_only_equals_rates(self, list_val_char_to: list[IsoCode]):
        rez = ""
        my_set = set()
        for parts in self:
            if str(parts.float_part) + parts.val_char_part not in my_set:
                my_set.add(str(parts.float_part) + parts.val_char_part)
                if parts.float_part == float('inf'):
                    rez += "Кто тут измеряет стоимость вселенной в " + \
                           self.first_src.val_chars[parts.val_char_part] + "?"
                elif parts.float_part > 9.9e-3:
                    next_rez = self.price_to_str(parts.float_part, parts.val_char_part)
                    for val_char_to in list_val_char_to:
                        if parts.val_char_part != val_char_to:
                            next_rez += " ≈ "
                            new_price, next_src = await self._new_price(
                                price=parts.float_part, old_val_char=parts.val_char_part, new_val_char=val_char_to,
                            )
                            self.used_src.update(next_src)
                            next_rez += self.price_to_str(
                                new_price,
                                val_char_to
                            )

                    if next_rez.find('≈') != -1:
                        rez += next_rez + "\n"
        if rez != '' and len(self.used_src) > 1:
            rez += "Все конвертации по курсам: " + self.used_source_names
        return rez

    async def found_rate(self, val_char: IsoCode):
        rate_val_char = None
        for r in self.available_src:
            try:
                rate_val_char = await r.get_rate(val_char)
            except KeyError:
                pass
            else:
                break
        if rate_val_char is None:
            raise KeyError("")
        return rate_val_char, r

    async def _new_price(self, price: float, old_val_char: IsoCode, new_val_char: IsoCode):
        rate_old_val_char, old_src = await self.found_rate(old_val_char)
        rate_new_val_char, new_src = await self.found_rate(new_val_char)
        rez = price * rate_old_val_char / rate_new_val_char
        return rez, {old_src, new_src}

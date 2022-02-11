import re
import datetime
from abc import ABC, abstractmethod

from app import config
from app.config import DEFAULT_SRC
from pycbrf import ExchangeRates as ExchangeCBRF
# import quandl
from openexchangerates.exchange import Exchange as ExchangeOER


# Общая идея ООП здесь: абстрактный класс Rates - описывает поведение - как конвертировать,
# наследники - добывают курсы валют и только дают уже определённым методам конкретные цифры
# ConvertedPrice - при инициализиации нарезает внутрь себя с сохранением позиций строку и ее части содержащие цены
# внешний пользователь просто создаёт объект строки с ценами и общается с её функциями, Rates - содержится в описании
# класса ConvertedPrice
# TODO разобраться с регулярками здесь. нужно чтобы "2 евроспорт" не считалось а "*,2.8бакса?" считалось
# таким образом надо думать о том, что разрешены знаки препинания после ключевых символов или слов, но не буквы
digits_re = r"\d+[.,]?\d*"
valuts_re = [
        r"(?:австралийский доллар|A\$|AUD)",  # $
        # r"(?азербайджанский манат|ман|₼|AZN)", # manat, ₼ - не обрабатывается
        r"(?:фунт(?:ами|ов|а|у|ом|) стерлингов|£|GBP)",
        r"(?:драм(?:ами|ов|а|у|ом|)|֏|AMD)",
        r"(?:белорусский рубль|Br|BYN)",  # rub
        r"(?:лев|лв|BGN)",
        r"(?:реал(?:ами|ов|а|у|ом|)|R\$|BRL)",
        r"(?:форинт(?:ами|ов|а|у|ом|)|ƒ|HUF)",
        r"(?:гонконгский доллар|HK\$|HKD)",  # $
        r"(?:(?:датск(?:ая|ую|ой|ую|ие|их|ими) )крона|дат.kr|DKK)",  # krona
        r"(?:доллар(?:ами|ов|ы|у|ом|а|)|бакс(?:ами|ов|а|у|ом|)|\$|USD)",  # $
        r"(?:евро|€|EUR)",
        r"(?:(?:индийск(?:ая|ую|ой|ую|ие|их|ими) )рупи(?:ями|й|ю|ей|и|ях|я)|₹|INR)",  # рупия
        r"(?:тенге|тңг|₸|KZT)",
        r"(?:канадский доллар|C\$|CAD)",  # $
        r"(?:сом(?:ами|ов|а|у|ом|)|KGS)",
        r"(?:юан(?:ями|й|ю|ей|ь|ях|я)|кит.¥|CNY)",
        r"(?:молдавский лей|молд.L|MDL)",
        r"(?:(?:норвежск(?:ая|ую|ой|ую|ие|их|ими) )крона|норв.kr|NOK)",  # krona
        r"(?:злоты(?:й|х)|zł|PLN)",
        r"(?:румынский лей|рум.L|RON)",
        r"(?:сингапурский доллар|S\$|SGD)",  # $
        r"(?:сомони|смн.|TJS)",
        r"(?:лир(?:ами|у|ы|ой|а|)|₺|TRY)",
        r"(?:туркменский манат|туркм.m|TMT)",  # manat
        r"(?:сум(?:ами|ов|ы|у|ом|а|е|ах|)|сўм|UZS)",
        r"(?:грив(?:нами|ны|не|ну|ной|на|ен)|грн|₴|UAH)",
        r"(?:(?:чешск(?:ая|ую|ой|ую|ие|их|ими) )?крон(?:ами|ы|е|у|ой|а|)|кч|Kč|CZK)",  # krona
        r"(?:(?:шведск(?:ая|ую|ой|ую|ие|их|ими) )крона|шв.kr|SEK)",  # krona
        r"(?:франк(?:ами|ов|а|у|ом|)|₣|CHF)",
        r"(?:ренд|ZAR)",
        r"(?:вон(?:ами|ы|е|у|ой|а|)|₩|KRW)",
        r"(?:иен(?:ами|ы|е|у|ой|а|)|яп.¥|JPY)",
        r"(?:рубл(?:ями|и|ем|ю|ей|я|ь)|руб|₽|RUB)",  # rub
        r"(?:шекел(?:ями|и|ем|ю|ей|я|ь)|NIS|₪|ILS)",
        r"(?:(?:сейшельск(?:ая|ую|ой|ую|ие|их|ими) )?рупи(?:ями|й|ю|ей|е|и|ям|ях|я)|sc|Re|SCR)",  # рупия
        r"(?:дирхам(?:ами|ов|а|у|ом|)|Dh|AED)",
    ]


class Rates(ABC):
    digits_reg = re.compile(digits_re)  # цифры, десятичная точка и снова цифры
    valuts = {
        val[-4:-1]: re.compile(
            r"(" + digits_re + r")\s*" + val + r"(?=[\r\n\t\f\v .,:;!?&]|$)",
            flags=re.IGNORECASE
        )
        for val in valuts_re
    }
    vault_dollar_reg2 = re.compile(r"\$(\d+[.,]?\d*)(?=[\r\n\t\f\v .,:;!?&]|$)")
    val_chars = {
        "AUD": "A$",
        "AZN": "₼",
        "GBP": "£",
        "AMD": "֏",
        "BYN": "Br",
        "BGN": "лв",
        "BRL": "R$",
        "HUF": "ƒ",
        "HKD": "HK$",
        "DKK": "дат.kr",
        "USD": "$",
        "EUR": "€",
        "INR": "₹",
        "KZT": "₸",
        "CAD": "C$",
        "KGS": "сом",
        "CNY": "кит.¥",
        "MDL": "молд.L",
        "NOK": "норв.kr",
        "PLN": "zł",
        "RON": "рум.L",
        "SGD": "S$",
        "TJS": "смн.",
        "TRY": "₺",
        "TMT": "туркм.m",
        "UZS": "сўм",
        "UAH": "₴",
        "CZK": "Kč",
        "SEK": "шв.kr",
        "CHF": "₣",
        "ZAR": "ренд",
        "KRW": "₩",
        "JPY": "яп.¥",
        "RUB": "₽",
        "ILS": "₪",
        "SCR": " SCR",
        "AED": "Dh"
    }

    def __init__(self):
        print(f'init {self.get_source_rates()}')
        return

    @abstractmethod
    def get_rate(self, val_char):
        pass

    @abstractmethod
    def get_updated_date(self):
        pass

    @abstractmethod
    def get_source_rates(self):
        pass

    source_rates = property(get_source_rates)


class RatesCBRF(Rates):
    def __init__(self):
        Rates.__init__(self)
        self.r = ExchangeCBRF(locale_en=True)

    def get_updated_date(self):
        return self.r.date_received

    def get_rate(self, char_val: str):
        if char_val == 'RUB':
            return 1
        else:
            try:
                return float(self.r[char_val].rate)
            except AttributeError as e:
                raise KeyError from e

    def get_source_rates(self):
        return 'ЦБ РФ'

    source_rates = property(get_source_rates)


class RatesOpenExchange(Rates):

    def __init__(self, api_key: str):
        super(RatesOpenExchange, self).__init__()
        self.api_key = api_key
        self.r = ExchangeOER(app_id=self.api_key)

    def get_updated_date(self):
        return datetime.datetime.fromtimestamp(self.r.latest()['timestamp']).isoformat()

    def get_rate(self, char_val: str):
        if char_val == 'RUB':
            return 1
        else:
            return self.r.rates()['RUB'] / self.r.rates()[char_val]

    def get_source_rates(self):
        return 'OpenExchangeRates'

    source_rates = property(get_source_rates)


class PartString:
    def __init__(self, str_part, float_part, val_char_part):
        self.str_part = str_part
        self.float_part = float_part
        self.val_char_part = val_char_part


rates_cb = RatesCBRF()
rates_oer = RatesOpenExchange(config.OPEN_EXCHANGE_RATES_API_KEY)


class ConvertedPrices:
    rates = list()

    def __init__(self, line="", *, rates_source=DEFAULT_SRC):
        self.used_src = set()
        if rates_source == 'cbrf':
            self.rates = [rates_cb, rates_oer]
            self.r = self.rates[0]
        elif rates_source == 'oer':
            self.rates = [rates_oer, rates_cb]
            self.r = self.rates[0]
        else:
            self.rates = [rates_cb, rates_oer]
            self.r = self.rates[0]

        def add_prices(pattern, line, val_char):
            i = 0
            while True:
                match = pattern.search(line, i)
                if not match:
                    break
                i = match.end(0)
                positions_of_prices.append((match.start(0), match.start(1), match.end(1), val_char, match.end(0)))

        positions_of_prices = list()
        for val_char_from, pattern in self.r.valuts.items():
            add_prices(pattern, line, val_char_from)
        add_prices(self.r.vault_dollar_reg2, line, "USD")
        positions_of_prices.sort()
        self.list_parts = list()
        i = 0
        for start_price, start_float, end_float, val_char, end_price in positions_of_prices:
            self.list_parts.append(
                PartString(
                    line[i:start_price],
                    float(line[start_float:end_float].replace(",", ".")),
                    val_char
                )
            )
            i = end_price
        self.end_str = line[i:]

    def __str__(self):
        rez = ""
        for part in self:
            rez += part.str_part + " " + self.price_to_str(part.float_part, part.val_char_part)
        rez += self.end_str
        return rez

    def __iter__(self):
        return (iter(self.list_parts))

    def __setitem__(self, key, value):
        self.list_parts[key] = value

    def __getitem__(self, item):
        return self.list_parts[item]

    def get_count_prices(self):
        return len(self.list_parts)

    def get_str_with_new_rates(self, val_char_to):
        new_conv_price = ConvertedPrices()
        new_conv_price.end_str = self.end_str
        for parts in self:
            new_price, next_src = self._new_price(
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

    def get_plain_str_with_new_rates(self, val_char_to):
        # rez = self.get_str_with_new_rates(val_char_to)
        # rez.end_str += "\nВсе конвертации по курсам: " + ', '.join(self.used_src)
        # return str(rez)
        new_conv_price = ""
        for parts in self:
            new_conv_price += parts.str_part
            new_price, next_src = self._new_price(
                parts.float_part, parts.val_char_part, val_char_to
            )
            self.used_src.update(next_src)
            new_conv_price += self.price_to_str(new_price, val_char_to)
            if val_char_to != parts.val_char_part:
                new_conv_price += f" (из {self.r.val_chars[parts.val_char_part]})"
        new_conv_price += self.end_str + "\nВсе конвертации по курсам: " + ' '.join(self.used_src)
        return new_conv_price

    def get_only_equals_rates(self, list_val_char_to):
        rez = ""
        mySet = set()
        for parts in self:
            if str(parts.float_part) + parts.val_char_part not in mySet:
                mySet.add(str(parts.float_part) + parts.val_char_part)
                if parts.float_part == float('inf'):
                    rez += "Кто тут измеряет стоимость вселенной в " + \
                           self.r.val_chars[parts.val_char_part] + "?"
                elif parts.float_part > 9.9e-3:
                    next_rez = self.price_to_str(parts.float_part, parts.val_char_part)
                    for val_char_to in list_val_char_to:
                        if parts.val_char_part != val_char_to:
                            next_rez += " ≈ "
                            new_price, next_src = self._new_price(parts.float_part, parts.val_char_part, val_char_to)
                            self.used_src.update(next_src)
                            next_rez += self.price_to_str(
                                new_price,
                                val_char_to
                            )

                    if next_rez.find('≈') != -1:
                        rez += next_rez + "\n"
        if rez != '' and len(self.used_src) > 1:
            rez += "Все конвертации по курсам: " + ', '.join(self.used_src)
        return rez

    def found_rate(self, val_char):
        for r in self.rates:
            try:
                rate_val_char = r.get_rate(val_char)
            except KeyError:
                pass
            else:
                break
        else:
            if rate_val_char is None:
                raise KeyError
        return rate_val_char, r.source_rates

    def _new_price(self, price, old_val_char, new_val_char):
        rez = None
        rate_old_val_char, old_src = self.found_rate(old_val_char)
        rate_new_val_char, new_src = self.found_rate(new_val_char)
        rez = price * rate_old_val_char / rate_new_val_char
        return rez, {old_src, new_src}

    def price_to_str(self, float_part, val_char_part):
        if val_char_part == "USD":
            result = self.r.val_chars[val_char_part] + str(round(float_part, 2))
        else:
            result = str(round(float_part, 2)) + self.r.val_chars[val_char_part]
        return result

    def validate_vals(self, words: list):
        err_list = list()
        to_append = set()
        if len(words) > 0:
            for word in words:
                if word in self.r.val_chars:
                    to_append.add(word)
                else:
                    err_list.append(word)
            return to_append, err_list
        else:
            raise ValueError

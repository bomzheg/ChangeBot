import re

from app.config import DEFAULT_SRC
from app.services.rates import RatesHolder, RatesSource
from app.services.rates.converted_price import PartString, ConvertedPrice
from app.utils.types import IsoCode


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


# TODO разобраться с регулярками здесь. нужно чтобы "2 евроспорт" не считалось а "*,2.8бакса?" считалось
#  таким образом надо думать о том, что разрешены знаки препинания после ключевых символов или слов, но не буквы
class ConvertedPricesFactory:
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

    def __init__(self, *, rates: RatesHolder):
        self.rates = rates

    def build(self, line="", primary_src: RatesSource = RatesSource[DEFAULT_SRC]):
        positions_of_prices = list()
        for val_char_from, pattern in self.valuts.items():
            add_prices(pattern, line, val_char_from, positions_of_prices)
        add_prices(self.vault_dollar_reg2, line, "USD", positions_of_prices)
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
        return ConvertedPrice(
            list_parts=list_parts,
            tail=end_str,
            rates_holder=self.rates,
            primary_src=primary_src,
            val_chars=self.val_chars,
        )

    def validate_vals(self, words: list[IsoCode]):
        err_list = list()
        to_append = set()
        if len(words) == 0:
            raise ValueError("no vals is present")
        for word in words:
            if word in self.val_chars:
                to_append.add(word)
            else:
                err_list.append(word)
        return to_append, err_list

    async def get_updated_date(self):
        return f"oer: {await self.get_updated_date()}"


def add_prices(pattern: re.Pattern, line: str, val_char: IsoCode, positions_of_prices: list):
    i = 0
    while True:
        match = pattern.search(line, i)
        if not match:
            break
        i = match.end(0)
        positions_of_prices.append((match.start(0), match.start(1), match.end(1), val_char, match.end(0)))

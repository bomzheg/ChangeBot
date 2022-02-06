from aiogram import types, Bot
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from app.utils.exch_rates import ConvertedPrices


VALUTA = {
    "RUB": "В рубли",
    "USD": "В доллары",
    "EUR": "В евро",
    "CZK": "В Чешскую крону",
    "SCR": "В Сейшельскую рупию",
}


async def inline_convert(inline_query: InlineQuery, bot: Bot):
    line = ConvertedPrices(inline_query.query)
    if line.get_count_prices() == 0:
        rez = [
            InlineQueryResultArticle(
                id='1', title="Ничего",
                description="Нечего конвертировать",
                input_message_content=InputTextMessageContent(
                    "Введённый текст не содержит распознаваемых цен, которые можно конвертировать в валюты"
                )
            )
        ]
    else:
        rez = list()
        for iso_code, desc in VALUTA:
            rez = line.get_plain_str_with_new_rates(iso_code)
            rez.append(
                InlineQueryResultArticle(
                    id='1', title=desc,
                    description=f"Сконвертировано: {rez}",
                    input_message_content=InputTextMessageContent(
                        message_text=rez)
                )
            )
    await bot.answer_inline_query(inline_query.id, results=rez)

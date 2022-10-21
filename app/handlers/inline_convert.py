from aiogram import Bot, Dispatcher
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from app.services.rates.factory import ConvertedPricesFactory

VALUTA = {
    "RUB": "В рубли",
    "USD": "В доллары",
    "EUR": "В евро",
    "CZK": "В Чешскую крону",
    "KZT": "В тенге",
    "AMD": "В драмы",
    "GEL": "В лари",
    "SCR": "В Сейшельскую рупию",
}


async def inline_convert(inline_query: InlineQuery, bot: Bot, rates_factory: ConvertedPricesFactory):
    line = rates_factory.build(inline_query.query)
    if line.get_count_prices() == 0:
        rez = [
            InlineQueryResultArticle(
                id='1', title="Ничего",
                description="Нечего конвертировать",
                input_message_content=InputTextMessageContent(
                    message_text="Введённый текст не содержит распознаваемых цен, которые можно конвертировать в валюты"
                )
            )
        ]
    else:
        rez = list()
        for iso_code, desc in VALUTA.items():
            current = await line.get_plain_str_with_new_rates(iso_code)
            rez.append(
                InlineQueryResultArticle(
                    id=iso_code, title=desc,
                    description=f"Сконвертировано: {current}",
                    input_message_content=InputTextMessageContent(
                        message_text=current,
                        disable_web_page_preview=True,
                    )
                )
            )
    await bot.answer_inline_query(inline_query.id, results=rez)


def setup_inline(dp: Dispatcher):
    dp.inline_query.register(inline_convert)

from aiogram import types
from app.misc import dp, bot
from app.utils.exch_rates import ConvertedPrices


@dp.inline_handler()
async def inline_convert(inline_query: types.InlineQuery):
    line = ConvertedPrices(inline_query.query)
    if line.get_count_prices() == 0:
        rez = [
            types.InlineQueryResultArticle(
                id='1', title="Ничего",
                description="Нечего конвертировать",
                input_message_content=types.InputTextMessageContent(
                    "Введённый текст не содержит распознаваемых цен, которые можно конвертировать в валюты"
                )
            )
        ]
    else:
        rez_to_rub = line.get_plain_str_with_new_rates("RUB")
        rez_to_dol = line.get_plain_str_with_new_rates("USD")
        rez_to_eur = line.get_plain_str_with_new_rates("EUR")
        rez_to_czk = line.get_plain_str_with_new_rates("CZK")
        rez_to_scr = line.get_plain_str_with_new_rates("SCR")
        rez = list()
        rez.append(
            types.InlineQueryResultArticle(
                id='1', title="В рубли",
                description=f"Сконвертировано: {rez_to_rub}",
                input_message_content=types.InputTextMessageContent(
                    message_text=rez_to_rub)
            )
        )
        rez.append(
            types.InlineQueryResultArticle(
                id='2', title="В доллары",
                description=f"Сконвертировано: {rez_to_dol}",
                input_message_content=types.InputTextMessageContent(
                    message_text=rez_to_dol)
            )
        )
        rez.append(
            types.InlineQueryResultArticle(
                id='3', title="В евро",
                description=f"Сконвертировано: {rez_to_eur}",
                input_message_content=types.InputTextMessageContent(
                    message_text=rez_to_eur)
            )
        )
        rez.append(
            types.InlineQueryResultArticle(
                id='4', title="В Чешскую крону",
                description=f"Сконвертировано: {rez_to_czk}",
                input_message_content=types.InputTextMessageContent(
                    message_text=rez_to_czk)
            )
        )
        rez.append(
            types.InlineQueryResultArticle(
                id='5', title="В Сейшельскую рупию",
                description=f"Сконвертировано: {rez_to_scr}",
                input_message_content=types.InputTextMessageContent(
                    message_text=rez_to_scr)
            )
        )
    await bot.answer_inline_query(inline_query.id, results=rez)

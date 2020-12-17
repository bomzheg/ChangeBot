from aiogram import types

from loguru import logger

from app import config
from app.misc import dp, bot
from app.models.chat import Chat
from app.models.settings import Settings
from app.utils.exch_rates import ConvertedPrices


@dp.message_handler(is_superuser=True, commands='date')
async def get_date(_: types.Message, chat: Chat):
    s, _ = await Settings.get_or_create(chat=chat)
    some_line = ConvertedPrices(rates_source=s.get_src())
    await bot.send_message(config.ADMIN_ID, some_line.r.get_updated_date(), disable_notification=True)


@dp.message_handler(commands='val_to', commands_prefix='!')
async def settings_val(message: types.Message, chat: Chat):
    words = message.text.upper().split()
    s, _ = await Settings.get_or_create(chat=chat)
    some_line = ConvertedPrices(rates_source=s.get_src())
    if len(words) > 1:
        to_append, err_list = some_line.validate_vals(words[1:])
        if len(err_list) > 0:
            await message.reply("Неизвестные валюты " + ", ".join(err_list), disable_notification=True)
        if len(to_append) > 0:
            await s.set_vals(to_append)
            await message.reply(
                "Теперь в чате будет проводиться конвертация в " +
                ", ".join(to_append),
                disable_notification=True
            )
        logger.info(
            f"In chat ID{message.chat.id} changed val_to: {to_append}. "
            f"Errors {err_list}"
        )
        return
    return await message.reply(config.HELP_MSG)


@dp.message_handler(commands='cbrf')
async def settings_src_cbrf(message: types.Message, chat: Chat):
    s, _ = await Settings.get_or_create(chat=chat)
    await s.set_src('cbrf')
    logger.info(f"In chat ID{message.chat.id} default src now cbrf")
    await message.reply("Теперь конвертация в чате будет проводиться по курсам ЦБ РФ", disable_notification=True)


@dp.message_handler(commands='oer')
async def settings_src_oer(message: types.Message, chat: Chat):
    s, _ = await Settings.get_or_create(chat=chat)
    await s.set_src('oer')
    logger.info(f"In chat ID{message.chat.id} default src now oer")
    await message.reply("Теперь конвертация в чате будет проводиться по курсам OpenExchangeRates",
                        disable_notification=True)


@dp.message_handler(content_types="text")
@dp.message_handler(content_types=['photo', 'document', 'audio', 'video', 'voice', 'animation'])
async def convert_valut(message: types.Message, chat: Chat):
    text = message.text or message.caption
    if text is None:
        return
    s, _ = await Settings.get_or_create(chat=chat)
    line = ConvertedPrices(
        text, 
        rates_source=s.get_src()
    )
    convert_text = line.get_only_equals_rates(s.get_vals())
    if convert_text != "":
        await message.reply(convert_text, disable_notification=True)

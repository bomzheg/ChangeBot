import logging

from aiogram import Dispatcher
from aiogram.types import ContentType, Message

from app import texts
from app.models import dto
from app.models.settings import Settings
from app.utils.exch_rates import ConvertedPrices


logger = logging.getLogger(__name__)


async def settings_val(message: Message, chat: dto.Chat):
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
    return await message.reply(texts.HELP_MSG)


async def settings_src_cbrf(message: Message, chat: dto.Chat):
    s, _ = await Settings.get_or_create(chat=chat)
    await s.set_src('cbrf')
    logger.info(f"In chat ID{message.chat.id} default src now cbrf")
    await message.reply("Теперь конвертация в чате будет проводиться по курсам ЦБ РФ", disable_notification=True)


async def settings_src_oer(message: Message, chat: dto.Chat):
    s, _ = await Settings.get_or_create(chat=chat)
    await s.set_src('oer')
    logger.info(f"In chat ID{message.chat.id} default src now oer")
    await message.reply("Теперь конвертация в чате будет проводиться по курсам OpenExchangeRates",
                        disable_notification=True)


async def convert_valut(message: Message, chat: dto.Chat):
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


def setup_message_convert(dp: Dispatcher):
    dp.message.register(settings_val, commands="val_to", commands_prefix="!")
    dp.message.register(settings_src_cbrf, commands="cbrf")
    dp.message.register(settings_src_oer, commands="oer")
    dp.message.register(convert_valut, content_types=[
        ContentType.TEXT,
        ContentType.PHOTO,
        ContentType.DOCUMENT,
        ContentType.AUDIO,
        ContentType.VIDEO,
        ContentType.VOICE,
        ContentType.ANIMATION,
    ])

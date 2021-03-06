import logging

from aiogram import Dispatcher
from aiogram.types import ContentType, Message

from app import texts
from app.dao.holder import HolderDao
from app.models import dto
from app.services.rates.factory import ConvertedPricesFactory
from app.services.settings import update_settings

logger = logging.getLogger(__name__)


async def settings_val(message: Message, settings: dto.Settings, dao: HolderDao, rates_factory: ConvertedPricesFactory):
    words = message.text.upper().split()
    if len(words) > 1:
        to_append, err_list = rates_factory.validate_vals(words[1:])
        if len(err_list) > 0:
            await message.reply("Неизвестные валюты " + ", ".join(err_list), disable_notification=True)
        if len(to_append) > 0:
            settings.vals = to_append
            await update_settings(settings, dao.settings)
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


async def settings_src_cbrf(message: Message, settings: dto.Settings, dao: HolderDao):
    settings.src = 'cbrf'
    await update_settings(settings, dao.settings)
    logger.info(f"In chat ID{message.chat.id} default src now cbrf")
    await message.reply("Теперь конвертация в чате будет проводиться по курсам ЦБ РФ", disable_notification=True)


async def settings_src_oer(message: Message, settings: dto.Settings, dao: HolderDao):
    settings.src = 'oer'
    await update_settings(settings, dao.settings)
    logger.info(f"In chat ID{message.chat.id} default src now oer")
    await message.reply("Теперь конвертация в чате будет проводиться по курсам OpenExchangeRates",
                        disable_notification=True)


async def convert_valut(message: Message, settings: dto.Settings, rates_factory: ConvertedPricesFactory):
    text = message.text or message.caption
    if text is None:
        return
    line = rates_factory.build(text, settings.source)
    convert_text = await line.get_only_equals_rates(settings.vals)
    if convert_text != "":
        await message.reply(convert_text, disable_notification=True, disable_web_page_preview=True)


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

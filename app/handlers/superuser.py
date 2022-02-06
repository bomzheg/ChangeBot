import asyncio
import logging
import threading
import time

from aiogram import Dispatcher, Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message
from functools import partial

from app.filters.superusers import is_superuser
from app.models import dto
from app.models.config.main import BotConfig
from app.utils.exch_rates import ConvertedPrices
from app.utils.send_text_file import send_log_files

logger = logging.getLogger(__name__)


async def exception(message: Message):
    raise RuntimeError(message.text)


async def leave_chat(message: Message, bot: Bot):
    await bot.leave_chat(message.chat.id)


async def restart(message: Message):
    def tread_stop(sec=1):
        time.sleep(sec)
        # noinspection PyProtectedMember
        # noinspection PyUnresolvedReferences
        os._exit(1)

    logger.warning("Exited by superuser %s command /restart", message.from_user.id)
    threading.Thread(target=tread_stop, args=()).start()


async def who_krasava(message):
    await message.reply("Ты конечно!", disable_notification=True)


async def get_log(_: Message, config: BotConfig):
    asyncio.create_task(send_log_files(config.log_chat_id))


async def get_logchat(message: Message, bot: Bot, config: BotConfig):
    logger.info("Superuser %s ask logchat link", message.from_user.id)
    try:
        log_ch = (await bot.get_chat(config.log_chat_id)).invite_link
        await message.reply(log_ch, disable_notification=True)
    except TelegramAPIError as e:
        await message.reply(
            f"{e}\nУбедитесь что бот находится в логчате, "
            "ID логчата верно указан в конфиге, а так же что бот "
            "имеет право администратора на создание пригласительных ссылок. "
            "Так же попробуйте нажать /generate_invite_logchat для создания "
            "ссылки если ранее она не была создана"
        )


async def generate_logchat_link(message: Message, bot: Bot, config: BotConfig):
    logger.info(f"Superuser %s ask new logchat link", message.from_user.id)
    try:
        await message.reply(
            await bot.export_chat_invite_link(config.log_chat_id),
            disable_notification=True,
        )
    except TelegramAPIError as e:
        await message.reply(
            f"{e}\nУбедитесь что бот находится в логчате, "
            "ID логчата верно указан в конфиге, а так же что бот "
            "имеет право администратора на создание пригласительных ссылок"
        )


async def get_date(message: Message, chat: dto.Chat):
    s, _ = await Settings.get_or_create(chat=chat)
    some_line = ConvertedPrices(rates_source=s.get_src())
    await message.answer(some_line.r.get_updated_date(), disable_notification=True)


def setup_superuser(dp: Dispatcher, bot_config: BotConfig):
    is_superuser_ = partial(is_superuser, superusers=bot_config.superusers)
    is_beauty_ = partial(is_superuser, superusers=bot_config.beauty)

    dp.message.register(exception, is_superuser_, commands="exception")
    dp.message.register(leave_chat, is_superuser_, commands="get_out")
    dp.message.register(restart, is_superuser_, commands="restart")

    dp.message.register(who_krasava, is_superuser_, lambda m: m.text.lower == "кто красавчик?")
    dp.message.register(who_krasava, is_beauty_, lambda m: m.text.lower == "кто красотка?")

    dp.message.register(restart, is_superuser_, commands="update_log")
    dp.message.register(get_logchat, is_superuser_, commands="logchat")
    dp.message.register(generate_logchat_link, is_superuser_, commands="generate_invite_logchat")

    dp.message.register(get_date, is_superuser_, commands="date")

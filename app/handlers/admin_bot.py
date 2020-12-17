import os
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import BadRequest, TelegramAPIError
from loguru import logger

from app import config
from app.misc import bot, dp
from app.utils.log import StreamToLogger
from app.utils.send_text_file import send_log_files

logger_ = StreamToLogger(logger)


@dp.message_handler(lambda message: message.chat.id == config.ADMIN_ID, commands='cancel_jobs')
async def cancel_jobs(message: types.Message):
    from app.services.apscheduller import scheduler
    logger.warning("removing all jobs")
    scheduler.print_jobs(out=logger_)
    scheduler.remove_all_jobs()
    await message.reply("Данные удалены")


@dp.async_task
@dp.message_handler(is_superuser=True, commands='update_log')
async def get_log(_: types.Message):
    await send_log_files(config.LOG_CHAT_ID)


@dp.message_handler(is_superuser=True, commands='restart')
async def restart(message: types.Message):
    def tread_stop(sec=1):
        import time
        time.sleep(sec)
        # noinspection PyProtectedMember
        # noinspection PyUnresolvedReferences
        os._exit(1)
    msg = f"Exited by superuser {message.from_user.id} command /restart"
    logger.warning(msg)
    import threading
    threading.Thread(target=tread_stop, args=()).start()


@dp.message_handler(is_superuser=True, commands='logchat')
async def get_logchat(message: types.Message):
    logger.info(f"Superuser {message.from_user.id} ask logchat link")
    try:
        log_ch = (await bot.get_chat(config.LOG_CHAT_ID)).invite_link
        await message.reply(log_ch, disable_notification=True)
    except TelegramAPIError as e:
        await message.reply(
            f"{e}\nУбедитесь что бот находится в логчате, "
            "ID логчата верно указан в конфиге, а так же что бот "
            "имеет право администратора на создание пригласительных ссылок. "
            "Так же попробуйте нажать /generate_invite_logchat для создания "
            "ссылки если ранее она не была создана"
        )


@dp.message_handler(is_superuser=True, commands='generate_invite_logchat')
async def generate_logchat_link(message: types.Message):
    logger.info(f"Superuser {message.from_user.id} ask new logchat link")
    try:
        await message.reply(await bot.export_chat_invite_link(config.LOG_CHAT_ID), disable_notification=True)
    except BadRequest as e:
        await message.reply(
            f"{e}\nУбедитесь что бот находится в логчате, "
            "ID логчата верно указан в конфиге, а так же что бот "
            "имеет право администратора на создание пригласительных ссылок"
        )


@dp.message_handler(is_superuser=True, commands='idchat')
async def get_idchat(message: types.Message):
    await message.reply(message.chat.id, disable_notification=True)


@dp.message_handler(is_superuser=True, commands=["exception"])
async def cmd_exception(_: types.Message):
    raise Exception('user press /exception')


@dp.message_handler(Text(equals="Кто красотка?", ignore_case=True), is_beauty=True)
@dp.message_handler(Text(equals="Кто красавчик?", ignore_case=True), is_superuser=True)
async def who_krasava(message):
    await message.reply("Ты конечно!", disable_notification=True)

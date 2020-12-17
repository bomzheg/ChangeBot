from aiogram import types
from loguru import logger
from app import config
from app.misc import dp, bot
from exeptions import CurChangeError


@dp.errors_handler()
async def errors_handler(update: types.Update, exception: Exception):
    exception_: Exception

    try:
        raise exception
    except Exception as e:
        type_e = e.__class__.__name__
        await bot.send_message(
            config.LOG_CHAT_ID,
            f"Получено исключение {type_e} {exception}\n"
            f"во время обработки апдейта {update}")
        logger.exception(
            "Cause exception {type_e} {e} in update {update}",
            type_e=type_e, e=exception, update=update
        )
    return True


async def notify_user_about_exception(e: CurChangeError):
    if e.chat_id is None:
        return await bot.send_message(e.user_id, e.notify_user)
    return await bot.send_message(e.chat_id, e.notify_user)

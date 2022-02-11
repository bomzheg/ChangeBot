from contextlib import suppress

from aiogram import Dispatcher
from aiogram.utils.exceptions import TelegramAPIError
from aiogram.utils.executor import Executor
from loguru import logger

from app import config
from app.misc import dp
from app.models import db
from app.services import healthcheck
from app.utils.send_text_file import send_log_files

runner = Executor(dp)


async def on_startup_webhook(dispatcher: Dispatcher):
    full_url_webhook = f"{config.WEBHOOK_URL_BASE}/{config.WEBHOOK_PATH_TOKEN}/"
    logger.info("Configure Web-Hook URL to: {url}", url=full_url_webhook)
    await dispatcher.bot.set_webhook(full_url_webhook)


async def on_startup_notify(dispatcher: Dispatcher):
    with suppress(TelegramAPIError):
        await dispatcher.bot.send_message(
            chat_id=config.LOG_CHAT_ID, text="Bot started", disable_notification=True
        )
        logger.info("Notified superuser {user} about bot is started.", user=config.ADMIN_ID)
    if config.send_logs:
        await send_log_files(config.LOG_CHAT_ID)


def setup():
    logger.info("Configure executor...")
    db.setup(runner)
    healthcheck.setup(runner)
    runner.on_startup(on_startup_webhook, webhook=True, polling=False)
    runner.on_startup(on_startup_notify)

import logging
import re

from aiogram import Dispatcher
from aiogram.dispatcher.filters.command import CommandStart
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, ContentType

from aiogram.utils.markdown import html_decoration as hd

from app import texts
from app.dao.holder import HolderDao
from app.models import dto
from app.services.chat import update_chat_id
from app.utils.exch_rates import ConvertedPrices, RatesOpenExchange

logger = logging.getLogger(__name__)


async def chat_id(message: Message):
    text = (
        f"id этого чата: {hd.pre(message.chat.id)}\n"
        f"Ваш id: {hd.pre(message.from_user.id)}"
    )
    if message.reply_to_message:
        text += (
            f"\nid {hd.bold(message.reply_to_message.from_user.full_name)}: "
            f"{hd.pre(message.reply_to_message.from_user.id)}"
        )
    await message.reply(text, disable_notification=True)


async def cancel_state(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logger.info('Cancelling state %s', current_state)
    # Cancel state and inform user about it
    await state.clear()
    # And remove keyboard (just in case)
    await message.reply('Диалог прекращён, данные удалены', reply_markup=ReplyKeyboardRemove())


async def chat_migrate(message: Message, chat: dto.Chat, dao: HolderDao):
    new_id = message.migrate_to_chat_id
    await update_chat_id(chat, new_id, dao.chat)
    logger.info(f"Migrate chat from %s to %s", message.chat.id, new_id)


async def cmd_start_deep_link(message: Message, oer: RatesOpenExchange):
    """
        deep linking распознают строки вида:
        https://t.me/curChangeBot?start=from-1200RUB_1500RUBto-EUR_USD
    """
    words = message.text.split()
    if len(words) <= 1:
        return await cmd_start(message)

    arg = words[1]
    if not arg.startswith('from-'):
        return await cmd_start(message)

    start_price = 5
    end_price = arg.find('to-')
    if not end_price:
        return await cmd_start(message)
    price = arg[start_price:end_price].split('_')
    vals_to = arg[end_price + 3:].split('_')

    line = ConvertedPrices(" ".join(price), rates=oer)
    convert_text = await line.get_only_equals_rates(vals_to)
    if convert_text != "":
        await message.reply(convert_text, disable_notification=True)
    else:
        return await cmd_start(message)


async def cmd_start(message: Message):
    await message.answer(texts.START_MSG)


async def cmd_help(message: Message):
    logger.info("User % read help in %", message.from_user.id, message.chat.id)
    await message.reply(texts.HELP_MSG)


async def cmd_about(message: Message):
    await message.reply(texts.ABOUT_MSG)


def setup_base(dp: Dispatcher):
    dp.message.register(cmd_start_deep_link, CommandStart(commands=re.compile(r'^from-[\d\w_]*to-[\w_]*')))
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_help, commands="help")
    dp.message.register(cmd_about, commands="about")
    dp.message.register(chat_id, commands=["idchat", "chat_id", "id"], commands_prefix="/!")
    dp.message.register(cancel_state, commands="cancel")
    dp.message.register(chat_migrate, content_types=ContentType.MIGRATE_TO_CHAT_ID)

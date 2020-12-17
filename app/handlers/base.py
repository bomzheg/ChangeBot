
import re
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandHelp, CommandStart
from loguru import logger

from app import config
from app.misc import dp, bot
from app.models.chat import Chat
from app.models.settings import Settings
from app.utils.exch_rates import ConvertedPrices


@dp.message_handler(CommandStart(re.compile(r'^from-[\d\w_]*to-[\w_]*')))
async def cmd_start_deep_link(message: types.Message, chat: Chat):
    """
        deep linking распознают строки вида:
        http://t.me/curChangeBot?start=from-1200RUB_1500RUBto-EUR_USD
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

    s, _ = await Settings.get_or_create(chat=chat)
    line = ConvertedPrices(" ".join(price), rates_source=s.get_src())
    convert_text = line.get_only_equals_rates(vals_to)
    if convert_text != "":
        await message.reply(convert_text, disable_notification=True)
    else:
        return await cmd_start(message)


@dp.message_handler(CommandStart())
async def cmd_start(message: types.Message):
    await bot.send_message(message.chat.id, config.START_MSG)


@dp.message_handler(CommandHelp())
async def cmd_help(message: types.Message):
    logger.info("User {user} read help in {chat}", user=message.from_user.id, chat=message.chat.id)
    await message.reply(config.HELP_MSG)


@dp.message_handler(commands=["about"])
async def cmd_about(message: types.Message):
    await message.reply(config.ABOUT_MSG)


@dp.message_handler(state='*', commands='cancel')
async def cancel_state(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logger.info(f'Cancelling state {current_state}')
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('messages.MSG_CANCEL', reply_markup=types.ReplyKeyboardRemove())

from datetime import date, timedelta

from aiogram import types
from aiogram.utils.markdown import quote_html
from loguru import logger
import json

from app import config
from app.misc import dp, bot
from app.services.apscheduller import scheduler
from app.utils.log import StreamToLogger

ANTON_GET_BACK = '2020-12-24'
PRIKAZ_DATE = '2020-09-27'
jokes = config.app_dir / "jokes.json"

_logger = StreamToLogger(logger)


def get_days_to_prikaz():
    date_prikaz = date.fromisoformat(PRIKAZ_DATE)
    td: timedelta = date_prikaz - date.today()
    return td.days


def get_days_anton_back():
    date_anton_back = date.fromisoformat(ANTON_GET_BACK)
    td: timedelta = date_anton_back - date.today()
    return td.days


def get_text_back_by_days(days: int):
    special_case = {
        0: "Антон вернётся сегодня!",
        1: "Антон вернётся уже завтра!",
        7: "Антон вернётся через неделю!",
        11: f"Антон вернётся через {days} дней. Барабанные палочки!",
        22: f"Антон вернётся через {days} дня. Снова лебеди, уииии!",
        30: "Антон вернётся через месяц!",
        91: f"Антон вернётся через {days} день. Иными словами осталась четверть службы!",
        100: f"Антон вернётся ровно через {days} дней!",
        111: f"Антон вернётся через {days} дней. Барабанные палочки трёхрукого человека!",
        122: "Антон вернётся через 122 дня. Осталась всего треть службы!",
        366 - 220: (f"Антон вернётся через {days} дней. "
                    "Кстати он отслужил уже 220 дней, т.е. празднует большую розетку"),
        366 - 200: f"Антон вернётся через {days} дней. Кстати он отслужил уже 200 дней!",
        183: "Антон вренётся через полгода! Экватор пройден!",
        200: f"Антон вернётся ровно через {days} дней!",
        220: f"Антон вернётся через {days} дней! Малая розетка, кстати!",
        222: f"Антон вернётся через {days} дней. Лебеди уииии",
    }
    text = special_case.get(
        days,
        f"До возвращения Антона осталось {days} д."
    )
    return text


def get_text_prikaz_by_days(days: int):
    if not 0 <= days <= 100:
        return ""
    text = "\n"
    special_case = {
        0: "А приказ выйдет сегодня!",
        1: "А приказ выйдет завтра!",
        7: "А приказ выйдет через неделю!",
        100: "Начинаем отсчёт дней до приказа, потому что до него осталось 100 дней!"
    }
    text += special_case.get(
        days,
        f"Кроме того, осталось {days} д. до приказа"
    )
    return text


async def send_date_anton():
    days_to_back = get_days_anton_back()
    if days_to_back < 0:
        logger.warning(f"Subzero count of days, remove this function. {days_to_back} days")
        return

    logger.info(f"Notification about Anton. {days_to_back} days")
    text = get_text_back_by_days(days_to_back)
    text += get_text_prikaz_by_days(get_days_to_prikaz())
    text += get_army_joke()
    await bot.send_message(config.KONI_CHAT_ID, text)


@dp.message_handler(is_superuser=True, commands='anton')
async def cmd_anton(message):
    scheduler.add_job(
        func=send_date_anton,
        trigger='cron',
        hour=8,
        end_date=ANTON_GET_BACK
    )
    logger.info("Schedule Anton")
    scheduler.print_jobs(out=_logger)
    await message.reply("Установлено ежедневное напоминание")


@dp.message_handler(is_superuser=True, commands='sendanton')
async def cmd_sendanton(_):
    await send_date_anton()


@dp.message_handler(is_superuser=True, commands='add_joke')
async def cmd_add_joke(message: types.Message):
    joke = message.get_args()
    if joke == "":
        return await message.answer("После команды надо ввести текст анекдота")
    if jokes.is_file():
        with jokes.open("r") as j_fp:
            joke_array: list = json.load(j_fp)
    else:
        joke_array = []
    joke_array.append(joke)
    with jokes.open("w") as j_fp:
        json.dump(joke_array, j_fp)
    return await message.answer(f"сохранена шутка\n{joke}")


@dp.message_handler(is_superuser=True, commands='get_jokes')
async def cmd_add_joke(message: types.Message):
    if jokes.is_file():
        with jokes.open("r") as j_fp:
            joke_array: list = json.load(j_fp)
            parts = [""]
            for joke in joke_array:
                if len(parts[-1]) + len(joke) < 4000:
                    parts[-1] += "\n\n" + joke
                else:
                    parts.append(joke)
            await message.answer(f"Сохранённые шутки:\n{parts[-1]}")
            for part in parts[1:]:
                await message.answer(part)
    else:
        return await message.answer(f"Шуток нет")


def get_army_joke():
    if not jokes.is_file():
        return ""
    with jokes.open("r") as j_fp:
        joke_array: list = json.load(j_fp)
    if len(joke_array) == 0:
        return ""
    joke = joke_array.pop(0)
    with jokes.open("w") as j_fp:
        json.dump(joke_array, j_fp)
    return "\n\n" + quote_html(joke)

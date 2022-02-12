import os
import secrets
from pathlib import Path

from dotenv import load_dotenv


app_dir: Path = Path(__file__).parent.parent
load_dotenv(app_dir / ".env")


PROG_NAME = "ChangeBot"
PROG_DESC = (
    "This programm is a Python 3+ script. "
    "The script launches a bot in Telegram, "
    "allowing you to convert the exchange rate"
)
PROG_EP = "© bomzheg, mrmidi. License WTFPL."
DESC_POLLING = "Run tg bot with polling. Default use WebHook"

BOT_TOKEN = os.getenv("BOT_TOKEN")

OPEN_EXCHANGE_RATES_API_KEY = os.getenv("OPEN_EXCHANGE_RATES_API_KEY")

DEBUG = True

ERR_LOG = "err.log"
PRINT_LOG = "print.log"
ADMIN_ID = 46866565
MIDI_ID = 1150695
DAWKINS_ID = 262934572
SUPERUSERS = {ADMIN_ID, MIDI_ID}
BEAUTY = {DAWKINS_ID}
LOG_CHAT_ID = -1001400331013
KONI_CHAT_ID = -1001306950892

WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT", 443)
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}"
WEBHOOK_PATH_TOKEN = secrets.token_urlsafe(32)
LISTEN_IP = os.getenv("LISTEN_IP", 'localhost')
LISTEN_PORT = os.getenv("LISTEN_PORT", 3000)

REDIS_DB = os.getenv("REDIS_DB")
REDIS_HOST = os.getenv("REDIS_HOST", 'localhost')
REDIS_PORT = os.getenv("LISTEN_PORT", 6379)

LOGIN_DB = os.getenv("LOGIN_DB")
PASSWORD_DB = os.getenv("PASSWORD_DB")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST", 'localhost')
DB_PORT = os.getenv("DB_PORT", 3306)
DB_TYPE = os.getenv("DB_TYPE", "mysql")

send_logs = True
std_err_catch = False

DEFAULT_VALS = ('USD', 'EUR', 'RUB')
DEFAULT_SRC = 'oer'


ABOUT_MSG = (
    "Разработчик бота - @bomzheg\n"
    "Канал о жизни бота - @aboutCurChangeBot\n"
    "Благодарности:\n"
    "mrmidi за хостинг бота на первых годах жизни, общую идею бота, "
    "попинывание на первых этапах разработки\n"
    "Kemarian за тестирование\n"
    "pblgblk за достаточное количество свободного времени"
)
START_MSG = (
    "Привет, я чат бот, я помогу сконвертировать значения цен "
    "из одних валют в другие.\n"
    "я умею работать в inline-режиме, "
    "или просто добавь меня в чат, я сам замечу, "
    "если в каком-то сообщении будут цены с указанием валют и сконвертирую их"
)
HELP_MSG = (
    'Подробное описание работы бота в канале @aboutCurChangeBot\n'
    'Для настройки в какие валюты конвертировать результат введите в чате '
    '"!val_to %СПИСОК ВАЛЮТ ЧЕРЕЗ ПРОБЕЛ%"' 
    'Например !val_to USD RUB EUR - даст команду боту конвертировать '
    'все цены в рубли доллары и евро.')

HOW_WORK_SIMPLE = (
    "Как работает обычный режим:\n"
    "Боту в личку или в просто в групповой чат с ботом можно писать что угодно. "
    "Если бот увидит что-то похожее на цену, "
    "т.е. число (можно с десятичной дробью) "
    "и знак или слово или словосочетание обозначающий валюту после числа, "
    "он следующим сообщением реплаем на сообщение содержащее цену "
    "отправит результат конвертации.\n"
    "Если цен в сообщении будет распознано несколько, "
    "то конвертация будет произведена для каждой."
)

HOW_WORK_VALS = (
    "Как бот распознаёт валюты:\n"
    "Бот для всех поддерживаемых валют гарантировано распознает трёхбуквенный код "
    "https://ru.wikipedia.org/wiki/ISO_4217 кроме того знак валюты, "
    "если существует уникальный знак. Например € - обозначает только евро, "
    "а вот ¥ означает как японскую иену, так и китайский юань, "
    "что разумеется не позволяет однозначно распознать, как конвертировать. "
    "В таких случаях приходится использовать неожиданные яп.¥ и кит.¥ "
    "что конечно не позволяет пользоваться удобно. Ещё хуже дела обстоят с кроной. "
    "Существует датская, норвежская, чешская и шведская кроны." 
    'Внимание, бот считает, что если в цене написано просто '
    '"ххх крон" то это чешская крона.\n'
    "В планах сделать настройку для каждого чата чтобы ¥ "
    "или словоформы кроны и др. - означали то, что нужно именно этому чату."
)

HOW_WORK_INLINE = (
    'Как работает inline-режим\n'
    'напишите в любом сообщении с самого начала сообщения " @ curChangeBot" '
    'и через пробел любую строку содержащую цены. '
    'как только бот найдёт хотя бы одну цену '
    'во всплывающих подсказках появится несколько вариантов конвертации строки.\n' 
    "Сейчас нет возможности настроить, "
    "в какую валюту конвертировать введённую в inline-режиме строку, "
    "есть всегда четыре варианта - в доллары, евро, рубли и в чешскую крону. "
    "В планах сделать соответствующую настройку"
)

GOOD_PRACTICE_GROUP = (
    'При использовании бота в обычном режиме, пожалуйста, не пытайтесь писать для бота.\n'
    'пишите сообщение, как если бы бота не было.' 
    'Плохое сообщение: "150 крон". '
    'Хорошее сообщение: "Сходили в кино, там сегодня скидки, заплатили всего 150 крон"\n'
    'Боту всё равно сколько лишнего в сообщении, но вашим собеседникам не всё равно, '
    'сколько сообщений читать, уважайте их.\n'
    'Если вам просто нужно быстро конвертировать, '
    'напишите боту в личные сообщения, не захламляйте групповые чаты!'
)

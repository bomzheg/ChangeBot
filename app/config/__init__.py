from .main import load_config


__all__ = [load_config]


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


send_logs = True
std_err_catch = True

DEFAULT_VALS = ('USD', 'EUR', 'RUB')
DEFAULT_SRC = 'oer'


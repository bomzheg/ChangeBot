from .main import load_config


PROG_NAME = "ChangeBot"
PROG_DESC = (
    "This program is a Python 3+ script. "
    "The script launches a bot in Telegram, "
    "allowing you to convert the exchange rate"
)
PROG_EP = "© bomzheg, mrmidi. License WTFPL."
DESC_POLLING = "Run tg bot with polling. Default use WebHook"

DEFAULT_VALS = ('USD', 'EUR', 'RUB')
DEFAULT_SRC = 'oer'


__all__ = ["load_config", "DEFAULT_SRC", "DEFAULT_VALS"]

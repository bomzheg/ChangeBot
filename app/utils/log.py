import logging
import pathlib
import sys
import warnings
from loguru import logger

from app.config import PRINT_LOG, ERR_LOG, app_dir, std_err_catch

# logging.basicConfig()

log_path = pathlib.Path(app_dir / 'log')
log_path.mkdir(parents=True, exist_ok=True)

showwarning_ = warnings.showwarning


def showwarning(message, *args, **kwargs):
    logger.warning(message)
    showwarning_(message, *args, **kwargs)


warnings.showwarning = showwarning


def setup():
    if std_err_catch:
        sys.stderr = open(log_path / ERR_LOG, 'a')  # noqa
    logger.add(
        sink=log_path / PRINT_LOG,
        format='{time} - {name} - {level} - {message}',
        level="DEBUG")
    logger.info("Program started")


async def log_msg(message):
    from app.utils.serialize_msg import serialize_message
    logger.debug(serialize_message(message))


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, in_logger):
        self.logger = in_logger
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.info(line.rstrip())

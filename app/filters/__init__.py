from aiogram import Dispatcher
from loguru import logger


def setup(dispatcher: Dispatcher):
    logger.info("Configure filters...")
    from .is_reply import IsReplyFilter
    from .superuser import IsSuperuserFilter, IsBeautyFilter

    text_messages = [
        dispatcher.message_handlers,
        dispatcher.edited_message_handlers,
        dispatcher.callback_query_handlers,
    ]

    dispatcher.filters_factory.bind(IsReplyFilter, event_handlers=text_messages)
    dispatcher.filters_factory.bind(IsSuperuserFilter, event_handlers=text_messages)
    dispatcher.filters_factory.bind(IsBeautyFilter, event_handlers=text_messages)

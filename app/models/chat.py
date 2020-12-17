import typing
from enum import Enum

from tortoise import fields
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model


class ChatType(str, Enum):
    private = "private"
    group = "group"
    supergroup = "supergroup"
    channel = 'channel'


class Chat(Model):
    chat_id = fields.BigIntField(pk=True, generated=False)
    type_: ChatType = typing.cast(ChatType, fields.CharEnumField(ChatType))
    title = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=32, null=True)
    description = fields.CharField(max_length=255, null=True)


    class Meta:
        table = "chats"

    @classmethod
    async def create_from_tg_chat(cls, chat_tg):
        chat = await cls.create(
            chat_id=chat_tg.id,
            type_=chat_tg.type,
            username=chat_tg.username
        )
        if chat_tg.title:
            chat.title=chat_tg.title
            await chat.save()
        return chat

    @classmethod
    async def get_or_create_from_tg_chat(cls, chat):
        try:
            chat = await cls.get(chat_id=chat.id)
        except DoesNotExist:
            chat = await cls.create_from_tg_chat(chat_tg=chat)
        return chat

    def __str__(self):
        rez = f"Chat with type: {self.type_} with ID {self.chat_id}, title: {self.title}"
        if self.username:
            rez += f" Username @{self.username}"
        if self.description:
            rez += f". description: {self.description}"
        return rez

    def __repr__(self):
        return str(self)

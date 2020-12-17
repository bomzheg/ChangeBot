from tortoise import fields
from tortoise.models import Model
from app.config import DEFAULT_SRC, DEFAULT_VALS


class Settings(Model):
    chat: fields.OneToOneRelation = fields.OneToOneField(
        'models.Chat', 
        related_name='settings', 
        pk=True, 
        source_field='chat_id'
    )
    _vals = fields.CharField(max_length=255, null=True, source_field='vals')
    _src = fields.CharField(max_length=20, null=True, source_field='src')

    class Meta:
        table = "settings"

    def __str__(self):
        rez = f"Settings object for {self.chat}"
        rez += f", vals_to: {self._vals}" if self._vals else ""
        rez += f", source: {self._src}" if self._src else ""
        rez += "."
        return rez

    def __repr__(self):
        return str(self)

    def get_vals(self) -> list:
        return list(self._vals.split()) if self._vals is not None else DEFAULT_VALS

    async def set_vals(self, vals: list):
        self._vals = " ".join(vals)
        await self.save()

    @classmethod
    async def get_vals_for_chat(cls, chat) -> list:
        rez = await cls.get_or_none(chat)
        return rez.get_vals()

    def get_src(self) -> str:
        return self._src if self._src is not None else DEFAULT_SRC

    async def set_src(self, src: str):
        self._src = src
        await self.save()

    @classmethod
    async def get_src_for_chat(cls, chat) -> str:
        rez = await cls.get_or_none(chat)
        return rez.get_src()

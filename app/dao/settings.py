from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import DEFAULT_VALS, DEFAULT_SRC
from app.dao import BaseDAO
from app.models import dto
from app.models.db import Settings


class SettingsDao(BaseDAO[Settings]):
    def __init__(self, session: AsyncSession):
        super(SettingsDao, self).__init__(Settings, session)

    async def get_by_chat(self, chat: dto.Chat) -> dto.Settings:
        return dto.Settings.from_db(await self._get_by_chat_id(chat.tg_id))

    async def update_settings(self, settings: dto.Settings):
        settings_db = await self._get_by_chat_id(settings.tg_id)
        was_changed = update_fields(settings, settings_db)
        if was_changed:
            self.save(settings_db)

    async def _get_by_chat_id(self, chat_tg_id: int) -> Settings:
        try:
            result = await self.session.execute(
                select(Settings).where(Settings.chat_id == chat_tg_id)
            )
            return result.scalar_one()
        except NoResultFound:
            settings = Settings(
                chat_id=chat_tg_id,
                vals=DEFAULT_VALS,
                src=DEFAULT_SRC,
            )
            self.save(settings)
            await self.flush(settings)
            return settings


def update_fields(source: dto.Settings, target: Settings) -> bool:
    if all([
        target.vals == source.db_vals,
        target.src == source.src,
    ]):
        return False
    target.vals = source.db_vals
    target.src = source.src
    return True

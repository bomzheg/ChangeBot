from app.dao.settings import SettingsDao
from app.models import dto


async def load_settings(chat: dto.Chat, dao: SettingsDao) -> dto.Settings:
    return await dao.get_by_chat(chat)


async def update_settings(settings: dto.Settings, dao: SettingsDao):
    await dao.update_settings(settings)
    await dao.commit()

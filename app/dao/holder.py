from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.dao import UserDao, ChatDao
from app.dao.settings import SettingsDao


@dataclass
class HolderDao:
    session: AsyncSession
    user: UserDao = field(init=False)
    chat: ChatDao = field(init=False)
    settings: SettingsDao = field(init=False)

    def __post_init__(self):
        self.user = UserDao(self.session)
        self.chat = ChatDao(self.session)
        self.settings = SettingsDao(self.session)

    async def commit(self):
        await self.session.commit()

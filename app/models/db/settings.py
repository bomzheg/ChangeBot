from sqlalchemy import Column, Text, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from app.config import DEFAULT_VALS, DEFAULT_SRC
from app.models.db.base import Base


class Settings(Base):
    __tablename__ = "settings"
    __mapper_args__ = {"eager_defaults": True}
    chat_id = Column(BigInteger, ForeignKey("chats.tg_id"), primary_key=True, autoincrement=False)
    """telegram chat id. 
        it is legacy relation key for db backward compatibility"""
    vals = Column(Text)
    src = Column(Text)
    chat = relationship("Chat", back_populates="settings")

    def get_vals(self) -> list[str]:
        return list(self.vals.split()) if self.vals is not None else DEFAULT_VALS

    def set_vals(self, vals: list[str]):
        self.vals = " ".join(vals)

    def get_src(self) -> str:
        return self.src or DEFAULT_SRC

    def set_src(self, src: str):
        self.src = src

    def __repr__(self):
        return (
            f"<Settings "
            f"chat_id={self.chat_id} "
            f"vals={self.vals} "
            f"src={self.src}"
            f" >"
        )


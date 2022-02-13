from __future__ import annotations
from dataclasses import dataclass

from app.models import db
from app.services.rates import RatesSource


@dataclass
class Settings:
    tg_id: int
    vals: list[str]
    _src: str

    @property
    def src(self):
        return self._src

    @src.setter
    def src(self, src_: str):
        self._src = src_

    @property
    def source(self):
        return RatesSource[self.src]

    @property
    def db_vals(self):
        return " ".join(self.vals)

    @classmethod
    def from_db(cls, settings: db.Settings) -> Settings:
        return cls(
            tg_id=settings.chat_id,
            vals=settings.get_vals(),
            _src=settings.get_src(),
        )

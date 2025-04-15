import datetime
import uuid

from advanced_alchemy.types import DateTimeUTC
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.persistence.models.base import BaseORM
from backend.infrastructure.persistence.models.film import FilmORM
from backend.infrastructure.persistence.models.mix import MixORM


class MixItemORM(BaseORM):
    __tablename__ = "mix_item"

    mix_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(MixORM.id), primary_key=True)
    film_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(FilmORM.id), primary_key=True)
    added_at: Mapped[datetime.datetime] = mapped_column(DateTimeUTC)

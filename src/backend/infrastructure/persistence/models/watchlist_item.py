import datetime
import uuid

from advanced_alchemy.types import DateTimeUTC
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.persistence.models.base import BaseORM
from backend.infrastructure.persistence.models.film import FilmORM
from backend.infrastructure.persistence.models.watchlist import WatchlistORM


class WatchlistItemORM(BaseORM):
    __tablename__ = "watchlist_item"

    watchlist_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(WatchlistORM.id), primary_key=True)
    film_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(FilmORM.id), primary_key=True)
    added_at: Mapped[datetime.datetime] = mapped_column(DateTimeUTC)

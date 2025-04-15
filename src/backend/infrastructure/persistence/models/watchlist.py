import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.domain.watchlist_type import WatchlistType
from backend.infrastructure.persistence.models.base import BaseORM
from backend.infrastructure.persistence.models.user import UserORM


class WatchlistORM(BaseORM):
    __tablename__ = "watchlist"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(UserORM.id))
    title: Mapped[str]
    type: Mapped[WatchlistType]
    color1: Mapped[str]
    color2: Mapped[str]
    color3: Mapped[str]

import datetime
import uuid

from advanced_alchemy.types import DateTimeUTC
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.persistence.models.base import BaseORM
from backend.infrastructure.persistence.models.film import FilmORM
from backend.infrastructure.persistence.models.user import UserORM


class RecommendedFilmORM(BaseORM):
    __tablename__ = "recommended_film"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(UserORM.id))
    film_id: Mapped[uuid.UUID] = mapped_column(ForeignKey(FilmORM.id))
    recommended_at: Mapped[datetime.datetime] = mapped_column(DateTimeUTC)

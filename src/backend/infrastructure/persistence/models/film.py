import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.persistence.models.base import BaseORM
from backend.infrastructure.persistence.models.user import UserORM


class FilmORM(BaseORM):
    __tablename__ = "film"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)

    title: Mapped[str]
    description: Mapped[str | None]
    country: Mapped[str | None]
    release_year: Mapped[int | None]
    poster_url: Mapped[str | None]

    tmdb_id: Mapped[int | None]

    owner_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey(UserORM.id))

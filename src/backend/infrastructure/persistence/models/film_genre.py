import uuid

from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.persistence.models.base import BaseORM


class FilmGenre(BaseORM):
    __tablename__ = "film_genre"

    film_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    genre_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)

import uuid

from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.persistence.models.base import BaseORM


class GenreMoodORM(BaseORM):
    __tablename__ = "genre_mood"

    genre_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    mood_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)

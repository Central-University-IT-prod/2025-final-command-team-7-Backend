import uuid

from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.persistence.models.base import BaseORM


class GenreORM(BaseORM):
    __tablename__ = "genre"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str]

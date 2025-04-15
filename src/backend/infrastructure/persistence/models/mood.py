import uuid

from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.persistence.models.base import BaseORM


class MoodORM(BaseORM):
    __tablename__ = "mood"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str]

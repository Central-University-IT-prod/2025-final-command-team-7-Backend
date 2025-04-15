import uuid

from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.persistence.models.base import BaseORM


class MixORM(BaseORM):
    __tablename__ = "mix"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    title: Mapped[str]
    color1: Mapped[str]
    color2: Mapped[str]
    color3: Mapped[str]

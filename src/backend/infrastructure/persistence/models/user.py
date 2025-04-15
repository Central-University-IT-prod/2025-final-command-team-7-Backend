import uuid

from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.persistence.models.base import BaseORM


class UserORM(BaseORM):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    username: Mapped[str]
    email: Mapped[str | None] = mapped_column(unique=True)
    hashed_password: Mapped[str | None]
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True)

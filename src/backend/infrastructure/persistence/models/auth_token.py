import datetime
import uuid

from advanced_alchemy.types import DateTimeUTC
from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from backend.infrastructure.persistence.models.base import BaseORM
from backend.infrastructure.persistence.models.user import UserORM


class AuthTokenORM(BaseORM):
    __tablename__ = "auth_token"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(unique=True, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey(UserORM.id), nullable=True)
    activated: Mapped[bool] = mapped_column(Boolean, default=False)
    declined: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTimeUTC)

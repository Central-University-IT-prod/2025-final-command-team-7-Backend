import dataclasses

from backend.domain.user_id import UserId


@dataclasses.dataclass
class User:
    id: UserId
    email: str | None
    hashed_password: str | None
    telegram_id: int | None
    username: str

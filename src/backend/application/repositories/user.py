import typing

from backend.domain.user import User
from backend.domain.user_id import UserId


class UserRepository(typing.Protocol):
    async def create(self, user: User) -> User:
        raise NotImplementedError

    async def get_by_id(self, user_id: UserId) -> User:
        raise NotImplementedError

    async def get_by_email(self, email: str) -> User:
        raise NotImplementedError

    async def update(self, user: User) -> User:
        raise NotImplementedError

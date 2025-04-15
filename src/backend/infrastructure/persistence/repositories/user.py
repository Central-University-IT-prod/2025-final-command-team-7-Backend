from advanced_alchemy.exceptions import NotFoundError
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import UserNotFoundError
from backend.application.repositories.user import UserRepository
from backend.domain.user import User
from backend.domain.user_id import UserId
from backend.infrastructure.persistence.mappers.user import orm_to_user, user_to_orm
from backend.infrastructure.persistence.models.user import UserORM


class _Repository(SQLAlchemyAsyncRepository[UserORM]):
    model_type = UserORM


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = _Repository(session=session)

    async def create(self, user: User) -> User:
        orm_user = user_to_orm(user)
        orm_user = await self._repo.add(orm_user)
        return orm_to_user(orm_user)

    async def get_by_id(self, user_id: UserId) -> User:
        try:
            user = await self._repo.get(user_id)
        except NotFoundError as exc:
            raise UserNotFoundError from exc
        return orm_to_user(user)

    async def get_by_email(self, email: str) -> User:
        try:
            user = await self._repo.get_one(email=email)
        except NotFoundError as exc:
            raise UserNotFoundError from exc
        return orm_to_user(user)

    async def update(self, user: User) -> User:
        orm_user = user_to_orm(user)
        try:
            orm_user = await self._repo.update(orm_user)
        except NotFoundError as exc:
            raise UserNotFoundError from exc
        return orm_to_user(orm_user)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import AuthTokenNotFoundError, UserNotFoundError
from backend.application.repositories.auth_token import AuthTokenRepository
from backend.application.repositories.user import UserRepository
from backend.domain.auth_token import AuthToken
from backend.domain.auth_token_id import AuthTokenId
from backend.domain.user import User
from backend.domain.user_id import UserId


class BotAuthTokenRepository(AuthTokenRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, auth_token: AuthToken) -> AuthToken:
        from backend.infrastructure.persistence.mappers.auth_token import auth_token_to_orm, orm_to_auth_token

        orm_auth_token = auth_token_to_orm(auth_token)
        self._session.add(orm_auth_token)
        await self._session.flush()
        return orm_to_auth_token(orm_auth_token)

    async def get_by_id(self, auth_token_id: AuthTokenId) -> AuthToken:
        from backend.infrastructure.persistence.mappers.auth_token import orm_to_auth_token
        from backend.infrastructure.persistence.models.auth_token import AuthTokenORM

        stmt = select(AuthTokenORM).where(AuthTokenORM.id == auth_token_id)
        result = await self._session.execute(stmt)
        orm_auth_token = result.scalars().first()

        if not orm_auth_token:
            raise AuthTokenNotFoundError(f"Auth token with id {auth_token_id} not found")

        return orm_to_auth_token(orm_auth_token)

    async def get_by_token(self, token: str) -> AuthToken:
        from backend.infrastructure.persistence.mappers.auth_token import orm_to_auth_token
        from backend.infrastructure.persistence.models.auth_token import AuthTokenORM

        stmt = select(AuthTokenORM).where(AuthTokenORM.token == token)
        result = await self._session.execute(stmt)
        orm_auth_token = result.scalars().first()

        if not orm_auth_token:
            raise AuthTokenNotFoundError(f"Auth token '{token}' not found")

        return orm_to_auth_token(orm_auth_token)

    async def update(self, auth_token: AuthToken) -> AuthToken:
        from backend.infrastructure.persistence.mappers.auth_token import auth_token_to_orm, orm_to_auth_token
        from backend.infrastructure.persistence.models.auth_token import AuthTokenORM

        stmt = select(AuthTokenORM).where(AuthTokenORM.id == auth_token.id)
        result = await self._session.execute(stmt)
        orm_auth_token = result.scalars().first()

        if not orm_auth_token:
            raise AuthTokenNotFoundError(f"Auth token with id {auth_token.id} not found")

        for key, value in auth_token_to_orm(auth_token).__dict__.items():
            if not key.startswith("_") and hasattr(orm_auth_token, key):
                setattr(orm_auth_token, key, value)

        await self._session.flush()
        return orm_to_auth_token(orm_auth_token)

    async def activate_token(self, token: str, user_id: UserId) -> AuthToken:
        try:
            auth_token = await self.get_by_token(token)
            if not auth_token.activated and not auth_token.declined:
                auth_token.user_id = user_id
                auth_token.activated = True
                return await self.update(auth_token)
            return auth_token
        except AuthTokenNotFoundError as exc:
            raise AuthTokenNotFoundError(f"Auth token '{token}' not found") from exc

    async def decline_token(self, token: str) -> AuthToken:
        try:
            auth_token = await self.get_by_token(token)
            if not auth_token.activated and not auth_token.declined:
                auth_token.declined = True
                return await self.update(auth_token)
            return auth_token
        except AuthTokenNotFoundError as exc:
            raise AuthTokenNotFoundError(f"Auth token '{token}' not found") from exc


class BotUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, user: User) -> User:
        from backend.infrastructure.persistence.mappers.user import orm_to_user, user_to_orm

        orm_user = user_to_orm(user)
        self._session.add(orm_user)
        await self._session.flush()
        return orm_to_user(orm_user)

    async def get_by_id(self, user_id: UserId) -> User:
        from backend.infrastructure.persistence.mappers.user import orm_to_user
        from backend.infrastructure.persistence.models.user import UserORM

        stmt = select(UserORM).where(UserORM.id == user_id)
        result = await self._session.execute(stmt)
        orm_user = result.scalars().first()

        if not orm_user:
            raise UserNotFoundError(f"User with id {user_id} not found")

        return orm_to_user(orm_user)

    async def get_by_email(self, email: str) -> User:
        from backend.infrastructure.persistence.mappers.user import orm_to_user
        from backend.infrastructure.persistence.models.user import UserORM

        stmt = select(UserORM).where(UserORM.email == email)
        result = await self._session.execute(stmt)
        orm_user = result.scalars().first()

        if not orm_user:
            raise UserNotFoundError(f"User with email {email} not found")

        return orm_to_user(orm_user)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        from backend.infrastructure.persistence.mappers.user import orm_to_user
        from backend.infrastructure.persistence.models.user import UserORM

        stmt = select(UserORM).where(UserORM.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        orm_user = result.scalars().first()

        if not orm_user:
            return None

        return orm_to_user(orm_user)

    async def update(self, user: User) -> User:
        from backend.infrastructure.persistence.mappers.user import orm_to_user, user_to_orm
        from backend.infrastructure.persistence.models.user import UserORM

        stmt = select(UserORM).where(UserORM.id == user.id)
        result = await self._session.execute(stmt)
        orm_user = result.scalars().first()

        if not orm_user:
            raise UserNotFoundError(f"User with id {user.id} not found")

        for key, value in user_to_orm(user).__dict__.items():
            if not key.startswith("_") and hasattr(orm_user, key):
                setattr(orm_user, key, value)

        await self._session.flush()
        return orm_to_user(orm_user)


class BotCommitter:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

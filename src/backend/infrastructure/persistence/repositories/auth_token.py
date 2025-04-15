from advanced_alchemy.exceptions import NotFoundError
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import AuthTokenNotFoundError
from backend.application.repositories.auth_token import AuthTokenRepository
from backend.domain.auth_token import AuthToken
from backend.domain.auth_token_id import AuthTokenId
from backend.domain.user_id import UserId
from backend.infrastructure.persistence.mappers.auth_token import auth_token_to_orm, orm_to_auth_token
from backend.infrastructure.persistence.models.auth_token import AuthTokenORM


class _Repository(SQLAlchemyAsyncRepository[AuthTokenORM]):
    model_type = AuthTokenORM


class SQLAlchemyAuthTokenRepository(AuthTokenRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = _Repository(session=session)

    async def create(self, auth_token: AuthToken) -> AuthToken:
        orm_auth_token = auth_token_to_orm(auth_token)
        orm_auth_token = await self._repo.add(orm_auth_token)
        return orm_to_auth_token(orm_auth_token)

    async def get_by_id(self, auth_token_id: AuthTokenId) -> AuthToken:
        try:
            orm_auth_token = await self._repo.get(auth_token_id)
        except NotFoundError as exc:
            raise AuthTokenNotFoundError from exc
        return orm_to_auth_token(orm_auth_token)

    async def get_by_token(self, token: str) -> AuthToken:
        try:
            orm_auth_token = await self._repo.get_one(token=token)
        except NotFoundError as exc:
            raise AuthTokenNotFoundError from exc
        return orm_to_auth_token(orm_auth_token)

    async def update(self, auth_token: AuthToken) -> AuthToken:
        orm_auth_token = auth_token_to_orm(auth_token)
        try:
            orm_auth_token = await self._repo.update(orm_auth_token)
        except NotFoundError as exc:
            raise AuthTokenNotFoundError from exc
        return orm_to_auth_token(orm_auth_token)

    async def activate_token(self, token: str, user_id: UserId) -> AuthToken:
        try:
            auth_token = await self.get_by_token(token)
            if not auth_token.activated and not auth_token.declined:
                auth_token.user_id = user_id
                auth_token.activated = True
                return await self.update(auth_token)
            return auth_token
        except NotFoundError as exc:
            raise AuthTokenNotFoundError from exc

    async def decline_token(self, token: str) -> AuthToken:
        try:
            auth_token = await self.get_by_token(token)
            if not auth_token.activated and not auth_token.declined:
                auth_token.declined = True
                return await self.update(auth_token)
            return auth_token
        except NotFoundError as exc:
            raise AuthTokenNotFoundError from exc

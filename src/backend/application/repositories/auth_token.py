import typing

from backend.domain.auth_token import AuthToken
from backend.domain.auth_token_id import AuthTokenId
from backend.domain.user_id import UserId


class AuthTokenRepository(typing.Protocol):
    async def create(self, auth_token: AuthToken) -> AuthToken:
        raise NotImplementedError

    async def get_by_id(self, auth_token_id: AuthTokenId) -> AuthToken:
        raise NotImplementedError

    async def get_by_token(self, token: str) -> AuthToken:
        raise NotImplementedError

    async def update(self, auth_token: AuthToken) -> AuthToken:
        raise NotImplementedError

    async def activate_token(self, token: str, user_id: UserId) -> AuthToken:
        raise NotImplementedError

    async def decline_token(self, token: str) -> AuthToken:
        raise NotImplementedError

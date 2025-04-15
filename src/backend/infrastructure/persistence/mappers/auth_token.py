from backend.domain.auth_token import AuthToken
from backend.domain.auth_token_id import AuthTokenId
from backend.domain.user_id import UserId
from backend.infrastructure.persistence.models.auth_token import AuthTokenORM


def orm_to_auth_token(orm_auth_token: AuthTokenORM) -> AuthToken:
    return AuthToken(
        id=AuthTokenId(orm_auth_token.id),
        token=orm_auth_token.token,
        user_id=UserId(orm_auth_token.user_id) if orm_auth_token.user_id is not None else None,
        activated=orm_auth_token.activated,
        declined=orm_auth_token.declined,
        created_at=orm_auth_token.created_at,
    )


def auth_token_to_orm(auth_token: AuthToken) -> AuthTokenORM:
    return AuthTokenORM(
        id=auth_token.id,
        token=auth_token.token,
        user_id=auth_token.user_id,
        activated=auth_token.activated,
        declined=auth_token.declined,
        created_at=auth_token.created_at,
    )

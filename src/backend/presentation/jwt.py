import datetime
import os
import typing
import uuid

from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.security.jwt import JWTAuth, Token

from backend.application.errors import UserNotFoundError
from backend.application.repositories.user import UserRepository
from backend.domain.user import User
from backend.domain.user_id import UserId

if typing.TYPE_CHECKING:
    import dishka


async def retrieve_user_handler(token: Token, connection: ASGIConnection) -> User:
    user_id = UserId(uuid.UUID(token.sub))

    container: dishka.AsyncContainer = connection.state.dishka_container
    user_repo = await container.get(UserRepository)

    try:
        return await user_repo.get_by_id(user_id)
    except UserNotFoundError as exc:
        raise NotAuthorizedException("User not found") from exc


jwt_auth = JWTAuth[User](
    token_secret=os.environ["JWT_SECRET"],
    retrieve_user_handler=retrieve_user_handler,
    default_token_expiration=datetime.timedelta(days=31),
    exclude=["/api/schema"],
)

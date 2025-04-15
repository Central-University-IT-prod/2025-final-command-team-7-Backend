import datetime
import secrets
import uuid

from dishka.integrations.litestar import FromDishka, inject
from litestar import Controller, Response, post, status_codes
from litestar.exceptions import NotAuthorizedException

from backend.application.committer import Committer
from backend.application.errors import AuthTokenNotFoundError
from backend.application.repositories.auth_token import AuthTokenRepository
from backend.application.repositories.user import UserRepository
from backend.application.repositories.watchlist import WatchlistRepository
from backend.domain.auth_token import AuthToken
from backend.domain.auth_token_id import AuthTokenId
from backend.presentation import schemas
from backend.presentation.jwt import jwt_auth


class TelegramAuthController(Controller):
    path = "/auth/telegram"
    tags = ("auth",)

    @post("/get_auth_key", exclude_from_auth=True)
    @inject
    async def get_auth_key(
        self, auth_token_repo: FromDishka[AuthTokenRepository], committer: FromDishka[Committer]
    ) -> schemas.AuthKeyInfo:
        auth_token = AuthToken(
            id=AuthTokenId(uuid.uuid4()),
            token=secrets.token_urlsafe(25),
            user_id=None,
            activated=False,
            declined=False,
            created_at=datetime.datetime.now(datetime.UTC),
        )

        await auth_token_repo.create(auth_token)
        await committer.commit()

        return schemas.AuthKeyInfo(auth_key=auth_token.token)

    @post("/check_auth_key", exclude_from_auth=True)
    @inject
    async def check_auth_key(
        self,
        data: schemas.TelegramLoginRequest,
        auth_token_repo: FromDishka[AuthTokenRepository],
        watchlist_repo: FromDishka[WatchlistRepository],
    ) -> Response:
        try:
            token = await auth_token_repo.get_by_token(token=data.tg_code)

            if token.declined:
                return Response(
                    status_code=status_codes.HTTP_400_BAD_REQUEST,
                    content={"error": "incorrect_auth_key"},
                    media_type="application/json",
                )

            await watchlist_repo.create_common_watchlist_for_user(token.user_id)

            return Response(
                content=schemas.AuthKeyIsConfirmed(is_confirmed=token.activated and token.user_id is not None),
                status_code=status_codes.HTTP_200_OK,
                media_type="application/json",
            )

        except AuthTokenNotFoundError:
            return Response(
                status_code=status_codes.HTTP_400_BAD_REQUEST,
                content={"error": "incorrect_auth_key"},
                media_type="application/json",
            )

    @post("/login", exclude_from_auth=True)
    @inject
    async def login_with_telegram(
        self,
        data: schemas.TelegramLoginRequest,
        auth_token_repo: FromDishka[AuthTokenRepository],
        user_repo: FromDishka[UserRepository],
        committer: FromDishka[Committer],
    ) -> schemas.UserLoginResponse:
        try:
            token = await auth_token_repo.get_by_token(token=data.tg_code)

            if not token.activated or token.declined or token.user_id is None:
                raise NotAuthorizedException("Invalid or inactive authentication token")

            user = await user_repo.get_by_id(token.user_id)
            jwt_token = jwt_auth.create_token(identifier=str(user.id))

            return schemas.UserLoginResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                telegram_id=user.telegram_id,
                token=jwt_token,
            )

        except (AuthTokenNotFoundError, NotAuthorizedException) as exc:
            raise NotAuthorizedException("Invalid authentication token") from exc

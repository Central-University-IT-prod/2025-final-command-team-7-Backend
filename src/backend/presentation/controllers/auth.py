import uuid

from dishka import FromDishka
from dishka.integrations.litestar import inject
from litestar import Controller, post, status_codes
from litestar.dto import DataclassDTO, DTOConfig
from litestar.exceptions import HTTPException, NotAuthorizedException
from litestar.openapi.datastructures import ResponseSpec

from backend.application.committer import Committer
from backend.application.errors import UserNotFoundError
from backend.application.password_hasher import PasswordHasher
from backend.application.repositories.user import UserRepository
from backend.application.repositories.watchlist import WatchlistRepository
from backend.domain.user import User
from backend.domain.user_id import UserId
from backend.presentation import schemas
from backend.presentation.jwt import jwt_auth


class UserRead(DataclassDTO[User]):
    config = DTOConfig(
        exclude={
            "hashed_password",
        },
    )


class AuthController(Controller):
    path = "/auth"
    tags = ("auth",)

    @post(
        "/register",
        responses={status_codes.HTTP_409_CONFLICT: ResponseSpec(data_container=None)},
        exclude_from_auth=True,
        return_dto=UserRead,
    )
    @inject
    async def register(
        self,
        data: schemas.UserRegister,
        user_repo: FromDishka[UserRepository],
        watchlist_repo: FromDishka[WatchlistRepository],
        password_hasher: FromDishka[PasswordHasher],
        committer: FromDishka[Committer],
    ) -> User:
        hashed_password = await password_hasher.hash_password(data.password)
        try:
            user = await user_repo.get_by_email(data.email)
        except UserNotFoundError:
            user = User(
                id=UserId(uuid.uuid4()),
                email=data.email,
                hashed_password=hashed_password,
                telegram_id=None,
                username=data.username,
            )
            user = await user_repo.create(user)
            await watchlist_repo.create_common_watchlist_for_user(user.id)
            await committer.commit()
            return user
        else:
            raise HTTPException(
                status_code=status_codes.HTTP_409_CONFLICT, detail="User with this email already exists"
            )

    @post("/login", raises=(NotAuthorizedException,), exclude_from_auth=True)
    @inject
    async def login(
        self,
        data: schemas.UserLogin,
        user_repo: FromDishka[UserRepository],
        password_hasher: FromDishka[PasswordHasher],
    ) -> schemas.UserLoginResponse:
        try:
            user = await user_repo.get_by_email(data.email)
        except UserNotFoundError as exc:
            raise NotAuthorizedException(detail="Invalid login data") from exc

        if user.hashed_password is None:
            raise NotAuthorizedException(detail="User doesn't support auth by password")

        is_password_valid = await password_hasher.check_password(
            password=data.password, hashed_password=user.hashed_password
        )
        if is_password_valid is False:
            raise NotAuthorizedException(detail="Invalid password")

        token = jwt_auth.create_token(identifier=str(user.id))

        return schemas.UserLoginResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            telegram_id=user.telegram_id,
            token=token,
        )

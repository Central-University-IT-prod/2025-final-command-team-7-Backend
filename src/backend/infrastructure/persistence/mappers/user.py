from backend.domain.user import User
from backend.domain.user_id import UserId
from backend.infrastructure.persistence.models.user import UserORM


def orm_to_user(orm_user: UserORM) -> User:
    return User(
        id=UserId(orm_user.id),
        email=orm_user.email,
        hashed_password=orm_user.hashed_password,
        telegram_id=orm_user.telegram_id,
        username=orm_user.username,
    )


def user_to_orm(user: User) -> UserORM:
    return UserORM(
        id=user.id,
        email=user.email,
        hashed_password=user.hashed_password,
        telegram_id=user.telegram_id,
        username=user.username,
    )

import uuid

import pytest

from backend.domain.user import User
from backend.domain.user_id import UserId
from backend.infrastructure.persistence.mappers.user import orm_to_user, user_to_orm
from backend.infrastructure.persistence.models.user import UserORM


class TestUserMappers:
    def test_user_to_orm(self):
        
        user_id = UserId(uuid.uuid4())
        user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword123",
            telegram_id=None
        )

        
        orm_user = user_to_orm(user)

        
        assert isinstance(orm_user, UserORM)
        assert orm_user.id == user_id
        assert orm_user.username == "testuser"
        assert orm_user.email == "test@example.com"
        assert orm_user.hashed_password == "hashedpassword123"
        assert orm_user.telegram_id is None

    def test_orm_to_user(self):
        
        user_id = uuid.uuid4()
        orm_user = UserORM(
            id=user_id,
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword123",
            telegram_id=None
        )

        
        user = orm_to_user(orm_user)

        
        assert isinstance(user, User)
        assert user.id == UserId(user_id)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashedpassword123"
        assert user.telegram_id is None

    def test_user_to_orm_with_telegram_id(self):
        
        user_id = UserId(uuid.uuid4())
        user = User(
            id=user_id,
            username="telegram_user",
            email=None,
            hashed_password=None,
            telegram_id=12345
        )

        
        orm_user = user_to_orm(user)

        
        assert isinstance(orm_user, UserORM)
        assert orm_user.id == user_id
        assert orm_user.username == "telegram_user"
        assert orm_user.email is None
        assert orm_user.hashed_password is None
        assert orm_user.telegram_id == 12345

    def test_orm_to_user_with_telegram_id(self):
        
        user_id = uuid.uuid4()
        orm_user = UserORM(
            id=user_id,
            username="telegram_user",
            email=None,
            hashed_password=None,
            telegram_id=12345
        )

        
        user = orm_to_user(orm_user)

        
        assert isinstance(user, User)
        assert user.id == UserId(user_id)
        assert user.username == "telegram_user"
        assert user.email is None
        assert user.hashed_password is None
        assert user.telegram_id == 12345
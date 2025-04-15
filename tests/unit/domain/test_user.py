import uuid

import pytest

from backend.domain.user import User
from backend.domain.user_id import UserId


class TestUser:
    def test_create_user(self):
        
        user_id = UserId(uuid.uuid4())

        
        user = User(
            id=user_id,
            username="testuser",
            email="test@example.com",
            hashed_password="hashedpassword123",
            telegram_id=None
        )

        
        assert user.id == user_id
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.hashed_password == "hashedpassword123"
        assert user.telegram_id is None

    def test_create_user_with_telegram_id(self):
        
        user_id = UserId(uuid.uuid4())

        
        user = User(
            id=user_id,
            username="telegram_user",
            email=None,
            hashed_password=None,
            telegram_id=123456789
        )

        
        assert user.id == user_id
        assert user.username == "telegram_user"
        assert user.email is None
        assert user.hashed_password is None
        assert user.telegram_id == 123456789
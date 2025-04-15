import datetime
import uuid

import pytest

from backend.domain.auth_token import AuthToken
from backend.domain.auth_token_id import AuthTokenId
from backend.domain.user_id import UserId


class TestAuthToken:
    def test_create_auth_token(self):
        
        auth_token_id = AuthTokenId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())
        created_at = datetime.datetime.now(datetime.UTC)

        
        auth_token = AuthToken(
            id=auth_token_id,
            token="token123",
            user_id=user_id,
            activated=True,
            declined=False,
            created_at=created_at
        )

        
        assert auth_token.id == auth_token_id
        assert auth_token.token == "token123"
        assert auth_token.user_id == user_id
        assert auth_token.activated is True
        assert auth_token.declined is False
        assert auth_token.created_at == created_at

    def test_create_auth_token_without_user(self):
        
        auth_token_id = AuthTokenId(uuid.uuid4())
        created_at = datetime.datetime.now(datetime.UTC)

        
        auth_token = AuthToken(
            id=auth_token_id,
            token="token123",
            user_id=None,
            activated=False,
            declined=False,
            created_at=created_at
        )

        
        assert auth_token.id == auth_token_id
        assert auth_token.token == "token123"
        assert auth_token.user_id is None
        assert auth_token.activated is False
        assert auth_token.declined is False
        assert auth_token.created_at == created_at
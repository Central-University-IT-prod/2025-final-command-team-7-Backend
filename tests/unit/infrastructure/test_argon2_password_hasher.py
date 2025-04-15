import pytest

from backend.infrastructure.argon2_password_hasher import Argon2PasswordHasher


class TestArgon2PasswordHasher:
    @pytest.mark.asyncio
    async def test_hash_password(self):
        
        password = "test_password"
        hasher = Argon2PasswordHasher()

        
        hashed_password = await hasher.hash_password(password)

        
        assert hashed_password.startswith("$argon2")
        assert hashed_password != password

    @pytest.mark.asyncio
    async def test_check_password_valid(self):
        
        password = "test_password"
        hasher = Argon2PasswordHasher()
        hashed_password = await hasher.hash_password(password)

        
        is_valid = await hasher.check_password(password=password, hashed_password=hashed_password)

        
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_check_password_invalid(self):
        
        password = "test_password"
        wrong_password = "wrong_password"
        hasher = Argon2PasswordHasher()
        hashed_password = await hasher.hash_password(password)

        
        is_valid = await hasher.check_password(password=wrong_password, hashed_password=hashed_password)

        
        assert is_valid is False
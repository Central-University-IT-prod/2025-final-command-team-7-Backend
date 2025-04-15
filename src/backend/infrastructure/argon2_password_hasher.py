import argon2

from backend.application.password_hasher import PasswordHasher


class Argon2PasswordHasher(PasswordHasher):
    def __init__(self) -> None:
        self._ph = argon2.PasswordHasher.from_parameters(
            argon2.profiles.CHEAPEST,  # cheap to make registration faster (for pitch)
        )

    async def hash_password(self, password: str) -> str:
        return self._ph.hash(password)

    async def check_password(self, *, password: str, hashed_password: str) -> bool:
        try:
            return self._ph.verify(password=password, hash=hashed_password)
        except argon2.exceptions.VerifyMismatchError:
            return False

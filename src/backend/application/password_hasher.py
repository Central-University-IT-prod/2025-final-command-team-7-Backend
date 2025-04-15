import typing


class PasswordHasher(typing.Protocol):
    async def hash_password(self, password: str) -> str:
        raise NotImplementedError

    async def check_password(self, *, password: str, hashed_password: str) -> bool:
        raise NotImplementedError

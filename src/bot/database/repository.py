import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.auth_token import AuthToken
from backend.domain.user import User
from backend.domain.user_id import UserId
from bot.adapters.repository_adapter import BotAuthTokenRepository, BotCommitter, BotUserRepository


class Repo:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = BotUserRepository(session)
        self.auth_token_repo = BotAuthTokenRepository(session)
        self.committer = BotCommitter(session)

    async def get_user_from_tg_id(self, tg_id: int) -> User | None:
        return await self.user_repo.get_by_telegram_id(tg_id)

    async def create_user(self, tg_id: int, username: str | None = None) -> User:
        user = User(
            id=UserId(uuid.uuid4()),
            username=username or f"user_{tg_id}",
            email=None,
            hashed_password=None,
            telegram_id=tg_id,
        )
        created_user = await self.user_repo.create(user)
        await self.committer.commit()
        return created_user

    async def get_auth_token(self, token: str) -> AuthToken:
        return await self.auth_token_repo.get_by_token(token)

    async def activate_auth_token(self, token: str, user_id: UserId) -> AuthToken:
        activated_token = await self.auth_token_repo.activate_token(token, user_id)
        await self.committer.commit()
        return activated_token

    async def decline_auth_token(self, token: str) -> AuthToken:
        declined_token = await self.auth_token_repo.decline_token(token)
        await self.committer.commit()
        return declined_token

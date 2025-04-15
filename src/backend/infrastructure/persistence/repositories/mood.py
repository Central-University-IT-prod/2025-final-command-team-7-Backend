from collections.abc import Sequence

from advanced_alchemy.exceptions import NotFoundError
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import MoodNotFoundError
from backend.application.repositories.mood import MoodRepository
from backend.domain.mood import Mood
from backend.domain.mood_id import MoodId
from backend.infrastructure.persistence.mappers.mood import orm_to_mood
from backend.infrastructure.persistence.models.mood import MoodORM


class _Repository(SQLAlchemyAsyncRepository[MoodORM]):
    model_type = MoodORM


class SQLAlchemyMoodRepository(MoodRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = _Repository(session=session)

    async def list_all(self) -> Sequence[Mood]:
        orm_moods = await self._repo.list()
        return [orm_to_mood(mood) for mood in orm_moods]

    async def get_by_id(self, mood_id: MoodId) -> Mood:
        try:
            orm_mood = await self._repo.get(mood_id)
        except NotFoundError as exc:
            raise MoodNotFoundError(f"Mood with id {mood_id} not found") from exc
        return orm_to_mood(orm_mood)

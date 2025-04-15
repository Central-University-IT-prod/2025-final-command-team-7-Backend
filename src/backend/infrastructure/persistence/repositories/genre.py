from advanced_alchemy.exceptions import NotFoundError
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import GenreNotFoundError
from backend.application.repositories.genre import GenreRepository
from backend.domain.genre import Genre
from backend.domain.genre_id import GenreId
from backend.domain.mood_id import MoodId
from backend.infrastructure.persistence.mappers.genre import orm_to_genre
from backend.infrastructure.persistence.models.genre import GenreORM
from backend.infrastructure.persistence.models.genre_mood import GenreMoodORM


class _Repository(SQLAlchemyAsyncRepository[GenreORM]):
    model_type = GenreORM


class SQLAlchemyGenreRepository(GenreRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = _Repository(session=session)

    async def list_all(self, moods_ids: list[MoodId] | None = None) -> list[Genre]:
        if moods_ids:
            stmt = (
                select(GenreORM)
                .join(GenreMoodORM, GenreORM.id == GenreMoodORM.genre_id)
                .where(GenreMoodORM.mood_id.in_(moods_ids))
                .distinct()
            )
            result = await self._session.execute(stmt)
            orm_genres = result.scalars().all()
        else:
            orm_genres = await self._repo.list()

        return [orm_to_genre(genre) for genre in orm_genres]

    async def get_by_id(self, genre_id: GenreId) -> Genre:
        try:
            orm_genre = await self._repo.get(genre_id)
        except NotFoundError as exc:
            raise GenreNotFoundError from exc
        return orm_to_genre(orm_genre)

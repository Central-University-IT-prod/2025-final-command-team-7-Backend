import datetime
from collections.abc import Sequence

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.repositories.recommended_film import RecommendedFilmRepository
from backend.domain.recommended_film import RecommendedFilm
from backend.domain.user_id import UserId
from backend.infrastructure.persistence.mappers.recommended_film import (
    orm_to_recommended_film,
    recommended_film_to_orm,
)
from backend.infrastructure.persistence.models.recommended_film import RecommendedFilmORM


class _Repository(SQLAlchemyAsyncRepository[RecommendedFilmORM]):
    model_type = RecommendedFilmORM


class SQLAlchemyRecommendedFilmRepository(RecommendedFilmRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = _Repository(session=session)

    async def create(self, recommendation: RecommendedFilm) -> RecommendedFilm:
        orm_recommendation = recommended_film_to_orm(recommendation)
        orm_recommendation = await self._repo.add(orm_recommendation)
        return orm_to_recommended_film(orm_recommendation)

    async def get_recent_by_user(self, user_id: UserId, time_threshold: datetime.datetime) -> Sequence[RecommendedFilm]:
        stmt = (
            select(RecommendedFilmORM)
            .where(RecommendedFilmORM.user_id == user_id)
            .where(RecommendedFilmORM.recommended_at >= time_threshold)
        )
        result = await self._session.execute(stmt)
        orm_recommendations = result.scalars().all()
        return [orm_to_recommended_film(orm) for orm in orm_recommendations]

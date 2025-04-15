import datetime
import typing
from collections.abc import Sequence

from backend.domain.recommended_film import RecommendedFilm
from backend.domain.user_id import UserId


class RecommendedFilmRepository(typing.Protocol):
    async def create(self, recommendation: RecommendedFilm) -> RecommendedFilm:
        raise NotImplementedError

    async def get_recent_by_user(self, user_id: UserId, time_threshold: datetime.datetime) -> Sequence[RecommendedFilm]:
        raise NotImplementedError

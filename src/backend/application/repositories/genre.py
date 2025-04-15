import typing
from collections.abc import Sequence

from backend.domain.genre import Genre
from backend.domain.genre_id import GenreId
from backend.domain.mood_id import MoodId


class GenreRepository(typing.Protocol):
    async def list_all(self, moods_ids: list[MoodId] | None = None) -> Sequence[Genre]:
        raise NotImplementedError

    async def get_by_id(self, genre_id: GenreId) -> Genre:
        raise NotImplementedError

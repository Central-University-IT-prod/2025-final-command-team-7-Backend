import typing

from backend.domain.film import Film
from backend.domain.film_id import FilmId
from backend.domain.genre_id import GenreId


class FilmRepository(typing.Protocol):
    async def create(self, film: Film) -> Film:
        raise NotImplementedError

    async def get_by_id(self, film_id: FilmId) -> Film:
        raise NotImplementedError

    async def update(self, updated_film: Film) -> Film:
        raise NotImplementedError

    async def update_genres(self, film_id: FilmId, genres_ids: list[GenreId]) -> None:
        raise NotImplementedError

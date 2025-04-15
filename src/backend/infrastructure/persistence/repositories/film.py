from advanced_alchemy.exceptions import NotFoundError
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import FilmNotFoundError, GenreNotFoundError
from backend.application.repositories.film import FilmRepository
from backend.domain.film import Film
from backend.domain.film_id import FilmId
from backend.domain.genre_id import GenreId
from backend.infrastructure.persistence.mappers.film import film_to_orm, orm_to_film
from backend.infrastructure.persistence.models.film import FilmORM
from backend.infrastructure.persistence.models.film_genre import FilmGenre
from backend.infrastructure.persistence.models.genre import GenreORM


class _Repository(SQLAlchemyAsyncRepository[FilmORM]):
    model_type = FilmORM


class SQLAlchemyFilmRepository(FilmRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = _Repository(session=session)

    async def create(self, film: Film) -> Film:
        orm_film = film_to_orm(film)
        orm_film = await self._repo.add(orm_film)
        return orm_to_film(orm_film)

    async def get_by_id(self, film_id: FilmId) -> Film:
        try:
            orm_film = await self._repo.get(film_id)
        except NotFoundError as exc:
            raise FilmNotFoundError from exc
        return orm_to_film(orm_film)

    async def update(self, updated_film: Film) -> Film:
        orm_film = film_to_orm(updated_film)
        try:
            orm_film = await self._repo.update(orm_film)
        except NotFoundError as exc:
            raise FilmNotFoundError from exc
        return orm_to_film(orm_film)

    async def update_genres(self, film_id: FilmId, genres_ids: list[GenreId]) -> None:
        film_genres: list[FilmGenre] = []
        for genre_id in genres_ids:
            genre = await self._session.get(GenreORM, genre_id)
            if genre is None:
                pass
            film_genre = await self._session.get(FilmGenre, (film_id, genre_id))
            if film_genre is None:
                film_genres.append(FilmGenre(film_id=film_id, genre_id=genre_id))
        self._session.add_all(film_genres)

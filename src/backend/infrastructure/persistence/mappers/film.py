from backend.domain.film import Film
from backend.domain.film_id import FilmId
from backend.domain.user_id import UserId
from backend.infrastructure.persistence.models.film import FilmORM


def orm_to_film(orm_film: FilmORM) -> Film:
    return Film(
        id=FilmId(orm_film.id),
        title=orm_film.title,
        description=orm_film.description,
        country=orm_film.country,
        release_year=orm_film.release_year,
        poster_url=orm_film.poster_url,
        tmdb_id=orm_film.tmdb_id,
        owner_id=UserId(orm_film.owner_id) if orm_film.owner_id is not None else None,
    )


def film_to_orm(film: Film) -> FilmORM:
    return FilmORM(
        id=film.id,
        title=film.title,
        description=film.description,
        country=film.country,
        release_year=film.release_year,
        poster_url=film.poster_url,
        tmdb_id=film.tmdb_id,
        owner_id=film.owner_id,
    )

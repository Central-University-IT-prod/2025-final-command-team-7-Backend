from backend.domain.genre import Genre
from backend.domain.genre_id import GenreId
from backend.infrastructure.persistence.models.genre import GenreORM


def orm_to_genre(orm_genre: GenreORM) -> Genre:
    return Genre(id=GenreId(orm_genre.id), name=orm_genre.name)


def genre_to_orm(genre: Genre) -> GenreORM:
    return GenreORM(id=genre.id, name=genre.name)

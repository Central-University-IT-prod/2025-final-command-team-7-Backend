import uuid

import pytest

from backend.domain.film import Film
from backend.domain.film_id import FilmId
from backend.domain.user_id import UserId
from backend.infrastructure.persistence.mappers.film import film_to_orm, orm_to_film
from backend.infrastructure.persistence.models.film import FilmORM


class TestFilmMappers:
    def test_film_to_orm(self):
        
        film_id = FilmId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())
        film = Film(
            id=film_id,
            title="Test Film",
            description="A test film description",
            country="Test Country",
            release_year=2023,
            poster_url="http://example.com/poster.jpg",
            tmdb_id=12345,
            owner_id=user_id
        )

        
        orm_film = film_to_orm(film)

        
        assert isinstance(orm_film, FilmORM)
        assert orm_film.id == film_id
        assert orm_film.title == "Test Film"
        assert orm_film.description == "A test film description"
        assert orm_film.country == "Test Country"
        assert orm_film.release_year == 2023
        assert orm_film.poster_url == "http://example.com/poster.jpg"
        assert orm_film.tmdb_id == 12345
        assert orm_film.owner_id == user_id

    def test_orm_to_film(self):
        
        film_id = uuid.uuid4()
        user_id = uuid.uuid4()
        orm_film = FilmORM(
            id=film_id,
            title="Test Film",
            description="A test film description",
            country="Test Country",
            release_year=2023,
            poster_url="http://example.com/poster.jpg",
            tmdb_id=12345,
            owner_id=user_id
        )

        
        film = orm_to_film(orm_film)

        
        assert isinstance(film, Film)
        assert film.id == FilmId(film_id)
        assert film.title == "Test Film"
        assert film.description == "A test film description"
        assert film.country == "Test Country"
        assert film.release_year == 2023
        assert film.poster_url == "http://example.com/poster.jpg"
        assert film.tmdb_id == 12345
        assert film.owner_id == UserId(user_id)

    def test_film_to_orm_with_none_values(self):
        
        film_id = FilmId(uuid.uuid4())
        film = Film(
            id=film_id,
            title="Test Film",
            description="A test film description",
            country=None,
            release_year=None,
            poster_url=None,
            tmdb_id=None,
            owner_id=None
        )

        
        orm_film = film_to_orm(film)

        
        assert isinstance(orm_film, FilmORM)
        assert orm_film.id == film_id
        assert orm_film.title == "Test Film"
        assert orm_film.description == "A test film description"
        assert orm_film.country is None
        assert orm_film.release_year is None
        assert orm_film.poster_url is None
        assert orm_film.tmdb_id is None
        assert orm_film.owner_id is None

    def test_orm_to_film_with_none_values(self):
        
        film_id = uuid.uuid4()
        orm_film = FilmORM(
            id=film_id,
            title="Test Film",
            description="A test film description",
            country=None,
            release_year=None,
            poster_url=None,
            tmdb_id=None,
            owner_id=None
        )

        
        film = orm_to_film(orm_film)

        
        assert isinstance(film, Film)
        assert film.id == FilmId(film_id)
        assert film.title == "Test Film"
        assert film.description == "A test film description"
        assert film.country is None
        assert film.release_year is None
        assert film.poster_url is None
        assert film.tmdb_id is None
        assert film.owner_id is None
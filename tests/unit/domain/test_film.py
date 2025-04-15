import uuid

import pytest

from backend.domain.film import Film
from backend.domain.film_id import FilmId
from backend.domain.user_id import UserId


class TestFilm:
    def test_create_film(self):
        
        film_id = FilmId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())

        
        film = Film(
            id=film_id,
            title="Test Film",
            description="A test film description",
            country="United States",
            release_year=2023,
            poster_url="http://example.com/poster.jpg",
            tmdb_id=12345,
            owner_id=user_id
        )

        
        assert film.id == film_id
        assert film.title == "Test Film"
        assert film.description == "A test film description"
        assert film.country == "United States"
        assert film.release_year == 2023
        assert film.poster_url == "http://example.com/poster.jpg"
        assert film.tmdb_id == 12345
        assert film.owner_id == user_id

    def test_create_film_with_optional_fields_as_none(self):
        
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

        
        assert film.id == film_id
        assert film.title == "Test Film"
        assert film.description == "A test film description"
        assert film.country is None
        assert film.release_year is None
        assert film.poster_url is None
        assert film.tmdb_id is None
        assert film.owner_id is None
import uuid

import pytest

from backend.domain.genre import Genre
from backend.domain.genre_id import GenreId


class TestGenre:
    def test_create_genre(self):
        
        genre_id = GenreId(uuid.uuid4())

        
        genre = Genre(
            id=genre_id,
            name="Action"
        )

        
        assert genre.id == genre_id
        assert genre.name == "Action"
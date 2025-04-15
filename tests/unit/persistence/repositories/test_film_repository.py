import uuid

import pytest
from advanced_alchemy.exceptions import NotFoundError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import FilmNotFoundError, GenreNotFoundError
from backend.domain.film import Film
from backend.domain.film_id import FilmId
from backend.domain.genre_id import GenreId
from backend.domain.user_id import UserId
from backend.infrastructure.persistence.mappers.film import film_to_orm
from backend.infrastructure.persistence.models.film import FilmORM
from backend.infrastructure.persistence.models.genre import GenreORM
from backend.infrastructure.persistence.repositories.film import SQLAlchemyFilmRepository


class TestSQLAlchemyFilmRepository:
    @pytest.mark.asyncio
    async def test_create(self, db_session: AsyncSession):
        
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
        repo = SQLAlchemyFilmRepository(session=db_session)

        
        created_film = await repo.create(film)

        
        assert created_film.id == film_id
        assert created_film.title == "Test Film"
        assert created_film.description == "A test film description"
        assert created_film.country == "Test Country"
        assert created_film.release_year == 2023
        assert created_film.poster_url == "http://example.com/poster.jpg"
        assert created_film.tmdb_id == 12345
        assert created_film.owner_id == user_id

        
        result = await db_session.execute(select(FilmORM).where(FilmORM.id == film_id))
        db_film = result.scalars().first()
        assert db_film is not None
        assert db_film.title == "Test Film"

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, db_session: AsyncSession):
        
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
        db_session.add(orm_film)
        await db_session.commit()

        repo = SQLAlchemyFilmRepository(session=db_session)

        
        retrieved_film = await repo.get_by_id(film_id)

        
        assert retrieved_film.id == film_id
        assert retrieved_film.title == "Test Film"
        assert retrieved_film.description == "A test film description"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        
        film_id = FilmId(uuid.uuid4())
        repo = SQLAlchemyFilmRepository(session=db_session)

        
        with pytest.raises(FilmNotFoundError):
            await repo.get_by_id(film_id)

    @pytest.mark.asyncio
    async def test_update(self, db_session: AsyncSession):
        
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
        db_session.add(orm_film)
        await db_session.commit()

        
        updated_film = Film(
            id=film_id,
            title="Updated Film Title",
            description="Updated description",
            country="Updated Country",
            release_year=2024,
            poster_url="http://example.com/updated_poster.jpg",
            tmdb_id=12345,
            owner_id=user_id
        )

        repo = SQLAlchemyFilmRepository(session=db_session)

        
        result = await repo.update(updated_film)

        
        assert result.title == "Updated Film Title"
        assert result.description == "Updated description"
        assert result.country == "Updated Country"
        assert result.release_year == 2024
        assert result.poster_url == "http://example.com/updated_poster.jpg"

        
        result = await db_session.execute(select(FilmORM).where(FilmORM.id == film_id))
        db_film = result.scalars().first()
        assert db_film is not None
        assert db_film.title == "Updated Film Title"

    @pytest.mark.asyncio
    async def test_update_not_found(self, db_session: AsyncSession):
        
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

        repo = SQLAlchemyFilmRepository(session=db_session)

        
        with pytest.raises(FilmNotFoundError):
            await repo.update(film)
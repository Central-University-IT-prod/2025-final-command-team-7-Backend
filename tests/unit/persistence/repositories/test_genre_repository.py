import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import GenreNotFoundError
from backend.domain.genre import Genre
from backend.domain.genre_id import GenreId
from backend.domain.mood_id import MoodId
from backend.infrastructure.persistence.mappers.genre import genre_to_orm
from backend.infrastructure.persistence.models.genre import GenreORM
from backend.infrastructure.persistence.models.genre_mood import GenreMoodORM
from backend.infrastructure.persistence.repositories.genre import SQLAlchemyGenreRepository


class TestSQLAlchemyGenreRepository:
    @pytest.mark.asyncio
    async def test_list_all(self, db_session: AsyncSession):
        
        genre_id1 = GenreId(uuid.uuid4())
        genre_id2 = GenreId(uuid.uuid4())

        genre1 = Genre(id=genre_id1, name="Action")
        genre2 = Genre(id=genre_id2, name="Comedy")

        orm_genre1 = genre_to_orm(genre1)
        orm_genre2 = genre_to_orm(genre2)

        db_session.add_all([orm_genre1, orm_genre2])
        await db_session.commit()

        repo = SQLAlchemyGenreRepository(session=db_session)

        
        genres = await repo.list_all()

        
        assert len(genres) == 2
        genre_names = [g.name for g in genres]
        assert "Action" in genre_names
        assert "Comedy" in genre_names

    @pytest.mark.asyncio
    async def test_list_all_with_moods_filter(self, db_session: AsyncSession):
        
        genre_id1 = GenreId(uuid.uuid4())
        genre_id2 = GenreId(uuid.uuid4())
        genre_id3 = GenreId(uuid.uuid4())
        mood_id1 = MoodId(uuid.uuid4())
        mood_id2 = MoodId(uuid.uuid4())

        genre1 = Genre(id=genre_id1, name="Action")
        genre2 = Genre(id=genre_id2, name="Comedy")
        genre3 = Genre(id=genre_id3, name="Drama")

        orm_genre1 = genre_to_orm(genre1)
        orm_genre2 = genre_to_orm(genre2)
        orm_genre3 = genre_to_orm(genre3)

        
        genre_mood1 = GenreMoodORM(genre_id=genre_id1, mood_id=mood_id1)
        genre_mood2 = GenreMoodORM(genre_id=genre_id2, mood_id=mood_id2)

        db_session.add_all([orm_genre1, orm_genre2, orm_genre3, genre_mood1, genre_mood2])
        await db_session.commit()

        repo = SQLAlchemyGenreRepository(session=db_session)

        
        genres = await repo.list_all(moods_ids=[mood_id1])

        
        assert len(genres) == 1
        assert genres[0].id == genre_id1
        assert genres[0].name == "Action"

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, db_session: AsyncSession):
        
        genre_id = GenreId(uuid.uuid4())
        genre = Genre(id=genre_id, name="Action")
        orm_genre = genre_to_orm(genre)

        db_session.add(orm_genre)
        await db_session.commit()

        repo = SQLAlchemyGenreRepository(session=db_session)

        
        retrieved_genre = await repo.get_by_id(genre_id)

        
        assert retrieved_genre.id == genre_id
        assert retrieved_genre.name == "Action"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        
        genre_id = GenreId(uuid.uuid4())
        repo = SQLAlchemyGenreRepository(session=db_session)

        
        with pytest.raises(GenreNotFoundError):
            await repo.get_by_id(genre_id)
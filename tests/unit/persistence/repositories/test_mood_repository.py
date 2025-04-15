import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import MoodNotFoundError
from backend.domain.mood import Mood
from backend.domain.mood_id import MoodId
from backend.infrastructure.persistence.mappers.mood import mood_to_orm
from backend.infrastructure.persistence.models.mood import MoodORM
from backend.infrastructure.persistence.repositories.mood import SQLAlchemyMoodRepository


class TestSQLAlchemyMoodRepository:
    @pytest.mark.asyncio
    async def test_list_all(self, db_session: AsyncSession):
        
        mood_id1 = MoodId(uuid.uuid4())
        mood_id2 = MoodId(uuid.uuid4())

        mood1 = Mood(id=mood_id1, name="Happy")
        mood2 = Mood(id=mood_id2, name="Sad")

        orm_mood1 = mood_to_orm(mood1)
        orm_mood2 = mood_to_orm(mood2)

        db_session.add_all([orm_mood1, orm_mood2])
        await db_session.commit()

        repo = SQLAlchemyMoodRepository(session=db_session)

        
        moods = await repo.list_all()

        
        assert len(moods) == 2
        mood_names = [m.name for m in moods]
        assert "Happy" in mood_names
        assert "Sad" in mood_names

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, db_session: AsyncSession):
        
        mood_id = MoodId(uuid.uuid4())
        mood = Mood(id=mood_id, name="Happy")
        orm_mood = mood_to_orm(mood)

        db_session.add(orm_mood)
        await db_session.commit()

        repo = SQLAlchemyMoodRepository(session=db_session)

        
        retrieved_mood = await repo.get_by_id(mood_id)

        
        assert retrieved_mood.id == mood_id
        assert retrieved_mood.name == "Happy"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        
        mood_id = MoodId(uuid.uuid4())
        repo = SQLAlchemyMoodRepository(session=db_session)

        
        with pytest.raises(MoodNotFoundError):
            await repo.get_by_id(mood_id)
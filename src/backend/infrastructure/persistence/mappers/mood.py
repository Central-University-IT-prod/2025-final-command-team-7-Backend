from backend.domain.mood import Mood
from backend.domain.mood_id import MoodId
from backend.infrastructure.persistence.models.mood import MoodORM


def orm_to_mood(orm_mood: MoodORM) -> Mood:
    return Mood(id=MoodId(orm_mood.id), name=orm_mood.name)


def mood_to_orm(mood: Mood) -> MoodORM:
    return MoodORM(id=mood.id, name=mood.name)

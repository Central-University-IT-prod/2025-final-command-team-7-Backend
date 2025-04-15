import dataclasses

from backend.domain.mood_id import MoodId


@dataclasses.dataclass
class Mood:
    id: MoodId
    name: str

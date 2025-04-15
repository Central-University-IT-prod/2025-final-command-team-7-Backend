import typing
from collections.abc import Sequence

from backend.domain.mood import Mood
from backend.domain.mood_id import MoodId


class MoodRepository(typing.Protocol):
    async def list_all(self) -> Sequence[Mood]:
        raise NotImplementedError

    async def get_by_id(self, mood_id: MoodId) -> Mood:
        raise NotImplementedError

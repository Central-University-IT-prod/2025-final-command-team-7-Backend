from collections.abc import Sequence

from dishka import FromDishka
from dishka.integrations.litestar import inject
from litestar import Controller, get
from litestar.exceptions import NotFoundException

from backend.application.errors import MoodNotFoundError
from backend.application.repositories.mood import MoodRepository
from backend.domain.mood import Mood
from backend.domain.mood_id import MoodId


class MoodController(Controller):
    path = "/moods"
    tags = ("mood",)

    @get()
    @inject
    async def list_moods(
        self,
        mood_repo: FromDishka[MoodRepository],
    ) -> Sequence[Mood]:
        return await mood_repo.list_all()

    @get("/{mood_id:uuid}")
    @inject
    async def get_mood_by_id(
        self,
        mood_id: MoodId,
        mood_repo: FromDishka[MoodRepository],
    ) -> Mood:
        try:
            return await mood_repo.get_by_id(mood_id)
        except MoodNotFoundError as exc:
            raise NotFoundException(detail="Mood not found") from exc

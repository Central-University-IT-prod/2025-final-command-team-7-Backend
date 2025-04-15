from dishka.integrations.litestar import FromDishka, inject
from litestar import Controller, get
from litestar.exceptions import NotFoundException

from backend.application.errors import GenreNotFoundError
from backend.application.repositories.genre import GenreRepository
from backend.domain.genre import Genre
from backend.domain.genre_id import GenreId
from backend.domain.mood_id import MoodId


class GenresController(Controller):
    path = "genres"
    tags = ("genre",)

    @get()
    @inject
    async def list_genres(
        self,
        genre_repo: FromDishka[GenreRepository],
        moods_ids: list[MoodId] | None = None,
    ) -> list[Genre]:
        return list(await genre_repo.list_all(moods_ids))

    @get("/{genre_id:uuid}")
    @inject
    async def get_genre_by_id(self, genre_id: GenreId, genre_repo: FromDishka[GenreRepository]) -> Genre:
        try:
            return await genre_repo.get_by_id(genre_id)
        except GenreNotFoundError as exc:
            raise NotFoundException("Genre not found") from exc

import dataclasses

from backend.domain.film_id import FilmId
from backend.domain.user_id import UserId


@dataclasses.dataclass
class Film:
    id: FilmId

    title: str
    description: str | None
    country: str | None
    release_year: int | None
    poster_url: str | None

    tmdb_id: int | None

    owner_id: UserId | None

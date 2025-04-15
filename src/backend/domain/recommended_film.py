import dataclasses
import datetime
import uuid

from backend.domain.film_id import FilmId
from backend.domain.user_id import UserId


@dataclasses.dataclass
class RecommendedFilm:
    id: uuid.UUID
    user_id: UserId
    film_id: FilmId
    recommended_at: datetime.datetime

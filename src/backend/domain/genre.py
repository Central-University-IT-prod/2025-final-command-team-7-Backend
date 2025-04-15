import dataclasses

from backend.domain.genre_id import GenreId


@dataclasses.dataclass
class Genre:
    id: GenreId
    name: str

import dataclasses
import datetime

from backend.domain.film_id import FilmId
from backend.domain.mix_id import MixId


@dataclasses.dataclass
class MixItem:
    mix_id: MixId
    film_id: FilmId
    added_at: datetime.datetime

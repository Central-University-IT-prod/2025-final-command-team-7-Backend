import dataclasses
import datetime

from backend.domain.film_id import FilmId
from backend.domain.watchlist_id import WatchlistId


@dataclasses.dataclass
class WatchlistItem:
    watchlist_id: WatchlistId
    film_id: FilmId
    added_at: datetime.datetime

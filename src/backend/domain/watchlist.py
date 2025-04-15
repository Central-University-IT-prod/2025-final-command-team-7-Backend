import dataclasses
from typing import Any

from backend.domain.user_id import UserId
from backend.domain.watchlist_id import WatchlistId
from backend.domain.watchlist_type import WatchlistType


@dataclasses.dataclass
class Watchlist:
    id: WatchlistId
    user_id: UserId
    title: str
    type: WatchlistType
    color1: str
    color2: str
    color3: str
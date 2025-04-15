import typing
from collections.abc import Sequence

from backend.domain.film_id import FilmId
from backend.domain.user_id import UserId
from backend.domain.watchlist import Watchlist
from backend.domain.watchlist_id import WatchlistId
from backend.domain.watchlist_item import WatchlistItem
from backend.domain.watchlist_type import WatchlistType


class WatchlistRepository(typing.Protocol):
    async def create_watchlist(self, watchlist: Watchlist) -> Watchlist:
        raise NotImplementedError

    async def get_by_id(self, watchlist_id: WatchlistId) -> Watchlist:
        raise NotImplementedError

    async def get_items_for_watchlist(self, watchlist_id: WatchlistId) -> Sequence[WatchlistItem]:
        raise NotImplementedError

    async def get_by_type(self, watchlist_type: WatchlistType) -> Sequence[WatchlistItem]:
        raise NotImplementedError

    async def add_item(self, item: WatchlistItem) -> None:
        raise NotImplementedError

    async def delete_item(self, watchlist_id: WatchlistId, film_id: FilmId) -> None:
        raise NotImplementedError

    async def create_common_watchlist_for_user(self, user_id: UserId) -> None:
        raise NotImplementedError

    async def get_common_watchlist_for_user(self, watchlist_type: WatchlistType, user_id: UserId) -> Watchlist:
        raise NotImplementedError

    async def get_all_for_user(self, user_id: UserId) -> Sequence[Watchlist]:
        raise NotImplementedError

    async def delete_watchlist(self, watchlist_id: WatchlistId) -> None:
        raise NotImplementedError

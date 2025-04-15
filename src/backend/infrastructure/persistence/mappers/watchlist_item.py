from backend.domain.film_id import FilmId
from backend.domain.watchlist_id import WatchlistId
from backend.domain.watchlist_item import WatchlistItem
from backend.infrastructure.persistence.models.watchlist_item import WatchlistItemORM


def orm_to_watchlist_item(orm_watchlist_item: WatchlistItemORM) -> WatchlistItem:
    return WatchlistItem(
        watchlist_id=WatchlistId(orm_watchlist_item.watchlist_id),
        film_id=FilmId(orm_watchlist_item.film_id),
        added_at=orm_watchlist_item.added_at,
    )


def watchlist_item_to_orm(watchlist_item: WatchlistItem) -> WatchlistItemORM:
    return WatchlistItemORM(
        watchlist_id=watchlist_item.watchlist_id,
        film_id=watchlist_item.film_id,
        added_at=watchlist_item.added_at,
    )

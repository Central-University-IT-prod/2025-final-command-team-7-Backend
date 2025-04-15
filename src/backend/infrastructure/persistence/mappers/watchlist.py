from backend.domain.user_id import UserId
from backend.domain.watchlist import Watchlist
from backend.domain.watchlist_id import WatchlistId
from backend.infrastructure.persistence.models.watchlist import WatchlistORM


def orm_to_watchlist(orm_watchlist: WatchlistORM) -> Watchlist:
    return Watchlist(
        id=WatchlistId(orm_watchlist.id),
        user_id=UserId(orm_watchlist.user_id),
        title=orm_watchlist.title,
        type=orm_watchlist.type,
        color1=orm_watchlist.color1,
        color2=orm_watchlist.color2,
        color3=orm_watchlist.color3,
    )


def watchlist_to_orm(watchlist: Watchlist) -> WatchlistORM:
    return WatchlistORM(
        id=watchlist.id,
        user_id=watchlist.user_id,
        title=watchlist.title,
        type=watchlist.type,
        color1=watchlist.color1,
        color2=watchlist.color2,
        color3=watchlist.color3,
    )

import uuid
from collections.abc import Sequence
from typing import cast

from advanced_alchemy.exceptions import NotFoundError
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.filters import OrderBy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import WatchlistNotFoundError
from backend.application.repositories.watchlist import WatchlistRepository
from backend.domain.film_id import FilmId
from backend.domain.user_id import UserId
from backend.domain.watchlist import Watchlist
from backend.domain.watchlist_id import WatchlistId
from backend.domain.watchlist_item import WatchlistItem
from backend.domain.watchlist_type import WatchlistType
from backend.infrastructure.persistence.mappers.watchlist import orm_to_watchlist, watchlist_to_orm
from backend.infrastructure.persistence.mappers.watchlist_item import orm_to_watchlist_item, watchlist_item_to_orm
from backend.infrastructure.persistence.models.watchlist import WatchlistORM
from backend.infrastructure.persistence.models.watchlist_item import WatchlistItemORM


class _Repository(SQLAlchemyAsyncRepository[WatchlistORM]):
    model_type = WatchlistORM


class _ItemRepository(SQLAlchemyAsyncRepository[WatchlistItemORM]):
    model_type = WatchlistItemORM


class SQLAlchemyWatchlistRepository(WatchlistRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = _Repository(session=session)
        self._item_repo = _ItemRepository(session=session)

    async def create_watchlist(self, watchlist: Watchlist) -> Watchlist:
        orm_watchlist = watchlist_to_orm(watchlist)
        orm_watchlist = await self._repo.add(orm_watchlist)
        return orm_to_watchlist(orm_watchlist)

    async def get_by_id(self, watchlist_id: WatchlistId) -> Watchlist:
        try:
            orm_watchlist = await self._repo.get(watchlist_id)
        except NotFoundError as exc:
            raise WatchlistNotFoundError from exc
        return orm_to_watchlist(orm_watchlist)

    async def get_items_for_watchlist(self, watchlist_id: WatchlistId) -> Sequence[WatchlistItem]:
        try:
            orm_watchlist = await self._repo.get(watchlist_id)
            orm_items = await self._item_repo.list(
                OrderBy(field_name="added_at", sort_order="desc"),
                watchlist_id=orm_watchlist.id,
            )
        except NotFoundError as exc:
            raise WatchlistNotFoundError from exc
        return [orm_to_watchlist_item(e) for e in orm_items]

    async def add_item(self, item: WatchlistItem) -> None:
        orm_item = await self._session.get(WatchlistItemORM, (item.watchlist_id, item.film_id))
        if orm_item is None:
            orm_item = watchlist_item_to_orm(item)
            await self._item_repo.add(orm_item)

    async def delete_item(self, watchlist_id: WatchlistId, film_id: FilmId) -> None:
        try:
            await self._item_repo.delete_where(watchlist_id=watchlist_id, film_id=film_id)
        except NotFoundError as exc:
            raise WatchlistNotFoundError from exc

    async def create_common_watchlist_for_user(self, user_id: UserId) -> None:
        watchlists = (
            WatchlistORM(
                id=uuid.uuid4(),
                user_id=user_id,
                title="Мои любимые",
                type=WatchlistType.liked,
                color1="#FF36AB",
                color2="#FF74D4",
                color3="#ED5C86",
            ),
            WatchlistORM(
                id=uuid.uuid4(),
                user_id=user_id,
                title="Просмотренные",
                type=WatchlistType.watched,
                color1="#31B4EA",
                color2="#6F97EB",
                color3="#B577EC",
            ),
            WatchlistORM(
                id=uuid.uuid4(),
                user_id=user_id,
                title="Хочу посмотреть",
                type=WatchlistType.wish,
                color1="#EE0979",
                color2="#FF6A00",
                color3="#FFF647",
            ),
        )
        self._session.add_all(watchlists)

    async def get_common_watchlist_for_user(self, watchlist_type: WatchlistType, user_id: UserId) -> Watchlist:
        if watchlist_type not in (WatchlistType.liked, WatchlistType.watched, WatchlistType.wish):
            raise ValueError("type is not common")
        orm_watchlist = await self._session.scalar(
            select(WatchlistORM).where(WatchlistORM.user_id == user_id).where(WatchlistORM.type == watchlist_type)
        )
        if orm_watchlist is None:
            if watchlist_type is WatchlistType.liked:
                orm_watchlist = WatchlistORM(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    title="Мои любимые",
                    type=WatchlistType.liked,
                    color1="#FF36AB",
                    color2="#FF74D4",
                    color3="#ED5C86",
                )
            elif watchlist_type is WatchlistType.watched:
                orm_watchlist = WatchlistORM(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    title="Просмотренные",
                    type=WatchlistType.watched,
                    color1="#31B4EA",
                    color2="#6F97EB",
                    color3="#B577EC",
                )
            elif watchlist_type is WatchlistType.wish:
                orm_watchlist = WatchlistORM(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    title="Хочу посмотреть",
                    type=WatchlistType.wish,
                    color1="#EE0979",
                    color2="#FF6A00",
                    color3="#FFF647",
                )
            self._session.add(orm_watchlist)
            await self._session.commit()

        return orm_to_watchlist(orm_watchlist)

    async def get_all_for_user(self, user_id: UserId) -> list[Watchlist]:
        # TODO: sort ok.
        watchlists_orm = await self._repo.list(user_id=user_id)
        return [orm_to_watchlist(i) for i in watchlists_orm]

    async def delete_watchlist(self, watchlist_id: WatchlistId) -> None:
        await self._repo.delete(watchlist_id)

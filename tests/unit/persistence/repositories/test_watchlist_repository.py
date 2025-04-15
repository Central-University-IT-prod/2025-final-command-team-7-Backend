import datetime
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import WatchlistNotFoundError
from backend.domain.film_id import FilmId
from backend.domain.user_id import UserId
from backend.domain.watchlist import Watchlist
from backend.domain.watchlist_id import WatchlistId
from backend.domain.watchlist_item import WatchlistItem
from backend.domain.watchlist_type import WatchlistType
from backend.infrastructure.persistence.mappers.watchlist import watchlist_to_orm
from backend.infrastructure.persistence.models.watchlist import WatchlistORM
from backend.infrastructure.persistence.models.watchlist_item import WatchlistItemORM
from backend.infrastructure.persistence.repositories.watchlist import SQLAlchemyWatchlistRepository


class TestSQLAlchemyWatchlistRepository:
    @pytest.mark.asyncio
    async def test_create_watchlist(self, db_session: AsyncSession):
        # Arrange
        watchlist_id = WatchlistId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())
        watchlist = Watchlist(
            id=watchlist_id,
            user_id=user_id,
            title="Test Watchlist",
            type=WatchlistType.custom,
            color1="#FF0000",
            color2="#00FF00",
            color3="#0000FF"
        )
        repo = SQLAlchemyWatchlistRepository(session=db_session)

        created_watchlist = await repo.create_watchlist(watchlist)

        assert created_watchlist.id == watchlist_id
        assert created_watchlist.user_id == user_id
        assert created_watchlist.title == "Test Watchlist"
        assert created_watchlist.type == WatchlistType.custom
        assert created_watchlist.color1 == "#FF0000"
        assert created_watchlist.color2 == "#00FF00"
        assert created_watchlist.color3 == "#0000FF"

        result = await db_session.execute(select(WatchlistORM).where(WatchlistORM.id == watchlist_id))
        db_watchlist = result.scalars().first()
        assert db_watchlist is not None
        assert db_watchlist.title == "Test Watchlist"

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, db_session: AsyncSession):
        watchlist_id = WatchlistId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())
        watchlist = Watchlist(
            id=watchlist_id,
            user_id=user_id,
            title="Test Watchlist",
            type=WatchlistType.custom,
            color1="#FF0000",
            color2="#00FF00",
            color3="#0000FF"
        )
        orm_watchlist = watchlist_to_orm(watchlist)
        db_session.add(orm_watchlist)
        await db_session.commit()

        repo = SQLAlchemyWatchlistRepository(session=db_session)

        retrieved_watchlist = await repo.get_by_id(watchlist_id)

        assert retrieved_watchlist.id == watchlist_id
        assert retrieved_watchlist.title == "Test Watchlist"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        watchlist_id = WatchlistId(uuid.uuid4())
        repo = SQLAlchemyWatchlistRepository(session=db_session)

        with pytest.raises(WatchlistNotFoundError):
            await repo.get_by_id(watchlist_id)

    @pytest.mark.asyncio
    async def test_add_item(self, db_session: AsyncSession):
        watchlist_id = WatchlistId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())
        film_id = FilmId(uuid.uuid4())

        watchlist = Watchlist(
            id=watchlist_id,
            user_id=user_id,
            title="Test Watchlist",
            type=WatchlistType.custom,
            color1="#FF0000",
            color2="#00FF00",
            color3="#0000FF"
        )
        orm_watchlist = watchlist_to_orm(watchlist)
        db_session.add(orm_watchlist)
        await db_session.commit()

        now = datetime.datetime.now(datetime.UTC)
        watchlist_item = WatchlistItem(
            watchlist_id=watchlist_id,
            film_id=film_id,
            added_at=now
        )

        repo = SQLAlchemyWatchlistRepository(session=db_session)

        await repo.add_item(watchlist_item)
        await db_session.commit()

        result = await db_session.execute(
            select(WatchlistItemORM).where(
                (WatchlistItemORM.watchlist_id == watchlist_id) &
                (WatchlistItemORM.film_id == film_id)
            )
        )
        db_item = result.scalars().first()
        assert db_item is not None
        assert db_item.watchlist_id == watchlist_id
        assert db_item.film_id == film_id

    @pytest.mark.asyncio
    async def test_get_items_for_watchlist(self, db_session: AsyncSession):
        # Arrange
        watchlist_id = WatchlistId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())
        film_id1 = FilmId(uuid.uuid4())
        film_id2 = FilmId(uuid.uuid4())

        watchlist = Watchlist(
            id=watchlist_id,
            user_id=user_id,
            title="Test Watchlist",
            type=WatchlistType.custom,
            color1="#FF0000",
            color2="#00FF00",
            color3="#0000FF"
        )
        orm_watchlist = watchlist_to_orm(watchlist)
        db_session.add(orm_watchlist)

        now = datetime.datetime.now(datetime.UTC)
        item1 = WatchlistItemORM(watchlist_id=watchlist_id, film_id=film_id1, added_at=now)
        item2 = WatchlistItemORM(watchlist_id=watchlist_id, film_id=film_id2, added_at=now)
        db_session.add_all([item1, item2])
        await db_session.commit()

        repo = SQLAlchemyWatchlistRepository(session=db_session)

        items = await repo.get_items_for_watchlist(watchlist_id)

        assert len(items) == 2
        item_film_ids = [item.film_id for item in items]
        assert film_id1 in item_film_ids
        assert film_id2 in item_film_ids

    @pytest.mark.asyncio
    async def test_delete_item(self, db_session: AsyncSession):
        watchlist_id = WatchlistId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())
        film_id = FilmId(uuid.uuid4())

        watchlist = Watchlist(
            id=watchlist_id,
            user_id=user_id,
            title="Test Watchlist",
            type=WatchlistType.custom,
            color1="#FF0000",
            color2="#00FF00",
            color3="#0000FF"
        )
        orm_watchlist = watchlist_to_orm(watchlist)
        db_session.add(orm_watchlist)

        now = datetime.datetime.now(datetime.UTC)
        item = WatchlistItemORM(watchlist_id=watchlist_id, film_id=film_id, added_at=now)
        db_session.add(item)
        await db_session.commit()

        repo = SQLAlchemyWatchlistRepository(session=db_session)

        await repo.delete_item(watchlist_id, film_id)
        await db_session.commit()

        result = await db_session.execute(
            select(WatchlistItemORM).where(
                (WatchlistItemORM.watchlist_id == watchlist_id) &
                (WatchlistItemORM.film_id == film_id)
            )
        )
        db_item = result.scalars().first()
        assert db_item is None

    @pytest.mark.asyncio
    async def test_create_common_watchlist_for_user(self, db_session: AsyncSession):
        user_id = UserId(uuid.uuid4())
        repo = SQLAlchemyWatchlistRepository(session=db_session)

        await repo.create_common_watchlist_for_user(user_id)
        await db_session.commit()

        result = await db_session.execute(select(WatchlistORM).where(WatchlistORM.user_id == user_id))
        watchlists = result.scalars().all()

        assert len(watchlists) == 3

        watchlist_types = [w.type for w in watchlists]
        assert WatchlistType.liked in watchlist_types
        assert WatchlistType.watched in watchlist_types
        assert WatchlistType.wish in watchlist_types

    @pytest.mark.asyncio
    async def test_get_common_watchlist_for_user(self, db_session: AsyncSession):
        user_id = UserId(uuid.uuid4())
        watchlist_id = WatchlistId(uuid.uuid4())

        watchlist = Watchlist(
            id=watchlist_id,
            user_id=user_id,
            title="My Liked Movies",
            type=WatchlistType.liked,
            color1="#FF0000",
            color2="#00FF00",
            color3="#0000FF"
        )
        orm_watchlist = watchlist_to_orm(watchlist)
        db_session.add(orm_watchlist)
        await db_session.commit()

        repo = SQLAlchemyWatchlistRepository(session=db_session)

        result = await repo.get_common_watchlist_for_user(WatchlistType.liked, user_id)

        assert result.id == watchlist_id
        assert result.type == WatchlistType.liked
        assert result.user_id == user_id#.*$
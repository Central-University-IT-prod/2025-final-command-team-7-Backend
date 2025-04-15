import datetime
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import MixNotFoundError
from backend.domain.film_id import FilmId
from backend.domain.mix import Mix
from backend.domain.mix_id import MixId
from backend.domain.mix_item import MixItem
from backend.infrastructure.persistence.mappers.mix import mix_to_orm
from backend.infrastructure.persistence.models.mix import MixORM
from backend.infrastructure.persistence.models.mix_item import MixItemORM
from backend.infrastructure.persistence.repositories.mix import SQLAlchemyMixRepository


class TestSQLAlchemyMixRepository:
    @pytest.mark.asyncio
    async def test_list_all(self, db_session: AsyncSession):
        
        mix_id1 = MixId(uuid.uuid4())
        mix_id2 = MixId(uuid.uuid4())

        mix1 = Mix(
            id=mix_id1,
            title="Action Movies",
            color1="",
            color2="",
            color3="",
        )
        mix2 = Mix(
            id=mix_id2,
            title="Comedy Movies",
            color1="",
            color2="",
            color3="",
        )

        orm_mix1 = mix_to_orm(mix1)
        orm_mix2 = mix_to_orm(mix2)

        db_session.add_all([orm_mix1, orm_mix2])
        await db_session.commit()

        repo = SQLAlchemyMixRepository(session=db_session)

        
        mixes = await repo.list_all()

        
        assert len(mixes) == 2
        mix_titles = [m.title for m in mixes]
        assert "Action Movies" in mix_titles
        assert "Comedy Movies" in mix_titles

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, db_session: AsyncSession):
        
        mix_id = MixId(uuid.uuid4())
        mix = Mix(
            id=mix_id,
            title="Action Movies",
            color1="",
            color2="",
            color3="",
        )
        orm_mix = mix_to_orm(mix)

        db_session.add(orm_mix)
        await db_session.commit()

        repo = SQLAlchemyMixRepository(session=db_session)

        
        retrieved_mix = await repo.get_by_id(mix_id)

        
        assert retrieved_mix.id == mix_id
        assert retrieved_mix.title == "Action Movies"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, db_session: AsyncSession):
        
        mix_id = MixId(uuid.uuid4())
        repo = SQLAlchemyMixRepository(session=db_session)

        
        with pytest.raises(MixNotFoundError):
            await repo.get_by_id(mix_id)

    @pytest.mark.asyncio
    async def test_add_item(self, db_session: AsyncSession):
        
        mix_id = MixId(uuid.uuid4())
        film_id = FilmId(uuid.uuid4())

        
        mix = Mix(
            id=mix_id,
            title="Action Movies",
            color1="",
            color2="",
            color3="",
        )
        orm_mix = mix_to_orm(mix)
        db_session.add(orm_mix)
        await db_session.commit()

        
        now = datetime.datetime.now(datetime.UTC)
        mix_item = MixItem(
            mix_id=mix_id,
            film_id=film_id,
            added_at=now
        )

        repo = SQLAlchemyMixRepository(session=db_session)

        
        await repo.add_item(mix_item)
        await db_session.commit()

        
        result = await db_session.execute(
            select(MixItemORM).where(
                (MixItemORM.mix_id == mix_id) &
                (MixItemORM.film_id == film_id)
            )
        )
        db_item = result.scalars().first()
        assert db_item is not None
        assert db_item.mix_id == mix_id
        assert db_item.film_id == film_id

    @pytest.mark.asyncio
    async def test_get_items_for_mix(self, db_session: AsyncSession):
        
        mix_id = MixId(uuid.uuid4())
        film_id1 = FilmId(uuid.uuid4())
        film_id2 = FilmId(uuid.uuid4())

        
        mix = Mix(
            id=mix_id,
            title="Action Movies",
            color1="",
            color2="",
            color3="",
        )
        orm_mix = mix_to_orm(mix)
        db_session.add(orm_mix)

        
        now = datetime.datetime.now(datetime.UTC)
        item1 = MixItemORM(mix_id=mix_id, film_id=film_id1, added_at=now)
        item2 = MixItemORM(mix_id=mix_id, film_id=film_id2, added_at=now)
        db_session.add_all([item1, item2])
        await db_session.commit()

        repo = SQLAlchemyMixRepository(session=db_session)

        
        items = await repo.get_items_for_mix(mix_id)

        
        assert len(items) == 2
        item_film_ids = [item.film_id for item in items]
        assert film_id1 in item_film_ids
        assert film_id2 in item_film_ids

    @pytest.mark.asyncio
    async def test_delete_item(self, db_session: AsyncSession):
        
        mix_id = MixId(uuid.uuid4())
        film_id = FilmId(uuid.uuid4())

        
        mix = Mix(
            id=mix_id,
            title="Action Movies",
            color1="",
            color2="",
            color3="",
        )
        orm_mix = mix_to_orm(mix)
        db_session.add(orm_mix)

        
        now = datetime.datetime.now(datetime.UTC)
        item = MixItemORM(mix_id=mix_id, film_id=film_id, added_at=now)
        db_session.add(item)
        await db_session.commit()

        repo = SQLAlchemyMixRepository(session=db_session)

        
        await repo.delete_item(mix_id, film_id)
        await db_session.commit()

        
        result = await db_session.execute(
            select(MixItemORM).where(
                (MixItemORM.mix_id == mix_id) &
                (MixItemORM.film_id == film_id)
            )
        )
        db_item = result.scalars().first()
        assert db_item is None

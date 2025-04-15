from collections.abc import Sequence

from advanced_alchemy.exceptions import NotFoundError
from advanced_alchemy.filters import OrderBy
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from backend.application.errors import MixNotFoundError
from backend.application.repositories.mix import MixRepository
from backend.domain.film_id import FilmId
from backend.domain.mix import Mix
from backend.domain.mix_id import MixId
from backend.domain.mix_item import MixItem
from backend.infrastructure.persistence.mappers.mix import orm_to_mix
from backend.infrastructure.persistence.mappers.mix_item import mix_item_to_orm, orm_to_mix_item
from backend.infrastructure.persistence.models.mix import MixORM
from backend.infrastructure.persistence.models.mix_item import MixItemORM


class _Repository(SQLAlchemyAsyncRepository[MixORM]):
    model_type = MixORM


class _ItemRepository(SQLAlchemyAsyncRepository[MixItemORM]):
    model_type = MixItemORM


class SQLAlchemyMixRepository(MixRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = _Repository(session=session)
        self._item_repo = _ItemRepository(session=session)

    async def list_all(self) -> Sequence[Mix]:
        orm_mixes = await self._repo.list()
        return [orm_to_mix(i) for i in orm_mixes]

    async def get_by_id(self, mix_id: MixId) -> Mix:
        try:
            orm_mix = await self._repo.get(mix_id)
        except NotFoundError as exc:
            raise MixNotFoundError from exc
        return orm_to_mix(orm_mix)

    async def get_items_for_mix(self, mix_id: MixId) -> Sequence[MixItem]:
        try:
            orm_mix = await self._repo.get(mix_id)
            orm_items = await self._item_repo.list(OrderBy(field_name="added_at", sort_order="desc"), mix_id=orm_mix.id)
        except NotFoundError as exc:
            raise MixNotFoundError from exc
        return [orm_to_mix_item(item) for item in orm_items]

    async def add_item(self, item: MixItem) -> None:
        orm_item = mix_item_to_orm(item)
        await self._item_repo.add(orm_item)

    async def delete_item(self, mix_id: MixId, film_id: FilmId) -> None:
        try:
            await self._item_repo.delete_where(mix_id=mix_id, film_id=film_id)
        except NotFoundError as exc:
            raise MixNotFoundError from exc

from backend.domain.film_id import FilmId
from backend.domain.mix_id import MixId
from backend.domain.mix_item import MixItem
from backend.infrastructure.persistence.models.mix_item import MixItemORM


def orm_to_mix_item(orm_item: MixItemORM) -> MixItem:
    return MixItem(
        mix_id=MixId(orm_item.mix_id),
        film_id=FilmId(orm_item.film_id),
        added_at=orm_item.added_at,
    )


def mix_item_to_orm(item: MixItem) -> MixItemORM:
    return MixItemORM(
        mix_id=item.mix_id,
        film_id=item.film_id,
        added_at=item.added_at,
    )

import typing
from collections.abc import Sequence

from backend.domain.film_id import FilmId
from backend.domain.mix import Mix
from backend.domain.mix_id import MixId
from backend.domain.mix_item import MixItem


class MixRepository(typing.Protocol):
    async def list_all(self) -> Sequence[Mix]:
        raise NotImplementedError

    async def get_by_id(self, mix_id: MixId) -> Mix:
        raise NotImplementedError

    async def get_items_for_mix(self, mix_id: MixId) -> Sequence[MixItem]:
        raise NotImplementedError

    async def add_item(self, item: MixItem) -> None:
        raise NotImplementedError

    async def delete_item(self, mix_id: MixId, film_id: FilmId) -> None:
        raise NotImplementedError

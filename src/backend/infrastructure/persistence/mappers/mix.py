from backend.domain.mix import Mix
from backend.domain.mix_id import MixId
from backend.infrastructure.persistence.models.mix import MixORM


def orm_to_mix(orm_mix: MixORM) -> Mix:
    return Mix(
        id=MixId(orm_mix.id),
        title=orm_mix.title,
        color1=orm_mix.color1,
        color2=orm_mix.color2,
        color3=orm_mix.color3,
    )


def mix_to_orm(mix: Mix) -> MixORM:
    return MixORM(
        id=mix.id,
        title=mix.title,
        color1=mix.color1,
        color2=mix.color2,
        color3=mix.color3,
    )

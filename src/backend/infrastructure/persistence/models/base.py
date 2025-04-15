from advanced_alchemy.base import CommonTableAttributes
from sqlalchemy.orm import DeclarativeBase


class BaseORM(CommonTableAttributes, DeclarativeBase):
    pass


def register_orm() -> None:
    from backend.infrastructure.persistence.models.auth_token import AuthTokenORM  # noqa: F401
    from backend.infrastructure.persistence.models.film import FilmORM  # noqa: F401
    from backend.infrastructure.persistence.models.film_genre import FilmGenre  # noqa: F401
    from backend.infrastructure.persistence.models.genre import GenreORM  # noqa: F401
    from backend.infrastructure.persistence.models.genre_mood import GenreMoodORM  # noqa: F401
    from backend.infrastructure.persistence.models.mix import MixORM  # noqa: F401
    from backend.infrastructure.persistence.models.mix_item import MixItemORM  # noqa: F401
    from backend.infrastructure.persistence.models.mood import MoodORM  # noqa: F401
    from backend.infrastructure.persistence.models.recommended_film import RecommendedFilmORM  # noqa: F401
    from backend.infrastructure.persistence.models.user import UserORM  # noqa: F401
    from backend.infrastructure.persistence.models.watchlist import WatchlistORM  # noqa: F401
    from backend.infrastructure.persistence.models.watchlist_item import WatchlistItemORM  # noqa: F401

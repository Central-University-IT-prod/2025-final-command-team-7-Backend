import dataclasses
import datetime
import typing

import pydantic

from backend.domain.film_id import FilmId
from backend.domain.genre_id import GenreId
from backend.domain.mix_id import MixId
from backend.domain.user_id import UserId
from backend.domain.watchlist_id import WatchlistId


class UserRegister(pydantic.BaseModel):
    email: typing.Annotated[str, pydantic.StringConstraints(min_length=1)]
    password: typing.Annotated[str, pydantic.StringConstraints(min_length=1)]
    username: typing.Annotated[str, pydantic.StringConstraints(min_length=1, max_length=128)]


class UserLogin(pydantic.BaseModel):
    email: str
    password: str


@dataclasses.dataclass
class UserLoginResponse:
    id: UserId
    username: str | None
    email: str | None
    telegram_id: int | None
    token: str


class FilmCreate(pydantic.BaseModel):
    title: typing.Annotated[str, pydantic.StringConstraints(min_length=1, max_length=512)]
    description: typing.Annotated[str, pydantic.StringConstraints(min_length=1, max_length=5000)]
    genres_ids: list[GenreId] = pydantic.Field(default_factory=list)
    country: typing.Annotated[str, pydantic.StringConstraints(min_length=1, max_length=128)] | None = None
    release_year: pydantic.PositiveInt | None = None


@dataclasses.dataclass
class MixItem:
    film_id: FilmId
    mix_id: MixId
    title: str
    description: str
    added_at: datetime.datetime
    country: str | None = None
    release_year: int | None = None
    poster_url: str | None = None
    tmdb_id: int | None = None


@dataclasses.dataclass
class TelegramLoginRequest:
    tg_code: str


@dataclasses.dataclass
class AuthKeyInfo:
    auth_key: str


@dataclasses.dataclass
class AuthKeyIsConfirmed:
    is_confirmed: bool


@dataclasses.dataclass
class FilmResponse:
    id: FilmId
    title: str
    description: str
    country: str | None = None
    release_year: int | None = None
    poster_url: str | None = None
    tmdb_id: int | None = None
    owner_id: UserId | None = None
    is_liked: bool = False
    is_wish: bool = False
    is_watched: bool = False


@dataclasses.dataclass
class WatchlistItemSchema:
    film_id: FilmId
    watchlist_id: WatchlistId
    title: str
    description: str
    added_at: datetime.datetime
    country: str | None = None
    release_year: int | None = None
    poster_url: str | None = None
    tmdb_id: int | None = None


@dataclasses.dataclass
class WatchlistAdd:
    film_id: FilmId


class WatchlistCreate(pydantic.BaseModel):
    title: typing.Annotated[str, pydantic.StringConstraints(min_length=1)]

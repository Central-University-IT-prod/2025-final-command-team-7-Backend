from typing import Any

from dishka.integrations.litestar import FromDishka, inject
from litestar import Controller, Request, get
from litestar.exceptions import NotFoundException

from backend.application.errors import MixNotFoundError, WatchlistNotFoundError
from backend.application.repositories.film import FilmRepository
from backend.application.repositories.mix import MixRepository
from backend.application.repositories.watchlist import WatchlistRepository
from backend.domain.film import Film
from backend.domain.mix import Mix
from backend.domain.mix_id import MixId
from backend.domain.user import User
from backend.domain.user_id import UserId
from backend.domain.watchlist_type import WatchlistType
from backend.presentation import schemas


class MixController(Controller):
    path = "/mix"
    tags = ("mix",)

    async def _get_film_response(
            self,
            film: Film,
            user_id: UserId | None,
            watchlist_repo: WatchlistRepository,
    ) -> schemas.FilmResponse:
        if not user_id:
            return schemas.FilmResponse(
                id=film.id,
                title=film.title,
                description=film.description,
                country=film.country,
                release_year=film.release_year,
                poster_url=film.poster_url,
                tmdb_id=film.tmdb_id,
                owner_id=film.owner_id,
                is_liked=False,
                is_wish=False,
                is_watched=False,
            )

        try:
            liked_list = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.liked, user_id)
            wish_list = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.wish, user_id)
            watched_list = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.watched, user_id)

            liked_items = await watchlist_repo.get_items_for_watchlist(liked_list.id)
            wish_items = await watchlist_repo.get_items_for_watchlist(wish_list.id)
            watched_items = await watchlist_repo.get_items_for_watchlist(watched_list.id)
        except WatchlistNotFoundError:
            liked_items = wish_items = watched_items = []

        return schemas.FilmResponse(
            id=film.id,
            title=film.title,
            description=film.description,
            country=film.country,
            release_year=film.release_year,
            poster_url=film.poster_url,
            tmdb_id=film.tmdb_id,
            owner_id=film.owner_id,
            is_liked=any(item.film_id == film.id for item in liked_items),
            is_wish=any(item.film_id == film.id for item in wish_items),
            is_watched=any(item.film_id == film.id for item in watched_items),
        )

    @get()
    @inject
    async def list_mixes(self, mix_repo: FromDishka[MixRepository]) -> list[Mix]:
        return list(await mix_repo.list_all())

    @get("/{mix_id:uuid}", raises=(NotFoundException,))
    @inject
    async def get_mix_by_id(
        self,
        mix_id: MixId,
        mix_repo: FromDishka[MixRepository],
    ) -> Mix:
        try:
            return await mix_repo.get_by_id(mix_id)
        except MixNotFoundError as exc:
            raise NotFoundException("Mix not found") from exc

    @get("/{mix_id:uuid}/items", raises=(NotFoundException,))
    @inject
    async def get_items_for_mix(
        self,
        mix_id: MixId,
        request: Request[User, Any, Any],
        mix_repo: FromDishka[MixRepository],
        film_repo: FromDishka[FilmRepository],
        watchlist_repo: FromDishka[WatchlistRepository],
    ) -> list[schemas.FilmResponse]:
        try:
            items = await mix_repo.get_items_for_mix(mix_id)
        except MixNotFoundError as exc:
            raise NotFoundException("Mix not found") from exc
        result: list[schemas.FilmResponse] = []
        for item in items:
            film = await film_repo.get_by_id(item.film_id)
            film_response = await self._get_film_response(
                film, request.user.id if request.user else None, watchlist_repo
            )
            result.append(film_response)
        return result

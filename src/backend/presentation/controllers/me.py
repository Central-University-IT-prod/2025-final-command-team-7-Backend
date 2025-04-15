import datetime
import random
import uuid
from typing import Any

from dishka import FromDishka
from dishka.integrations.litestar import inject
from litestar import Controller, Request, delete, get, post, put, status_codes
from litestar.exceptions import NotFoundException, PermissionDeniedException

from backend.application.committer import Committer
from backend.application.errors import FilmNotFoundError, WatchlistNotFoundError
from backend.application.repositories.film import FilmRepository
from backend.application.repositories.watchlist import WatchlistRepository
from backend.constant import GRADIENTS
from backend.domain.film import Film
from backend.domain.film_id import FilmId
from backend.domain.user import User
from backend.domain.user_id import UserId
from backend.domain.watchlist import Watchlist
from backend.domain.watchlist_id import WatchlistId
from backend.domain.watchlist_item import WatchlistItem
from backend.domain.watchlist_type import WatchlistType
from backend.presentation.schemas import FilmResponse, WatchlistAdd, WatchlistCreate


class MeController(Controller):
    path = "/me"
    tags = ("me",)

    async def _get_film_response(
        self, film: Film, user_id: UserId, watchlist_repo: WatchlistRepository
    ) -> FilmResponse:
        liked_list = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.liked, user_id)
        wish_list = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.wish, user_id)
        watched_list = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.watched, user_id)

        liked_items = await watchlist_repo.get_items_for_watchlist(liked_list.id)
        wish_items = await watchlist_repo.get_items_for_watchlist(wish_list.id)
        watched_items = await watchlist_repo.get_items_for_watchlist(watched_list.id)

        return FilmResponse(
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
    async def get_me(self, request: Request[User, Any, Any]) -> User:
        return request.user

    @get("/watchlists")
    @inject
    async def list_watchlists(
        self, request: Request[User, Any, Any], watchlist_repo: FromDishka[WatchlistRepository]
    ) -> list[Watchlist]:
        watchlists = list(await watchlist_repo.get_all_for_user(request.user.id))
        return [watchlist for watchlist in watchlists if watchlist.type is WatchlistType.custom]

    @post("/watchlists")
    @inject
    async def create_watchlist(
        self,
        data: WatchlistCreate,
        request: Request[User, Any, Any],
        watchlist_repo: FromDishka[WatchlistRepository],
        committer: FromDishka[Committer],
    ) -> Watchlist:
        gradient = random.choice(GRADIENTS)
        watchlist = Watchlist(
            id=WatchlistId(uuid.uuid4()),
            user_id=request.user.id,
            title=data.title,
            type=WatchlistType.custom,
            color1=gradient[0],
            color2=gradient[1],
            color3=gradient[2],
        )
        watchlist = await watchlist_repo.create_watchlist(watchlist)
        await committer.commit()
        return watchlist

    @delete("/watchlists/{watchlist_id:uuid}")
    @inject
    async def delete_watchlist(
        self,
        watchlist_id: WatchlistId,
        request: Request[User, Any, Any],
        watchlist_repo: FromDishka[WatchlistRepository],
        committer: FromDishka[Committer],
    ) -> None:
        watchlist = await watchlist_repo.get_by_id(watchlist_id)
        if watchlist.owner_id != request.user.id:
            raise PermissionDeniedException
        await watchlist_repo.delete_watchlist(watchlist_id)
        await committer.commit()

    @get("/watchlists/{watchlist_id:uuid}", raises=(NotFoundException, PermissionDeniedException))
    @inject
    async def get_watchlist_by_id(
        self,
        watchlist_id: WatchlistId,
        request: Request[User, Any, Any],
        watchlist_repo: FromDishka[WatchlistRepository],
    ) -> Watchlist:
        try:
            watchlist = await watchlist_repo.get_by_id(watchlist_id)
        except WatchlistNotFoundError as exc:
            raise NotFoundException from exc
        if request.user.id != watchlist.user_id:
            raise PermissionDeniedException("Watchlist is not yours")
        return watchlist

    @get("/watchlists/{watchlist_id:uuid}/items", raises=(NotFoundException, PermissionDeniedException))
    @inject
    async def get_watchlist_items_for_id(
        self,
        watchlist_id: WatchlistId,
        request: Request[User, Any, Any],
        watchlist_repo: FromDishka[WatchlistRepository],
        film_repo: FromDishka[FilmRepository],
    ) -> list[FilmResponse]:
        try:
            watchlist = await watchlist_repo.get_by_id(watchlist_id)
        except WatchlistNotFoundError as exc:
            raise NotFoundException from exc

        if request.user.id != watchlist.user_id:
            raise PermissionDeniedException("Watchlist is not yours")

        items = await watchlist_repo.get_items_for_watchlist(watchlist_id)

        result: list[FilmResponse] = []
        for item in items:
            film = await film_repo.get_by_id(item.film_id)
            film_response = await self._get_film_response(film, request.user.id, watchlist_repo)
            result.append(film_response)

        return result

    @put(
        "/watchlists/{watchlist_id:uuid}/items/add",
        raises=(NotFoundException,),
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    @inject
    async def add_item_to_watchlist(
        self,
        data: WatchlistAdd,
        request: Request[User, Any, Any],
        watchlist_id: WatchlistId,
        watchlist_repo: FromDishka[WatchlistRepository],
        committer: FromDishka[Committer],
    ) -> None:
        try:
            watchlist = await watchlist_repo.get_by_id(watchlist_id)
        except WatchlistNotFoundError as exc:
            raise NotFoundException from exc

        if request.user.id != watchlist.user_id:
            raise PermissionDeniedException("Watchlist is not yours")

        item = WatchlistItem(
            watchlist_id=watchlist_id,
            film_id=data.film_id,
            added_at=datetime.datetime.now(datetime.UTC),
        )
        await watchlist_repo.add_item(item)
        await committer.commit()

    @delete(
        "/watchlists/{watchlist_id:uuid}/items/{film_id:uuid}",
        raises=(NotFoundException,),
        status_code=status_codes.HTTP_204_NO_CONTENT,
    )
    @inject
    async def remove_item_from_watchlist(
        self,
        watchlist_id: WatchlistId,
        film_id: FilmId,
        watchlist_repo: FromDishka[WatchlistRepository],
        film_repo: FromDishka[FilmRepository],
        committer: FromDishka[Committer],
    ) -> None:
        try:
            watchlist = await watchlist_repo.get_by_id(watchlist_id)
        except WatchlistNotFoundError as exc:
            raise NotFoundException("Watchlist not found") from exc

        try:
            await film_repo.get_by_id(film_id)
        except FilmNotFoundError as exc:
            raise NotFoundException("Film not found") from exc

        films_ids = [item.film_id for item in await watchlist_repo.get_items_for_watchlist(watchlist.id)]
        if film_id not in films_ids:
            raise NotFoundException("Film not found in watchlist")

        await watchlist_repo.delete_item(watchlist_id, film_id)
        await committer.commit()

    # Liked watchlist
    @get("/watchlists/liked", tags=("liked",))
    @inject
    async def get_liked_watchlist(
        self, request: Request[User, Any, Any], watchlist_repo: FromDishka[WatchlistRepository]
    ) -> Watchlist:
        return await watchlist_repo.get_common_watchlist_for_user(WatchlistType.liked, request.user.id)

    @get("/watchlists/liked/items", raises=(NotFoundException,), tags=("liked",))
    @inject
    async def get_liked_watchlist_items(
        self,
        request: Request[User, Any, Any],
        watchlist_repo: FromDishka[WatchlistRepository],
        film_repo: FromDishka[FilmRepository],
    ) -> list[FilmResponse]:
        liked_watchlist = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.liked, request.user.id)
        items = await watchlist_repo.get_items_for_watchlist(liked_watchlist.id)
        result: list[FilmResponse] = []
        for item in items:
            film = await film_repo.get_by_id(item.film_id)
            film_response = await self._get_film_response(film, request.user.id, watchlist_repo)
            result.append(film_response)

        return result

    @put("/watchlists/liked/items/add", status_code=status_codes.HTTP_204_NO_CONTENT, tags=("liked",))
    @inject
    async def add_item_to_liked_watchlist(
        self,
        data: WatchlistAdd,
        request: Request[User, Any, Any],
        watchlist_repo: FromDishka[WatchlistRepository],
        committer: FromDishka[Committer],
    ) -> None:
        liked_watchlist = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.liked, request.user.id)
        # TODO: Ignore if added existed item.
        item = WatchlistItem(
            watchlist_id=liked_watchlist.id,
            film_id=data.film_id,
            added_at=datetime.datetime.now(datetime.UTC),
        )
        await watchlist_repo.add_item(item)
        await committer.commit()

    @delete("/watchlists/liked/items/{film_id:uuid}", raises=(NotFoundException,), tags=("liked",))
    @inject
    async def remove_item_from_liked_watchlist(
        self,
        film_id: FilmId,
        request: Request[User, Any, Any],
        watchlist_repo: FromDishka[WatchlistRepository],
        film_repo: FromDishka[FilmRepository],
        committer: FromDishka[Committer],
    ) -> None:
        watchlist = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.liked, request.user.id)

        try:
            film = await film_repo.get_by_id(film_id)
        except FilmNotFoundError as exc:
            raise NotFoundException("Film not found") from exc

        films_ids = [item.film_id for item in await watchlist_repo.get_items_for_watchlist(watchlist.id)]
        if film.id not in films_ids:
            raise NotFoundException("Film not found in watchlist")

        await watchlist_repo.delete_item(watchlist.id, film_id)

        await committer.commit()

    @get("/watchlists/watched", tags=("watched",))
    @inject
    async def get_watched_watchlist(
        self, request: Request[User, Any, Any], watchlist_repo: FromDishka[WatchlistRepository]
    ) -> Watchlist:
        return await watchlist_repo.get_common_watchlist_for_user(WatchlistType.watched, request.user.id)

    @get("/watchlists/watched/items", raises=(NotFoundException,), tags=("watched",))
    @inject
    async def get_watched_watchlist_items(
        self,
        request: Request[User, Any, Any],
        watchlist_repo: FromDishka[WatchlistRepository],
        film_repo: FromDishka[FilmRepository],
    ) -> list[FilmResponse]:
        watched_watchlist = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.watched, request.user.id)
        items = await watchlist_repo.get_items_for_watchlist(watched_watchlist.id)
        result: list[FilmResponse] = []
        for item in items:
            film = await film_repo.get_by_id(item.film_id)
            film_response = await self._get_film_response(film, request.user.id, watchlist_repo)
            result.append(film_response)
        return result

    @put("/watchlists/watched/items/add", status_code=status_codes.HTTP_204_NO_CONTENT, tags=("watched",))
    @inject
    async def add_item_to_watched_watchlist(
        self,
        data: WatchlistAdd,
        request: Request[User, Any, Any],
        watchlist_repo: FromDishka[WatchlistRepository],
        committer: FromDishka[Committer],
    ) -> None:
        watched_watchlist = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.watched, request.user.id)
        item = WatchlistItem(
            watchlist_id=watched_watchlist.id,
            film_id=data.film_id,
            added_at=datetime.datetime.now(datetime.UTC),
        )
        await watchlist_repo.add_item(item)
        await committer.commit()

    @delete("/watchlists/watched/items/{film_id:uuid}", raises=(NotFoundException,), tags=("watched",))
    @inject
    async def remove_item_from_watched_watchlist(
        self,
        film_id: FilmId,
        request: Request[User, Any, Any],
        watchlist_repo: FromDishka[WatchlistRepository],
        film_repo: FromDishka[FilmRepository],
        committer: FromDishka[Committer],
    ) -> None:
        watchlist = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.watched, request.user.id)

        try:
            film = await film_repo.get_by_id(film_id)
        except FilmNotFoundError as exc:
            raise NotFoundException("Film not found") from exc

        films_ids = [item.film_id for item in await watchlist_repo.get_items_for_watchlist(watchlist.id)]
        if film.id not in films_ids:
            raise NotFoundException("Film not found in watchlist")

        await watchlist_repo.delete_item(watchlist.id, film_id)

        await committer.commit()

    @get("/watchlists/wish", tags=("wish",))
    @inject
    async def get_wish_watchlist(
        self, request: Request[User, Any, Any], watchlist_repo: FromDishka[WatchlistRepository]
    ) -> Watchlist:
        return await watchlist_repo.get_common_watchlist_for_user(WatchlistType.wish, request.user.id)

    @get("/watchlists/wish/items", raises=(NotFoundException,), tags=("wish",))
    @inject
    async def get_wish_watchlist_items(
        self,
        request: Request[User, Any, Any],
        watchlist_repo: FromDishka[WatchlistRepository],
        film_repo: FromDishka[FilmRepository],
    ) -> list[FilmResponse]:
        wish_watchlist = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.wish, request.user.id)
        items = await watchlist_repo.get_items_for_watchlist(wish_watchlist.id)
        result: list[FilmResponse] = []
        for item in items:
            film = await film_repo.get_by_id(item.film_id)
            film_response = await self._get_film_response(film, request.user.id, watchlist_repo)
            result.append(film_response)

        return result

    @put("/watchlists/wish/items/add", status_code=status_codes.HTTP_204_NO_CONTENT, tags=("wish",))
    @inject
    async def add_item_to_wish_watchlist(
        self,
        data: WatchlistAdd,
        request: Request[User, Any, Any],
        watchlist_repo: FromDishka[WatchlistRepository],
        committer: FromDishka[Committer],
    ) -> None:
        wish_watchlist = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.wish, request.user.id)
        item = WatchlistItem(
            watchlist_id=wish_watchlist.id,
            film_id=data.film_id,
            added_at=datetime.datetime.now(datetime.UTC),
        )
        await watchlist_repo.add_item(item)
        await committer.commit()

    @delete("/watchlists/wish/items/{film_id:uuid}", raises=(NotFoundException,), tags=("wish",))
    @inject
    async def remove_item_from_wish_watchlist(
        self,
        film_id: FilmId,
        request: Request[User, Any, Any],
        watchlist_repo: FromDishka[WatchlistRepository],
        committer: FromDishka[Committer],
    ) -> None:
        try:
            wish_watchlist = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.wish, request.user.id)
            await watchlist_repo.delete_item(wish_watchlist.id, film_id)
            await committer.commit()
        except WatchlistNotFoundError as exc:
            raise NotFoundException("Wish watchlist not found") from exc

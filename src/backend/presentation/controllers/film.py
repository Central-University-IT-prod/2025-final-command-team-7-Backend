import asyncio
import os
import uuid
from typing import Annotated, Any

from dishka.integrations.litestar import FromDishka, inject
from litestar import Controller, Request, delete, get, post, put, status_codes
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.exceptions import ClientException, HTTPException, NotFoundException, PermissionDeniedException
from litestar.params import Body
from litestar.status_codes import HTTP_400_BAD_REQUEST
from sqlalchemy import select

from backend.application.committer import Committer
from backend.application.errors import FilmNotFoundError, GenreNotFoundError, WatchlistNotFoundError
from backend.application.repositories.film import FilmRepository
from backend.application.repositories.watchlist import WatchlistRepository
from backend.domain.film import Film
from backend.domain.film_id import FilmId
from backend.domain.user import User
from backend.domain.user_id import UserId
from backend.domain.watchlist_type import WatchlistType
from backend.infrastructure.persistence.models.film import FilmORM
from backend.infrastructure.services.gpt import GPTService
from backend.infrastructure.services.s3 import S3Service
from backend.infrastructure.services.tmdb import TMDBService
from backend.presentation import schemas


class FilmController(Controller):
    path = "/films"
    tags = ("films",)

    async def _get_film_by_tmdb_id(self, tmdb_id: int, film_repo: FilmRepository) -> Film | None:
        async with film_repo._session as session:
            stmt = select(FilmORM).where(FilmORM.tmdb_id == tmdb_id)
            result = await session.execute(stmt)
            existing_film = result.scalars().first()

        if existing_film:
            return await film_repo.get_by_id(FilmId(existing_film.id))
        return None

    async def _create_film_from_tmdb_data(self, item: dict, film_repo: FilmRepository, committer: Committer) -> Film:
        film = Film(
            id=FilmId(uuid.uuid4()),
            title=item["title"],
            description=item["description"],
            country=item["country"],
            release_year=item["release_year"],
            poster_url=item["poster_url"],
            tmdb_id=item["tmdb_id"],
            owner_id=None,
        )
        film = await film_repo.create(film)
        await committer.commit()
        return film

    async def _process_tmdb_result(
            self,
            item: dict,
            user_id: UserId | None,
            film_repo: FilmRepository,
            watchlist_repo: WatchlistRepository,
            committer: Committer,
            seen_tmdb_ids: set,
    ) -> schemas.FilmResponse | None:
        tmdb_id = item.get("tmdb_id")
        if not tmdb_id:
            return None

        if tmdb_id in seen_tmdb_ids:
            return None

        film = await self._get_film_by_tmdb_id(tmdb_id, film_repo)

        if not film:
            try:
                film = await self._create_film_from_tmdb_data(item, film_repo, committer)
            except Exception:
                return None

        film_response = await self._get_film_response(film, user_id, watchlist_repo)
        seen_tmdb_ids.add(tmdb_id)
        return film_response

    async def _search_by_title(
        self,
        title: str,
        limit: int,
        user_id: UserId | None,
        tmdb_service: TMDBService,
        film_repo: FilmRepository,
        watchlist_repo: WatchlistRepository,
        committer: Committer,
    ) -> list[schemas.FilmResponse]:
        results = []
        seen_tmdb_ids = set()
        total_results_limit = 20

        try:
            kinopoisk_results = await tmdb_service.search_kinopoisk_and_get_details(title, limit=total_results_limit)
        except Exception:
            kinopoisk_results = await tmdb_service.search_all_and_get_details(title, limit=total_results_limit)

        for item in kinopoisk_results:
            film_response = await self._process_tmdb_result(
                item, user_id, film_repo, watchlist_repo, committer, seen_tmdb_ids
            )
            if film_response:
                results.append(film_response)

        return results[:limit]

    async def _distribute_slots(self, suggestions, total_slots: int) -> list[int]:
        max_suggestions = min(len(suggestions), 10)
        total_confidence = sum(s.confidence for s in suggestions[:max_suggestions])

        min_slots = 1
        max_slots_per_title = 5
        slots = []
        remaining_slots = total_slots - (min_slots * max_suggestions)
        freed_slots = 0

        for s in suggestions[:max_suggestions]:
            additional_slots = int((s.confidence / total_confidence) * remaining_slots) if total_confidence > 0 else 0
            total_slots_for_item = min(min_slots + additional_slots, max_slots_per_title)
            original_slots = min_slots + additional_slots
            if original_slots > max_slots_per_title:
                freed_slots += original_slots - max_slots_per_title
            slots.append(total_slots_for_item)

        if freed_slots > 0:
            eligible_indices = [i for i, slot in enumerate(slots) if slot < max_slots_per_title]
            eligible_indices.sort(key=lambda i: suggestions[i].confidence, reverse=True)
            for i in eligible_indices:
                if freed_slots <= 0:
                    break
                available_slots = max_slots_per_title - slots[i]
                to_add = min(available_slots, freed_slots)
                slots[i] += to_add
                freed_slots -= to_add

        while sum(slots) < total_slots:
            eligible_indices = [i for i, slot in enumerate(slots) if slot < max_slots_per_title]
            if not eligible_indices:
                break
            max_confidence_index = max(eligible_indices, key=lambda i: suggestions[i].confidence)
            slots[max_confidence_index] += 1

        return slots

    async def _fetch_search_results(self, suggestions: list, slots: list[int], tmdb_service: TMDBService) -> list[dict]:
        tasks = []

        async def kinopoisk_or_tmdb(q: str, s: int) -> list[dict[str, Any]]:
            try:
                return await tmdb_service.search_kinopoisk_and_get_details(q, limit=s)
            except Exception:
                return await tmdb_service.search_all_and_get_details(q, limit=s)

        for i, suggestion in enumerate(suggestions):
            if i >= len(slots) or slots[i] <= 0:
                continue
            tasks.append(kinopoisk_or_tmdb(suggestion.media_name, slots[i]))

        tmdb_results_list = await asyncio.gather(*tasks, return_exceptions=True)

        all_results = []
        for item_or_exc in tmdb_results_list:
            if isinstance(item_or_exc, Exception):
                continue
            all_results.extend(item_or_exc)

        return all_results

    async def _search_by_description(
            self,
            description: str,
            title: str | None,
            limit: int,
            user_id: UserId | None,
            gpt_service: GPTService,
            tmdb_service: TMDBService,
            film_repo: FilmRepository,
            watchlist_repo: WatchlistRepository,
            committer: Committer,
    ) -> list[schemas.FilmResponse]:
        results = []
        seen_tmdb_ids = set()
        total_results_limit = 20

        try:
            kinopoisk_direct_results = await tmdb_service.search_kinopoisk_and_get_details(description, limit=2)

            for item in kinopoisk_direct_results:
                film_response = await self._process_tmdb_result(
                    item, user_id, film_repo, watchlist_repo, committer, seen_tmdb_ids
                )
                if film_response:
                    results.append(film_response)
        except Exception:
            pass

        gpt_result = await gpt_service.identify_multiple_media(description, limit=10)
        if gpt_result.not_found or not gpt_result.suggestions:
            return results

        suggestions = sorted(gpt_result.suggestions, key=lambda x: x.confidence, reverse=True)

        slots = await self._distribute_slots(suggestions, total_results_limit)

        tmdb_results = await self._fetch_search_results(suggestions[: len(slots)], slots, tmdb_service)

        for item in tmdb_results:
            film_response = await self._process_tmdb_result(
                item, user_id, film_repo, watchlist_repo, committer, seen_tmdb_ids
            )
            if film_response:
                results.append(film_response)

        if len(results) < limit and title:
            remaining_search_limit = total_results_limit - len(results)
            if remaining_search_limit > 0:
                additional_results = await self._get_additional_results_by_title(
                    title, remaining_search_limit, tmdb_service
                )

                for item in additional_results:
                    film_response = await self._process_tmdb_result(
                        item, user_id, film_repo, watchlist_repo, committer, seen_tmdb_ids
                    )
                    if film_response:
                        results.append(film_response)

        return results[:limit]

    async def _get_additional_results_by_title(self, title: str, limit: int, tmdb_service: TMDBService) -> list[dict]:
        """Get additional results by title as fallback"""
        try:
            return await tmdb_service.search_kinopoisk_and_get_details(title, limit=limit)
        except Exception:
            return await tmdb_service.search_all_and_get_details(title, limit=limit)

    async def _get_film_response(
        self, film: Film, user_id: UserId | None, watchlist_repo: WatchlistRepository
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

    @post()
    @inject
    async def create_film(
        self,
        data: schemas.FilmCreate,
        request: Request[User, Any, Any],
        film_repo: FromDishka[FilmRepository],
        watchlist_repo: FromDishka[WatchlistRepository],
        committer: FromDishka[Committer],
    ) -> schemas.FilmResponse:
        film = Film(
            id=FilmId(uuid.uuid4()),
            title=data.title,
            description=data.description,
            country=data.country,
            release_year=data.release_year,
            poster_url=None,
            tmdb_id=None,
            owner_id=request.user.id,
        )
        film = await film_repo.create(film)
        try:
            await film_repo.update_genres(film.id, data.genres_ids)
        except GenreNotFoundError as exc:
            raise ClientException(detail="Genre not found") from exc
        await committer.commit()
        return await self._get_film_response(film, request.user.id, watchlist_repo)

    @put("/{film_id:uuid}/poster", status_code=status_codes.HTTP_204_NO_CONTENT)
    @inject
    async def upload_poster_to_film(
        self,
        film_id: FilmId,
        request: Request[User, Any, Any],
        film_repo: FromDishka[FilmRepository],
        s3_service: FromDishka[S3Service],
        committer: FromDishka[Committer],
        data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
    ) -> None:
        try:
            film = await film_repo.get_by_id(film_id)
        except FilmNotFoundError as exc:
            raise NotFoundException(detail="Film not found") from exc

        if film.owner_id is None or film.owner_id != request.user.id:
            raise PermissionDeniedException(detail="Film is not owned by you")

        file_extension = os.path.splitext(data.filename)[1][1:] if data.filename else ""
        if not file_extension or data.content_type not in ["image/jpeg", "image/png", "image/webp"]:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only JPEG, PNG, and WebP images are allowed.",
            )

        file_content = await data.read()

        if film.poster_url:
            await s3_service.delete_file_from_url(film.poster_url)

        try:
            poster_url = await s3_service.upload_file(file_content, file_extension)
            film.poster_url = poster_url
            await film_repo.update(film)
            await committer.commit()
        except Exception as exc:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Failed to upload poster: {exc!s}") from exc

    @delete("/{film_id:uuid}/poster", status_code=status_codes.HTTP_204_NO_CONTENT)
    @inject
    async def delete_poster_from_film(
        self,
        film_id: FilmId,
        request: Request[User, Any, Any],
        film_repo: FromDishka[FilmRepository],
        s3_service: FromDishka[S3Service],
        committer: FromDishka[Committer],
    ) -> None:
        try:
            film = await film_repo.get_by_id(film_id)
        except FilmNotFoundError as exc:
            raise NotFoundException(detail="Film not found") from exc

        if film.owner_id is None or film.owner_id != request.user.id:
            raise PermissionDeniedException(detail="Film is not owned by you")

        if film.poster_url:
            await s3_service.delete_file_from_url(film.poster_url)

        film.poster_url = None
        await film_repo.update(film)
        await committer.commit()

    @get("/{film_id:uuid}", raises=(NotFoundException,))
    @inject
    async def get_film_by_id(
        self,
        film_id: FilmId,
        request: Request[User, Any, Any],
        film_repo: FromDishka[FilmRepository],
        watchlist_repo: FromDishka[WatchlistRepository],
    ) -> schemas.FilmResponse:
        try:
            film = await film_repo.get_by_id(film_id)
            return await self._get_film_response(film, request.user.id if request.user else None, watchlist_repo)
        except FilmNotFoundError as exc:
            raise NotFoundException from exc

    @put("/{film_id:uuid}", raises=(PermissionDeniedException,))
    @inject
    async def update_film(
        self,
        data: schemas.FilmCreate,
        film_id: FilmId,
        request: Request[User, Any, Any],
        film_repo: FromDishka[FilmRepository],
        watchlist_repo: FromDishka[WatchlistRepository],
        committer: FromDishka[Committer],
    ) -> schemas.FilmResponse:
        try:
            film = await film_repo.get_by_id(film_id)
        except FilmNotFoundError as exc:
            raise NotFoundException from exc
        if film.owner_id is None or film.owner_id != request.user.id:
            raise PermissionDeniedException(detail="Film is not owned by you")
        film.title = data.title
        film.description = data.description
        film.country = data.country
        film.release_year = data.release_year
        film = await film_repo.update(film)
        try:
            await film_repo.update_genres(film.id, data.genres_ids)
        except GenreNotFoundError as exc:
            raise ClientException(detail="Genre not found") from exc
        await committer.commit()
        return await self._get_film_response(film, request.user.id, watchlist_repo)

    @get("/search")
    @inject
    async def search_film(
        self,
        request: Request[User, Any, Any],
        gpt_service: FromDishka[GPTService],
        tmdb_service: FromDishka[TMDBService],
        film_repo: FromDishka[FilmRepository],
        watchlist_repo: FromDishka[WatchlistRepository],
        committer: FromDishka[Committer],
        title: str | None = None,
        description: str | None = None,
        limit: int = 10,
    ) -> list[schemas.FilmResponse]:
        user_id = request.user.id if request.user else None

        if title and not description:
            return await self._search_by_title(
                title, limit, user_id, tmdb_service, film_repo, watchlist_repo, committer
            )

        if description:
            return await self._search_by_description(
                description, title, limit, user_id, gpt_service, tmdb_service, film_repo, watchlist_repo, committer
            )

        return []

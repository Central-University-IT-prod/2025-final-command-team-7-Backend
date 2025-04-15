import datetime
import random
import uuid
from typing import Any

from dishka.integrations.litestar import FromDishka, inject
from litestar import Controller, Request, post
from litestar.exceptions import NotFoundException
from sqlalchemy import select, func

from backend.application.committer import Committer
from backend.application.errors import WatchlistNotFoundError, FilmNotFoundError
from backend.application.repositories.film import FilmRepository
from backend.application.repositories.genre import GenreRepository
from backend.application.repositories.mood import MoodRepository
from backend.application.repositories.recommended_film import RecommendedFilmRepository
from backend.application.repositories.watchlist import WatchlistRepository
from backend.domain.film import Film
from backend.domain.film_id import FilmId
from backend.domain.genre_id import GenreId
from backend.domain.mood_id import MoodId
from backend.domain.recommended_film import RecommendedFilm
from backend.domain.user import User
from backend.domain.user_id import UserId
from backend.domain.watchlist_type import WatchlistType
from backend.infrastructure.persistence.models.film import FilmORM
from backend.infrastructure.persistence.models.film_genre import FilmGenre
from backend.infrastructure.persistence.models.genre import GenreORM
from backend.infrastructure.persistence.models.genre_mood import GenreMoodORM
from backend.infrastructure.persistence.models.watchlist import WatchlistORM
from backend.infrastructure.persistence.models.watchlist_item import WatchlistItemORM
from backend.infrastructure.persistence.models.recommended_film import RecommendedFilmORM
from backend.infrastructure.services.tmdb import TMDBService
from backend.presentation.schemas import FilmResponse


class RecommendController(Controller):
    path = "/recommend"
    tags = ("recommend",)

    async def _get_film_response(
        self,
        film: Film,
        user_id: UserId,
        watchlist_repo: WatchlistRepository,
    ) -> FilmResponse:
        try:
            liked_list = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.liked, user_id)
            wish_list = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.wish, user_id)
            watched_list = await watchlist_repo.get_common_watchlist_for_user(WatchlistType.watched, user_id)

            liked_items = await watchlist_repo.get_items_for_watchlist(liked_list.id)
            wish_items = await watchlist_repo.get_items_for_watchlist(wish_list.id)
            watched_items = await watchlist_repo.get_items_for_watchlist(watched_list.id)
        except WatchlistNotFoundError:
            liked_items = wish_items = watched_items = []

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

    async def _recommend_from_tmdb(
        self,
        film_repo: FilmRepository,
        recommended_film_repo: RecommendedFilmRepository,
        watchlist_repo: WatchlistRepository,
        tmdb_service: TMDBService,
        committer: Committer,
        user_id: UserId,
        final_genre_ids: list[GenreId],
        movie_type: str | None,
        recently_recommended_film_ids: set[FilmId],
    ) -> FilmResponse:
        genre_names = []
        if final_genre_ids:
            async with film_repo._session as session:
                stmt = select(GenreORM).where(GenreORM.id.in_(final_genre_ids))
                existing_genres = (await session.execute(stmt)).scalars().all()
            genre_names = [g.name for g in existing_genres]

        excluded_tmdb_ids = []
        for fid in recently_recommended_film_ids:
            try:
                existing_film = await film_repo.get_by_id(fid)
                if existing_film.tmdb_id is not None:
                    excluded_tmdb_ids.append(existing_film.tmdb_id)
            except FilmNotFoundError:
                pass

        tmdb_movie = await tmdb_service.get_random_tmdb_movie(
            genres=genre_names or None,
            movie_type=movie_type,
            excluded_ids=excluded_tmdb_ids
        )
        if not tmdb_movie:
            raise NotFoundException("No suitable film found from TMDB fallback")

        tmdb_id = tmdb_movie["tmdb_id"]
        session = film_repo._session

        existing_film_orm = await session.scalar(
            select(FilmORM).where(FilmORM.tmdb_id == tmdb_id)
        )
        if existing_film_orm:
            film = Film(
                id=FilmId(existing_film_orm.id),
                title=existing_film_orm.title,
                description=existing_film_orm.description,
                country=existing_film_orm.country,
                release_year=existing_film_orm.release_year,
                poster_url=existing_film_orm.poster_url,
                tmdb_id=existing_film_orm.tmdb_id,
                owner_id=existing_film_orm.owner_id and UserId(existing_film_orm.owner_id),
            )
        else:
            film = Film(
                id=FilmId(uuid.uuid4()),
                title=tmdb_movie["title"],
                description=tmdb_movie["description"],
                country=tmdb_movie["country"],
                release_year=tmdb_movie["release_year"],
                poster_url=tmdb_movie["poster_url"],
                tmdb_id=tmdb_id,
                owner_id=None,
            )
            film = await film_repo.create(film)

            genre_orms_all = (await session.execute(select(GenreORM))).scalars().all()
            name_to_id = {g.name.lower(): g.id for g in genre_orms_all}
            found_genres_ids = []
            for gdict in tmdb_movie.get("genres", []):
                gname = gdict.get("name", "").lower()
                if gname in name_to_id:
                    found_genres_ids.append(name_to_id[gname])

            if not found_genres_ids and final_genre_ids:
                found_genres_ids = [final_genre_ids[0]]

            await film_repo.update_genres(film.id, found_genres_ids)
            await session.flush()

        new_rec = RecommendedFilm(
            id=uuid.uuid4(),
            user_id=user_id,
            film_id=film.id,
            recommended_at=datetime.datetime.now(datetime.UTC),
        )
        await recommended_film_repo.create(new_rec)

        await committer.commit()

        return await self._get_film_response(film, user_id, watchlist_repo)

    async def _get_random_wish_film_from_db(
        self,
        user_id: UserId,
        time_threshold: datetime.datetime,
        film_repo: FilmRepository,
    ) -> Film | None:
        session = film_repo._session

        stmt = (
            select(FilmORM)
            .join(WatchlistItemORM, WatchlistItemORM.film_id == FilmORM.id)
            .join(WatchlistORM, WatchlistORM.id == WatchlistItemORM.watchlist_id)
            .outerjoin(
                RecommendedFilmORM,
                (RecommendedFilmORM.film_id == FilmORM.id)
                & (RecommendedFilmORM.user_id == user_id)
                & (RecommendedFilmORM.recommended_at >= time_threshold),
            )
            .where(WatchlistORM.user_id == user_id)
            .where(WatchlistORM.type == WatchlistType.wish)
            .where(RecommendedFilmORM.film_id.is_(None))
            .order_by(func.random())
            .limit(1)
        )
        result = await session.execute(stmt)
        film_orm = result.scalar_one_or_none()
        if not film_orm:
            return None

        return Film(
            id=FilmId(film_orm.id),
            title=film_orm.title,
            description=film_orm.description,
            country=film_orm.country,
            release_year=film_orm.release_year,
            poster_url=film_orm.poster_url,
            tmdb_id=film_orm.tmdb_id,
            owner_id=film_orm.owner_id and UserId(film_orm.owner_id),
        )

    @post()
    @inject
    async def recommend_film(
        self,
        request: Request[User, Any, Any],
        mood_repo: FromDishka[MoodRepository],
        genre_repo: FromDishka[GenreRepository],
        film_repo: FromDishka[FilmRepository],
        recommended_film_repo: FromDishka[RecommendedFilmRepository],
        watchlist_repo: FromDishka[WatchlistRepository],
        tmdb_service: FromDishka[TMDBService],
        committer: FromDishka[Committer],
        moods_ids: list[MoodId] | None = None,
        genres_ids: list[GenreId] | None = None,
        movie_type: str | None = None,
    ) -> FilmResponse:
        user_id = request.user.id

        final_genre_ids = genres_ids or []
        if moods_ids:
            async with film_repo._session as session:
                stmt = select(GenreMoodORM).where(GenreMoodORM.mood_id.in_(moods_ids))
                mood_genres = (await session.execute(stmt)).scalars().all()
            mood_genre_ids = {mg.genre_id for mg in mood_genres}
            final_genre_ids = list(set(final_genre_ids) | mood_genre_ids)

        time_threshold = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=24)

        film = await self._get_random_wish_film_from_db(user_id, time_threshold, film_repo)

        if film is not None:
            new_rec = RecommendedFilm(
                id=uuid.uuid4(),
                user_id=user_id,
                film_id=film.id,
                recommended_at=datetime.datetime.now(datetime.UTC),
            )
            await recommended_film_repo.create(new_rec)
            await committer.commit()

            return await self._get_film_response(film, user_id, watchlist_repo)

        recent_recs = await recommended_film_repo.get_recent_by_user(user_id, time_threshold)
        recently_recommended_film_ids = {r.film_id for r in recent_recs}

        return await self._recommend_from_tmdb(
            film_repo=film_repo,
            recommended_film_repo=recommended_film_repo,
            watchlist_repo=watchlist_repo,
            tmdb_service=tmdb_service,
            committer=committer,
            user_id=user_id,
            final_genre_ids=final_genre_ids,
            movie_type=movie_type,
            recently_recommended_film_ids=recently_recommended_film_ids,
        )

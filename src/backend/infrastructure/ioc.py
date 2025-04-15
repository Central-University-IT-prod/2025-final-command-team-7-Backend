import os
from collections.abc import AsyncGenerator

import dishka
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from backend.application.committer import Committer
from backend.application.password_hasher import PasswordHasher
from backend.application.repositories.auth_token import AuthTokenRepository
from backend.application.repositories.film import FilmRepository
from backend.application.repositories.genre import GenreRepository
from backend.application.repositories.mix import MixRepository
from backend.application.repositories.mood import MoodRepository
from backend.application.repositories.recommended_film import RecommendedFilmRepository
from backend.application.repositories.user import UserRepository
from backend.application.repositories.watchlist import WatchlistRepository
from backend.infrastructure.argon2_password_hasher import Argon2PasswordHasher
from backend.infrastructure.persistence.committer import SQLAlchemyCommitter
from backend.infrastructure.persistence.repositories.auth_token import SQLAlchemyAuthTokenRepository
from backend.infrastructure.persistence.repositories.film import SQLAlchemyFilmRepository
from backend.infrastructure.persistence.repositories.genre import SQLAlchemyGenreRepository
from backend.infrastructure.persistence.repositories.mix import SQLAlchemyMixRepository
from backend.infrastructure.persistence.repositories.mood import SQLAlchemyMoodRepository
from backend.infrastructure.persistence.repositories.recommended_film import SQLAlchemyRecommendedFilmRepository
from backend.infrastructure.persistence.repositories.user import SQLAlchemyUserRepository
from backend.infrastructure.persistence.repositories.watchlist import SQLAlchemyWatchlistRepository
from backend.infrastructure.services.gpt import GPTService
from backend.infrastructure.services.s3 import S3Service
from backend.infrastructure.services.tmdb import TMDBService


class MainProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_sa_engine(self) -> AsyncGenerator[AsyncEngine]:
        engine = create_async_engine(os.environ["POSTGRES_DSN"])
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    def get_sa_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(engine)

    @provide(scope=Scope.REQUEST)
    async def get_sa_session(self, sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncGenerator[AsyncSession]:
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.APP)
    def get_gpt_service(self) -> GPTService:
        return GPTService()

    @provide(scope=Scope.APP)
    def get_s3_service(self) -> S3Service:
        return S3Service()

    @provide(scope=Scope.APP)
    async def get_tmdb_service(self) -> AsyncGenerator[TMDBService]:
        service = TMDBService()
        yield service
        await service.close()

    committer = dishka.provide(SQLAlchemyCommitter, provides=Committer, scope=Scope.REQUEST)
    user_repo = dishka.provide(SQLAlchemyUserRepository, provides=UserRepository, scope=Scope.REQUEST)
    film_repo = dishka.provide(SQLAlchemyFilmRepository, provides=FilmRepository, scope=Scope.REQUEST)
    mix_repo = dishka.provide(SQLAlchemyMixRepository, provides=MixRepository, scope=Scope.REQUEST)
    watchlist_repo = dishka.provide(SQLAlchemyWatchlistRepository, provides=WatchlistRepository, scope=Scope.REQUEST)
    mood_repo = dishka.provide(SQLAlchemyMoodRepository, provides=MoodRepository, scope=Scope.REQUEST)
    genre_repo = dishka.provide(SQLAlchemyGenreRepository, provides=GenreRepository, scope=Scope.REQUEST)
    auth_token_repo = dishka.provide(SQLAlchemyAuthTokenRepository, provides=AuthTokenRepository, scope=Scope.REQUEST)
    recommended_film_repo = dishka.provide(
        SQLAlchemyRecommendedFilmRepository, provides=RecommendedFilmRepository, scope=Scope.REQUEST
    )
    password_hasher = dishka.provide(Argon2PasswordHasher, provides=PasswordHasher, scope=Scope.REQUEST)

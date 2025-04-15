from dishka import make_async_container
from dishka.integrations.litestar import setup_dishka
from litestar import Litestar, Router
from litestar.config.cors import CORSConfig
from litestar.logging.config import LoggingConfig
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin, SwaggerRenderPlugin

from backend.infrastructure.ioc import MainProvider
from backend.presentation.controllers.auth import AuthController
from backend.presentation.controllers.film import FilmController
from backend.presentation.controllers.genre import GenresController
from backend.presentation.controllers.me import MeController
from backend.presentation.controllers.mix import MixController
from backend.presentation.controllers.mood import MoodController
from backend.presentation.controllers.recommend import RecommendController
from backend.presentation.controllers.telegram_auth import TelegramAuthController
from backend.presentation.jwt import jwt_auth


def create_app() -> Litestar:
    router = Router(
        "/api/v1",
        route_handlers=(
            FilmController,
            MixController,
            MeController,
            GenresController,
            MoodController,
            AuthController,
            TelegramAuthController,
            RecommendController,
        ),
    )
    app = Litestar(
        route_handlers=(router,),
        on_app_init=(jwt_auth.on_app_init,),
        cors_config=CORSConfig(
            allow_origins=[
                "http://localhost:5173",
                "*",
            ],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
        ),
        openapi_config=OpenAPIConfig(
            title="Film Hub",
            version="1.0.0",
            path="/api/schema",
            render_plugins=(
                SwaggerRenderPlugin(),
                ScalarRenderPlugin(),
            ),
        ),
        logging_config=LoggingConfig(
            log_exceptions="always",
        ),
    )
    container = make_async_container(MainProvider())
    setup_dishka(container, app)
    return app

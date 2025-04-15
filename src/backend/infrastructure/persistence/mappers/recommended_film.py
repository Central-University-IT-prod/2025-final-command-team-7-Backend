from backend.domain.film_id import FilmId
from backend.domain.recommended_film import RecommendedFilm
from backend.domain.user_id import UserId
from backend.infrastructure.persistence.models.recommended_film import RecommendedFilmORM


def orm_to_recommended_film(orm_recommendation: RecommendedFilmORM) -> RecommendedFilm:
    return RecommendedFilm(
        id=orm_recommendation.id,
        user_id=UserId(orm_recommendation.user_id),
        film_id=FilmId(orm_recommendation.film_id),
        recommended_at=orm_recommendation.recommended_at,
    )


def recommended_film_to_orm(recommendation: RecommendedFilm) -> RecommendedFilmORM:
    return RecommendedFilmORM(
        id=recommendation.id,
        user_id=recommendation.user_id,
        film_id=recommendation.film_id,
        recommended_at=recommendation.recommended_at,
    )

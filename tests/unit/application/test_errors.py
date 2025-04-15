import pytest

from backend.application.errors import (
    ApplicationError,
    FilmNotFoundError,
    UserNotFoundError,
    WatchlistNotFoundError,
    MixNotFoundError,
    MoodNotFoundError,
    GenreNotFoundError,
    DuplicateEntryError,
    AuthTokenNotFoundError,
)


class TestApplicationErrors:
    def test_application_error_is_exception(self):
        
        assert issubclass(ApplicationError, Exception)

    def test_film_not_found_error_is_application_error(self):
        
        error = FilmNotFoundError()

        
        assert isinstance(error, ApplicationError)

    def test_user_not_found_error_is_application_error(self):
        
        error = UserNotFoundError()

        
        assert isinstance(error, ApplicationError)

    def test_watchlist_not_found_error_is_application_error(self):
        
        error = WatchlistNotFoundError()

        
        assert isinstance(error, ApplicationError)

    def test_mix_not_found_error_is_application_error(self):
        
        error = MixNotFoundError()

        
        assert isinstance(error, ApplicationError)

    def test_mood_not_found_error_is_application_error(self):
        
        error = MoodNotFoundError()

        
        assert isinstance(error, ApplicationError)

    def test_genre_not_found_error_is_application_error(self):
        
        error = GenreNotFoundError()

        
        assert isinstance(error, ApplicationError)

    def test_duplicate_entry_error_is_application_error(self):
        
        error = DuplicateEntryError()

        
        assert isinstance(error, ApplicationError)

    def test_auth_token_not_found_error_is_application_error(self):
        
        error = AuthTokenNotFoundError()

        
        assert isinstance(error, ApplicationError)

    def test_errors_can_include_message(self):
        
        message = "Test error message"

        
        error = FilmNotFoundError(message)

        
        assert str(error) == message
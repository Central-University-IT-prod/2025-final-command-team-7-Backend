class ApplicationError(Exception):
    pass


class FilmNotFoundError(ApplicationError):
    pass


class UserNotFoundError(ApplicationError):
    pass


class WatchlistNotFoundError(ApplicationError):
    pass


class MixNotFoundError(ApplicationError):
    pass


class MoodNotFoundError(ApplicationError):
    pass


class GenreNotFoundError(ApplicationError):
    pass


class DuplicateEntryError(ApplicationError):
    pass


class AuthTokenNotFoundError(ApplicationError):
    pass

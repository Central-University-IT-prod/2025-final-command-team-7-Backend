import enum


@enum.unique
class WatchlistType(enum.StrEnum):
    liked = enum.auto()
    wish = enum.auto()
    watched = enum.auto()
    custom = enum.auto()

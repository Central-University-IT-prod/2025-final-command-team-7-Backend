import uuid

import pytest

from backend.domain.watchlist import Watchlist
from backend.domain.watchlist_id import WatchlistId
from backend.domain.user_id import UserId
from backend.domain.watchlist_type import WatchlistType


class TestWatchlist:
    def test_create_watchlist(self):
        # Arrange
        watchlist_id = WatchlistId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())

        # Act
        watchlist = Watchlist(
            id=watchlist_id,
            user_id=user_id,
            title="My Favorites",
            type=WatchlistType.custom,
            color1="#FF0000",
            color2="#00FF00",
            color3="#0000FF"
        )

        # Assert
        assert watchlist.id == watchlist_id
        assert watchlist.user_id == user_id
        assert watchlist.title == "My Favorites"
        assert watchlist.type == WatchlistType.custom
        assert watchlist.color1 == "#FF0000"
        assert watchlist.color2 == "#00FF00"
        assert watchlist.color3 == "#0000FF"

    def test_watchlist_gradient_property(self):
        # Arrange
        watchlist_id = WatchlistId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())

        watchlist = Watchlist(
            id=watchlist_id,
            user_id=user_id,
            title="My Favorites",
            type=WatchlistType.custom,
            color1="#FF0000",
            color2="#00FF00",
            color3="#0000FF"
        )



        # Assert
        assert watchlist.color1 == "#FF0000"
        assert watchlist.color2 == "#00FF00"
        assert watchlist.color3 == "#0000FF"

    def test_watchlist_common_types(self):
        # Arrange
        watchlist_id = WatchlistId(uuid.uuid4())
        user_id = UserId(uuid.uuid4())

        # Act & Assert - Check that we can create all common watchlist types
        for watchlist_type in [WatchlistType.liked, WatchlistType.watched, WatchlistType.wish]:
            watchlist = Watchlist(
                id=watchlist_id,
                user_id=user_id,
                title=f"My {watchlist_type} list",
                type=watchlist_type,
                color1="#FF0000",
                color2="#00FF00",
                color3="#0000FF"
            )

            assert watchlist.type == watchlist_type
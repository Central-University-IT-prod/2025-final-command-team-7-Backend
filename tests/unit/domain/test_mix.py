import uuid

import pytest

from backend.domain.mix import Mix
from backend.domain.mix_id import MixId


class TestMix:
    def test_create_mix(self):
        # Arrange
        mix_id = MixId(uuid.uuid4())

        # Act
        mix = Mix(
            id=mix_id,
            title="Action Movies",
            color1="#FF0000",
            color2="#00FF00",
            color3="#0000FF"
        )

        # Assert
        assert mix.id == mix_id
        assert mix.title == "Action Movies"
        assert mix.color1 == "#FF0000"
        assert mix.color2 == "#00FF00"
        assert mix.color3 == "#0000FF"

    def test_mix_gradient_property(self):
        # Arrange
        mix_id = MixId(uuid.uuid4())

        # Act
        mix = Mix(
            id=mix_id,
            title="Action Movies",
            color1="#FF0000",
            color2="#00FF00",
            color3="#0000FF"
        )

        # Assert
        assert mix.color1 == "#FF0000"
        assert mix.color2 == "#00FF00"
        assert mix.color3 == "#0000FF"
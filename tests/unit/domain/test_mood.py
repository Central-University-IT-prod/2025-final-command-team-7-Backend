import uuid

import pytest

from backend.domain.mood import Mood
from backend.domain.mood_id import MoodId


class TestMood:
    def test_create_mood(self):
        
        mood_id = MoodId(uuid.uuid4())

        
        mood = Mood(
            id=mood_id,
            name="Happy"
        )

        
        assert mood.id == mood_id
        assert mood.name == "Happy"
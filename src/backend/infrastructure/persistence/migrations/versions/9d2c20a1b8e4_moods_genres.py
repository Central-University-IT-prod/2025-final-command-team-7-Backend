"""moods & genres

Revision ID: 9d2c20a1b8e4
Revises: 88269ef4a4a8
Create Date: 2025-03-03 23:19:24.943623

"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9d2c20a1b8e4"
down_revision: str | None = "88269ef4a4a8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


MOODS_AND_GENRES = {
    "Весёлое, позитивное": [
        "комедия",
        "мультфильм",
        "семейный",
        "приключения",
        "мелодрама",
        "музыка",
        "фэнтези",
        "боевик",
    ],
    "Романтическое": ["мелодрама", "драма", "музыка", "комедия", "семейный", "история", "приключения", "фэнтези"],
    "Напряжённое, захватывающее": [
        "боевик",
        "триллер",
        "детектив",
        "криминал",
        "фантастика",
        "ужасы",
        "военный",
        "приключения",
    ],
    "Страшное, пугающее": ["ужасы", "триллер", "детектив", "фантастика", "криминал", "драма", "боевик", "история"],
    "Фантастическое, воображаемое": [
        "фантастика",
        "фэнтези",
        "приключения",
        "мультфильм",
        "семейный",
        "боевик",
        "комедия",
        "ужасы",
    ],
    "Историческое, познавательное": [
        "история",
        "военный",
        "документальный",
        "драма",
        "криминал",
        "вестерн",
        "телевизионный фильм",
        "детектив",
    ],
    "Серьёзное, драматическое": [
        "драма",
        "военный",
        "история",
        "криминал",
        "детектив",
        "триллер",
        "боевик",
        "документальный",
    ],
    "Ностальгическое, классическое": [
        "вестерн",
        "телевизионный фильм",
        "история",
        "драма",
        "приключения",
        "военный",
        "мелодрама",
        "комедия",
    ],
    "Лёгкое, расслабляющее": [
        "комедия",
        "семейный",
        "мультфильм",
        "мелодрама",
        "музыка",
        "приключения",
        "фэнтези",
        "документальный",
    ],
}


def upgrade() -> None:
    mood_table = sa.table("mood", sa.column("id", sa.Uuid), sa.column("name", sa.String))
    genre_table = sa.table("genre", sa.column("id", sa.Uuid), sa.column("name", sa.String))
    genre_mood_table = sa.table("genre_mood", sa.column("genre_id", sa.Uuid), sa.column("mood_id", sa.Uuid))

    all_genres = set()
    for genres in MOODS_AND_GENRES.values():
        all_genres.update(genres)

    genre_data = [{"id": uuid.uuid4(), "name": genre} for genre in all_genres]
    op.bulk_insert(genre_table, genre_data)

    genre_map = {row["name"]: row["id"] for row in genre_data}

    mood_data = [{"id": uuid.uuid4(), "name": mood_name} for mood_name in MOODS_AND_GENRES]
    op.bulk_insert(mood_table, mood_data)

    mood_map = {row["name"]: row["id"] for row in mood_data}

    genre_mood_data = []
    for mood_name, genres in MOODS_AND_GENRES.items():
        mood_id = mood_map[mood_name]
        for genre_name in genres:
            genre_id = genre_map[genre_name]
            genre_mood_data.append({"genre_id": genre_id, "mood_id": mood_id})

    op.bulk_insert(genre_mood_table, genre_mood_data)


def downgrade() -> None:
    op.execute("DELETE FROM genre_mood")
    op.execute("DELETE FROM mood")
    op.execute("DELETE FROM genre")

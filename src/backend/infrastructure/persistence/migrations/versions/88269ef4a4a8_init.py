"""init

Revision ID: 88269ef4a4a8
Revises:
Create Date: 2025-03-03 23:18:13.770315

"""

from collections.abc import Sequence

import advanced_alchemy
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "88269ef4a4a8"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "film_genre",
        sa.Column("film_id", sa.Uuid(), nullable=False),
        sa.Column("genre_id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("film_id", "genre_id"),
    )
    op.create_table(
        "genre",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "genre_mood",
        sa.Column("genre_id", sa.Uuid(), nullable=False),
        sa.Column("mood_id", sa.Uuid(), nullable=False),
        sa.PrimaryKeyConstraint("genre_id", "mood_id"),
    )
    op.create_table(
        "mix",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("color1", sa.String(), nullable=False),
        sa.Column("color2", sa.String(), nullable=False),
        sa.Column("color3", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mood",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=True),
        sa.Column("telegram_id", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("telegram_id"),
    )
    op.create_table(
        "auth_token",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("token", sa.String(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("activated", sa.Boolean(), nullable=False),
        sa.Column("declined", sa.Boolean(), nullable=False),
        sa.Column("created_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_auth_token_token"), "auth_token", ["token"], unique=True)
    op.create_table(
        "film",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("country", sa.String(), nullable=True),
        sa.Column("release_year", sa.Integer(), nullable=True),
        sa.Column("poster_url", sa.String(), nullable=True),
        sa.Column("tmdb_id", sa.Integer(), nullable=True),
        sa.Column("owner_id", sa.Uuid(), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "watchlist",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("type", sa.Enum("liked", "wish", "watched", "custom", name="watchlisttype"), nullable=False),
        sa.Column("color1", sa.String(), nullable=False),
        sa.Column("color2", sa.String(), nullable=False),
        sa.Column("color3", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "mix_item",
        sa.Column("mix_id", sa.Uuid(), nullable=False),
        sa.Column("film_id", sa.Uuid(), nullable=False),
        sa.Column("added_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["film_id"],
            ["film.id"],
        ),
        sa.ForeignKeyConstraint(
            ["mix_id"],
            ["mix.id"],
        ),
        sa.PrimaryKeyConstraint("mix_id", "film_id"),
    )
    op.create_table(
        "recommended_film",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("film_id", sa.Uuid(), nullable=False),
        sa.Column("recommended_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["film_id"],
            ["film.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "watchlist_item",
        sa.Column("watchlist_id", sa.Uuid(), nullable=False),
        sa.Column("film_id", sa.Uuid(), nullable=False),
        sa.Column("added_at", advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["film_id"],
            ["film.id"],
        ),
        sa.ForeignKeyConstraint(
            ["watchlist_id"],
            ["watchlist.id"],
        ),
        sa.PrimaryKeyConstraint("watchlist_id", "film_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("watchlist_item")
    op.drop_table("recommended_film")
    op.drop_table("mix_item")
    op.drop_table("watchlist")
    op.drop_table("film")
    op.drop_index(op.f("ix_auth_token_token"), table_name="auth_token")
    op.drop_table("auth_token")
    op.drop_table("user")
    op.drop_table("mood")
    op.drop_table("mix")
    op.drop_table("genre_mood")
    op.drop_table("genre")
    op.drop_table("film_genre")
    # ### end Alembic commands ###

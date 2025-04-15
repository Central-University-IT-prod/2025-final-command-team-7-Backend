"""optional description

Revision ID: 71543e4825b3
Revises: 9d2c20a1b8e4
Create Date: 2025-03-04 02:04:35.064291

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "71543e4825b3"
down_revision: str | None = "9d2c20a1b8e4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("film", "description", existing_type=sa.VARCHAR(), nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("film", "description", existing_type=sa.VARCHAR(), nullable=False)
    # ### end Alembic commands ###

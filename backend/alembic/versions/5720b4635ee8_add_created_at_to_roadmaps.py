"""add created_at to roadmaps

Revision ID: 5720b4635ee8
Revises: e1ac3bd2a020
Create Date: 2026-03-31 00:25:51.285205

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5720b4635ee8'
down_revision: Union[str, Sequence[str], None] = 'e1ac3bd2a020'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

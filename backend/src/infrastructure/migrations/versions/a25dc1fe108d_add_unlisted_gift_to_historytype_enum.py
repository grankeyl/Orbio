"""add UNLISTED_GIFT to historytype enum

Revision ID: a25dc1fe108d
Revises: 447900c1888f
Create Date: 2025-06-23 23:28:55.971053

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a25dc1fe108d'
down_revision: Union[str, None] = '447900c1888f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

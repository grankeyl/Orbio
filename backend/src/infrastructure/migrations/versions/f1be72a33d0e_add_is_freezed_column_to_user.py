"""add is_freezed column to user

Revision ID: f1be72a33d0e
Revises: fa4c892a334d
Create Date: 2025-08-21 16:34:45.788056

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f1be72a33d0e'
down_revision: Union[str, None] = 'fa4c892a334d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_freezed', sa.Boolean(), nullable=True, server_default=sa.false()))

def downgrade() -> None:
    op.drop_column('users', 'is_freezed')
"""Add role column to users

Revision ID: a6c801cd73d3
Revises: 
Create Date: 2025-08-21 16:18:14.393877

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6c801cd73d3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # добавляем колонку с дефолтом
    op.add_column(
        "users",
        sa.Column("role", sa.String(), server_default="user", nullable=False)
    )

def downgrade():
    op.drop_column("users", "role")
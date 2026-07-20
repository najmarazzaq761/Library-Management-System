"""Add auth columns to members table

Revision ID: c1a9c3d77591
Revises: b54073a77590
Create Date: 2026-07-09 06:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1a9c3d77591'
down_revision: Union[str, Sequence[str], None] = 'b54073a77590'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('members', sa.Column('hashed_password', sa.String(length=255), nullable=True))
    op.add_column('members', sa.Column('role', sa.String(length=50), server_default='member', nullable=False))


def downgrade() -> None:
    op.drop_column('members', 'role')
    op.drop_column('members', 'hashed_password')

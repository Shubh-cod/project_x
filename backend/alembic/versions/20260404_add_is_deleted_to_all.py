"""Add is_deleted column to leads, deals, and tasks.

Revision ID: c1d2e3f4g5h6
Revises: b1c2d3e4f5g6
Create Date: 2026-04-04 14:58:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4g5h6'
down_revision: Union[str, None] = 'b1c2d3e4f5g6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_deleted column to leads, deals, tasks
    for table in ['leads', 'deals', 'tasks']:
        op.add_column(table, sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')))
        op.create_index(f'ix_{table}_is_deleted', table, ['is_deleted'], unique=False)


def downgrade() -> None:
    for table in ['tasks', 'deals', 'leads']:
        op.drop_index(f'ix_{table}_is_deleted', table_name=table)
        op.drop_column(table, 'is_deleted')

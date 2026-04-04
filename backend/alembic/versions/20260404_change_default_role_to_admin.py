"""Change default user role to admin.

Revision ID: b1c2d3e4f5g6
Revises: a1b2c3d4e5f6
Create Date: 2026-04-04 14:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5g6'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update existing users from 'agent' to 'admin'
    # Use raw SQL to avoid issues with Enum types in different environments
    op.execute("UPDATE users SET role = 'admin' WHERE role = 'agent'")

    # 2. Change column default in DB if possible (Postgres Enum default)
    # Note: Using op.alter_column for server_default usually works
    op.alter_column('users', 'role', server_default='admin')


def downgrade() -> None:
    # Optional: revert default but don't force downgrade all users back to agent
    op.alter_column('users', 'role', server_default='agent')
    # op.execute("UPDATE users SET role = 'agent' WHERE role = 'admin'") # Probably not desired

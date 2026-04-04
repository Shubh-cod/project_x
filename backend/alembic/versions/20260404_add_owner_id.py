"""Add owner_id column to all ownable models for data isolation.

Revision ID: a1b2c3d4e5f6
Revises: 001
Create Date: 2026-04-04 13:38:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Ensure automation_rules table exists (was previously created at app startup, not via Alembic) ---
    op.create_table(
        'automation_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('trigger_event', sa.String(50), nullable=False),
        sa.Column('conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('action_type', sa.String(50), nullable=False, server_default='create_task'),
        sa.Column('action_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        if_not_exists=True,
    )
    op.create_index('ix_automation_rules_name', 'automation_rules', ['name'], unique=False, if_not_exists=True)
    op.create_index('ix_automation_rules_trigger_event', 'automation_rules', ['trigger_event'], unique=False, if_not_exists=True)
    op.create_index('ix_automation_rules_created_by', 'automation_rules', ['created_by'], unique=False, if_not_exists=True)

    # --- Add owner_id columns (nullable) to all ownable tables ---
    tables = ['contacts', 'leads', 'deals', 'tasks', 'notes', 'automation_rules', 'email_logs']
    for table in tables:
        op.add_column(table, sa.Column('owner_id', sa.Uuid(), nullable=True))
        op.create_index(f'ix_{table}_owner_id', table, ['owner_id'])
        op.create_foreign_key(
            f'fk_{table}_owner_id_users',
            table, 'users',
            ['owner_id'], ['id'],
            ondelete='SET NULL',
        )

    # --- Backfill owner_id from existing columns ---
    # Contacts, Leads, Deals, Tasks: use assigned_to
    for table in ['contacts', 'leads', 'deals', 'tasks']:
        op.execute(
            f"UPDATE {table} SET owner_id = assigned_to WHERE assigned_to IS NOT NULL AND owner_id IS NULL"
        )

    # Notes: use created_by
    op.execute(
        "UPDATE notes SET owner_id = created_by WHERE created_by IS NOT NULL AND owner_id IS NULL"
    )

    # AutomationRules: use created_by
    op.execute(
        "UPDATE automation_rules SET owner_id = created_by WHERE created_by IS NOT NULL AND owner_id IS NULL"
    )

    # EmailLogs: use sent_by
    op.execute(
        "UPDATE email_logs SET owner_id = sent_by WHERE sent_by IS NOT NULL AND owner_id IS NULL"
    )


def downgrade() -> None:
    for table in ['email_logs', 'automation_rules', 'notes', 'tasks', 'deals', 'leads', 'contacts']:
        op.drop_constraint(f'fk_{table}_owner_id_users', table, type_='foreignkey')
        op.drop_index(f'ix_{table}_owner_id', table_name=table)
        op.drop_column(table, 'owner_id')
    # Don't drop automation_rules on downgrade — it may have data

"""Add notifications table for Phase 22

Revision ID: 014_notifications_inbox
Revises: 013_demand_memory
Create Date: 2026-11-23 16:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '014_notifications_inbox'
down_revision: Union[str, None] = '013_demand_memory'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'notifications',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('category', sa.String(64), nullable=False),
        sa.Column('priority', sa.String(32), nullable=False, server_default='medium'),
        sa.Column('status', sa.String(32), nullable=False, server_default='unread'),
        sa.Column('target_entity_type', sa.String(64), nullable=True),
        sa.Column('target_entity_id', sa.String(36), nullable=True),
        sa.Column('dedup_key', sa.String(128), nullable=False),
        sa.Column('snoozed_until', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_notifications_tenant_id', 'notifications', ['tenant_id'])
    op.create_index('ix_notifications_dedup_key', 'notifications', ['dedup_key'])


def downgrade() -> None:
    op.drop_table('notifications')

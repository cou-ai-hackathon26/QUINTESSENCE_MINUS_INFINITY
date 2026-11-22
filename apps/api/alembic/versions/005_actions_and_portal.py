"""Add actions and customer_portal_tokens tables for Phase 08

Revision ID: 005_actions_and_portal
Revises: 004_scenarios_schema
Create Date: 2026-11-23 02:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '005_actions_and_portal'
down_revision: Union[str, None] = '004_scenarios_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Actions table
    op.create_table(
        'actions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('action_type', sa.String(64), nullable=False),
        sa.Column('recipient', sa.String(255), nullable=False),
        sa.Column('amount_paisa', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(32), nullable=False, server_default='draft'),
        sa.Column('idempotency_key', sa.String(128), nullable=True),
        sa.Column('payload_json', sa.Text(), nullable=True),
        sa.Column('outcome_json', sa.Text(), nullable=True),
        sa.Column('created_by_user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('approved_by_user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('tenant_id', 'idempotency_key', name='uq_tenant_action_idempotency'),
    )

    # 2. Customer portal tokens table
    op.create_table(
        'customer_portal_tokens',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('token', sa.String(64), unique=True, nullable=False, index=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('party_id', sa.String(36), sa.ForeignKey('parties.id', ondelete='CASCADE'), nullable=False),
        sa.Column('invoice_number', sa.String(64), nullable=False),
        sa.Column('amount_paisa', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_paid', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('dispute_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('customer_portal_tokens')
    op.drop_table('actions')

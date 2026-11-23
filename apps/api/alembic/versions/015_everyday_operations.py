"""Add customer reservations, returnable containers, and shift handovers for Phase 23

Revision ID: 015_everyday_operations
Revises: 014_notifications_inbox
Create Date: 2026-11-23 17:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '015_everyday_operations'
down_revision: Union[str, None] = '014_notifications_inbox'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'customer_reservations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_name', sa.String(255), nullable=True),
        sa.Column('customer_phone', sa.String(64), nullable=True),
        sa.Column('items_json', sa.Text(), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='reserved'),
        sa.Column('total_estimated_paisa', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('deposit_paisa', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_customer_reservations_tenant_id', 'customer_reservations', ['tenant_id'])

    op.create_table(
        'returnable_containers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('container_type', sa.String(64), nullable=False),
        sa.Column('party_id', sa.String(36), sa.ForeignKey('parties.id', ondelete='SET NULL'), nullable=True),
        sa.Column('party_name', sa.String(255), nullable=False),
        sa.Column('issued_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('returned_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('outstanding_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('deposit_per_unit_paisa', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('total_deposit_held_paisa', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_returnable_containers_tenant_id', 'returnable_containers', ['tenant_id'])

    op.create_table(
        'shift_handovers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('shift_name', sa.String(64), nullable=False),
        sa.Column('opened_by', sa.String(255), nullable=False),
        sa.Column('closed_by', sa.String(255), nullable=False),
        sa.Column('declared_cash_paisa', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('system_cash_paisa', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('variance_paisa', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('possible_reasons_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_shift_handovers_tenant_id', 'shift_handovers', ['tenant_id'])


def downgrade() -> None:
    op.drop_table('shift_handovers')
    op.drop_table('returnable_containers')
    op.drop_table('customer_reservations')

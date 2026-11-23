"""Add unmet_demands and stockout_periods tables for Phase 21

Revision ID: 013_demand_memory
Revises: 012_receiving_and_returns
Create Date: 2026-11-23 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '013_demand_memory'
down_revision: Union[str, None] = '012_receiving_and_returns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. unmet_demands
    op.create_table(
        'unmet_demands',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('customer_name', sa.String(255), nullable=True),
        sa.Column('requested_product', sa.String(255), nullable=False),
        sa.Column('sku', sa.String(64), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('reason', sa.String(64), nullable=False, server_default='stockout'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_unmet_demands_tenant_id', 'unmet_demands', ['tenant_id'])
    op.create_index('ix_unmet_demands_sku', 'unmet_demands', ['sku'])

    # 2. stockout_periods
    op.create_table(
        'stockout_periods',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sku', sa.String(64), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('total_lost_requests_count', sa.Integer(), nullable=False, server_default='0'),
    )
    op.create_index('ix_stockout_periods_tenant_id', 'stockout_periods', ['tenant_id'])
    op.create_index('ix_stockout_periods_sku', 'stockout_periods', ['sku'])


def downgrade() -> None:
    op.drop_table('stockout_periods')
    op.drop_table('unmet_demands')

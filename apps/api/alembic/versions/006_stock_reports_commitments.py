"""Add stock enhancements, purchase_drafts and recurring_commitments tables for Phase 09

Revision ID: 006_stock_reports_commitments
Revises: 005_actions_and_portal
Create Date: 2026-11-23 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '006_stock_reports_commitments'
down_revision: Union[str, None] = '005_actions_and_portal'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add reorder_threshold and lead_time_days to products
    with op.batch_alter_table('products') as batch_op:
        batch_op.add_column(sa.Column('reorder_threshold', sa.Integer(), nullable=True, server_default='5'))
        batch_op.add_column(sa.Column('lead_time_days', sa.Integer(), nullable=True, server_default='3'))

    # 2. Add total_sales_paisa to daily_snapshots
    with op.batch_alter_table('daily_snapshots') as batch_op:
        batch_op.add_column(sa.Column('total_sales_paisa', sa.Integer(), nullable=True, server_default='0'))

    # 3. Purchase drafts table
    op.create_table(
        'purchase_drafts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('supplier_id', sa.String(36), sa.ForeignKey('parties.id', ondelete='SET NULL'), nullable=True),
        sa.Column('product_id', sa.String(36), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_cost_paisa', sa.Integer(), nullable=False),
        sa.Column('total_cost_paisa', sa.Integer(), nullable=False),
        sa.Column('lead_time_days', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('status', sa.String(32), nullable=False, server_default='draft'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('received_at', sa.DateTime(), nullable=True),
    )

    # 3. Recurring commitments table
    op.create_table(
        'recurring_commitments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('category', sa.String(64), nullable=False, server_default='other'),
        sa.Column('amount_paisa', sa.Integer(), nullable=False),
        sa.Column('frequency', sa.String(32), nullable=False, server_default='monthly'),
        sa.Column('party_id', sa.String(36), sa.ForeignKey('parties.id', ondelete='SET NULL'), nullable=True),
        sa.Column('due_day_of_month', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('recurring_commitments')
    op.drop_table('purchase_drafts')
    with op.batch_alter_table('daily_snapshots') as batch_op:
        batch_op.drop_column('total_sales_paisa')
    with op.batch_alter_table('products') as batch_op:
        batch_op.drop_column('lead_time_days')
        batch_op.drop_column('reorder_threshold')

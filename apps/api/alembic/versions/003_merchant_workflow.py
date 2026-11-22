"""Add daily_snapshots, parties, products, and stock_movements tables

Revision ID: 003_merchant_workflow
Revises: 002_evidence_schema
Create Date: 2026-11-23 01:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '003_merchant_workflow'
down_revision: Union[str, None] = '002_evidence_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Daily Snapshots
    op.create_table(
        'daily_snapshots',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('snapshot_date', sa.String(10), nullable=False),
        sa.Column('opening_cash_paisa', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('closing_cash_paisa', sa.Integer(), nullable=True),
        sa.Column('actual_drawer_cash_paisa', sa.Integer(), nullable=True),
        sa.Column('discrepancy_paisa', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(16), nullable=False, server_default='open'),
        sa.Column('closed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('tenant_id', 'snapshot_date', name='uq_tenant_snapshot_date'),
    )

    # 2. Parties (Customers & Suppliers)
    op.create_table(
        'parties',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(32), nullable=True),
        sa.Column('party_type', sa.String(16), nullable=False, server_default='customer'),
        sa.Column('current_due_paisa', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # 3. Products
    op.create_table(
        'products',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('sku', sa.String(64), nullable=True),
        sa.Column('unit', sa.String(32), nullable=False, server_default='pcs'),
        sa.Column('quantity_on_hand', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cost_price_paisa', sa.Integer(), nullable=True),
        sa.Column('selling_price_paisa', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # 4. Stock Movements
    op.create_table(
        'stock_movements',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', sa.String(36), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('movement_type', sa.String(32), nullable=False),
        sa.Column('quantity_change', sa.Integer(), nullable=False),
        sa.Column('reference_id', sa.String(64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('stock_movements')
    op.drop_table('products')
    op.drop_table('parties')
    op.drop_table('daily_snapshots')

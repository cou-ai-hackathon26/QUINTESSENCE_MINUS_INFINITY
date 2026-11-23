"""Add goods_receipts and credit_notes tables for Phase 20

Revision ID: 012_receiving_and_returns
Revises: 011_buying_desk
Create Date: 2026-11-23 14:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '012_receiving_and_returns'
down_revision: Union[str, None] = '011_buying_desk'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. goods_receipts
    op.create_table(
        'goods_receipts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('purchase_draft_id', sa.String(36), nullable=True),
        sa.Column('supplier_name', sa.String(255), nullable=False),
        sa.Column('sku', sa.String(64), nullable=False),
        sa.Column('ordered_quantity', sa.Integer(), nullable=False),
        sa.Column('received_quantity', sa.Integer(), nullable=False),
        sa.Column('damaged_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('shortage_quantity', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('batch_number', sa.String(64), nullable=True),
        sa.Column('expiry_date', sa.String(32), nullable=True),
        sa.Column('status', sa.String(32), nullable=False, server_default='complete'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_goods_receipts_tenant_id', 'goods_receipts', ['tenant_id'])
    op.create_index('ix_goods_receipts_sku', 'goods_receipts', ['sku'])

    # 2. credit_notes
    op.create_table(
        'credit_notes',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('receipt_id', sa.String(36), sa.ForeignKey('goods_receipts.id', ondelete='SET NULL'), nullable=True),
        sa.Column('supplier_name', sa.String(255), nullable=False),
        sa.Column('claim_reason', sa.String(64), nullable=False),
        sa.Column('amount_paisa', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='suspected'),
        sa.Column('applied_invoice_ref', sa.String(64), nullable=True),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.Column('return_window_deadline', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_credit_notes_tenant_id', 'credit_notes', ['tenant_id'])


def downgrade() -> None:
    op.drop_table('credit_notes')
    op.drop_table('goods_receipts')

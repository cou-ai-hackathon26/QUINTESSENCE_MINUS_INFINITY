"""Add supplier_offers and buying_comparisons tables for Phase 19

Revision ID: 011_buying_desk
Revises: 010_copilot_workspace
Create Date: 2026-11-23 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '011_buying_desk'
down_revision: Union[str, None] = '010_copilot_workspace'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. supplier_offers
    op.create_table(
        'supplier_offers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('supplier_name', sa.String(255), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('sku', sa.String(64), nullable=False),
        sa.Column('pack_size', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('pack_unit', sa.String(32), nullable=False, server_default='পিস'),
        sa.Column('base_unit_price_paisa', sa.Integer(), nullable=False),
        sa.Column('min_order_quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('bonus_condition_json', sa.Text(), nullable=True),
        sa.Column('cash_discount_percent', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('credit_period_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('delivery_fee_paisa', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('payment_method_required', sa.String(32), nullable=False, server_default='any'),
        sa.Column('source_type', sa.String(32), nullable=False, server_default='manual'),
        sa.Column('source_doc_id', sa.String(36), nullable=True),
        sa.Column('confidence_score', sa.Integer(), nullable=False, server_default='80'),
        sa.Column('has_critical_blocker', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_supplier_offers_tenant_id', 'supplier_offers', ['tenant_id'])
    op.create_index('ix_supplier_offers_sku', 'supplier_offers', ['sku'])

    # 2. buying_comparisons
    op.create_table(
        'buying_comparisons',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_sku', sa.String(64), nullable=False),
        sa.Column('required_quantity', sa.Integer(), nullable=False),
        sa.Column('best_offer_id', sa.String(36), sa.ForeignKey('supplier_offers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('comparison_summary_json', sa.Text(), nullable=False),
        sa.Column('feasibility_status', sa.String(64), nullable=False, server_default='feasible_cash'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_buying_comparisons_tenant_id', 'buying_comparisons', ['tenant_id'])
    op.create_index('ix_buying_comparisons_target_sku', 'buying_comparisons', ['target_sku'])


def downgrade() -> None:
    op.drop_table('buying_comparisons')
    op.drop_table('supplier_offers')

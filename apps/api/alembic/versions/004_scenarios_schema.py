"""Add scenarios table for Phase 07 planning and decision lab

Revision ID: 004_scenarios_schema
Revises: 003_merchant_workflow
Create Date: 2026-11-23 02:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '004_scenarios_schema'
down_revision: Union[str, None] = '003_merchant_workflow'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'scenarios',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('horizon_days', sa.Integer(), nullable=False, server_default='7'),
        sa.Column('opening_cash_paisa', sa.Integer(), nullable=False),
        sa.Column('assumed_daily_receipt_paisa', sa.Integer(), nullable=False),
        sa.Column('planned_outflows_json', sa.Text(), nullable=False),
        sa.Column('reserve_target_paisa', sa.Integer(), nullable=False),
        sa.Column('extra_expense_paisa', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('extra_expense_day', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('conditional_promise_paisa', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('conditional_promise_date', sa.String(10), nullable=True),
        sa.Column('first_reserve_breach_date', sa.String(10), nullable=True),
        sa.Column('first_funding_shortfall_date', sa.String(10), nullable=True),
        sa.Column('closing_series_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('scenarios')

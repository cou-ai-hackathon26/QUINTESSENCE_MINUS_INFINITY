"""Initial multi-tenant financial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-23 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tenants
    op.create_table(
        'tenants',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, server_default='BDT'),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # 2. Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('phone', sa.String(32), nullable=False),
        sa.Column('role', sa.String(32), nullable=False, server_default='owner'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('tenant_id', 'phone', name='uq_tenant_phone'),
    )

    # 3. Accounts
    op.create_table(
        'accounts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('code', sa.String(64), nullable=False),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('type', sa.String(32), nullable=False),
        sa.Column('current_balance_paisa', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('tenant_id', 'code', name='uq_tenant_account_code'),
    )

    # 4. Journal Entries
    op.create_table(
        'journal_entries',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('entry_number', sa.String(64), nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('event_id', sa.String(128), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('tenant_id', 'event_id', name='uq_tenant_event_id'),
    )

    # 5. Postings
    op.create_table(
        'postings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('journal_entry_id', sa.String(36), sa.ForeignKey('journal_entries.id', ondelete='CASCADE'), nullable=False),
        sa.Column('account_id', sa.String(36), sa.ForeignKey('accounts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('direction', sa.String(8), nullable=False),
        sa.Column('amount_paisa', sa.Integer(), nullable=False),
    )

    # 6. Obligations
    op.create_table(
        'obligations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('party_name', sa.String(255), nullable=False),
        sa.Column('invoice_ref', sa.String(64), nullable=True),
        sa.Column('amount_paisa', sa.Integer(), nullable=False),
        sa.Column('accepted_methods', sa.String(128), nullable=False, server_default='cash'),
        sa.Column('status', sa.String(32), nullable=False, server_default='unresolved'),
        sa.Column('due_at', sa.DateTime(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # 7. Allocations
    op.create_table(
        'allocations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('obligation_id', sa.String(36), sa.ForeignKey('obligations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_payment_id', sa.String(64), nullable=False),
        sa.Column('amount_paisa', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # 8. Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('action', sa.String(64), nullable=False),
        sa.Column('details', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('allocations')
    op.drop_table('obligations')
    op.drop_table('postings')
    op.drop_table('journal_entries')
    op.drop_table('accounts')
    op.drop_table('users')
    op.drop_table('tenants')

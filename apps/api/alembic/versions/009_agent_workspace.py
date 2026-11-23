"""Add agent_runs, agent_tasks, and agent_events tables for Phase 17

Revision ID: 009_agent_workspace
Revises: 008_hybrid_memory
Create Date: 2026-11-23 10:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '009_agent_workspace'
down_revision: Union[str, None] = '008_hybrid_memory'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. agent_runs table
    op.create_table(
        'agent_runs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('case_id', sa.String(36), sa.ForeignKey('cases.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', sa.String(32), nullable=False, server_default='queued'),
        sa.Column('budget_calls_max', sa.Integer(), nullable=False, server_default='8'),
        sa.Column('budget_calls_used', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_agent_runs_tenant_id', 'agent_runs', ['tenant_id'])
    op.create_index('ix_agent_runs_case_id', 'agent_runs', ['case_id'])

    # 2. agent_tasks table
    op.create_table(
        'agent_tasks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('run_id', sa.String(36), sa.ForeignKey('agent_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(64), nullable=False),
        sa.Column('business_question', sa.String(255), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='queued'),
        sa.Column('result_summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_agent_tasks_run_id', 'agent_tasks', ['run_id'])

    # 3. agent_events table
    op.create_table(
        'agent_events',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('run_id', sa.String(36), sa.ForeignKey('agent_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('task_id', sa.String(36), sa.ForeignKey('agent_tasks.id', ondelete='SET NULL'), nullable=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_seq', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(64), nullable=False),
        sa.Column('event_type', sa.String(64), nullable=False),
        sa.Column('payload_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_agent_events_run_id', 'agent_events', ['run_id'])
    op.create_index('ix_agent_events_task_id', 'agent_events', ['task_id'])


def downgrade() -> None:
    op.drop_table('agent_events')
    op.drop_table('agent_tasks')
    op.drop_table('agent_runs')

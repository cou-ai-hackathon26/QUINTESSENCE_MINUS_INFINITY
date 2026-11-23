"""Add copilot_sessions and copilot_messages tables for Phase 18

Revision ID: 010_copilot_workspace
Revises: 009_agent_workspace
Create Date: 2026-11-23 11:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '010_copilot_workspace'
down_revision: Union[str, None] = '009_agent_workspace'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. copilot_sessions
    op.create_table(
        'copilot_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False, server_default='নতুন আলোচনা'),
        sa.Column('context_entity_type', sa.String(64), nullable=True),
        sa.Column('context_entity_id', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_copilot_sessions_tenant_id', 'copilot_sessions', ['tenant_id'])
    op.create_index('ix_copilot_sessions_context_entity_id', 'copilot_sessions', ['context_entity_id'])

    # 2. copilot_messages
    op.create_table(
        'copilot_messages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('copilot_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(32), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('intent', sa.String(64), nullable=True),
        sa.Column('confidence_score', sa.Integer(), nullable=True),
        sa.Column('confidence_band', sa.String(32), nullable=True),
        sa.Column('readiness', sa.String(32), nullable=True),
        sa.Column('citations_json', sa.Text(), nullable=True),
        sa.Column('action_draft_id', sa.String(36), sa.ForeignKey('actions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('audio_metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_copilot_messages_session_id', 'copilot_messages', ['session_id'])
    op.create_index('ix_copilot_messages_tenant_id', 'copilot_messages', ['tenant_id'])


def downgrade() -> None:
    op.drop_table('copilot_messages')
    op.drop_table('copilot_sessions')

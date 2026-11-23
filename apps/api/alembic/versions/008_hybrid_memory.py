"""Add document_chunks table for Phase 16 Hybrid Memory

Revision ID: 008_hybrid_memory
Revises: 007_cases_and_confidence
Create Date: 2026-11-23 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '008_hybrid_memory'
down_revision: Union[str, None] = '007_cases_and_confidence'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_id', sa.String(36), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('source_type', sa.String(32), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('normalized_content', sa.Text(), nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('embedding_json', sa.Text(), nullable=True),
        sa.Column('model_version', sa.String(64), nullable=False, server_default='text-embedding-004'),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_document_chunks_tenant_id', 'document_chunks', ['tenant_id'])
    op.create_index('ix_document_chunks_document_id', 'document_chunks', ['document_id'])


def downgrade() -> None:
    op.drop_table('document_chunks')

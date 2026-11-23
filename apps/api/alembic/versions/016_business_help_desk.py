"""Add business documents and regulatory corpus for Phase 24

Revision ID: 016_business_help_desk
Revises: 015_everyday_operations
Create Date: 2026-11-23 18:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '016_business_help_desk'
down_revision: Union[str, None] = '015_everyday_operations'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'business_documents',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('doc_type', sa.String(64), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(512), nullable=True),
        sa.Column('issuing_authority', sa.String(255), nullable=False),
        sa.Column('issue_date', sa.String(32), nullable=True),
        sa.Column('expiry_date', sa.String(32), nullable=True),
        sa.Column('status', sa.String(32), nullable=False, server_default='valid'),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_business_documents_tenant_id', 'business_documents', ['tenant_id'])

    op.create_table(
        'regulatory_corpus',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('jurisdiction', sa.String(32), nullable=False, server_default='BD'),
        sa.Column('topic', sa.String(64), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('citation_reference', sa.String(255), nullable=False),
        sa.Column('effective_date', sa.String(32), nullable=False),
        sa.Column('last_reviewed_date', sa.String(32), nullable=False),
        sa.Column('authority_name', sa.String(255), nullable=False),
        sa.Column('official_portal_url', sa.String(512), nullable=False),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('applicability_rules_json', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_regulatory_corpus_topic', 'regulatory_corpus', ['topic'])


def downgrade() -> None:
    op.drop_table('regulatory_corpus')
    op.drop_table('business_documents')

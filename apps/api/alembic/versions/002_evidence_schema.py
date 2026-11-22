"""Add evidence and extracted_claims tables

Revision ID: 002_evidence_schema
Revises: 001_initial_schema
Create Date: 2026-11-23 01:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '002_evidence_schema'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'evidence',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('mime_type', sa.String(128), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=False),
        sa.Column('content_sha256', sa.String(64), nullable=False),
        sa.Column('storage_path', sa.String(512), nullable=False),
        sa.Column('source_type', sa.String(32), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='uploaded'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'extracted_claims',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('evidence_id', sa.String(36), sa.ForeignKey('evidence.id', ondelete='CASCADE'), nullable=False),
        sa.Column('party_name', sa.String(255), nullable=True),
        sa.Column('invoice_ref', sa.String(64), nullable=True),
        sa.Column('amount_paisa', sa.Integer(), nullable=True),
        sa.Column('claim_date', sa.String(32), nullable=True),
        sa.Column('payment_method', sa.String(64), nullable=True),
        sa.Column('status', sa.String(32), nullable=False, server_default='proposed'),
        sa.Column('raw_model_response', sa.Text(), nullable=True),
        sa.Column('is_reviewed', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('corrected_amount_paisa', sa.Integer(), nullable=True),
        sa.Column('corrected_party_name', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('extracted_claims')
    op.drop_table('evidence')

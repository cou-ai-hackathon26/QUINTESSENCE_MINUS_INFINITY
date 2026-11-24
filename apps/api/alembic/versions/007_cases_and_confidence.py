"""Add cases, case_versions, evidence_claims and confidence_assessments tables for Phase 15

Revision ID: 007_cases_and_confidence
Revises: 006_stock_reports_commitments
Create Date: 2026-11-23 09:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '007_cases_and_confidence'
down_revision: Union[str, None] = '006_stock_reports_commitments'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. cases table
    op.create_table(
        'cases',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('case_type', sa.String(64), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, server_default='open'),
        sa.Column('current_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_cases_tenant_id', 'cases', ['tenant_id'])

    # 2. case_versions table
    op.create_table(
        'case_versions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('case_id', sa.String(36), sa.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version_num', sa.Integer(), nullable=False),
        sa.Column('state_snapshot_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('case_id', 'version_num', name='uq_case_version'),
    )
    op.create_index('ix_case_versions_case_id', 'case_versions', ['case_id'])

    # 3. evidence_claims table
    op.create_table(
        'evidence_claims',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('case_id', sa.String(36), sa.ForeignKey('cases.id', ondelete='SET NULL'), nullable=True),
        sa.Column('claim_key', sa.String(64), nullable=False),
        sa.Column('is_critical', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('state', sa.String(32), nullable=False, server_default='unknown'),
        sa.Column('weight', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('source_locator_json', sa.Text(), nullable=True),
        sa.Column('claim_value_json', sa.Text(), nullable=True),
        sa.Column('evaluator_type', sa.String(32), nullable=False, server_default='deterministic'),
        sa.Column('reasons_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_evidence_claims_tenant_id', 'evidence_claims', ['tenant_id'])
    op.create_index('ix_evidence_claims_case_id', 'evidence_claims', ['case_id'])

    # 4. confidence_assessments table
    op.create_table(
        'confidence_assessments',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('tenant_id', sa.String(36), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('case_id', sa.String(36), sa.ForeignKey('cases.id', ondelete='CASCADE'), nullable=False),
        sa.Column('case_version', sa.Integer(), nullable=False),
        sa.Column('policy_version', sa.String(32), nullable=False, server_default='evidence-support-v1'),
        sa.Column('kind', sa.String(32), nullable=False, server_default='evidence_support_index'),
        sa.Column('base_score', sa.Integer(), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('band', sa.String(32), nullable=False),
        sa.Column('readiness', sa.String(32), nullable=False),
        sa.Column('can_execute_without_approval', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('blocking_validation_failure', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('unavailable_reason', sa.String(64), nullable=True),
        sa.Column('model_self_confidence', sa.Float(), nullable=True),
        sa.Column('assessed_at', sa.DateTime(), nullable=False),
        sa.Column('assessment_details_json', sa.Text(), nullable=True),
    )
    op.create_index('ix_confidence_assessments_tenant_id', 'confidence_assessments', ['tenant_id'])
    op.create_index('ix_confidence_assessments_case_id', 'confidence_assessments', ['case_id'])


def downgrade() -> None:
    op.drop_table('confidence_assessments')
    op.drop_table('evidence_claims')
    op.drop_table('case_versions')
    op.drop_table('cases')

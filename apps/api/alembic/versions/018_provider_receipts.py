"""Persist actual provider operation receipts without credentials or private prompts."""
from alembic import op
import sqlalchemy as sa
revision='018_provider_receipts'
down_revision='017_workbench_credentials'
branch_labels=None
depends_on=None
def upgrade():
    op.create_table('provider_receipts',sa.Column('id',sa.String(36),primary_key=True),sa.Column('tenant_id',sa.String(36),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),sa.Column('entity_type',sa.String(32)),sa.Column('entity_id',sa.String(36)),sa.Column('capability',sa.String(48),nullable=False),sa.Column('provider',sa.String(32),nullable=False),sa.Column('model',sa.String(128),nullable=False),sa.Column('status',sa.String(24),nullable=False),sa.Column('request_fingerprint',sa.String(64),nullable=False),sa.Column('provider_request_id',sa.String(128)),sa.Column('input_tokens',sa.Integer()),sa.Column('output_tokens',sa.Integer()),sa.Column('latency_ms',sa.Integer(),nullable=False),sa.Column('error_code',sa.String(64)),sa.Column('created_at',sa.DateTime(),nullable=False))
    op.create_index('ix_provider_receipts_tenant_id','provider_receipts',['tenant_id'])
    op.create_index('ix_provider_receipts_entity_id','provider_receipts',['entity_id'])
def downgrade():
    op.drop_table('provider_receipts')

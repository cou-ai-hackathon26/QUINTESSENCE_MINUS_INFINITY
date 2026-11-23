"""Credentials for existing users; no second identity/ledger store."""
from alembic import op
import sqlalchemy as sa
revision = '017_workbench_credentials'
down_revision = '016_business_help_desk'
branch_labels = None
depends_on = None
def upgrade():
    op.create_table('revoked_sessions', sa.Column('token_hash', sa.String(64), primary_key=True), sa.Column('created_at', sa.DateTime(), nullable=False))
    op.create_table('user_credentials',
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('phone', sa.String(32), nullable=False, unique=True),
        sa.Column('display_name', sa.String(100), nullable=False),
        sa.Column('password_salt', sa.String(64), nullable=False),
        sa.Column('password_hash', sa.String(128), nullable=False))
def downgrade():
    op.drop_table('user_credentials')
    op.drop_table('revoked_sessions')

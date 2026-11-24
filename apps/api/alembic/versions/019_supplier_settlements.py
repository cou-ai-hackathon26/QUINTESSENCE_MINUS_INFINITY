"""Add reviewed supplier settlement, aliases and invoice allocations.

Revision ID: 019_supplier_settlements
Revises: 018_provider_receipts
"""
from alembic import op
import sqlalchemy as sa

revision = "019_supplier_settlements"
down_revision = "018_provider_receipts"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("obligations") as batch:
        batch.add_column(sa.Column("party_id", sa.String(36), nullable=True))
        batch.create_foreign_key("fk_obligations_party", "parties", ["party_id"], ["id"], ondelete="RESTRICT")
        batch.create_index("ix_obligations_party_id", ["party_id"])
    # Preserve existing data without fuzzy matching: only an exact, unique supplier name is linked.
    op.execute(sa.text("""
        UPDATE obligations
        SET party_id = (
            SELECT parties.id FROM parties
            WHERE parties.tenant_id = obligations.tenant_id
              AND parties.party_type = 'supplier'
              AND lower(trim(parties.name)) = lower(trim(obligations.party_name))
        )
        WHERE party_id IS NULL
          AND 1 = (
            SELECT count(*) FROM parties
            WHERE parties.tenant_id = obligations.tenant_id
              AND parties.party_type = 'supplier'
              AND lower(trim(parties.name)) = lower(trim(obligations.party_name))
          )
    """))

    op.create_table(
        "party_aliases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("party_id", sa.String(36), sa.ForeignKey("parties.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alias", sa.String(255), nullable=False),
        sa.Column("normalized_alias", sa.String(255), nullable=False),
        sa.Column("source_evidence_id", sa.String(36), sa.ForeignKey("evidence.id", ondelete="SET NULL")),
        sa.Column("reviewed_by_user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("tenant_id", "normalized_alias", name="uq_tenant_party_alias"),
    )
    op.create_index("ix_party_aliases_tenant_id", "party_aliases", ["tenant_id"])
    op.create_index("ix_party_aliases_party_id", "party_aliases", ["party_id"])

    op.create_table(
        "supplier_settlements",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("supplier_party_id", sa.String(36), sa.ForeignKey("parties.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("amount_paisa", sa.BigInteger(), nullable=False),
        sa.Column("channel", sa.String(16), nullable=False, server_default="cash"),
        sa.Column("status", sa.String(32), nullable=False, server_default="collecting_evidence"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("journal_entry_id", sa.String(36), sa.ForeignKey("journal_entries.id", ondelete="SET NULL")),
        sa.Column("created_by_user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("recorded_at", sa.DateTime()),
        sa.UniqueConstraint("tenant_id", "idempotency_key", name="uq_tenant_supplier_settlement_key"),
    )
    op.create_index("ix_supplier_settlements_tenant_id", "supplier_settlements", ["tenant_id"])
    op.create_index("ix_supplier_settlements_supplier_party_id", "supplier_settlements", ["supplier_party_id"])

    op.create_table(
        "supplier_settlement_evidence",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("settlement_id", sa.String(36), sa.ForeignKey("supplier_settlements.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evidence_id", sa.String(36), sa.ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_role", sa.String(32), nullable=False, server_default="other"),
        sa.Column("review_status", sa.String(32), nullable=False, server_default="needs_review"),
        sa.Column("extracted_party_name", sa.String(255)),
        sa.Column("party_match_status", sa.String(32), nullable=False, server_default="unknown"),
        sa.Column("reviewed_by_user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("reviewed_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("settlement_id", "evidence_id", name="uq_settlement_evidence"),
    )
    op.create_index("ix_supplier_settlement_evidence_tenant_id", "supplier_settlement_evidence", ["tenant_id"])
    op.create_index("ix_supplier_settlement_evidence_settlement_id", "supplier_settlement_evidence", ["settlement_id"])
    op.create_index("ix_supplier_settlement_evidence_evidence_id", "supplier_settlement_evidence", ["evidence_id"])

    op.create_table(
        "supplier_settlement_lines",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("settlement_id", sa.String(36), sa.ForeignKey("supplier_settlements.id", ondelete="CASCADE"), nullable=False),
        sa.Column("obligation_id", sa.String(36), sa.ForeignKey("obligations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("amount_paisa", sa.BigInteger(), nullable=False),
        sa.Column("allocation_rule", sa.String(32), nullable=False, server_default="oldest_due_first"),
        sa.Column("obligation_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("settlement_id", "obligation_id", name="uq_settlement_obligation"),
    )
    op.create_index("ix_supplier_settlement_lines_tenant_id", "supplier_settlement_lines", ["tenant_id"])
    op.create_index("ix_supplier_settlement_lines_settlement_id", "supplier_settlement_lines", ["settlement_id"])
    op.create_index("ix_supplier_settlement_lines_obligation_id", "supplier_settlement_lines", ["obligation_id"])


def downgrade():
    op.drop_table("supplier_settlement_lines")
    op.drop_table("supplier_settlement_evidence")
    op.drop_table("supplier_settlements")
    op.drop_table("party_aliases")
    with op.batch_alter_table("obligations") as batch:
        batch.drop_index("ix_obligations_party_id")
        batch.drop_constraint("fk_obligations_party", type_="foreignkey")
        batch.drop_column("party_id")

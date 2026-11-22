"""
SQLAlchemy Persistence Models.
Defines Tenant, User, Account, JournalEntry, Posting, Obligation, Allocation, and AuditLog.
Enforces multi-tenancy constraints and integer paisa storage.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class TenantModel(Base):
    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    currency = Column(String(3), nullable=False, default="BDT")
    is_demo = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=now_utc)

    users = relationship("UserModel", back_populates="tenant", cascade="all, delete-orphan")
    accounts = relationship("AccountModel", back_populates="tenant", cascade="all, delete-orphan")
    journal_entries = relationship("JournalEntryModel", back_populates="tenant", cascade="all, delete-orphan")
    obligations = relationship("ObligationModel", back_populates="tenant", cascade="all, delete-orphan")


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    phone = Column(String(32), nullable=False)
    role = Column(String(32), nullable=False, default="owner")  # "owner", "cashier", "accountant"
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)

    tenant = relationship("TenantModel", back_populates="users")

    __table_args__ = (
        UniqueConstraint("tenant_id", "phone", name="uq_tenant_phone"),
    )


class AccountModel(Base):
    __tablename__ = "accounts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(64), nullable=False)  # e.g. "asset:cash", "asset:wallet:nagad"
    name = Column(String(128), nullable=False)
    type = Column(String(32), nullable=False)  # "asset", "liability", "equity", "revenue", "expense"
    current_balance_paisa = Column(Integer, nullable=False, default=0)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=now_utc)

    tenant = relationship("TenantModel", back_populates="accounts")

    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_tenant_account_code"),
    )


class JournalEntryModel(Base):
    __tablename__ = "journal_entries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    entry_number = Column(String(64), nullable=False)
    description = Column(String(255), nullable=False)
    event_id = Column(String(128), nullable=True)  # Provider event or idempotency key
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=now_utc)

    tenant = relationship("TenantModel", back_populates="journal_entries")
    postings = relationship("PostingModel", back_populates="journal_entry", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("tenant_id", "event_id", name="uq_tenant_event_id"),
    )


class PostingModel(Base):
    __tablename__ = "postings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    journal_entry_id = Column(String(36), ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(String(36), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    direction = Column(String(8), nullable=False)  # "debit" or "credit"
    amount_paisa = Column(Integer, nullable=False)

    journal_entry = relationship("JournalEntryModel", back_populates="postings")
    account = relationship("AccountModel")


class ObligationModel(Base):
    __tablename__ = "obligations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    party_name = Column(String(255), nullable=False)
    invoice_ref = Column(String(64), nullable=True)
    amount_paisa = Column(Integer, nullable=False)
    accepted_methods = Column(String(128), nullable=False, default="cash")
    status = Column(String(32), nullable=False, default="unresolved")  # "unresolved", "supported", "settled"
    due_at = Column(DateTime, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=now_utc)

    tenant = relationship("TenantModel", back_populates="obligations")
    allocations = relationship("AllocationModel", back_populates="obligation", cascade="all, delete-orphan")


class AllocationModel(Base):
    __tablename__ = "allocations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    obligation_id = Column(String(36), ForeignKey("obligations.id", ondelete="CASCADE"), nullable=False)
    source_payment_id = Column(String(64), nullable=False)
    amount_paisa = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=now_utc)

    obligation = relationship("ObligationModel", back_populates="allocations")


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), nullable=True)
    action = Column(String(64), nullable=False)
    details = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=now_utc)


class EvidenceModel(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    mime_type = Column(String(128), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    content_sha256 = Column(String(64), nullable=False)
    storage_path = Column(String(512), nullable=False)
    source_type = Column(String(32), nullable=False)  # "pdf", "image", "audio", "text"
    status = Column(String(32), nullable=False, default="uploaded")  # "uploaded", "processing", "extracted", "failed", "reviewed"
    created_at = Column(DateTime, nullable=False, default=now_utc)

    claims = relationship("ExtractedClaimModel", back_populates="evidence", cascade="all, delete-orphan")


class ExtractedClaimModel(Base):
    __tablename__ = "extracted_claims"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    evidence_id = Column(String(36), ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False)
    party_name = Column(String(255), nullable=True)
    invoice_ref = Column(String(64), nullable=True)
    amount_paisa = Column(Integer, nullable=True)
    claim_date = Column(String(32), nullable=True)
    payment_method = Column(String(64), nullable=True)
    status = Column(String(32), nullable=False, default="proposed")  # "proposed", "corrected", "confirmed", "rejected"
    raw_model_response = Column(Text, nullable=True)
    is_reviewed = Column(Boolean, nullable=False, default=False)
    corrected_amount_paisa = Column(Integer, nullable=True)
    corrected_party_name = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)

    evidence = relationship("EvidenceModel", back_populates="claims")


class DailySnapshotModel(Base):
    __tablename__ = "daily_snapshots"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    snapshot_date = Column(String(10), nullable=False)  # "YYYY-MM-DD"
    opening_cash_paisa = Column(Integer, nullable=False, default=0)
    closing_cash_paisa = Column(Integer, nullable=True)
    actual_drawer_cash_paisa = Column(Integer, nullable=True)
    discrepancy_paisa = Column(Integer, nullable=True)
    status = Column(String(16), nullable=False, default="open")  # "open" or "closed"
    closed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)

    __table_args__ = (
        UniqueConstraint("tenant_id", "snapshot_date", name="uq_tenant_snapshot_date"),
    )


class PartyModel(Base):
    __tablename__ = "parties"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(32), nullable=True)
    party_type = Column(String(16), nullable=False, default="customer")  # "customer" or "supplier"
    current_due_paisa = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=now_utc)


class ProductItemModel(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    sku = Column(String(64), nullable=True)
    unit = Column(String(32), nullable=False, default="pcs")
    quantity_on_hand = Column(Integer, nullable=False, default=0)
    cost_price_paisa = Column(Integer, nullable=True)  # WAC per unit
    selling_price_paisa = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=now_utc)

    movements = relationship("StockMovementModel", back_populates="product", cascade="all, delete-orphan")


class StockMovementModel(Base):
    __tablename__ = "stock_movements"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    movement_type = Column(String(32), nullable=False)  # "sale_deduction", "purchase_addition", "return_restock", "adjustment"
    quantity_change = Column(Integer, nullable=False)  # positive or negative
    reference_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)

    product = relationship("ProductItemModel", back_populates="movements")

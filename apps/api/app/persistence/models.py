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
    Float,
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
    total_sales_paisa = Column(Integer, nullable=True, default=0)
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
    reorder_threshold = Column(Integer, nullable=True, default=5)
    lead_time_days = Column(Integer, nullable=True, default=3)
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


class ScenarioModel(Base):
    __tablename__ = "scenarios"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    horizon_days = Column(Integer, nullable=False, default=7)
    opening_cash_paisa = Column(Integer, nullable=False)
    assumed_daily_receipt_paisa = Column(Integer, nullable=False)
    planned_outflows_json = Column(Text, nullable=False)  # JSON list of paisa amounts
    reserve_target_paisa = Column(Integer, nullable=False)
    extra_expense_paisa = Column(Integer, nullable=False, default=0)
    extra_expense_day = Column(Integer, nullable=False, default=0)
    conditional_promise_paisa = Column(Integer, nullable=False, default=0)
    conditional_promise_date = Column(String(10), nullable=True)
    first_reserve_breach_date = Column(String(10), nullable=True)
    first_funding_shortfall_date = Column(String(10), nullable=True)
    closing_series_json = Column(Text, nullable=False)  # JSON list of closing balances
    created_at = Column(DateTime, nullable=False, default=now_utc)


class ActionModel(Base):
    __tablename__ = "actions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(64), nullable=False)  # "supplier_payment", "customer_reminder", "stock_reorder"
    recipient = Column(String(255), nullable=False)
    amount_paisa = Column(Integer, nullable=True)
    status = Column(String(32), nullable=False, default="draft")  # "draft", "pending_approval", "approved", "completed", "cancelled", "failed"
    idempotency_key = Column(String(128), nullable=True)
    payload_json = Column(Text, nullable=True)
    outcome_json = Column(Text, nullable=True)
    created_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)

    __table_args__ = (
        UniqueConstraint("tenant_id", "idempotency_key", name="uq_tenant_action_idempotency"),
    )


class CustomerPortalTokenModel(Base):
    __tablename__ = "customer_portal_tokens"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    token = Column(String(64), unique=True, nullable=False, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    party_id = Column(String(36), ForeignKey("parties.id", ondelete="CASCADE"), nullable=False)
    invoice_number = Column(String(64), nullable=False)
    amount_paisa = Column(Integer, nullable=False)
    description = Column(String(255), nullable=True)
    is_revoked = Column(Boolean, nullable=False, default=False)
    is_paid = Column(Boolean, nullable=False, default=False)
    expires_at = Column(DateTime, nullable=False)
    dispute_note = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)


class PurchaseDraftModel(Base):
    __tablename__ = "purchase_drafts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    supplier_id = Column(String(36), ForeignKey("parties.id", ondelete="SET NULL"), nullable=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost_paisa = Column(Integer, nullable=False)
    total_cost_paisa = Column(Integer, nullable=False)
    lead_time_days = Column(Integer, nullable=False, default=3)
    status = Column(String(32), nullable=False, default="draft")  # draft, approved, received, cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)
    received_at = Column(DateTime, nullable=True)

    product = relationship("ProductItemModel")
    supplier = relationship("PartyModel")


class RecurringCommitmentModel(Base):
    __tablename__ = "recurring_commitments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(String(64), nullable=False, default="other")  # rent, utilities, salary, loan, other
    amount_paisa = Column(Integer, nullable=False)
    frequency = Column(String(32), nullable=False, default="monthly")  # daily, weekly, monthly
    party_id = Column(String(36), ForeignKey("parties.id", ondelete="SET NULL"), nullable=True)
    due_day_of_month = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)

    party = relationship("PartyModel")


class CaseModel(Base):
    __tablename__ = "cases"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    case_type = Column(String(64), nullable=False)  # reconciliation, offer, receiving, claim, chat, business_help
    title = Column(String(255), nullable=False)
    status = Column(String(32), nullable=False, default="open")  # open, waiting_user, ready_for_review, approved, closed, rejected
    current_version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=False, default=now_utc)
    updated_at = Column(DateTime, nullable=False, default=now_utc, onupdate=now_utc)


class CaseVersionModel(Base):
    __tablename__ = "case_versions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    version_num = Column(Integer, nullable=False)
    state_snapshot_json = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)

    __table_args__ = (
        UniqueConstraint("case_id", "version_num", name="uq_case_version"),
    )


class EvidenceClaimModel(Base):
    __tablename__ = "evidence_claims"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True)
    claim_key = Column(String(64), nullable=False)
    is_critical = Column(Boolean, nullable=False, default=False)
    state = Column(String(32), nullable=False, default="unknown")  # supported, unknown, conflicted, unsupported
    weight = Column(Integer, nullable=False, default=1)
    source_locator_json = Column(Text, nullable=True)
    claim_value_json = Column(Text, nullable=True)
    evaluator_type = Column(String(32), nullable=False, default="deterministic")  # deterministic, model_rubric, human
    reasons_json = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)


class ConfidenceAssessmentModel(Base):
    __tablename__ = "confidence_assessments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    case_version = Column(Integer, nullable=False)
    policy_version = Column(String(32), nullable=False, default="evidence-support-v1")
    kind = Column(String(32), nullable=False, default="evidence_support_index")
    base_score = Column(Integer, nullable=True)
    score = Column(Integer, nullable=True)
    band = Column(String(32), nullable=False)  # strong, review, limited, unavailable
    readiness = Column(String(32), nullable=False)  # ready_for_review, needs_review, needs_clarification, blocked, unavailable
    can_execute_without_approval = Column(Boolean, nullable=False, default=False)
    blocking_validation_failure = Column(Boolean, nullable=False, default=False)
    unavailable_reason = Column(String(64), nullable=True)
    model_self_confidence = Column(Float, nullable=True)
    assessed_at = Column(DateTime, nullable=False, default=now_utc)
    assessment_details_json = Column(Text, nullable=True)


class DocumentChunkModel(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    document_id = Column(String(36), nullable=True, index=True)
    chunk_index = Column(Integer, nullable=False, default=0)
    source_type = Column(String(32), nullable=False)  # invoice, bill, offer, note, audio_transcript, return_terms
    content = Column(Text, nullable=False)
    normalized_content = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)
    embedding_json = Column(Text, nullable=True)
    model_version = Column(String(64), nullable=False, default="text-embedding-004")
    is_revoked = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=now_utc)


class AgentRunModel(Base):
    __tablename__ = "agent_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(String(36), ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="queued")  # queued, running, waiting_user, completed, failed, cancelled
    budget_calls_max = Column(Integer, nullable=False, default=8)
    budget_calls_used = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=now_utc)
    completed_at = Column(DateTime, nullable=True)


class AgentTaskModel(Base):
    __tablename__ = "agent_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(64), nullable=False)  # coordinator, terms_evidence, stock_demand, reconciliation, skeptic
    business_question = Column(String(255), nullable=False)
    status = Column(String(32), nullable=False, default="queued")  # queued, running, waiting_tool, succeeded, failed, cancelled, skipped
    result_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)
    completed_at = Column(DateTime, nullable=True)


class AgentEventModel(Base):
    __tablename__ = "agent_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    run_id = Column(String(36), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String(36), ForeignKey("agent_tasks.id", ondelete="SET NULL"), nullable=True, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    event_seq = Column(Integer, nullable=False)
    role = Column(String(64), nullable=False)
    event_type = Column(String(64), nullable=False)  # plan_created, tool_called, tool_receipt, clarification_requested, skeptic_critique, task_completed
    payload_json = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)


class CopilotSessionModel(Base):
    __tablename__ = "copilot_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="নতুন আলোচনা")
    context_entity_type = Column(String(64), nullable=True)  # case, supplier, product, general
    context_entity_id = Column(String(36), nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)
    updated_at = Column(DateTime, nullable=False, default=now_utc, onupdate=now_utc)


class CopilotMessageModel(Base):
    __tablename__ = "copilot_messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("copilot_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(32), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    intent = Column(String(64), nullable=True)  # canonical_query, hybrid_retrieval, agent_investigation, scenario_simulation, action_draft, clarification
    confidence_score = Column(Integer, nullable=True)
    confidence_band = Column(String(32), nullable=True)
    readiness = Column(String(32), nullable=True)
    citations_json = Column(Text, nullable=True)
    action_draft_id = Column(String(36), ForeignKey("actions.id", ondelete="SET NULL"), nullable=True)
    audio_metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=now_utc)


class SupplierOfferModel(Base):
    __tablename__ = "supplier_offers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    supplier_name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    sku = Column(String(64), nullable=False, index=True)
    pack_size = Column(Integer, nullable=False, default=1)
    pack_unit = Column(String(32), nullable=False, default="পিস")
    base_unit_price_paisa = Column(Integer, nullable=False)
    min_order_quantity = Column(Integer, nullable=False, default=1)
    bonus_condition_json = Column(Text, nullable=True)
    cash_discount_percent = Column(Float, nullable=False, default=0.0)
    credit_period_days = Column(Integer, nullable=False, default=0)
    delivery_fee_paisa = Column(Integer, nullable=False, default=0)
    payment_method_required = Column(String(32), nullable=False, default="any")  # cash, credit, any
    source_type = Column(String(32), nullable=False, default="manual")  # pdf, message, manual
    source_doc_id = Column(String(36), nullable=True)
    confidence_score = Column(Integer, nullable=False, default=80)
    has_critical_blocker = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=now_utc)


class BuyingComparisonModel(Base):
    __tablename__ = "buying_comparisons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    target_sku = Column(String(64), nullable=False, index=True)
    required_quantity = Column(Integer, nullable=False)
    best_offer_id = Column(String(36), ForeignKey("supplier_offers.id", ondelete="SET NULL"), nullable=True)
    comparison_summary_json = Column(Text, nullable=False)
    feasibility_status = Column(String(64), nullable=False, default="feasible_cash")  # feasible_cash, feasible_credit, infeasible_insufficient_cash
    created_at = Column(DateTime, nullable=False, default=now_utc)





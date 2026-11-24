"""Evidence-aware, owner-reviewed supplier settlement workspace."""
from __future__ import annotations
from datetime import datetime, timezone
from difflib import SequenceMatcher
import json
import re
import unicodedata
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, StrictInt
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.permissions import require_role
from app.domain.ledger import StandardAccount
from app.domain.supplier_settlement import OpenInvoice, propose_oldest_due_first, validate_manual_split
from app.persistence.models import (
    AccountModel, AllocationModel, AuditLogModel, EvidenceModel, ExtractedClaimModel,
    JournalEntryModel, ObligationModel, PartyAliasModel, PartyModel, PostingModel,
    SupplierSettlementEvidenceModel, SupplierSettlementLineModel, SupplierSettlementModel,
    UserModel, now_utc,
)

router = APIRouter(prefix="/api/v1/supplier-settlements", tags=["Supplier settlements"])


def normalize_party_name(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").casefold()
    value = re.sub(r"[^\w\u0980-\u09ff]+", " ", value, flags=re.UNICODE)
    return " ".join(value.split())


def remaining_for(db: Session, obligation: ObligationModel) -> int:
    used = db.query(func.coalesce(func.sum(AllocationModel.amount_paisa), 0)).filter_by(
        tenant_id=obligation.tenant_id, obligation_id=obligation.id
    ).scalar()
    return max(0, obligation.amount_paisa - int(used or 0))


def candidate_parties(db: Session, tenant_id: str, extracted_name: str | None):
    if not extracted_name:
        return {"match_status": "missing", "candidates": []}
    normalized = normalize_party_name(extracted_name)
    parties = db.query(PartyModel).filter_by(tenant_id=tenant_id, party_type="supplier").all()
    aliases = db.query(PartyAliasModel).filter_by(tenant_id=tenant_id).all()
    alias_by_party: dict[str, list[PartyAliasModel]] = {}
    for alias in aliases:
        alias_by_party.setdefault(alias.party_id, []).append(alias)
    exact = []
    scored = []
    for party in parties:
        names = [(normalize_party_name(party.name), "registered_name")]
        names += [(alias.normalized_alias, "reviewed_alias") for alias in alias_by_party.get(party.id, [])]
        best = max((SequenceMatcher(None, normalized, name).ratio(), kind, name) for name, kind in names)
        item = {"party_id": party.id, "name": party.name, "score": round(best[0], 3), "reason": best[1]}
        if any(name == normalized for name, _ in names):
            exact.append(item)
        elif best[0] >= 0.35:
            scored.append(item)
    if len(exact) == 1:
        return {"match_status": "exact", "candidates": exact}
    if len(exact) > 1:
        return {"match_status": "ambiguous", "candidates": exact}
    return {"match_status": "similar" if scored else "none", "candidates": sorted(scored, key=lambda x: -x["score"])[:5]}


class CreateSettlementDTO(BaseModel):
    supplier_party_id: str
    amount_paisa: StrictInt = Field(gt=0, le=99_999_999_999)
    channel: Literal["cash", "bkash", "nagad"] = "cash"
    idempotency_key: str = Field(min_length=4, max_length=128)


class AttachEvidenceDTO(BaseModel):
    evidence_id: str
    document_role: Literal["invoice", "payment_receipt", "supplier_message", "return_credit", "other"] = "other"


class ReviewEvidenceDTO(BaseModel):
    confirmed_party_id: str
    remember_extracted_name_as_alias: bool = False
    decision: Literal["confirmed", "ignored"] = "confirmed"
    verified_amount_paisa: StrictInt | None = Field(default=None, gt=0, le=99_999_999_999)
    verified_invoice_ref: str | None = Field(default=None, max_length=64)


class InvoiceDTO(BaseModel):
    invoice_ref: str = Field(min_length=1, max_length=64)
    amount_paisa: StrictInt = Field(gt=0, le=99_999_999_999)
    due_at: datetime
    evidence_id: str | None = None


class ManualLineDTO(BaseModel):
    obligation_id: str
    amount_paisa: StrictInt = Field(gt=0)


class PreviewDTO(BaseModel):
    expected_version: StrictInt = Field(ge=1)
    allocations: list[ManualLineDTO] | None = None


class ConfirmDTO(BaseModel):
    expected_version: StrictInt = Field(ge=1)
    expected_party_due_paisa: StrictInt = Field(ge=0)
    expected_account_balance_paisa: StrictInt = Field(ge=0)
    confirmed: Literal[True]


def get_settlement(db, tenant_id, settlement_id, lock=False):
    query = db.query(SupplierSettlementModel).filter_by(id=settlement_id, tenant_id=tenant_id)
    row = query.with_for_update().first() if lock else query.first()
    if not row:
        raise HTTPException(404, "Settlement not found.")
    return row


def evidence_contradictions(db: Session, row: SupplierSettlementModel) -> list[dict]:
    """Find incompatible reviewed supplier messages without inventing a winner."""
    links = db.query(SupplierSettlementEvidenceModel).filter_by(
        tenant_id=row.tenant_id, settlement_id=row.id, document_role="supplier_message", review_status="confirmed"
    ).all()
    groups: dict[str, list[dict]] = {}
    for link in links:
        claim = db.query(ExtractedClaimModel).filter_by(
            tenant_id=row.tenant_id, evidence_id=link.evidence_id
        ).order_by(ExtractedClaimModel.created_at.desc()).first()
        if not claim:
            continue
        amount = claim.corrected_amount_paisa or claim.amount_paisa
        if amount is None:
            continue
        invoice_ref = (claim.invoice_ref or "").strip()
        key = normalize_party_name(invoice_ref) if invoice_ref else "__settlement__"
        groups.setdefault(key, []).append({"link_id": link.id, "invoice_ref": invoice_ref or None, "amount_paisa": amount})
    conflicts = []
    for values in groups.values():
        amounts = sorted({item["amount_paisa"] for item in values})
        if len(values) > 1 and len(amounts) > 1:
            conflicts.append({"invoice_ref": values[0]["invoice_ref"], "amounts_paisa": amounts, "link_ids": [item["link_id"] for item in values]})
    return conflicts


def settlement_payload(db, row):
    party = db.query(PartyModel).filter_by(id=row.supplier_party_id, tenant_id=row.tenant_id).one()
    source_code = StandardAccount.CASH.value if row.channel == "cash" else "asset:wallet:" + row.channel
    account = db.query(AccountModel).filter_by(tenant_id=row.tenant_id, code=source_code).first()
    evidence_rows = db.query(SupplierSettlementEvidenceModel).filter_by(settlement_id=row.id, tenant_id=row.tenant_id).order_by(SupplierSettlementEvidenceModel.created_at).all()
    evidence = []
    for link in evidence_rows:
        document = db.query(EvidenceModel).filter_by(id=link.evidence_id, tenant_id=row.tenant_id).first()
        claim = db.query(ExtractedClaimModel).filter_by(evidence_id=link.evidence_id, tenant_id=row.tenant_id).order_by(ExtractedClaimModel.created_at.desc()).first()
        match = candidate_parties(db, row.tenant_id, link.extracted_party_name)
        evidence.append({
            "link_id": link.id, "evidence_id": link.evidence_id, "filename": document.filename if document else "unavailable",
            "mime_type": document.mime_type if document else None, "source_type": document.source_type if document else None,
            "processing_status": document.status if document else "unavailable", "document_role": link.document_role,
            "review_status": link.review_status, "party_match_status": link.party_match_status,
            "extracted_party_name": link.extracted_party_name,
            "extracted_invoice_ref": claim.invoice_ref if claim else None,
            "extracted_amount_paisa": (claim.corrected_amount_paisa or claim.amount_paisa) if claim else None,
            "extraction": json.loads(claim.raw_model_response or "{}") if claim else None,
            "party_candidates": match["candidates"], "suggestion_status": match["match_status"],
        })
    obligations = db.query(ObligationModel).filter_by(tenant_id=row.tenant_id, party_id=party.id).order_by(ObligationModel.due_at, ObligationModel.invoice_ref).all()
    invoice_rows = []
    for obligation in obligations:
        remaining = remaining_for(db, obligation)
        invoice_rows.append({"id": obligation.id, "invoice_ref": obligation.invoice_ref, "amount_paisa": obligation.amount_paisa, "remaining_paisa": remaining, "due_at": obligation.due_at.isoformat(), "status": obligation.status, "version": obligation.version})
    lines = db.query(SupplierSettlementLineModel).filter_by(tenant_id=row.tenant_id, settlement_id=row.id).all()
    line_rows = [{"id": line.id, "obligation_id": line.obligation_id, "amount_paisa": line.amount_paisa, "allocation_rule": line.allocation_rule, "obligation_version": line.obligation_version} for line in lines]
    allocated = sum(line["amount_paisa"] for line in line_rows)
    needs_review = [item for item in evidence if item["review_status"] == "needs_review"]
    contradictions = evidence_contradictions(db, row)
    return {
        "id": row.id, "status": row.status, "version": row.version, "amount_paisa": row.amount_paisa, "channel": row.channel,
        "supplier": {"id": party.id, "name": party.name, "current_due_paisa": party.current_due_paisa},
        "source_account": {"code": source_code, "current_balance_paisa": account.current_balance_paisa if account else 0},
        "evidence": evidence, "invoices": invoice_rows, "lines": line_rows,
        "allocated_paisa": allocated, "unallocated_paisa": row.amount_paisa - allocated,
        "needs_human_review": bool(needs_review or contradictions), "contradictions": contradictions, "journal_entry_id": row.journal_entry_id,
        "recording_scope": "Internal accounting only. No external payment is sent.",
    }


@router.get("")
def list_settlements(current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(SupplierSettlementModel).filter_by(tenant_id=current_user.tenant_id).order_by(SupplierSettlementModel.created_at.desc()).all()
    return [settlement_payload(db, row) for row in rows]


@router.post("")
def create_settlement(req: CreateSettlementDTO, current_user: UserModel = Depends(require_role(["owner", "accountant"])), db: Session = Depends(get_db)):
    party = db.query(PartyModel).filter_by(id=req.supplier_party_id, tenant_id=current_user.tenant_id, party_type="supplier").first()
    if not party:
        raise HTTPException(422, "Choose a registered supplier. Customer records cannot receive supplier settlements.")
    existing = db.query(SupplierSettlementModel).filter_by(tenant_id=current_user.tenant_id, idempotency_key=req.idempotency_key).first()
    if existing:
        if (existing.supplier_party_id, existing.amount_paisa, existing.channel) != (party.id, req.amount_paisa, req.channel):
            raise HTTPException(409, "This idempotency key belongs to a different settlement.")
        return settlement_payload(db, existing)
    row = SupplierSettlementModel(tenant_id=current_user.tenant_id, supplier_party_id=party.id, amount_paisa=req.amount_paisa, channel=req.channel, idempotency_key=req.idempotency_key, created_by_user_id=current_user.id)
    db.add(row); db.commit(); db.refresh(row)
    return settlement_payload(db, row)


@router.get("/{settlement_id}")
def get_settlement_detail(settlement_id: str, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    return settlement_payload(db, get_settlement(db, current_user.tenant_id, settlement_id))


@router.post("/{settlement_id}/evidence")
def attach_evidence(settlement_id: str, req: AttachEvidenceDTO, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    row = get_settlement(db, current_user.tenant_id, settlement_id)
    if row.status == "recorded": raise HTTPException(409, "Recorded settlements cannot accept new evidence.")
    document = db.query(EvidenceModel).filter_by(id=req.evidence_id, tenant_id=current_user.tenant_id).first()
    if not document: raise HTTPException(404, "Evidence not found.")
    claim = db.query(ExtractedClaimModel).filter_by(evidence_id=document.id, tenant_id=current_user.tenant_id).order_by(ExtractedClaimModel.created_at.desc()).first()
    extracted = (claim.corrected_party_name or claim.party_name) if claim else None
    match = candidate_parties(db, current_user.tenant_id, extracted)
    exact_ids = [item["party_id"] for item in match["candidates"]] if match["match_status"] == "exact" else []
    match_status = "matches_selected" if exact_ids == [row.supplier_party_id] else "conflict" if exact_ids else "needs_review"
    existing = db.query(SupplierSettlementEvidenceModel).filter_by(settlement_id=row.id, evidence_id=document.id).first()
    if not existing:
        existing = SupplierSettlementEvidenceModel(tenant_id=current_user.tenant_id, settlement_id=row.id, evidence_id=document.id, document_role=req.document_role, extracted_party_name=extracted, party_match_status=match_status)
        db.add(existing)
    row.version += 1; row.status = "collecting_evidence"; db.commit()
    return settlement_payload(db, row)


@router.post("/{settlement_id}/evidence/{link_id}/review")
def review_evidence(settlement_id: str, link_id: str, req: ReviewEvidenceDTO, current_user: UserModel = Depends(require_role(["owner", "accountant"])), db: Session = Depends(get_db)):
    row = get_settlement(db, current_user.tenant_id, settlement_id)
    link = db.query(SupplierSettlementEvidenceModel).filter_by(id=link_id, settlement_id=row.id, tenant_id=current_user.tenant_id).first()
    if not link: raise HTTPException(404, "Settlement evidence not found.")
    if req.confirmed_party_id != row.supplier_party_id:
        raise HTTPException(422, "Evidence can only be confirmed for the supplier selected on this settlement.")
    claim = db.query(ExtractedClaimModel).filter_by(
        evidence_id=link.evidence_id, tenant_id=current_user.tenant_id
    ).order_by(ExtractedClaimModel.created_at.desc()).first()
    match = candidate_parties(db, current_user.tenant_id, link.extracted_party_name)
    exact_other = any(item["score"] == 1 and item["party_id"] != row.supplier_party_id for item in match["candidates"])
    if req.decision == "confirmed" and exact_other:
        raise HTTPException(409, "The extracted name exactly matches another registered supplier. Ignore this source or start a settlement for that supplier.")
    if req.decision == "confirmed" and not claim:
        raise HTTPException(422, "No extracted claim is available to review. Ignore this source or re-upload a readable copy.")
    if claim and req.verified_amount_paisa is not None:
        claim.corrected_amount_paisa = req.verified_amount_paisa
        claim.reviewed_by_user_id = current_user.id
        claim.status = "corrected"
    if claim and req.verified_invoice_ref is not None:
        claim.invoice_ref = req.verified_invoice_ref.strip() or None
        claim.reviewed_by_user_id = current_user.id
        claim.status = "corrected"
    if req.decision == "confirmed" and link.document_role == "payment_receipt":
        effective_amount = (claim.corrected_amount_paisa or claim.amount_paisa) if claim else None
        if effective_amount != row.amount_paisa:
            raise HTTPException(422, "Verify a readable receipt amount equal to this settlement payment, or ignore the source.")
    if req.decision == "confirmed" and link.document_role == "invoice":
        if not claim or not claim.invoice_ref or (claim.corrected_amount_paisa or claim.amount_paisa) is None:
            raise HTTPException(422, "Verify the invoice number and amount, or ignore the unreadable source.")
    if req.remember_extracted_name_as_alias:
        if not link.extracted_party_name: raise HTTPException(422, "There is no extracted name to remember.")
        normalized = normalize_party_name(link.extracted_party_name)
        canonical_conflict = db.query(PartyModel).filter(PartyModel.tenant_id == current_user.tenant_id, PartyModel.party_type == "supplier", PartyModel.id != row.supplier_party_id).all()
        if any(normalize_party_name(p.name) == normalized for p in canonical_conflict):
            raise HTTPException(409, "That name is another registered supplier, so it cannot be saved as this supplier's alias.")
        alias = db.query(PartyAliasModel).filter_by(tenant_id=current_user.tenant_id, normalized_alias=normalized).first()
        if alias and alias.party_id != row.supplier_party_id:
            raise HTTPException(409, "That reviewed alias already belongs to another supplier.")
        if not alias:
            db.add(PartyAliasModel(tenant_id=current_user.tenant_id, party_id=row.supplier_party_id, alias=link.extracted_party_name, normalized_alias=normalized, source_evidence_id=link.evidence_id, reviewed_by_user_id=current_user.id))
    link.review_status = req.decision
    link.party_match_status = "merchant_confirmed" if req.decision == "confirmed" else "ignored"
    link.reviewed_by_user_id = current_user.id; link.reviewed_at = now_utc()
    row.version += 1; db.commit()
    return settlement_payload(db, row)


@router.post("/{settlement_id}/invoices")
def add_invoice(settlement_id: str, req: InvoiceDTO, current_user: UserModel = Depends(require_role(["owner", "accountant"])), db: Session = Depends(get_db)):
    row = get_settlement(db, current_user.tenant_id, settlement_id, lock=True)
    party = db.query(PartyModel).filter_by(id=row.supplier_party_id, tenant_id=current_user.tenant_id).with_for_update().one()
    ref = req.invoice_ref.strip()
    if db.query(ObligationModel).filter_by(tenant_id=current_user.tenant_id, party_id=party.id, invoice_ref=ref).first():
        raise HTTPException(409, "This supplier invoice is already registered.")
    if req.evidence_id:
        link = db.query(SupplierSettlementEvidenceModel).filter_by(settlement_id=row.id, evidence_id=req.evidence_id, tenant_id=current_user.tenant_id).first()
        if not link or link.review_status != "confirmed": raise HTTPException(422, "Review the source and supplier identity before registering its invoice.")
    existing = db.query(ObligationModel).filter_by(tenant_id=current_user.tenant_id, party_id=party.id).all()
    assigned = sum(remaining_for(db, obligation) for obligation in existing)
    if assigned + req.amount_paisa > party.current_due_paisa:
        raise HTTPException(422, "Invoice details exceed this supplier's verified aggregate due. Record the purchase liability through its dedicated workflow first.")
    obligation = ObligationModel(tenant_id=current_user.tenant_id, party_id=party.id, party_name=party.name, invoice_ref=ref, amount_paisa=req.amount_paisa, accepted_methods=row.channel, status="supported", due_at=req.due_at)
    db.add(obligation); row.version += 1; db.commit()
    return settlement_payload(db, row)


@router.post("/{settlement_id}/preview")
def preview_split(settlement_id: str, req: PreviewDTO, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    row = get_settlement(db, current_user.tenant_id, settlement_id, lock=True)
    if row.status == "recorded": raise HTTPException(409, "This settlement is already recorded.")
    if row.version != req.expected_version: raise HTTPException(409, "Settlement inputs changed. Refresh before recalculating.")
    obligations = db.query(ObligationModel).filter_by(tenant_id=current_user.tenant_id, party_id=row.supplier_party_id, status="supported").all()
    invoice_map = {ob.id: OpenInvoice(ob.id, remaining_for(db, ob), ob.due_at.isoformat(), ob.invoice_ref or "", ob.version) for ob in obligations}
    try:
        if req.allocations is None:
            proposal = propose_oldest_due_first(row.amount_paisa, invoice_map.values()); rule = "oldest_due_first"
        else:
            proposal = validate_manual_split(row.amount_paisa, invoice_map, [(line.obligation_id, line.amount_paisa) for line in req.allocations]); rule = "merchant_reviewed"
    except ValueError as error:
        raise HTTPException(422, str(error))
    db.query(SupplierSettlementLineModel).filter_by(tenant_id=current_user.tenant_id, settlement_id=row.id).delete()
    for line in proposal.lines:
        db.add(SupplierSettlementLineModel(tenant_id=current_user.tenant_id, settlement_id=row.id, obligation_id=line.obligation_id, amount_paisa=line.amount_paisa, allocation_rule=rule, obligation_version=line.obligation_version))
    pending = db.query(SupplierSettlementEvidenceModel).filter_by(tenant_id=current_user.tenant_id, settlement_id=row.id, review_status="needs_review").count()
    contradictions = evidence_contradictions(db, row)
    row.version += 1
    row.status = "ready_for_review" if proposal.unallocated_paisa == 0 and pending == 0 and not contradictions else "needs_clarification"
    db.commit()
    return settlement_payload(db, row)


@router.post("/{settlement_id}/confirm")
def confirm_settlement(settlement_id: str, req: ConfirmDTO, current_user: UserModel = Depends(require_role(["owner", "accountant"])), db: Session = Depends(get_db)):
    row = get_settlement(db, current_user.tenant_id, settlement_id, lock=True)
    if row.status == "recorded": return settlement_payload(db, row)
    if row.version != req.expected_version: raise HTTPException(409, "Settlement changed. Refresh before recording.")
    if row.status != "ready_for_review": raise HTTPException(422, "Resolve evidence review and allocate the full payment first.")
    if db.query(SupplierSettlementEvidenceModel).filter_by(tenant_id=current_user.tenant_id, settlement_id=row.id, review_status="needs_review").count():
        raise HTTPException(422, "Human review is still required for one or more sources.")
    if evidence_contradictions(db, row):
        raise HTTPException(422, "Reviewed supplier messages still contradict each other. Correct or ignore one source first.")
    party = db.query(PartyModel).filter_by(id=row.supplier_party_id, tenant_id=current_user.tenant_id, party_type="supplier").with_for_update().one()
    if party.current_due_paisa != req.expected_party_due_paisa: raise HTTPException(409, "Supplier due changed. Refresh the settlement.")
    source_code = StandardAccount.CASH.value if row.channel == "cash" else "asset:wallet:" + row.channel
    source = db.query(AccountModel).filter_by(tenant_id=current_user.tenant_id, code=source_code).with_for_update().first()
    payable = db.query(AccountModel).filter_by(tenant_id=current_user.tenant_id, code=StandardAccount.PAYABLES.value).with_for_update().first()
    if not source or source.current_balance_paisa != req.expected_account_balance_paisa: raise HTTPException(409, "Source account balance changed. Refresh the settlement.")
    if not payable: raise HTTPException(422, "Accounts payable ledger is unavailable.")
    lines = db.query(SupplierSettlementLineModel).filter_by(tenant_id=current_user.tenant_id, settlement_id=row.id).order_by(SupplierSettlementLineModel.obligation_id).all()
    if sum(line.amount_paisa for line in lines) != row.amount_paisa: raise HTTPException(422, "The payment is not fully allocated.")
    obligations = []
    for line in lines:
        obligation = db.query(ObligationModel).filter_by(id=line.obligation_id, tenant_id=current_user.tenant_id, party_id=party.id).with_for_update().one_or_none()
        if not obligation or obligation.version != line.obligation_version: raise HTTPException(409, "An invoice changed. Recalculate the split.")
        if line.amount_paisa > remaining_for(db, obligation): raise HTTPException(409, "An invoice no longer has enough remaining balance.")
        obligations.append((line, obligation))
    if row.amount_paisa > party.current_due_paisa or row.amount_paisa > source.current_balance_paisa or row.amount_paisa > payable.current_balance_paisa:
        raise HTTPException(422, "Payment exceeds a verified balance. Nothing was recorded.")
    try:
        entry = JournalEntryModel(tenant_id=current_user.tenant_id, entry_number="SST-" + uuid.uuid4().hex[:10].upper(), event_id="supplier-settlement:" + row.id, description="Reviewed supplier settlement for " + party.name)
        db.add(entry); db.flush()
        db.add_all([PostingModel(journal_entry_id=entry.id, account_id=payable.id, direction="debit", amount_paisa=row.amount_paisa), PostingModel(journal_entry_id=entry.id, account_id=source.id, direction="credit", amount_paisa=row.amount_paisa)])
        if db.query(AccountModel).filter_by(id=source.id, tenant_id=current_user.tenant_id, current_balance_paisa=req.expected_account_balance_paisa).filter(AccountModel.current_balance_paisa >= row.amount_paisa).update({AccountModel.current_balance_paisa: AccountModel.current_balance_paisa - row.amount_paisa}, synchronize_session=False) != 1: raise HTTPException(409, "Source balance changed concurrently.")
        if db.query(AccountModel).filter_by(id=payable.id, tenant_id=current_user.tenant_id).filter(AccountModel.current_balance_paisa >= row.amount_paisa).update({AccountModel.current_balance_paisa: AccountModel.current_balance_paisa - row.amount_paisa}, synchronize_session=False) != 1: raise HTTPException(409, "Payable balance changed concurrently.")
        if db.query(PartyModel).filter_by(id=party.id, tenant_id=current_user.tenant_id, current_due_paisa=req.expected_party_due_paisa).filter(PartyModel.current_due_paisa >= row.amount_paisa).update({PartyModel.current_due_paisa: PartyModel.current_due_paisa - row.amount_paisa}, synchronize_session=False) != 1: raise HTTPException(409, "Supplier due changed concurrently.")
        for line, obligation in obligations:
            db.add(AllocationModel(tenant_id=current_user.tenant_id, obligation_id=obligation.id, source_payment_id=entry.id, amount_paisa=line.amount_paisa))
            final_remaining = remaining_for(db, obligation) - line.amount_paisa
            obligation.status = "settled" if final_remaining == 0 else "supported"; obligation.version += 1
        row.status = "recorded"; row.journal_entry_id = entry.id; row.recorded_at = now_utc(); row.version += 1
        db.add(AuditLogModel(tenant_id=current_user.tenant_id, user_id=current_user.id, action="supplier_settlement_recorded", details=json.dumps({"settlement_id": row.id, "journal_entry_id": entry.id, "supplier_party_id": party.id, "amount_paisa": row.amount_paisa, "allocations": [{"obligation_id": line.obligation_id, "amount_paisa": line.amount_paisa} for line in lines], "scope": "internal_accounting_no_external_transfer"})))
        db.commit()
    except HTTPException:
        db.rollback(); raise
    except IntegrityError:
        db.rollback()
        existing = db.query(JournalEntryModel).filter_by(tenant_id=current_user.tenant_id, event_id="supplier-settlement:" + row.id).first()
        if existing: return settlement_payload(db, get_settlement(db, current_user.tenant_id, settlement_id))
        raise HTTPException(409, "A concurrent settlement changed these records. Refresh before retrying.")
    return settlement_payload(db, row)

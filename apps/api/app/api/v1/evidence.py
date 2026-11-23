"""
Evidence and Claim Ingestion Router.
Handles file upload, claim extraction, human review, and corrections.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.permissions import require_role
from app.ingestion.adapters import AIModelAdapter, NativePdfParser
from app.ingestion.storage import storage
from app.ingestion.schemas import StructuredClaimExtraction
from app.persistence.models import EvidenceModel, ExtractedClaimModel, UserModel

evidence_router = APIRouter(prefix="/api/v1/evidence", tags=["Evidence"])


class ClaimCorrectionRequest(BaseModel):
    corrected_amount_paisa: Optional[int] = Field(None, gt=0)
    corrected_party_name: Optional[str] = None
    status: str = Field("corrected", pattern="^(corrected|confirmed|rejected)$")


@evidence_router.post("/upload")
async def upload_evidence(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Tenant-owned evidence upload.
    Calculates SHA-256, stores in private folder, and performs initial extraction.
    """
    content = await file.read()
    sha256, storage_path, file_size, source_type = storage.store_file(
        tenant_id=current_user.tenant_id,
        original_filename=file.filename or "file.bin",
        content=content,
        mime_type=file.content_type or "application/octet-stream",
    )

    evidence = EvidenceModel(
        tenant_id=current_user.tenant_id,
        filename=file.filename or "file.bin",
        mime_type=file.content_type or "application/octet-stream",
        file_size_bytes=file_size,
        content_sha256=sha256,
        storage_path=storage_path,
        source_type=source_type,
        status="uploaded",
    )
    db.add(evidence)
    db.flush()

    # Perform initial parse
    extracted_text = ""
    if source_type == "pdf":
        extracted_text = NativePdfParser.extract_text(storage_path)
    elif source_type == "text":
        try:
            extracted_text = content.decode("utf-8")
        except UnicodeDecodeError:
            extracted_text = ""

    adapter = AIModelAdapter()
    try:
        if not adapter.is_configured():
            claim_extraction = StructuredClaimExtraction(party_name=None, invoice_ref=None, amount_paisa=None, claim_date=None, payment_method=None, confidence=0.0, raw_snippet=extracted_text)
        else:
            claim_extraction = adapter.parse_bangla_document(
            text_or_content=extracted_text,
            source_type=source_type,
            raw_bytes=content,
            mime_type=file.content_type,
            file_path=storage_path,
        )
    except Exception as exc:
        # Fallback to explicit unknowns on provider exception rather than crashing upload
        claim_extraction = StructuredClaimExtraction(
            party_name=None,
            invoice_ref=None,
            amount_paisa=None,
            claim_date=None,
            payment_method=None,
            confidence=0.0,
            raw_snippet=f"Extraction failure: {exc}",
        )

    claim = ExtractedClaimModel(
        tenant_id=current_user.tenant_id,
        evidence_id=evidence.id,
        party_name=claim_extraction.party_name,
        invoice_ref=claim_extraction.invoice_ref,
        amount_paisa=claim_extraction.amount_paisa,
        claim_date=claim_extraction.claim_date,
        payment_method=claim_extraction.payment_method,
        status="proposed",
        raw_model_response=claim_extraction.raw_snippet,
    )
    db.add(claim)
    evidence.status = "extracted" if adapter.is_configured() and claim.amount_paisa is not None else "needs_review"
    db.commit()

    return {
        "evidence_id": evidence.id,
        "content_sha256": evidence.content_sha256,
        "source_type": evidence.source_type,
        "claim_id": claim.id,
        "proposed_party": claim.party_name,
        "proposed_amount_paisa": claim.amount_paisa,
        "status": evidence.status,
    }


@evidence_router.get("/{evidence_id}")
def get_evidence_details(
    evidence_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Enforces tenant isolation: users can only view their tenant's evidence."""
    evidence = (
        db.query(EvidenceModel)
        .filter(EvidenceModel.id == evidence_id, EvidenceModel.tenant_id == current_user.tenant_id)
        .first()
    )
    if not evidence:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found.")

    claims = [
        {
            "id": c.id,
            "party_name": c.corrected_party_name or c.party_name,
            "amount_paisa": c.corrected_amount_paisa or c.amount_paisa,
            "status": c.status,
            "is_reviewed": c.is_reviewed,
            "claim_date": c.claim_date,
        }
        for c in evidence.claims
    ]

    return {
        "id": evidence.id,
        "filename": evidence.filename,
        "content_sha256": evidence.content_sha256,
        "source_type": evidence.source_type,
        "status": evidence.status,
        "claims": claims,
    }


@evidence_router.patch("/{evidence_id}/claims/{claim_id}")
def correct_claim(
    evidence_id: str,
    claim_id: str,
    req: ClaimCorrectionRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Human review and correction: allows editing amounts or parties."""
    claim = (
        db.query(ExtractedClaimModel)
        .filter(
            ExtractedClaimModel.id == claim_id,
            ExtractedClaimModel.evidence_id == evidence_id,
            ExtractedClaimModel.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not claim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Claim not found.")

    if req.corrected_amount_paisa is not None:
        claim.corrected_amount_paisa = req.corrected_amount_paisa
    if req.corrected_party_name is not None:
        claim.corrected_party_name = req.corrected_party_name

    claim.status = req.status
    claim.is_reviewed = True
    db.commit()

    return {
        "status": "updated",
        "claim_id": claim.id,
        "effective_amount_paisa": claim.corrected_amount_paisa or claim.amount_paisa,
        "effective_party_name": claim.corrected_party_name or claim.party_name,
        "is_reviewed": claim.is_reviewed,
    }

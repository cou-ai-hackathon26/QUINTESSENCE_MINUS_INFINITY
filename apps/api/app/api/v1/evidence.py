"""
Evidence and Claim Ingestion Router.
Handles file upload, claim extraction, human review, and corrections.
"""
from typing import List, Optional
import json
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.permissions import require_role
from app.ingestion.adapters import AIModelAdapter, NativePdfParser
from app.ingestion.storage import storage
from app.ingestion.schemas import StructuredClaimExtraction
from app.persistence.models import EvidenceModel, ExtractedClaimModel, UserModel,ProviderReceiptModel
from app.document_inference import extract_document,index_extracted_text
from app.groq_provider import configured,InferenceUnavailable,receipt_dict
from app.core.config import settings

evidence_router = APIRouter(prefix="/api/v1/evidence", tags=["Evidence"])


@evidence_router.get("/{evidence_id}/content")
def download_evidence(evidence_id: str, current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    evidence=db.query(EvidenceModel).filter(EvidenceModel.id==evidence_id,EvidenceModel.tenant_id==current_user.tenant_id).first()
    if not evidence:
        raise HTTPException(404,"Evidence not found.")
    path=Path(evidence.storage_path).resolve()
    root=(Path(storage.base_dir)/current_user.tenant_id).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise HTTPException(404,"Evidence content is unavailable.")
    return FileResponse(path,media_type='application/octet-stream',filename=evidence.filename,headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'none'; sandbox"})


class ClaimCorrectionRequest(BaseModel):
    corrected_amount_paisa: Optional[int] = Field(None, gt=0)
    corrected_party_name: Optional[str] = None
    status: str = Field("corrected", pattern="^(corrected|confirmed|rejected)$")


@evidence_router.post("/upload")
def upload_evidence(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Tenant-owned evidence upload.
    Calculates SHA-256, stores in private folder, and performs initial extraction.
    """
    content = file.file.read(10*1024*1024+1)
    if not content:raise HTTPException(422,'The uploaded file is empty.')
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

    return process_stored_evidence(evidence,content,current_user,db)


def process_stored_evidence(evidence,content,current_user,db):
    source_type=evidence.source_type;storage_path=evidence.storage_path
    # Parse original stored bytes; never create a second document for a retry.
    extracted_text = ""
    if source_type == "pdf":
        extracted_text = NativePdfParser.extract_text(storage_path)
    elif source_type == "text":
        try:
            extracted_text = content.decode("utf-8")
        except UnicodeDecodeError:
            extracted_text = ""

    adapter = AIModelAdapter()
    extraction=None;receipts=[];extraction_error=None
    try:
        if settings.AI_PROVIDER=='groq' and configured():
            extraction,receipts=extract_document(db,current_user.tenant_id,evidence,content,extracted_text)
            claim_extraction=StructuredClaimExtraction(party_name=extraction.party_name,invoice_ref=extraction.invoice_ref,amount_paisa=extraction.amount_paisa,claim_date=extraction.claim_date,payment_method=extraction.payment_method,confidence=None,raw_snippet=extraction.source_quote)
            extracted_text=extraction.extracted_text
        elif not adapter.is_configured() or settings.AI_PROVIDER=='groq':
            extraction_error='not_configured'
            claim_extraction = StructuredClaimExtraction(party_name=None, invoice_ref=None, amount_paisa=None, claim_date=None, payment_method=None, confidence=0.0, raw_snippet=extracted_text)
        else:
            claim_extraction = adapter.parse_bangla_document(
            text_or_content=extracted_text,
            source_type=source_type,
            raw_bytes=content,
            mime_type=evidence.mime_type,
            file_path=storage_path,
        )
    except Exception as exc:
        extraction_error=exc.code if isinstance(exc,InferenceUnavailable) else 'extraction_failed'
        # Fallback to explicit unknowns on provider exception rather than crashing upload
        claim_extraction = StructuredClaimExtraction(
            party_name=None,
            invoice_ref=None,
            amount_paisa=None,
            claim_date=None,
            payment_method=None,
            confidence=0.0,
            raw_snippet="Extraction unavailable. Original source remains stored for human review.",
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
        raw_model_response=json.dumps({'extraction':extraction.model_dump() if extraction else None,'extracted_text':extracted_text,'extraction_error':extraction_error,'source_quote':claim_extraction.raw_snippet},ensure_ascii=False),
    )
    db.add(claim)
    evidence.status = "extracted" if extraction or (adapter.is_configured() and settings.AI_PROVIDER!='groq' and claim.amount_paisa is not None) else "needs_review"
    index_extracted_text(db,current_user.tenant_id,evidence.id,extracted_text,'audio_transcript' if source_type=='audio' else 'invoice',claim.invoice_ref)
    db.commit()

    return {
        "evidence_id": evidence.id,
        "content_sha256": evidence.content_sha256,
        "source_type": evidence.source_type,
        "claim_id": claim.id,
        "proposed_party": claim.party_name,
        "proposed_amount_paisa": claim.amount_paisa,
        "status": evidence.status,
        "extraction_error":extraction_error,
        "provider_receipts":[receipt_dict(receipt) for receipt in receipts],
    }


@evidence_router.post('/{evidence_id}/reprocess')
def reprocess_evidence(evidence_id:str,current_user:UserModel=Depends(require_role(['owner','manager'])),db:Session=Depends(get_db)):
    evidence=db.query(EvidenceModel).filter_by(id=evidence_id,tenant_id=current_user.tenant_id).with_for_update().first()
    if not evidence:raise HTTPException(404,'Evidence not found.')
    if any(claim.is_reviewed for claim in evidence.claims):raise HTTPException(409,'Human-reviewed claims are preserved. Upload a new revision instead of replacing this review.')
    path=Path(evidence.storage_path).resolve();root=(Path(storage.base_dir)/current_user.tenant_id).resolve()
    if not path.is_relative_to(root) or not path.is_file():raise HTTPException(404,'Original source is unavailable.')
    content=path.read_bytes()
    if len(content)>10*1024*1024:raise HTTPException(413,'Original source exceeds the current upload limit.')
    import hashlib
    if hashlib.sha256(content).hexdigest()!=evidence.content_sha256:raise HTTPException(409,'The stored source checksum changed. Re-upload and review the original.')
    for claim in list(evidence.claims):db.delete(claim)
    db.flush()
    return process_stored_evidence(evidence,content,current_user,db)


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

    raw=next((claim.raw_model_response for claim in evidence.claims if claim.raw_model_response),'')
    try:extracted=json.loads(raw)
    except (ValueError,TypeError):extracted={'extracted_text':raw}
    receipts=db.query(ProviderReceiptModel).filter_by(tenant_id=current_user.tenant_id,entity_type='evidence',entity_id=evidence.id).order_by(ProviderReceiptModel.created_at.asc()).all()
    return {
        "id": evidence.id,
        "filename": evidence.filename,
        "content_sha256": evidence.content_sha256,
        "source_type": evidence.source_type,
        "status": evidence.status,
        "claims": claims,
        "extraction":extracted.get('extraction'),
        "extracted_text":extracted.get('extracted_text'),
        "extraction_error":extracted.get('extraction_error'),
        "provider_receipts":[receipt_dict(receipt) for receipt in receipts],
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

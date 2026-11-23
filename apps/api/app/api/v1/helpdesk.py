"""Business Help Desk API endpoints for Phase 24."""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.auth import get_current_user
from app.persistence.models import (
    BusinessDocumentModel,
    RegulatoryCorpusModel,
    UserModel,
)
from app.helpdesk.engine import BusinessHelpDeskEngine

helpdesk_router = APIRouter(prefix="/api/v1/helpdesk", tags=["Business Help Desk"])


class UploadDocumentIn(BaseModel):
    doc_type: str  # trade_license, tin_certificate, vat_bin_certificate, lease_agreement, fire_license
    title: str
    issuing_authority: str
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    file_path: Optional[str] = None


class SourcedGuidanceIn(BaseModel):
    query_text: str = Field(..., min_length=2)
    shop_type: str = "grocery"
    annual_turnover_paisa: int = Field(default=0, ge=0)


@helpdesk_router.get("/checklist")
def get_compliance_checklist(
    shop_type: str = Query("grocery"),
    annual_turnover_paisa: int = Query(0, ge=0),
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns business document compliance checklist tailored to shop type and turnover."""
    return BusinessHelpDeskEngine.get_compliance_checklist(
        db=db,
        tenant_id=current_user.tenant_id,
        shop_type=shop_type,
        annual_turnover_paisa=annual_turnover_paisa,
    )


@helpdesk_router.post("/documents", status_code=status.HTTP_201_CREATED)
def upload_document(
    payload: UploadDocumentIn,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Registers or updates a business compliance document in the vault."""
    doc = BusinessHelpDeskEngine.upload_document(
        db=db,
        tenant_id=current_user.tenant_id,
        doc_type=payload.doc_type,
        title=payload.title,
        issuing_authority=payload.issuing_authority,
        issue_date=payload.issue_date,
        expiry_date=payload.expiry_date,
        file_path=payload.file_path,
    )
    return {
        "id": doc.id,
        "doc_type": doc.doc_type,
        "title": doc.title,
        "issuing_authority": doc.issuing_authority,
        "issue_date": doc.issue_date,
        "expiry_date": doc.expiry_date,
        "status": doc.status,
    }


@helpdesk_router.get("/documents")
def list_documents(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lists registered business documents for current tenant."""
    docs = db.query(BusinessDocumentModel).filter(
        BusinessDocumentModel.tenant_id == current_user.tenant_id
    ).all()
    return [
        {
            "id": d.id,
            "doc_type": d.doc_type,
            "title": d.title,
            "issuing_authority": d.issuing_authority,
            "issue_date": d.issue_date,
            "expiry_date": d.expiry_date,
            "status": d.status,
            "created_at": d.created_at.isoformat(),
        }
        for d in docs
    ]


@helpdesk_router.post("/guidance")
def query_guidance(
    payload: SourcedGuidanceIn,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves authoritative statutory guidance with primary source citations."""
    return BusinessHelpDeskEngine.query_sourced_guidance(
        db=db,
        tenant_id=current_user.tenant_id,
        query_text=payload.query_text,
        shop_type=payload.shop_type,
        annual_turnover_paisa=payload.annual_turnover_paisa,
    )


@helpdesk_router.get("/corpus")
def list_corpus(
    db: Session = Depends(get_db),
):
    """Lists verified primary regulatory corpus topics and versions."""
    BusinessHelpDeskEngine.ensure_corpus_seeded(db)
    records = db.query(RegulatoryCorpusModel).filter(RegulatoryCorpusModel.is_active == True).all()
    return [
        {
            "id": r.id,
            "topic": r.topic,
            "title": r.title,
            "citation_reference": r.citation_reference,
            "authority_name": r.authority_name,
            "effective_date": r.effective_date,
            "last_reviewed_date": r.last_reviewed_date,
            "official_portal_url": r.official_portal_url,
        }
        for r in records
    ]

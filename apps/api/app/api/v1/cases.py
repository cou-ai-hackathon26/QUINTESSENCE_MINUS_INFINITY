"""
Cases, Claims, and Confidence Assessment API Router.
Tenant-isolated case lifecycle, required claim management, and deterministic evidence-support-v1 scoring.
"""
import json
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.confidence.policy import evaluate_confidence
from app.core.auth import get_current_user
from app.core.database import get_db
from app.persistence.models import (
    CaseModel,
    CaseVersionModel,
    ConfidenceAssessmentModel,
    EvidenceClaimModel,
    UserModel,
    now_utc,
)

cases_router = APIRouter(prefix="/api/v1/cases", tags=["Cases"])


class CaseCreateDTO(BaseModel):
    case_type: str = Field(..., pattern="^(reconciliation|offer|receiving|claim|chat|business_help)$")
    title: str = Field(..., min_length=2, max_length=255)


class ClaimRegisterDTO(BaseModel):
    claim_key: str
    is_critical: bool = False
    state: str = Field("unknown", pattern="^(supported|unknown|conflicted|unsupported)$")
    weight: Optional[int] = None
    source_locator: Optional[str] = None
    claim_value: Optional[Dict[str, Any]] = None
    reasons: List[str] = Field(default_factory=list)


class AssessCaseRequest(BaseModel):
    unavailable_reason: Optional[str] = None
    blocking_validation_failure: bool = False
    model_self_confidence: Optional[float] = None


@cases_router.post("", status_code=status.HTTP_201_CREATED)
def create_case(
    req: CaseCreateDTO,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = CaseModel(
        tenant_id=current_user.tenant_id,
        case_type=req.case_type,
        title=req.title,
        status="open",
        current_version=1,
    )
    db.add(case)
    db.flush()

    # Initial version record
    v1 = CaseVersionModel(
        case_id=case.id,
        tenant_id=current_user.tenant_id,
        version_num=1,
        state_snapshot_json=json.dumps({"status": "open", "title": req.title}),
    )
    db.add(v1)
    db.commit()
    db.refresh(case)

    return {
        "id": case.id,
        "case_type": case.case_type,
        "title": case.title,
        "status": case.status,
        "current_version": case.current_version,
    }


@cases_router.get("")
def list_cases(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cases = (
        db.query(CaseModel)
        .filter(CaseModel.tenant_id == current_user.tenant_id)
        .order_by(CaseModel.created_at.desc())
        .all()
    )
    return [
        {
            "id": c.id,
            "case_type": c.case_type,
            "title": c.title,
            "status": c.status,
            "current_version": c.current_version,
            "created_at": c.created_at.isoformat(),
        }
        for c in cases
    ]


@cases_router.get("/{case_id}")
def get_case_details(
    case_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = (
        db.query(CaseModel)
        .filter(CaseModel.id == case_id, CaseModel.tenant_id == current_user.tenant_id)
        .first()
    )
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")

    claims = (
        db.query(EvidenceClaimModel)
        .filter(EvidenceClaimModel.case_id == case_id, EvidenceClaimModel.tenant_id == current_user.tenant_id)
        .all()
    )

    latest_assessment = (
        db.query(ConfidenceAssessmentModel)
        .filter(ConfidenceAssessmentModel.case_id == case_id, ConfidenceAssessmentModel.tenant_id == current_user.tenant_id)
        .order_by(ConfidenceAssessmentModel.case_version.desc(), ConfidenceAssessmentModel.assessed_at.desc())
        .first()
    )

    return {
        "id": case.id,
        "case_type": case.case_type,
        "title": case.title,
        "status": case.status,
        "current_version": case.current_version,
        "claims": [
            {
                "id": cl.id,
                "claim_key": cl.claim_key,
                "is_critical": cl.is_critical,
                "state": cl.state,
                "weight": cl.weight,
                "reasons": json.loads(cl.reasons_json) if cl.reasons_json else [],
            }
            for cl in claims
        ],
        "latest_assessment": {
            "score": latest_assessment.score,
            "base_score": latest_assessment.base_score,
            "band": latest_assessment.band,
            "readiness": latest_assessment.readiness,
            "can_execute_without_approval": latest_assessment.can_execute_without_approval,
            "blocking_validation_failure": latest_assessment.blocking_validation_failure,
            "unavailable_reason": latest_assessment.unavailable_reason,
            "policy_version": latest_assessment.policy_version,
        }
        if latest_assessment
        else None,
    }


@cases_router.post("/{case_id}/claims")
def register_case_claims(
    case_id: str,
    claims: List[ClaimRegisterDTO],
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = (
        db.query(CaseModel)
        .filter(CaseModel.id == case_id, CaseModel.tenant_id == current_user.tenant_id)
        .first()
    )
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")

    registered = []
    for c in claims:
        ec = EvidenceClaimModel(
            tenant_id=current_user.tenant_id,
            case_id=case.id,
            claim_key=c.claim_key,
            is_critical=c.is_critical,
            state=c.state,
            weight=c.weight or (3 if c.is_critical else 1),
            source_locator_json=json.dumps({"locator": c.source_locator}) if c.source_locator else None,
            claim_value_json=json.dumps(c.claim_value) if c.claim_value else None,
            reasons_json=json.dumps(c.reasons) if c.reasons else None,
        )
        db.add(ec)
        registered.append(ec)

    db.commit()
    return {"status": "claims_registered", "count": len(registered)}


@cases_router.post("/{case_id}/assess")
def assess_case_confidence(
    case_id: str,
    req: AssessCaseRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    case = (
        db.query(CaseModel)
        .filter(CaseModel.id == case_id, CaseModel.tenant_id == current_user.tenant_id)
        .first()
    )
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found.")

    claims = (
        db.query(EvidenceClaimModel)
        .filter(EvidenceClaimModel.case_id == case_id, EvidenceClaimModel.tenant_id == current_user.tenant_id)
        .all()
    )

    claims_data = [
        {
            "key": cl.claim_key,
            "critical": cl.is_critical,
            "state": cl.state,
            "weight": cl.weight,
        }
        for cl in claims
    ]

    conf_result = evaluate_confidence(
        claims=claims_data,
        unavailable_reason=req.unavailable_reason,
        blocking_validation_failure=req.blocking_validation_failure,
        model_self_confidence=req.model_self_confidence,
    )

    assessment = ConfidenceAssessmentModel(
        tenant_id=current_user.tenant_id,
        case_id=case.id,
        case_version=case.current_version,
        policy_version=conf_result.policy_version,
        kind=conf_result.kind,
        base_score=conf_result.base_score,
        score=conf_result.score,
        band=conf_result.band,
        readiness=conf_result.readiness,
        can_execute_without_approval=conf_result.can_execute_without_approval,
        blocking_validation_failure=conf_result.blocking_validation_failure,
        unavailable_reason=conf_result.unavailable_reason,
        model_self_confidence=conf_result.model_self_confidence,
        assessed_at=now_utc(),
        assessment_details_json=json.dumps({
            "has_critical_blocker": conf_result.has_critical_blocker,
            "critical_blockers": conf_result.critical_blockers,
        }),
    )
    db.add(assessment)

    # Update case status based on readiness
    if conf_result.readiness == "needs_clarification":
        case.status = "waiting_user"
    elif conf_result.readiness == "ready_for_review":
        case.status = "ready_for_review"

    db.commit()

    return {
        "assessment_id": assessment.id,
        "case_id": case.id,
        "case_version": case.current_version,
        "base_score": conf_result.base_score,
        "score": conf_result.score,
        "band": conf_result.band,
        "readiness": conf_result.readiness,
        "has_critical_blocker": conf_result.has_critical_blocker,
        "critical_blockers": conf_result.critical_blockers,
        "can_execute_without_approval": conf_result.can_execute_without_approval,
        "calibrated_probability": None,
    }

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
    EvidenceModel,
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


class ReconciliationInputsDTO(BaseModel):
    demand_paisa: int = Field(...,gt=0)
    payment_paisa: int = Field(...,gt=0)
    return_paisa: int = Field(...,gt=0)
    supplier: str = Field(...,min_length=1,max_length=255)
    source_refs: List[str] = Field(...,min_length=3,max_length=3)
    source_ids: List[Optional[str]] = Field(default_factory=list,max_length=3)
    payment_applicable: bool
    return_accepted: bool
    payment_included: Optional[bool] = None
    return_included: Optional[bool] = None
    expected_version: int = Field(...,ge=1)


@cases_router.put('/{case_id}/inputs')
def save_reconciliation_inputs(case_id:str, req:ReconciliationInputsDTO, current_user:UserModel=Depends(get_current_user),db:Session=Depends(get_db)):
    case=db.query(CaseModel).filter_by(id=case_id,tenant_id=current_user.tenant_id).first()
    if not case: raise HTTPException(404,'Case not found.')
    if case.current_version!=req.expected_version: raise HTTPException(409,'The case changed. Refresh before saving your review.')
    if any(not ref.strip() for ref in req.source_refs): raise HTTPException(422,'Each fact needs a source reference.')
    for source_id in req.source_ids:
        if source_id and not db.query(EvidenceModel).filter_by(id=source_id,tenant_id=current_user.tenant_id).first(): raise HTTPException(404,'Source evidence not found in this workspace.')
    values=req.model_dump(exclude={'expected_version'})
    definitions=[('payment_applicable','supported' if req.payment_applicable else 'unknown',1,{'amount_paisa':req.payment_paisa}),('return_acceptance_and_prior_inclusion','supported' if req.return_accepted and req.return_included is not None else 'unknown',2,{'accepted':req.return_accepted,'prior_included':req.return_included}),('payment_prior_inclusion','supported' if req.payment_included is not None else 'unknown',0,{'included':req.payment_included})]
    for key,state,index,value in definitions:
        claim=db.query(EvidenceClaimModel).filter_by(tenant_id=current_user.tenant_id,case_id=case.id,claim_key=key).first()
        if not claim:
            claim=EvidenceClaimModel(tenant_id=current_user.tenant_id,case_id=case.id,claim_key=key,is_critical=True,weight=3)
            db.add(claim)
        claim.state=state;claim.claim_value_json=json.dumps(value);claim.evaluator_type='human';claim.source_locator_json=json.dumps({'reference':req.source_refs[index],'evidence_id':req.source_ids[index] if len(req.source_ids)>index else None});claim.reasons_json=json.dumps(['Owner-confirmed source interpretation; unknown inclusion remains unknown'])
    case.current_version+=1;case.status='waiting_user';case.updated_at=now_utc()
    db.add(CaseVersionModel(tenant_id=current_user.tenant_id,case_id=case.id,version_num=case.current_version,state_snapshot_json=json.dumps({'inputs':values})))
    db.commit()
    return {'case_id':case.id,'current_version':case.current_version,'inputs':values}


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

    snapshot=db.query(CaseVersionModel).filter_by(case_id=case.id,version_num=case.current_version,tenant_id=current_user.tenant_id).first()
    inputs=json.loads(snapshot.state_snapshot_json or '{}').get('inputs') if snapshot else None
    return {
        "id": case.id,
        "case_type": case.case_type,
        "title": case.title,
        "status": case.status,
        "current_version": case.current_version,
        "inputs": inputs,
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
        .filter(ConfidenceAssessmentModel.case_id == case_id, ConfidenceAssessmentModel.tenant_id == current_user.tenant_id, ConfidenceAssessmentModel.case_version == case.current_version)
        .order_by(ConfidenceAssessmentModel.case_version.desc(), ConfidenceAssessmentModel.assessed_at.desc())
        .first()
    )

    current_snapshot=db.query(CaseVersionModel).filter_by(case_id=case.id,version_num=case.current_version,tenant_id=current_user.tenant_id).first()
    return {
        "id": case.id,
        "case_type": case.case_type,
        "title": case.title,
        "status": case.status,
        "current_version": case.current_version,
        "inputs": json.loads(current_snapshot.state_snapshot_json or '{}').get('inputs') if current_snapshot else None,
        "claims": [
            {
                "id": cl.id,
                "claim_key": cl.claim_key,
                "is_critical": cl.is_critical,
                "state": cl.state,
                "weight": cl.weight,
                "source_locator": json.loads(cl.source_locator_json) if cl.source_locator_json else None,
                "claim_value": json.loads(cl.claim_value_json) if cl.claim_value_json else None,
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

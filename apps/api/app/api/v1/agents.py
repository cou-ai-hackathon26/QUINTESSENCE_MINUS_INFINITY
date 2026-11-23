"""
Agent Collaboration Router for Bounded Multi-Agent Workflows.
Endpoints for starting investigation runs, viewing task/event timelines,
and cancelling active runs with strict tenant isolation.
"""
from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.persistence.models import (
    AgentEventModel,
    AgentRunModel,
    AgentTaskModel,
    UserModel,
)
from app.agents.real_orchestrator import AgentOrchestrator, DEFAULT_BUDGET_MAX,execute_background
from app.groq_provider import configured,receipt_dict
from app.persistence.models import ProviderReceiptModel,CaseModel,ConfidenceAssessmentModel

agents_router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])


class StartRunRequestDTO(BaseModel):
    case_type: str = Field(default="reconciliation")
    case_id: Optional[str] = None
    query: str = Field(..., min_length=1, max_length=8000)
    budget_max: int = Field(default=DEFAULT_BUDGET_MAX, ge=1, le=20)


class AgentTaskResponseDTO(BaseModel):
    id: str
    role: str
    business_question: str
    status: str
    result_summary: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class AgentRunResponseDTO(BaseModel):
    id: str
    tenant_id: str
    case_id: Optional[str] = None
    status: str
    budget_calls_max: int
    budget_calls_used: int
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    tasks: List[AgentTaskResponseDTO] = []
    provider_receipts: List[Dict[str, Any]] = []
    case_assessment:Optional[Dict[str,Any]]=None
    source_version_stale:bool=False


class AgentEventResponseDTO(BaseModel):
    id: str
    run_id: str
    task_id: Optional[str] = None
    event_seq: int
    role: str
    event_type: str
    payload: Dict[str, Any] = {}
    created_at: Optional[str] = None


@agents_router.get('/runs')
def list_agent_runs(current_user:UserModel=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.query(AgentRunModel).filter_by(tenant_id=current_user.tenant_id).order_by(AgentRunModel.created_at.desc()).limit(30).all()
    return [{'id':r.id,'case_id':r.case_id,'status':r.status,'created_at':r.created_at.isoformat(),'budget_calls_used':r.budget_calls_used} for r in rows]


@agents_router.post("/runs", status_code=status.HTTP_202_ACCEPTED)
def start_agent_run(
    req: StartRunRequestDTO,
    background_tasks: BackgroundTasks,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Starts bounded multi-agent collaboration investigation under tenant isolation."""
    orchestrator = AgentOrchestrator(db=db, tenant_id=current_user.tenant_id)
    from app.core.limits import admit
    admit('agents:' + current_user.tenant_id, 10)
    active=db.query(AgentRunModel).filter(AgentRunModel.tenant_id==current_user.tenant_id,AgentRunModel.status.in_(['queued','running'])).count()
    if active>=2:raise HTTPException(429,'Two investigations are already active. Wait or cancel one before starting another.')
    if req.case_type not in ('stock_check','cash_query') and not configured():raise HTTPException(503,'Configure Groq inference before starting model specialists.')
    try:run = orchestrator.create_run(
        case_type=req.case_type,
        case_id=req.case_id,
        query=req.query,
        budget_max=req.budget_max,
    )
    except ValueError:raise HTTPException(404,'Case not found.')
    background_tasks.add_task(execute_background,db.get_bind(),current_user.tenant_id,run.id)
    return {'run_id':run.id,'status':'queued','mode':'actual_provider_and_tools'}


@agents_router.get("/runs/{run_id}", response_model=AgentRunResponseDTO)
def get_agent_run(
    run_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves an agent run with its tasks, enforcing tenant isolation."""
    run = (
        db.query(AgentRunModel)
        .filter(
            AgentRunModel.id == run_id,
            AgentRunModel.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent run not found")

    tasks = (
        db.query(AgentTaskModel)
        .filter(
            AgentTaskModel.run_id == run_id,
            AgentTaskModel.tenant_id == current_user.tenant_id,
        )
        .order_by(AgentTaskModel.created_at.asc())
        .all()
    )

    assessment=None;stale=run.status=='stale'
    if run.case_id:
        case=db.query(CaseModel).filter_by(id=run.case_id,tenant_id=current_user.tenant_id).first()
        source_event=db.query(AgentEventModel).filter_by(run_id=run.id,tenant_id=current_user.tenant_id,event_type='source_pack').first()
        source_version=json.loads(source_event.payload_json).get('case_version') if source_event else None
        stale=stale or bool(case and source_version is not None and case.current_version!=source_version)
        policy=db.query(ConfidenceAssessmentModel).filter_by(case_id=case.id,tenant_id=current_user.tenant_id,case_version=source_version).order_by(ConfidenceAssessmentModel.assessed_at.desc()).first() if case and source_version else None
        if policy and not stale:assessment={'score':policy.score,'band':policy.band,'readiness':policy.readiness,'case_version':policy.case_version,'policy_version':policy.policy_version,'scope':'Case evidence support at this version; not probability that model prose is correct.'}
    return AgentRunResponseDTO(
        id=run.id,
        tenant_id=run.tenant_id,
        case_id=run.case_id,
        status=run.status,
        budget_calls_max=run.budget_calls_max,
        budget_calls_used=run.budget_calls_used,
        created_at=run.created_at.isoformat() if run.created_at else None,
        completed_at=run.completed_at.isoformat() if run.completed_at else None,
        tasks=[
            AgentTaskResponseDTO(
                id=t.id,
                role=t.role,
                business_question=t.business_question,
                status=t.status,
                result_summary=t.result_summary,
                created_at=t.created_at.isoformat() if t.created_at else None,
                completed_at=t.completed_at.isoformat() if t.completed_at else None,
            )
            for t in tasks
        ],
        provider_receipts=[receipt_dict(r) for r in db.query(ProviderReceiptModel).filter_by(tenant_id=current_user.tenant_id,entity_type='agent_run',entity_id=run.id).order_by(ProviderReceiptModel.created_at.asc()).all()],
        case_assessment=assessment,source_version_stale=stale,
    )


@agents_router.get("/runs/{run_id}/events", response_model=List[AgentEventResponseDTO])
def get_agent_events(
    run_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves ordered event timeline for an agent run."""
    run = (
        db.query(AgentRunModel)
        .filter(
            AgentRunModel.id == run_id,
            AgentRunModel.tenant_id == current_user.tenant_id,
        )
        .first()
    )
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent run not found")

    events = (
        db.query(AgentEventModel)
        .filter(
            AgentEventModel.run_id == run_id,
            AgentEventModel.tenant_id == current_user.tenant_id,
        )
        .order_by(AgentEventModel.event_seq.asc())
        .all()
    )

    return [
        AgentEventResponseDTO(
            id=e.id,
            run_id=e.run_id,
            task_id=e.task_id,
            event_seq=e.event_seq,
            role=e.role,
            event_type=e.event_type,
            payload=json.loads(e.payload_json) if e.payload_json else {},
            created_at=e.created_at.isoformat() if e.created_at else None,
        )
        for e in events
    ]


@agents_router.post("/runs/{run_id}/cancel")
def cancel_agent_run(
    run_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancels an active agent run and logs cancellation event."""
    orchestrator = AgentOrchestrator(db=db, tenant_id=current_user.tenant_id)
    cancelled = orchestrator.cancel_run(run_id)
    if not cancelled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent run not found")
    return {"status": cancelled.status, "run_id": cancelled.id}

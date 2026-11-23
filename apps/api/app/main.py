"""
Shongoti Main FastAPI Application
"""
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.core.limits import BodyLimitMiddleware

from app.core.config import settings
from app.core.database import check_db_connection
from app.api.v1.router import api_router
from app.api.v1.evidence import evidence_router
from app.api.v1.merchant import merchant_router
from app.api.v1.scenarios import scenarios_router
from app.api.v1.actions_and_portal import actions_router
from app.api.v1.stock_and_reports import stock_reports_router
from app.api.v1.reconciliation import reconciliation_router
from app.api.v1.cases import cases_router
from app.api.v1.search import search_router
from app.api.v1.agents import agents_router
from app.api.v1.copilot import copilot_router
from app.api.v1.proposal_review import proposal_router
from app.api.v1.buying import buying_router
from app.api.v1.receiving import receiving_router
from app.api.v1.demand import demand_router
from app.api.v1.notifications import notifications_router
from app.api.v1.operations import operations_router
from app.api.v1.helpdesk import helpdesk_router
from app.api.v1.voice_speak import voice_router
from app.api.v1.workbench_auth import workbench_auth_router
from app.api.v1.workbench_data import workbench_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Bangla-first MSME financial workspace backend API",
)
app.add_middleware(BodyLimitMiddleware, maximum=settings.API_MAX_BODY_BYTES)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=[host.strip() for host in settings.ALLOWED_HOSTS.split(',') if host.strip()])

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(evidence_router)
app.include_router(merchant_router)
app.include_router(scenarios_router)
app.include_router(actions_router)
app.include_router(stock_reports_router)
app.include_router(reconciliation_router)
app.include_router(cases_router)
app.include_router(search_router)
app.include_router(agents_router)
app.include_router(copilot_router)
app.include_router(proposal_router)
app.include_router(buying_router)
app.include_router(receiving_router)
app.include_router(demand_router)
app.include_router(notifications_router)
app.include_router(operations_router)
app.include_router(helpdesk_router)
app.include_router(voice_router)
app.include_router(workbench_auth_router)
app.include_router(workbench_router)


@app.get("/health", status_code=status.HTTP_200_OK, tags=["System"])
def health_check():
    """Liveness probe: verifies API process is alive."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/ready", tags=["System"])
def readiness_check():
    """Readiness probe: distinguishes dependency readiness (e.g. database)."""
    db_status = check_db_connection()
    if db_status.get("connected"):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ready",
                "database": db_status,
                "version": settings.APP_VERSION,
            },
        )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "degraded",
            "database": db_status,
            "version": settings.APP_VERSION,
        },
    )


@app.get("/api/v1/info", tags=["Metadata"])
def get_info():
    """Application metadata and supported capabilities."""
    return {
        "name": "সংগতি (Shongoti)",
        "tagline": "ক্ষুদ্র ব্যবসার হিসাব, ভবিষ্যৎ পরিকল্পনা ও সিদ্ধান্ত",
        "version": settings.APP_VERSION,
        "currency": "BDT",
        "money_unit": "paisa",
        "supported_features": [
            "daily_merchant_workflow",
            "supplier_reconciliation",
            "cash_liquidity_planner",
            "decision_lab",
            "tenant_isolation",
        ],
    }

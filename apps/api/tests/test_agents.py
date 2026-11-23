"""
Phase 17 Test Suite: Bounded Collaboration & Visible Teamwork.
Validates:
1. Multi-agent collaboration with parallel specialists on compound cases.
2. Query optimization: simple factual queries skip unnecessary specialists.
3. Budget exhaustion: halts execution strictly when max call budget is reached.
4. Cancellation lifecycle and state transition.
5. Strict cross-tenant isolation on runs, tasks, and event timeline.
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


@pytest.fixture(scope="module")
def client():
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def tenant_a(client):
    suffix = uuid.uuid4().hex[:6]
    res = client.post("/api/v1/auth/login", json={"phone": f"0171{suffix}", "otp": "123456", "role": "owner"})
    data = res.json()
    return {"Authorization": f"Bearer {data['access_token']}", "tenant_id": data["tenant_id"]}


@pytest.fixture
def tenant_b(client):
    suffix = uuid.uuid4().hex[:6]
    res = client.post("/api/v1/auth/login", json={"phone": f"0172{suffix}", "otp": "123456", "role": "owner"})
    data = res.json()
    return {"Authorization": f"Bearer {data['access_token']}", "tenant_id": data["tenant_id"]}


def test_compound_case_multi_specialist_collaboration(client, tenant_a):
    """Verifies coordinator, terms specialist, reconciliation specialist, and skeptic auditor execution."""
    res = client.post(
        "/api/v1/agents/runs",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "case_type": "supplier_discrepancy",
            "query": "প্রাণ ডেইরি চালান ৪১ এর সাথে ফেরত ও মূল্যছাড়ের সমন্বয় হিসাব",
            "budget_max": 8,
        },
    )
    assert res.status_code == 201
    data = res.json()
    run_id = data["run_id"]
    assert data["status"] == "completed"
    assert data["budget_used"] > 1
    assert data["budget_used"] <= 8

    # Verify tasks created
    run_res = client.get(
        f"/api/v1/agents/runs/{run_id}",
        headers={"Authorization": tenant_a["Authorization"]},
    )
    assert run_res.status_code == 200
    run_data = run_res.json()
    assert run_data["id"] == run_id
    assert run_data["status"] == "completed"

    roles = [t["role"] for t in run_data["tasks"]]
    assert "terms_evidence" in roles
    assert "reconciliation" in roles
    assert "skeptic" in roles

    # Verify events timeline
    events_res = client.get(
        f"/api/v1/agents/runs/{run_id}/events",
        headers={"Authorization": tenant_a["Authorization"]},
    )
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) >= 4

    event_types = [e["event_type"] for e in events]
    assert "plan_created" in event_types
    assert "tool_receipt" in event_types
    assert "skeptic_critique" in event_types


def test_simple_query_optimization_skips_unnecessary_specialists(client, tenant_a):
    """Verifies simple query executes factual check and skips spawning heavy specialists."""
    res = client.post(
        "/api/v1/agents/runs",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "case_type": "stock_check",
            "query": "মিনিকেট চাল স্টক",
            "budget_max": 8,
        },
    )
    assert res.status_code == 201
    data = res.json()
    run_id = data["run_id"]
    assert data["status"] == "completed"

    # Tasks should only have single specialist and no heavy reconciliation or skeptic
    run_res = client.get(
        f"/api/v1/agents/runs/{run_id}",
        headers={"Authorization": tenant_a["Authorization"]},
    )
    run_data = run_res.json()
    roles = [t["role"] for t in run_data["tasks"]]
    assert "stock_demand" in roles
    assert "reconciliation" not in roles
    assert "skeptic" not in roles


def test_budget_exhaustion_halts_execution(client, tenant_a):
    """Verifies that when call budget is too low (e.g. 1), execution halts and status becomes failed."""
    res = client.post(
        "/api/v1/agents/runs",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "case_type": "supplier_discrepancy",
            "query": "বড় চালান ও জটিল বাকি হিসাব পর্যালোচনা",
            "budget_max": 1,  # Exhausted immediately after coordinator plan
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "failed"
    assert data["reason"] == "budget_exhausted"


def test_run_cancellation(client, tenant_a):
    """Verifies cancelling an active run updates status to cancelled and logs event."""
    # First create a run
    res = client.post(
        "/api/v1/agents/runs",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "case_type": "cash_query",
            "query": "ক্যাশ ব্যালেন্স",
            "budget_max": 5,
        },
    )
    run_id = res.json()["run_id"]

    # Cancel it
    cancel_res = client.post(
        f"/api/v1/agents/runs/{run_id}/cancel",
        headers={"Authorization": tenant_a["Authorization"]},
    )
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"

    # Verify run details reflect cancelled
    run_res = client.get(
        f"/api/v1/agents/runs/{run_id}",
        headers={"Authorization": tenant_a["Authorization"]},
    )
    assert run_res.json()["status"] == "cancelled"


def test_cross_tenant_isolation(client, tenant_a, tenant_b):
    """Tenant B must not see or access Tenant A's runs or events."""
    res_a = client.post(
        "/api/v1/agents/runs",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "case_type": "supplier_discrepancy",
            "query": "Tenant A Secret Supplier Dispute",
            "budget_max": 5,
        },
    )
    run_id_a = res_a.json()["run_id"]

    # Tenant B tries to get Tenant A's run -> 404
    get_res = client.get(
        f"/api/v1/agents/runs/{run_id_a}",
        headers={"Authorization": tenant_b["Authorization"]},
    )
    assert get_res.status_code == 404

    # Tenant B tries to get Tenant A's events -> 404
    events_res = client.get(
        f"/api/v1/agents/runs/{run_id_a}/events",
        headers={"Authorization": tenant_b["Authorization"]},
    )
    assert events_res.status_code == 404

    # Tenant B tries to cancel Tenant A's run -> 404
    cancel_res = client.post(
        f"/api/v1/agents/runs/{run_id_a}/cancel",
        headers={"Authorization": tenant_b["Authorization"]},
    )
    assert cancel_res.status_code == 404

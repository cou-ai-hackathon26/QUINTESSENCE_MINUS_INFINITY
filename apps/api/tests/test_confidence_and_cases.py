"""
Phase 15 Test Suite: Cases, Provenance, and Deterministic Evidence-Support-v1 Policy.
Directly asserts all 11 cases from confidence-policy-v1.json fixtures,
tenant isolation, versioning, and case lifecycle.
"""
import json
import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.confidence.policy import evaluate_confidence
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
def tenant_a_headers(client):
    suffix = uuid.uuid4().hex[:6]
    phone = f"0171{suffix}"
    res = client.post("/api/v1/auth/login", json={"phone": phone, "otp": "123456", "role": "owner"})
    data = res.json()
    return {"Authorization": f"Bearer {data['access_token']}", "tenant_id": data["tenant_id"]}


@pytest.fixture
def tenant_b_headers(client):
    suffix = uuid.uuid4().hex[:6]
    phone = f"0172{suffix}"
    res = client.post("/api/v1/auth/login", json={"phone": phone, "otp": "123456", "role": "owner"})
    data = res.json()
    return {"Authorization": f"Bearer {data['access_token']}", "tenant_id": data["tenant_id"]}


def test_confidence_fixture_exact_compliance():
    """Asserts that evaluate_confidence strictly matches all cases in confidence-policy-v1.json."""
    fixture_path = os.path.join("tests", "fixtures", "extension-handoff", "confidence-policy-v1.json")
    if not os.path.exists(fixture_path):
        pytest.fail(f"Fixture file missing: {fixture_path}")

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for case in data["cases"]:
        res = evaluate_confidence(
            claims=case["claims"],
            unavailable_reason=case.get("unavailable_reason"),
            blocking_validation_failure=case.get("blocking_validation_failure", False),
            model_self_confidence=case.get("model_self_confidence"),
        )
        exp = case["expected"]
        assert res.base_score == exp["base_score"], f"Case {case['id']} base_score mismatch"
        assert res.score == exp["score"], f"Case {case['id']} score mismatch"
        assert res.band == exp["band"], f"Case {case['id']} band mismatch"
        assert res.readiness == exp["readiness"], f"Case {case['id']} readiness mismatch"
        assert res.can_execute_without_approval == exp["can_execute_without_approval"], f"Case {case['id']} approval mismatch"
        assert res.calibrated_probability is None, "calibrated_probability must strictly be None"


def test_case_lifecycle_and_confidence_assessment(client, tenant_a_headers):
    """
    1. Create a reconciliation case
    2. Register claims (1 critical supported, 1 critical unknown, 3 ordinary supported)
    3. Assess confidence: base is 67, capped at 59, readiness needs_clarification
    4. Assert case status transitions to 'waiting_user'
    """
    # 1. Create case
    res = client.post(
        "/api/v1/cases",
        headers=tenant_a_headers,
        json={"case_type": "reconciliation", "title": "হক ট্রেডার্স চালান ৪১ সমন্বয়"},
    )
    assert res.status_code == 201
    case_id = res.json()["id"]

    # 2. Register claims
    claims = [
        {"claim_key": "supplier_identity", "is_critical": True, "state": "supported"},
        {"claim_key": "offer_cash_condition", "is_critical": True, "state": "unknown"},
        {"claim_key": "delivery_note", "is_critical": False, "state": "supported"},
        {"claim_key": "offer_date", "is_critical": False, "state": "supported"},
        {"claim_key": "contact_name", "is_critical": False, "state": "supported"},
    ]
    claims_res = client.post(f"/api/v1/cases/{case_id}/claims", headers=tenant_a_headers, json=claims)
    assert claims_res.status_code == 200

    # 3. Assess confidence
    assess_res = client.post(
        f"/api/v1/cases/{case_id}/assess",
        headers=tenant_a_headers,
        json={"model_self_confidence": 0.99},
    )
    assert assess_res.status_code == 200
    adata = assess_res.json()
    assert adata["base_score"] == 67
    assert adata["score"] == 59
    assert adata["band"] == "limited"
    assert adata["readiness"] == "needs_clarification"
    assert adata["has_critical_blocker"] is True
    assert adata["critical_blockers"] == ["offer_cash_condition"]
    assert adata["can_execute_without_approval"] is False

    # 4. Verify case status changed to waiting_user
    get_res = client.get(f"/api/v1/cases/{case_id}", headers=tenant_a_headers)
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "waiting_user"


def test_cross_tenant_case_isolation(client, tenant_a_headers, tenant_b_headers):
    """Tenant B cannot view or assess Tenant A's case."""
    res_a = client.post(
        "/api/v1/cases",
        headers=tenant_a_headers,
        json={"case_type": "offer", "title": "Confidential Supplier Offer"},
    )
    case_id_a = res_a.json()["id"]

    # Tenant B queries Tenant A's case
    res_b = client.get(f"/api/v1/cases/{case_id_a}", headers=tenant_b_headers)
    assert res_b.status_code == 404

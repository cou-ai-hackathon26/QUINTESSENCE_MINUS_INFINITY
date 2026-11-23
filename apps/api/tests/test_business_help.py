"""Tests for Phase 24: Maintained Business Help Desk

Verifies compliance checklist evaluation, document vault management,
verified statutory guidance citations, out-of-scope escalation safeguards, and tenant isolation.
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.persistence.models import (
    BusinessDocumentModel,
    RegulatoryCorpusModel,
)


@pytest.fixture(scope="module")
def client_and_session():
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
        yield c, TestingSessionLocal
    app.dependency_overrides.clear()


@pytest.fixture
def client(client_and_session):
    c, _ = client_and_session
    return c


@pytest.fixture
def db_session(client_and_session):
    _, SessionLocal = client_and_session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def tenant_a(client):
    suffix = uuid.uuid4().hex[:6]
    res = client.post("/api/v1/auth/login", json={"phone": f"0171{suffix}", "otp": "123456", "role": "owner"})
    data = res.json()
    return {"Authorization": data["access_token"], "tenant_id": data["tenant_id"]}


@pytest.fixture
def tenant_b(client):
    suffix = uuid.uuid4().hex[:6]
    res = client.post("/api/v1/auth/login", json={"phone": f"0172{suffix}", "otp": "123456", "role": "owner"})
    data = res.json()
    return {"Authorization": data["access_token"], "tenant_id": data["tenant_id"]}


def test_compliance_checklist_and_document_vault(client, tenant_a):
    """Verifies document upload updates checklist status from missing to valid."""
    auth_headers = {"Authorization": f"Bearer {tenant_a['Authorization']}"}

    # Step 1: Initial checklist - all documents missing
    chk_resp = client.get("/api/v1/helpdesk/checklist?shop_type=grocery&annual_turnover_paisa=200000000", headers=auth_headers)
    assert chk_resp.status_code == 200
    chk_data = chk_resp.json()
    assert chk_data["all_mandatory_compliant"] is False
    trade_item = next(item for item in chk_data["checklist"] if item["doc_type"] == "trade_license")
    assert trade_item["status"] == "missing"

    # Step 2: Upload trade license with valid future expiry
    up_resp = client.post(
        "/api/v1/helpdesk/documents",
        headers=auth_headers,
        json={
            "doc_type": "trade_license",
            "title": "ঢাকা উত্তর সিটি কর্পোরেশন ট্রেড লাইসেন্স",
            "issuing_authority": "ঢাকা উত্তর সিটি কর্পোরেশন অঞ্চল-৩",
            "issue_date": "2026-07-01",
            "expiry_date": "2027-06-30",
        },
    )
    assert up_resp.status_code == 201

    # Step 3: Re-check checklist - trade license must now be 'valid'
    chk_resp2 = client.get("/api/v1/helpdesk/checklist?shop_type=grocery", headers=auth_headers)
    assert chk_resp2.status_code == 200
    trade_item2 = next(item for item in chk_resp2.json()["checklist"] if item["doc_type"] == "trade_license")
    assert trade_item2["status"] == "valid"


def test_sourced_guidance_with_statutory_citation(client, tenant_a):
    """Verifies that queries retrieve verified primary statutes with official citations."""
    auth_headers = {"Authorization": f"Bearer {tenant_a['Authorization']}"}

    resp = client.post(
        "/api/v1/helpdesk/guidance",
        headers=auth_headers,
        json={
            "query_text": "ট্রেড লাইসেন্স নবায়নের শেষ তারিখ কবে এবং কোথায় করতে হবে?",
            "shop_type": "grocery",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["matched"] is True
    assert data["topic"] == "trade_license"
    assert "আইন ২০০৯" in data["citation"]["reference"]
    assert "etradelicense.gov.bd" in data["citation"]["official_portal_url"]
    assert data["escalation_required"] is False


def test_unverified_query_escalation_required(client, tenant_a):
    """Verifies that out-of-scope legal queries strictly trigger professional escalation rather than guessing."""
    auth_headers = {"Authorization": f"Bearer {tenant_a['Authorization']}"}

    resp = client.post(
        "/api/v1/helpdesk/guidance",
        headers=auth_headers,
        json={
            "query_text": "দোকানের পাশের জমির সীমানা নিয়ে প্রতিবেশীর সাথে মারামারি হলে কী মামলা করব?",
            "shop_type": "grocery",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["matched"] is False
    assert data["escalation_required"] is True
    assert "আইনজীবী" in data["advisory_bn"]


def test_cross_tenant_document_vault_isolation(client, tenant_a, tenant_b):
    """Verifies Tenant B cannot access Tenant A's uploaded business documents."""
    headers_a = {"Authorization": f"Bearer {tenant_a['Authorization']}"}
    headers_b = {"Authorization": f"Bearer {tenant_b['Authorization']}"}

    # Tenant A uploads a document
    client.post(
        "/api/v1/helpdesk/documents",
        headers=headers_a,
        json={
            "doc_type": "tin_certificate",
            "title": "Tenant A Secret TIN",
            "issuing_authority": "NBR",
        },
    )

    # Tenant B lists documents
    resp_b = client.get("/api/v1/helpdesk/documents", headers=headers_b)
    assert resp_b.status_code == 200
    assert len(resp_b.json()) == 0

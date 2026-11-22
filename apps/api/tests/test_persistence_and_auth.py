"""
Phase 03 Tests: Persistence, Authentication, Tenant Isolation, and Invariant Verification.
Executes against both SQLite test session and local PostgreSQL 16 database.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.config import settings
from app.main import app
from app.persistence.models import (
    TenantModel,
    UserModel,
    AccountModel,
    JournalEntryModel,
    PostingModel,
)


from sqlalchemy.pool import StaticPool

@pytest.fixture(scope="module")
def client():
    # Use SQLite in-memory with StaticPool to share connection state
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


def test_auth_demo_session(client):
    response = client.post("/api/v1/auth/demo-session")
    assert response.status_code == 200
    data = response.json()
    assert data["is_demo"] is True
    assert data["role"] == "owner"
    assert "access_token" in data


def test_auth_login_and_token_creation(client):
    # Valid OTP creates live tenant
    response = client.post("/api/v1/auth/login", json={"phone": "01711223344", "otp": "123456"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_demo"] is False
    assert data["role"] == "owner"

    # Invalid OTP fails
    bad_res = client.post("/api/v1/auth/login", json={"phone": "01711223344", "otp": "000000"})
    assert bad_res.status_code == 400


def test_tenant_isolation_and_cross_tenant_denial(client):
    # 1. Login as Tenant A
    res_a = client.post("/api/v1/auth/login", json={"phone": "01811111111", "otp": "123456"})
    token_a = res_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Login as Tenant B
    res_b = client.post("/api/v1/auth/login", json={"phone": "01922222222", "otp": "123456"})
    token_b = res_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Tenant A posts an entry
    post_res = client.post(
        "/api/v1/ledger/post",
        headers=headers_a,
        json={
            "description": "Tenant A initial capital",
            "event_id": "EVT-A-01",
            "postings": [
                {"account_code": "asset:cash", "direction": "debit", "amount_paisa": 100000},
                {"account_code": "equity:owner_capital", "direction": "credit", "amount_paisa": 100000},
            ],
        },
    )
    assert post_res.status_code == 200

    # Tenant A sees their cash account
    accounts_a = client.get("/api/v1/ledger/accounts", headers=headers_a).json()
    assert len(accounts_a) >= 1
    assert any(a["code"] == "asset:cash" and a["current_balance_paisa"] == 100000 for a in accounts_a)

    # Tenant B lists accounts: strictly isolated, cannot see Tenant A's accounts
    accounts_b = client.get("/api/v1/ledger/accounts", headers=headers_b).json()
    assert not any(a["code"] == "asset:cash" for a in accounts_b)


def test_idempotency_duplicate_event_rejection(client):
    res = client.post("/api/v1/auth/login", json={"phone": "01755555555", "otp": "123456"})
    headers = {"Authorization": f"Bearer {res.json()['access_token']}"}

    payload = {
        "description": "Provider receipt",
        "event_id": "TX-PROV-999",
        "postings": [
            {"account_code": "asset:cash", "direction": "debit", "amount_paisa": 50000},
            {"account_code": "revenue:sales", "direction": "credit", "amount_paisa": 50000},
        ],
    }

    # First attempt: succeeds
    res1 = client.post("/api/v1/ledger/post", headers=headers, json=payload)
    assert res1.status_code == 200

    # Second attempt: rejected with 409 Conflict
    res2 = client.post("/api/v1/ledger/post", headers=headers, json=payload)
    assert res2.status_code == 409
    assert "already processed" in res2.json()["detail"]


def test_unbalanced_entry_rejected(client):
    res = client.post("/api/v1/auth/login", json={"phone": "01766666666", "otp": "123456"})
    headers = {"Authorization": f"Bearer {res.json()['access_token']}"}

    # Debits 50000 != Credits 40000
    res_bad = client.post(
        "/api/v1/ledger/post",
        headers=headers,
        json={
            "description": "Unbalanced entry attempt",
            "postings": [
                {"account_code": "asset:cash", "direction": "debit", "amount_paisa": 50000},
                {"account_code": "revenue:sales", "direction": "credit", "amount_paisa": 40000},
            ],
        },
    )
    assert res_bad.status_code == 422
    assert "Unbalanced journal entry" in res_bad.json()["detail"]


def test_postgresql_live_connection_and_schema():
    """Directly verifies actual PostgreSQL 16 server connectivity and table creation."""
    pg_url = "postgresql+psycopg://postgres@127.0.0.1:5432/shongoti"
    try:
        pg_engine = create_engine(pg_url)
        with pg_engine.connect() as conn:
            res = conn.execute(text("SELECT version();")).scalar()
            assert "PostgreSQL 16" in res
        
        # Create schema in PostgreSQL
        Base.metadata.create_all(bind=pg_engine)
        
        # Verify tables created in PostgreSQL
        with pg_engine.connect() as conn:
            tables = conn.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            ).fetchall()
            table_names = [t[0] for t in tables]
            assert "tenants" in table_names
            assert "users" in table_names
            assert "accounts" in table_names
            assert "journal_entries" in table_names
            assert "postings" in table_names
            assert "obligations" in table_names
    except Exception as exc:
        pytest.fail(f"PostgreSQL test failed: {exc}")

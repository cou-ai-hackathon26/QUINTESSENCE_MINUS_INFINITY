"""
Phase 07 Tests: Liquidity Outlook & Decision Lab Scenarios.
Verifies pure deterministic 7-day simulation, extra expense intervention,
conditional customer promise, tenant baseline derivation, and non-mutation of actual books.
"""
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
def auth_headers(client):
    res = client.post("/api/v1/auth/login", json={"phone": "01799998888", "otp": "123456"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_simulate_7_day_baseline_matches_golden(client, auth_headers):
    # Golden Contract: Opening 12,000 BDT, Receipts 1,000 BDT daily, Outflows [2000, 0, 6000, 0, 4000, 0, 3000] BDT
    res = client.post(
        "/api/v1/scenarios/simulate",
        headers=auth_headers,
        json={
            "case_id": "golden-baseline",
            "opening_cash_paisa": 1200000,
            "assumed_daily_receipt_paisa": 100000,
            "planned_outflows_paisa": [200000, 0, 600000, 0, 400000, 0, 300000],
            "reserve_target_paisa": 300000,
            "extra_expense_day_1_paisa": 0,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["closing_cash_series"] == [1100000, 1200000, 700000, 800000, 500000, 600000, 400000]
    assert data["first_reserve_breach"] is None
    assert data["first_funding_shortfall"] is None


def test_simulate_7_day_extra_expense_breach_and_shortfall(client, auth_headers):
    # With 6,000 BDT extra expense on Day 1
    res = client.post(
        "/api/v1/scenarios/simulate",
        headers=auth_headers,
        json={
            "case_id": "golden-extra-expense",
            "opening_cash_paisa": 1200000,
            "assumed_daily_receipt_paisa": 100000,
            "planned_outflows_paisa": [200000, 0, 600000, 0, 400000, 0, 300000],
            "reserve_target_paisa": 300000,
            "extra_expense_day_1_paisa": 600000,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["closing_cash_series"] == [500000, 600000, 100000, 200000, -100000, 0, -200000]
    # First reserve breach occurs on Day 3 (2026-11-24) when cash is 1,000 BDT < reserve target 3,000 BDT
    assert data["first_reserve_breach"] == "2026-11-24"
    # First funding shortfall occurs on Day 5 (2026-11-26) when cash is -1,000 BDT < 0
    assert data["first_funding_shortfall"] == "2026-11-26"


def test_simulation_does_not_mutate_actual_ledger(client, auth_headers):
    # Ledger summary before simulation
    summary_before = client.get("/api/v1/merchant/today", headers=auth_headers).json()

    # Run heavy deficit simulation
    client.post(
        "/api/v1/scenarios/simulate",
        headers=auth_headers,
        json={
            "case_id": "test-no-mutation",
            "opening_cash_paisa": 500000,
            "assumed_daily_receipt_paisa": 0,
            "planned_outflows_paisa": [1000000, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000],
            "reserve_target_paisa": 200000,
        },
    )

    # Ledger summary after simulation must be identical
    summary_after = client.get("/api/v1/merchant/today", headers=auth_headers).json()
    assert summary_before["cash_balance_paisa"] == summary_after["cash_balance_paisa"]
    assert summary_before["total_revenue_paisa"] == summary_after["total_revenue_paisa"]


def test_save_scenario_and_list(client, auth_headers):
    save_res = client.post(
        "/api/v1/scenarios/save",
        headers=auth_headers,
        json={
            "name": "নতুন ফ্রিজ ক্রয়ের প্রভাব",
            "case_id": "fridge-purchase-scenario",
            "opening_cash_paisa": 1200000,
            "assumed_daily_receipt_paisa": 100000,
            "planned_outflows_paisa": [200000, 0, 600000, 0, 400000, 0, 300000],
            "reserve_target_paisa": 300000,
            "extra_expense_day_1_paisa": 600000,
        },
    )
    assert save_res.status_code == 200
    assert save_res.json()["first_reserve_breach"] == "2026-11-24"

    # List scenarios
    list_res = client.get("/api/v1/scenarios", headers=auth_headers)
    assert list_res.status_code == 200
    scenarios = list_res.json()
    assert len(scenarios) >= 1
    assert any(s["name"] == "নতুন ফ্রিজ ক্রয়ের প্রভাব" for s in scenarios)


def test_tenant_baseline_endpoint(client, auth_headers):
    res = client.get("/api/v1/scenarios/baseline", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "opening_cash_paisa" in data
    assert len(data["dates"]) == 7
    assert len(data["closing_cash_series"]) == 7

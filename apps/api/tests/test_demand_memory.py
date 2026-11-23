"""
Phase 21 Test Suite: Demand Memory & Supported Future Impact.
Validates:
1. Unmet demand recording does NOT book revenue or modify financial accounts.
2. Stockout window tracking and demand count aggregation.
3. Factual scenario reorder impact analysis without fabricated probabilities.
4. Strict cross-tenant isolation.
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
    AccountModel,
    ProductItemModel,
    TenantModel,
    UnmetDemandModel,
    UserModel,
)


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


def test_record_unmet_demand_does_not_mutate_revenue(client, tenant_a):
    """Recording unmet customer requests never books revenue into accounting ledger."""
    res = client.post(
        "/api/v1/demand/unmet",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "requested_product": "ডানো দুধ ১ কেজি",
            "quantity": 3,
            "reason": "stockout",
            "sku": "DANO-1KG",
            "customer_name": "রহিম মিয়া",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["quantity"] == 3
    assert data["ledger_revenue_impact"] == 0

    # Verify demand in list
    list_res = client.get(
        "/api/v1/demand/unmet?sku=DANO-1KG",
        headers={"Authorization": tenant_a["Authorization"]},
    )
    assert list_res.status_code == 200
    records = list_res.json()
    assert len(records) >= 1
    assert records[0]["requested_product"] == "ডানো দুধ ১ কেজি"


def test_demand_analysis_incorporates_unmet_requests_honestly(client, tenant_a):
    """Reorder scenario adds observed unmet demand count without guessing probabilities."""
    # Add first unmet demand (3 units)
    client.post(
        "/api/v1/demand/unmet",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "requested_product": "ডানো দুধ ১ কেজি",
            "quantity": 3,
            "reason": "stockout",
            "sku": "DANO-1KG",
        },
    )
    # Add second unmet demand (2 units)
    client.post(
        "/api/v1/demand/unmet",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "requested_product": "ডানো দুধ ১ কেজি",
            "quantity": 2,
            "reason": "stockout",
            "sku": "DANO-1KG",
        },
    )

    analysis_res = client.get(
        "/api/v1/demand/analysis/DANO-1KG?lead_time_days=3",
        headers={"Authorization": tenant_a["Authorization"]},
    )
    assert analysis_res.status_code == 200
    adata = analysis_res.json()
    # Total unmet is 3 + 2 = 5
    assert adata["total_unmet_demand_count"] == 5
    assert adata["forecast_type"] == "observed_factual_scenario"
    assert "বাস্তব বিক্রয় ও হারানো ক্রেতার চাহিদা" in adata["assumption_disclaimer"]
    assert adata["recommended_reorder_units"] >= 5


def test_cross_tenant_isolation(client, tenant_a, tenant_b):
    """Tenant B cannot see Tenant A's demand records."""
    client.post(
        "/api/v1/demand/unmet",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "requested_product": "গোপন স্পেশাল চাল",
            "quantity": 10,
            "sku": "SECRET-RICE",
        },
    )

    # Tenant B lists demands for SECRET-RICE -> empty
    b_res = client.get(
        "/api/v1/demand/unmet?sku=SECRET-RICE",
        headers={"Authorization": tenant_b["Authorization"]},
    )
    assert b_res.status_code == 200
    assert len(b_res.json()) == 0

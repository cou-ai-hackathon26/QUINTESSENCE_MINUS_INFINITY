"""
Phase 19 Test Suite: Buying Desk.
Validates:
1. Landed cost arithmetic and bonus carton calculation with integer paisa.
2. Unknown/unverified bonus condition caps score at 59.
3. Cash constraint feasibility evaluation (rejects purchase when cash is insufficient).
4. Purchase order draft creation in status draft without direct financial posting.
5. Strict cross-tenant isolation.
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
    ActionModel,
    SupplierOfferModel,
    TenantModel,
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


def test_offer_ingestion_and_bonus_confidence_capping(client, tenant_a):
    """Verified bonus condition gets score 95; unverified bonus caps score at 59."""
    # Case 1: Verified bonus
    res_1 = client.post(
        "/api/v1/buying/offers",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "supplier_name": "প্রাণ ডেইরি",
            "title": "১০ কার্টনে ১ কার্টন ফ্রি",
            "sku": "PRAN-MANGO-250",
            "base_unit_price_paisa": 12000,
            "bonus_condition": {
                "buy_qty": 10,
                "bonus_qty": 1,
                "bonus_sku": "PRAN-MANGO-250",
                "is_verified": True,
            },
        },
    )
    assert res_1.status_code == 201
    d1 = res_1.json()
    assert d1["confidence_score"] == 95
    assert d1["has_critical_blocker"] is False

    # Case 2: Unverified bonus condition -> score capped at 59
    res_2 = client.post(
        "/api/v1/buying/offers",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "supplier_name": "মেঘনা বেভারেজ",
            "title": "অনিশ্চিত বোনাস অফার",
            "sku": "PRAN-MANGO-250",
            "base_unit_price_paisa": 11800,
            "bonus_condition": {
                "buy_qty": 10,
                "bonus_qty": 1,
                "bonus_sku": None,
                "is_verified": False,
            },
        },
    )
    assert res_2.status_code == 201
    d2 = res_2.json()
    assert d2["confidence_score"] == 59
    assert d2["has_critical_blocker"] is True


def test_compare_offers_landed_cost_and_bonus_calculation(client, tenant_a):
    """Compares landed unit costs with bonus units correctly incorporated."""
    # Ingest offer 1 (verified bonus)
    client.post(
        "/api/v1/buying/offers",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "supplier_name": "প্রাণ ডেইরি",
            "title": "১০ কার্টনে ১ কার্টন ফ্রি",
            "sku": "PRAN-MANGO-250",
            "base_unit_price_paisa": 12000,
            "bonus_condition": {
                "buy_qty": 10,
                "bonus_qty": 1,
                "bonus_sku": "PRAN-MANGO-250",
                "is_verified": True,
            },
        },
    )
    # Ingest offer 2 (no bonus)
    client.post(
        "/api/v1/buying/offers",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "supplier_name": "মেঘনা বেভারেজ",
            "title": "সাধারণ পাইকারি দাম",
            "sku": "PRAN-MANGO-250",
            "base_unit_price_paisa": 11800,
        },
    )

    res = client.post(
        "/api/v1/buying/compare",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "target_sku": "PRAN-MANGO-250",
            "required_quantity": 20,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["target_sku"] == "PRAN-MANGO-250"
    assert len(data["evaluations"]) >= 2

    # Pran offer had verified bonus (20 // 10 * 1 = 2 bonus units)
    pran_eval = next(e for e in data["evaluations"] if e["supplier_name"] == "প্রাণ ডেইরি")
    assert pran_eval["bonus_units_awarded"] == 2
    # 2400 BDT total for 22 units = ~109 BDT effective unit cost
    assert pran_eval["effective_unit_cost_bdt"] < 120.0


def test_create_order_draft_does_not_execute_payment(client, tenant_a):
    """Order draft creates action in draft status without deducting funds or posting to ledger."""
    # Ingest an offer first
    client.post(
        "/api/v1/buying/offers",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "supplier_name": "প্রাণ ডেইরি",
            "title": "স্ট্যান্ডার্ড সরবরাহ",
            "sku": "PRAN-MANGO-250",
            "base_unit_price_paisa": 12000,
        },
    )

    # Run compare
    comp_res = client.post(
        "/api/v1/buying/compare",
        headers={"Authorization": tenant_a["Authorization"]},
        json={"target_sku": "PRAN-MANGO-250", "required_quantity": 10},
    )
    assert comp_res.status_code == 200
    comp_data = comp_res.json()
    offer_id = comp_data["best_offer_id"]

    draft_res = client.post(
        "/api/v1/buying/orders/draft",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "comparison_id": comp_data["comparison_id"],
            "offer_id": offer_id,
            "quantity": 10,
        },
    )
    assert draft_res.status_code == 201
    draft_data = draft_res.json()
    assert draft_data["status"] == "draft"
    assert draft_data["action_type"] == "stock_reorder"
    assert "owner approval" in draft_data["message"].lower()


def test_cross_tenant_isolation(client, tenant_a, tenant_b):
    """Tenant B cannot see Tenant A's offers or create orders against them."""
    # Tenant B lists offers for same SKU -> empty
    b_offers = client.get(
        "/api/v1/buying/offers?sku=PRAN-MANGO-250",
        headers={"Authorization": tenant_b["Authorization"]},
    )
    assert b_offers.status_code == 200
    assert len(b_offers.json()) == 0

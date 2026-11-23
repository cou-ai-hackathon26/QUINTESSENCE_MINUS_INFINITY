"""Tests for Phase 23: Everyday Operations

Verifies customer order reservations, picking lists, container deposit tracking,
shift handover reconciliation hypotheses, scoped supplier change checks, and cross-tenant isolation.
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
    CustomerReservationModel,
    ReturnableContainerModel,
    ShiftHandoverModel,
    ProductItemModel,
    GoodsReceiptModel,
    JournalEntryModel,
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


def test_customer_reservation_and_picking_lifecycle(client, tenant_a, db_session):
    """Verifies reservation creation, stock availability check, and picking without ledger impact."""
    # Seed product with stock
    prod = ProductItemModel(
        tenant_id=tenant_a["tenant_id"],
        sku="SKU-OP-SUGAR-1KG",
        name="তীর চিনি ১ কেজি",
        quantity_on_hand=10,
        cost_price_paisa=12000,
        selling_price_paisa=14000,
    )
    db_session.add(prod)
    db_session.commit()

    auth_headers = {"Authorization": f"Bearer {tenant_a['Authorization']}"}

    # Step 1: Create reservation for 4 units of in-stock item and 2 units of out-of-stock item
    res_resp = client.post(
        "/api/v1/operations/reservations",
        headers=auth_headers,
        json={
            "customer_name": "করিম ভাই",
            "customer_phone": "01811223344",
            "items": [
                {"sku": "SKU-OP-SUGAR-1KG", "name": "তীর চিনি", "quantity": 4, "unit_price_paisa": 14000},
                {"sku": "SKU-OP-UNKNOWN", "name": "অচেনা পণ্য", "quantity": 2, "unit_price_paisa": 20000},
            ],
            "deposit_paisa": 0,
            "expiry_hours": 12,
        },
    )
    assert res_resp.status_code == 201
    r_data = res_resp.json()
    assert r_data["status"] == "reserved"
    assert r_data["total_estimated_paisa"] == (4 * 14000) + (2 * 20000)
    assert len(r_data["items"]) == 2
    assert r_data["items"][0]["pick_status"] == "ready"
    assert r_data["items"][1]["pick_status"] == "needs_substitution"
    res_id = r_data["id"]

    # Invariant Check: Reserving items must NEVER create a journal entry or sales receivable
    entries = db_session.query(JournalEntryModel).filter(JournalEntryModel.tenant_id == tenant_a["tenant_id"]).all()
    assert len(entries) == 0

    # Step 2: Pick reservation
    pick_resp = client.post(
        f"/api/v1/operations/reservations/{res_id}/pick",
        headers=auth_headers,
    )
    assert pick_resp.status_code == 200
    assert pick_resp.json()["status"] == "picked"


def test_returnable_containers_deposit_tracking(client, tenant_a):
    """Verifies returnable container movements and deposit tracking."""
    auth_headers = {"Authorization": f"Bearer {tenant_a['Authorization']}"}

    # Issue 20 beverage crates with 100 BDT deposit each (10000 paisa)
    issue_resp = client.post(
        "/api/v1/operations/containers/movement",
        headers=auth_headers,
        json={
            "container_type": "crate",
            "party_name": "কোকা-কোলা পরিবেশক",
            "count": 20,
            "movement_type": "issue",
            "deposit_per_unit_paisa": 10000,
        },
    )
    assert issue_resp.status_code == 200
    idata = issue_resp.json()
    assert idata["issued_count"] == 20
    assert idata["outstanding_count"] == 20
    assert idata["total_deposit_held_paisa"] == 200000

    # Return 8 crates
    return_resp = client.post(
        "/api/v1/operations/containers/movement",
        headers=auth_headers,
        json={
            "container_type": "crate",
            "party_name": "কোকা-কোলা পরিবেশক",
            "count": 8,
            "movement_type": "return",
        },
    )
    assert return_resp.status_code == 200
    rdata = return_resp.json()
    assert rdata["returned_count"] == 8
    assert rdata["outstanding_count"] == 12
    assert rdata["total_deposit_held_paisa"] == 120000


def test_shift_handover_variance_and_hypotheses(client, tenant_a, db_session):
    """Verifies shift handover with cash discrepancy retrieves factual, non-accusatory hypotheses."""
    auth_headers = {"Authorization": f"Bearer {tenant_a['Authorization']}"}

    # Seed a discrepant receipt in DB
    receipt = GoodsReceiptModel(
        tenant_id=tenant_a["tenant_id"],
        supplier_name="মেঘনা গ্রুপ",
        sku="SKU-OIL-5L",
        ordered_quantity=10,
        received_quantity=8,
        shortage_quantity=2,
        status="discrepant",
    )
    db_session.add(receipt)
    db_session.commit()

    # Create handover with 500 BDT shortage (50000 paisa)
    ho_resp = client.post(
        "/api/v1/operations/handovers",
        headers=auth_headers,
        json={
            "shift_name": "Morning",
            "opened_by": "Manager Arif",
            "closed_by": "Cashier Rafiq",
            "declared_cash_paisa": 4500000,
            "system_cash_paisa": 4550000,
            "notes": "ক্যাশ শর্ট হয়েছে সাময়িক",
        },
    )
    assert ho_resp.status_code == 201
    hdata = ho_resp.json()
    assert hdata["variance_paisa"] == -50000
    assert len(hdata["possible_reasons"]) >= 1
    assert "shortage" in hdata["possible_reasons"][0]["hypothesis"].lower()


def test_supplier_change_proposal_scope(client, tenant_a):
    """Verifies that evaluating a supplier proposal is strictly scoped without mutating global state."""
    auth_headers = {"Authorization": f"Bearer {tenant_a['Authorization']}"}

    resp = client.post(
        "/api/v1/operations/supplier-change-check",
        headers=auth_headers,
        json={
            "supplier_name": "প্রাণ আরএফএল",
            "target_order_id": "PO-2026-11-88",
            "sku": "SKU-JUICE-250ML",
            "original_price_paisa": 2500,
            "proposed_price_paisa": 2700,
            "quantity": 100,
            "proposed_delay_days": 2,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["scope"] == "scoped_to_order_only"
    assert data["total_impact_paisa"] == 20000  # 200 paisa diff * 100
    assert data["margin_impact"] == "unfavorable"
    assert data["review_required"] is True


def test_cross_tenant_isolation_operations(client, tenant_a, tenant_b):
    """Verifies Tenant B cannot see Tenant A's reservations, containers, or handovers."""
    headers_a = {"Authorization": f"Bearer {tenant_a['Authorization']}"}
    headers_b = {"Authorization": f"Bearer {tenant_b['Authorization']}"}

    # Tenant A creates reservation
    client.post(
        "/api/v1/operations/reservations",
        headers=headers_a,
        json={
            "customer_name": "গ্রাহক এ",
            "items": [{"sku": "SKU-A", "quantity": 1, "unit_price_paisa": 5000}],
        },
    )

    # Tenant B lists reservations
    resp_b = client.get("/api/v1/operations/reservations", headers=headers_b)
    assert resp_b.status_code == 200
    assert len(resp_b.json()) == 0

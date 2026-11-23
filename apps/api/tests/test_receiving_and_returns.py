"""
Phase 20 Test Suite: Receiving, Returns, and Credit Recovery.
Validates:
1. Usable stock inventory update strictly reflecting (received - damaged).
2. Shortage and damage automatic discrepancy detection and credit note generation.
3. Strictly exactly-once credit application (duplicate application rejected).
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
    CreditNoteModel,
    GoodsReceiptModel,
    ProductItemModel,
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


def test_record_receipt_with_shortage_and_damage(client, tenant_a):
    """Usable stock is (received - damaged); shortage and damage create a credit note."""
    assert client.post('/api/v1/merchant/products',headers={'Authorization':tenant_a['Authorization']},json={'name':'Synthetic juice','sku':'PRAN-MANGO-JUICE-250','selling_price_paisa':15000,'quantity_on_hand':0}).status_code==200
    res = client.post(
        "/api/v1/receiving/receipts",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "supplier_name": "প্রাণ আরএফএল",
            "sku": "PRAN-MANGO-JUICE-250",
            "ordered_quantity": 20,
            "received_quantity": 18,
            "damaged_quantity": 1,
            "unit_price_paisa": 12000,
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "discrepant"
    assert data["usable_quantity_added"] == 17  # 18 received - 1 damaged
    assert data["shortage"] == 2
    assert data["damaged"] == 1
    assert data["credit_note_id"] is not None
    # 3 discrepant units * 120 BDT = 360 BDT
    assert data["claim_amount_bdt"] == 360.0


def test_exactly_once_credit_application(client, tenant_a):
    """Credit notes can be applied to an invoice exactly once; second attempt is rejected."""
    assert client.post('/api/v1/merchant/products',headers={'Authorization':tenant_a['Authorization']},json={'name':'Synthetic water','sku':'MEGHNA-WATER-500','selling_price_paisa':2500,'quantity_on_hand':0}).status_code==200
    # 1. Create a receipt with discrepancy
    rcpt_res = client.post(
        "/api/v1/receiving/receipts",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "supplier_name": "মেঘনা বেভারেজ",
            "sku": "MEGHNA-WATER-500",
            "ordered_quantity": 10,
            "received_quantity": 8,
            "unit_price_paisa": 2000,
        },
    )
    credit_note_id = rcpt_res.json()["credit_note_id"]
    assert credit_note_id is not None

    # A suspected claim must first be accepted by the supplier.
    pending=client.post(f"/api/v1/receiving/credits/{credit_note_id}/apply",headers={"Authorization":tenant_a["Authorization"]},json={"invoice_ref":"INV-2026-041"})
    assert pending.status_code == 400
    generator=app.dependency_overrides[get_db]()
    db=next(generator)
    try:
        note=db.query(CreditNoteModel).filter_by(id=credit_note_id).one()
        note.status='accepted_by_supplier'  # Explicit synthetic acceptance fixture, not inferred by the API.
        db.commit()
    finally:
        generator.close()

    # 2. First accepted application -> Success
    apply_res_1 = client.post(
        f"/api/v1/receiving/credits/{credit_note_id}/apply",
        headers={"Authorization": tenant_a["Authorization"]},
        json={"invoice_ref": "INV-2026-041"},
    )
    assert apply_res_1.status_code == 200
    assert apply_res_1.json()["status"] == "applied_to_bill"
    assert apply_res_1.json()["applied_invoice_ref"] == "INV-2026-041"

    # 3. Duplicate application attempt -> Rejected (400 Bad Request)
    apply_res_2 = client.post(
        f"/api/v1/receiving/credits/{credit_note_id}/apply",
        headers={"Authorization": tenant_a["Authorization"]},
        json={"invoice_ref": "INV-2026-042"},
    )
    assert apply_res_2.status_code == 400
    assert "already been applied" in apply_res_2.json()["detail"].lower()


def test_cross_tenant_isolation(client, tenant_a, tenant_b):
    """Tenant B cannot access or apply Tenant A's credit notes."""
    assert client.post('/api/v1/merchant/products',headers={'Authorization':tenant_a['Authorization']},json={'name':'Synthetic chips','sku':'PRAN-CHIPS','selling_price_paisa':1500,'quantity_on_hand':0}).status_code==200
    rcpt_res = client.post(
        "/api/v1/receiving/receipts",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "supplier_name": "প্রাণ আরএফএল",
            "sku": "PRAN-CHIPS",
            "ordered_quantity": 10,
            "received_quantity": 5,
            "unit_price_paisa": 1000,
        },
    )
    credit_note_id = rcpt_res.json()["credit_note_id"]

    # Tenant B tries to apply Tenant A's credit note -> 400 (not found/unauthorized)
    b_apply = client.post(
        f"/api/v1/receiving/credits/{credit_note_id}/apply",
        headers={"Authorization": tenant_b["Authorization"]},
        json={"invoice_ref": "INV-STEAL"},
    )
    assert b_apply.status_code == 400
    assert "not found" in b_apply.json()["detail"].lower()

"""
Phase 08 Tests: Action Center, Scoped Customer Invoice Portal, and SSLCOMMERZ Connector.
Tests approval workflows, role permissions, scoped portal access, dispute intake,
tampered callback rejection, duplicate callback rejection, and ledger reflection.
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
    res = client.post("/api/v1/auth/login", json={"phone": "01733334444", "otp": "123456", "role": "owner"})
    data = res.json()
    return {"Authorization": f"Bearer {data['access_token']}", "tenant_id": data["tenant_id"]}


@pytest.fixture
def cashier_headers(client, auth_headers):
    res = client.post(
        "/api/v1/auth/login",
        json={"phone": "01733334445", "otp": "123456", "role": "cashier", "tenant_id": auth_headers["tenant_id"]},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_action_draft_approval_and_execution_workflow(client, auth_headers, cashier_headers):
    headers = {"Authorization": auth_headers["Authorization"]}
    # 1. Create a supplier payment action
    res = client.post(
        "/api/v1/actions",
        headers=headers,
        json={
            "action_type": "supplier_payment",
            "recipient": "M/S Haque Traders",
            "amount_paisa": 2500000,
            "idempotency_key": "ACT-TEST-001",
        },
    )
    assert res.status_code == 200
    action_id = res.json()["action_id"]

    # 2. Cashier in same tenant attempting to approve financial payment is forbidden (403)
    cashier_app = client.post(f"/api/v1/actions/{action_id}/approve", headers=cashier_headers)
    assert cashier_app.status_code == 403

    # 3. Owner approves action
    owner_app = client.post(f"/api/v1/actions/{action_id}/approve", headers=headers)
    assert owner_app.status_code == 200
    assert owner_app.json()["status"] == "approved"

    # 4. Execute action
    exec_res = client.post(f"/api/v1/actions/{action_id}/execute", headers=headers)
    assert exec_res.status_code == 200
    assert exec_res.json()["status"] == "completed"


def test_action_cancellation_and_idempotency(client, auth_headers):
    # 1. Create action
    res = client.post(
        "/api/v1/actions",
        headers=auth_headers,
        json={
            "action_type": "customer_reminder",
            "recipient": "Kamal Hossain",
            "idempotency_key": "REMINDER-001",
        },
    )
    assert res.status_code == 200
    action_id = res.json()["action_id"]

    # 2. Duplicate submission returns existing action
    dup_res = client.post(
        "/api/v1/actions",
        headers=auth_headers,
        json={
            "action_type": "customer_reminder",
            "recipient": "Kamal Hossain",
            "idempotency_key": "REMINDER-001",
        },
    )
    assert dup_res.status_code == 200
    assert dup_res.json()["status"] == "existing"

    # 3. Cancel action
    cancel_res = client.post(f"/api/v1/actions/{action_id}/cancel", headers=auth_headers)
    assert cancel_res.status_code == 200

    # 4. Cannot execute cancelled action
    bad_exec = client.post(f"/api/v1/actions/{action_id}/execute", headers=auth_headers)
    assert bad_exec.status_code == 400


def test_scoped_customer_portal_and_dispute(client, auth_headers):
    # 1. Create customer party
    party_res = client.post(
        "/api/v1/merchant/parties",
        headers=auth_headers,
        json={"name": "তানভীর আহমেদ", "phone": "01722334455", "initial_due_paisa": 50000},
    )
    party_id = party_res.json()["id"]

    # 2. Generate scoped invoice link
    link_res = client.post(
        "/api/v1/portal/generate-link",
        headers=auth_headers,
        json={
            "party_id": party_id,
            "invoice_number": "INV-2026-088",
            "amount_paisa": 50000,
            "description": "মুদি সামগ্রী বাকির চালান",
        },
    )
    assert link_res.status_code == 200
    token = link_res.json()["token"]

    # 3. Customer accesses portal without authentication credentials
    portal_res = client.get(f"/api/v1/portal/{token}")
    assert portal_res.status_code == 200
    data = portal_res.json()
    assert data["customer_name"] == "তানভীর আহমেদ"
    assert data["amount_paisa"] == 50000
    assert data["currency"] == "BDT"
    assert data["is_paid"] is False

    # 4. Customer submits dispute note
    disp_res = client.post(
        f"/api/v1/portal/{token}/dispute",
        json={"dispute_note": "চালানে একটি ৫ লিটার তেলের ক্যান অতিরিক্ত যুক্ত করা হয়েছে।"},
    )
    assert disp_res.status_code == 200

    # 5. Verified note is stored
    updated_portal = client.get(f"/api/v1/portal/{token}").json()
    assert "৫ লিটার তেল" in updated_portal["dispute_note"]


def test_sslcommerz_initiate_and_tampered_amount_rejection(client, auth_headers):
    # Create customer and portal link for 40,000 paisa (BDT 400)
    party = client.post(
        "/api/v1/merchant/parties",
        headers=auth_headers,
        json={"name": "সজিব রায়", "initial_due_paisa": 40000},
    ).json()

    portal = client.post(
        "/api/v1/portal/generate-link",
        headers=auth_headers,
        json={"party_id": party["id"], "invoice_number": "INV-TAMPER-01", "amount_paisa": 40000},
    ).json()
    token = portal["token"]

    # Initiate payment session
    init_res = client.post(f"/api/v1/portal/{token}/pay")
    assert init_res.status_code == 200
    tran_id = init_res.json()["tran_id"]

    # Attack attempt: Tampered amount callback (trying to pay BDT 10 instead of BDT 400)
    bad_cb = client.post(
        "/api/v1/payments/sslcommerz/ipn",
        json={
            "token": token,
            "tran_id": tran_id,
            "status": "VALID",
            "amount": "10.00",
            "currency": "BDT",
        },
    )
    assert bad_cb.status_code == 400
    assert "Tampered amount detected" in bad_cb.json()["detail"]

    # Attack attempt: Tampered currency callback (USD instead of BDT)
    bad_curr = client.post(
        "/api/v1/payments/sslcommerz/ipn",
        json={
            "token": token,
            "tran_id": tran_id,
            "status": "VALID",
            "amount": "400.00",
            "currency": "USD",
        },
    )
    assert bad_curr.status_code == 400
    assert "Currency mismatch" in bad_curr.json()["detail"]


def test_sslcommerz_valid_payment_posts_to_ledger_and_reduces_due(client, auth_headers):
    # Customer owing 75,000 paisa (BDT 750)
    party = client.post(
        "/api/v1/merchant/parties",
        headers=auth_headers,
        json={"name": "হাবিবুর রহমান", "initial_due_paisa": 75000},
    ).json()

    portal = client.post(
        "/api/v1/portal/generate-link",
        headers=auth_headers,
        json={"party_id": party["id"], "invoice_number": "INV-SETTLE-01", "amount_paisa": 75000},
    ).json()
    token = portal["token"]

    init_res = client.post(f"/api/v1/portal/{token}/pay")
    tran_id = init_res.json()["tran_id"]

    # 1. Valid callback
    valid_res = client.post(
        "/api/v1/payments/sslcommerz/ipn",
        json={
            "token": token,
            "tran_id": tran_id,
            "val_id": f"VAL-{tran_id}",
            "status": "VALID",
            "amount": "750.00",
            "currency": "BDT",
            "card_type": "BKASH-BKash",
        },
    )
    assert valid_res.status_code == 200
    assert valid_res.json()["status"] == "verified_and_posted"

    # 2. Portal is now marked paid
    portal_data = client.get(f"/api/v1/portal/{token}").json()
    assert portal_data["is_paid"] is True

    # 3. Customer party due balance is decreased to 0
    parties = client.get("/api/v1/merchant/parties", headers=auth_headers).json()
    updated_party = next(p for p in parties if p["id"] == party["id"])
    assert updated_party["current_due_paisa"] == 0

    # 4. Duplicate callback does not double post
    dup_cb = client.post(
        "/api/v1/payments/sslcommerz/ipn",
        json={
            "token": token,
            "tran_id": tran_id,
            "status": "VALID",
            "amount": "750.00",
            "currency": "BDT",
        },
    )
    assert dup_cb.status_code == 200
    assert dup_cb.json()["status"] in ["duplicate", "already_processed"]

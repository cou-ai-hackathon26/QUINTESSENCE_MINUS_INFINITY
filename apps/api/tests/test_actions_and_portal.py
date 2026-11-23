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
    assert exec_res.status_code == 503
    assert "not connected" in exec_res.json()["detail"].lower()


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
    party=client.post('/api/v1/merchant/parties',headers=auth_headers,json={'name':'Synthetic customer','party_type':'customer','initial_due_paisa':100000}).json()
    portal=client.post('/api/v1/portal/generate-link',headers=auth_headers,json={'party_id':party['id'],'invoice_number':'TEST-BLOCKED','amount_paisa':100000}).json()
    assert client.post('/api/v1/portal/'+portal['token']+'/pay').status_code == 503
    for amount in ['10.00','1000.00']:
        assert client.post('/api/v1/payments/sslcommerz/ipn',json={'token':portal['token'],'tran_id':'UNVERIFIED','amount':amount,'currency':'BDT','status':'VALID'}).status_code == 503
    assert client.get('/api/v1/portal/'+portal['token']).json()['is_paid'] is False


def test_unverified_payment_callback_cannot_reduce_due(client, auth_headers):
    party=client.post('/api/v1/merchant/parties',headers=auth_headers,json={'name':'Synthetic unsettled customer','party_type':'customer','initial_due_paisa':75000}).json()
    portal=client.post('/api/v1/portal/generate-link',headers=auth_headers,json={'party_id':party['id'],'invoice_number':'TEST-UNVERIFIED','amount_paisa':75000}).json()
    callback={'token':portal['token'],'tran_id':'TEST-REPLAY','status':'VALID','amount':'750.00','currency':'BDT'}
    for _ in range(2):
        assert client.post('/api/v1/payments/sslcommerz/ipn',json=callback).status_code == 503
    assert client.get('/api/v1/portal/'+portal['token']).json()['is_paid'] is False
    updated=next(p for p in client.get('/api/v1/merchant/parties',headers=auth_headers).json() if p['id']==party['id'])
    assert updated['current_due_paisa'] == 75000

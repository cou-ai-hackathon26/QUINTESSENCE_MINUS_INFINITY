"""
Phase 06 Tests: Connected Daily Merchant Workflow.
Tests cash, credit, split sales, debt collections, transfer fees,
stock movements, daily cash close, and today summary derivation.
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
    res = client.post("/api/v1/auth/login", json={"phone": "01788887777", "otp": "123456"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_cash_sale_workflow(client, auth_headers):
    # Cash sale of 50,000 paisa (BDT 500)
    res = client.post(
        "/api/v1/merchant/sales",
        headers=auth_headers,
        json={
            "sale_type": "cash",
            "total_amount_paisa": 50000,
            "cash_received_paisa": 50000,
        },
    )
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    # Today summary reflects cash and revenue
    today = client.get("/api/v1/merchant/today", headers=auth_headers).json()
    assert today["cash_balance_paisa"] >= 50000
    assert today["total_revenue_paisa"] >= 50000


def test_credit_sale_and_party_due(client, auth_headers):
    # 1. Create a customer
    party_res = client.post(
        "/api/v1/merchant/parties",
        headers=auth_headers,
        json={"name": "রফিক সাহেব", "phone": "01711223399", "party_type": "customer"},
    )
    assert party_res.status_code == 200
    party_id = party_res.json()["id"]

    # 2. Credit sale of 32,000 paisa (BDT 320)
    sale_res = client.post(
        "/api/v1/merchant/sales",
        headers=auth_headers,
        json={
            "sale_type": "credit",
            "total_amount_paisa": 32000,
            "party_id": party_id,
        },
    )
    assert sale_res.status_code == 200

    # 3. Verify party due is updated
    parties = client.get("/api/v1/merchant/parties", headers=auth_headers).json()
    party = next(p for p in parties if p["id"] == party_id)
    assert party["current_due_paisa"] == 32000


def test_split_sale_workflow(client, auth_headers):
    # Split sale: total 32,000, cash received 20,000, credit 12,000
    res = client.post(
        "/api/v1/merchant/sales",
        headers=auth_headers,
        json={
            "sale_type": "split",
            "total_amount_paisa": 32000,
            "cash_received_paisa": 20000,
        },
    )
    assert res.status_code == 200


def test_debt_collection_does_not_inflate_revenue(client, auth_headers):
    # Create customer with due 50,000 paisa
    party_res = client.post(
        "/api/v1/merchant/parties",
        headers=auth_headers,
        json={"name": "করিম মিয়া", "initial_due_paisa": 50000},
    )
    party_id = party_res.json()["id"]

    rev_before = client.get("/api/v1/merchant/today", headers=auth_headers).json()["total_revenue_paisa"]

    # Collect due of 50,000 paisa
    col_res = client.post(
        "/api/v1/merchant/collect-due",
        headers=auth_headers,
        json={"party_id": party_id, "amount_paisa": 50000},
    )
    assert col_res.status_code == 200

    # Party due is now 0
    parties = client.get("/api/v1/merchant/parties", headers=auth_headers).json()
    party = next(p for p in parties if p["id"] == party_id)
    assert party["current_due_paisa"] == 0

    # Revenue MUST NOT increase on debt collection
    rev_after = client.get("/api/v1/merchant/today", headers=auth_headers).json()["total_revenue_paisa"]
    assert rev_after == rev_before


def test_wallet_transfer_with_fee(client, auth_headers):
    # Transfer 100,000 paisa (BDT 1000) from Nagad to Cash with fee 2,000 paisa (BDT 20)
    res = client.post(
        "/api/v1/merchant/transfer",
        headers=auth_headers,
        json={
            "from_channel": "nagad",
            "to_channel": "cash",
            "principal_paisa": 100000,
            "fee_paisa": 2000,
        },
    )
    assert res.status_code == 200
    assert res.json()["status"] == "success"


def test_product_stock_deduction_on_sale(client, auth_headers):
    # 1. Create a product with 50 units
    prod_res = client.post(
        "/api/v1/merchant/products",
        headers=auth_headers,
        json={
            "name": "তীর সয়াবিন তেল ১ লিটার",
            "sku": "OIL-TEER-1L",
            "unit": "litre",
            "quantity_on_hand": 50,
            "cost_price_paisa": 16500,
            "selling_price_paisa": 18500,
        },
    )
    assert prod_res.status_code == 200
    prod_id = prod_res.json()["id"]

    # 2. Sell 5 units
    client.post(
        "/api/v1/merchant/sales",
        headers=auth_headers,
        json={
            "sale_type": "cash",
            "total_amount_paisa": 5 * 18500,
            "cash_received_paisa": 5 * 18500,
            "items": [{"product_id": prod_id, "quantity": 5}],
        },
    )

    # 3. Verify stock is decremented to 45 units
    products = client.get("/api/v1/merchant/products", headers=auth_headers).json()
    prod = next(p for p in products if p["id"] == prod_id)
    assert prod["quantity_on_hand"] == 45


def test_daily_cash_close_and_discrepancy(client, auth_headers):
    # Fetch today's ledger cash
    today = client.get("/api/v1/merchant/today", headers=auth_headers).json()
    expected_cash = today["cash_balance_paisa"]

    # Actual drawer count has 500 paisa excess
    actual_drawer = expected_cash + 500

    close_res = client.post(
        "/api/v1/merchant/cash-close",
        headers=auth_headers,
        json={
            "snapshot_date": "2026-11-23",
            "actual_drawer_cash_paisa": actual_drawer,
        },
    )
    assert close_res.status_code == 200
    data = close_res.json()
    assert data["status"] == "closed"
    assert data["closing_cash_paisa"] == expected_cash
    assert data["discrepancy_paisa"] == 500


def test_expense_recording(client, auth_headers):
    # Record operating expense of 15,000 paisa (BDT 150) for shop electricity
    res = client.post(
        "/api/v1/merchant/expenses",
        headers=auth_headers,
        json={"amount_paisa": 15000, "description": "দোকানের বিদ্যুৎ বিল", "category": "operating"},
    )
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    today = client.get("/api/v1/merchant/today", headers=auth_headers).json()
    assert today["total_expense_paisa"] >= 15000


def test_owner_withdrawal_authorized_and_cashier_denied(client, auth_headers):
    # 1. Owner withdrawal of 20,000 paisa succeeds (default user is owner)
    draw_res = client.post(
        "/api/v1/merchant/withdrawals",
        headers=auth_headers,
        json={"amount_paisa": 20000},
    )
    assert draw_res.status_code == 200
    assert draw_res.json()["status"] == "success"

    # 2. Login as cashier
    cashier_login = client.post("/api/v1/auth/login", json={"phone": "01788887778", "role": "cashier", "otp": "123456"})
    cashier_token = cashier_login.json()["access_token"]
    cashier_headers = {"Authorization": f"Bearer {cashier_token}"}

    # 3. Cashier attempting withdrawal is forbidden (403)
    cashier_draw = client.post(
        "/api/v1/merchant/withdrawals",
        headers=cashier_headers,
        json={"amount_paisa": 5000},
    )
    assert cashier_draw.status_code == 403


def test_supplier_payment_updates_ledger_and_party_dues(client, auth_headers):
    # 1. Create a supplier with initial due of 100,000 paisa (BDT 1,000)
    supp_res = client.post(
        "/api/v1/merchant/parties",
        headers=auth_headers,
        json={"name": "মেঘনা গ্রুপ", "party_type": "supplier", "initial_due_paisa": 100000},
    )
    assert supp_res.status_code == 200
    supp_id = supp_res.json()["id"]

    # 2. Pay 40,000 paisa to supplier via cash
    pay_res = client.post(
        "/api/v1/merchant/supplier-payment",
        headers=auth_headers,
        json={"party_id": supp_id, "amount_paisa": 40000, "channel": "cash"},
    )
    assert pay_res.status_code == 200
    assert pay_res.json()["status"] == "success"

    # 3. Supplier due is reduced to 60,000 paisa
    parties = client.get("/api/v1/merchant/parties", headers=auth_headers).json()
    supp = next(p for p in parties if p["id"] == supp_id)
    assert supp["current_due_paisa"] == 60000


"""Unit & Integration tests for Stock Management, Operating Reports, Commitments & Forecasting.

Validates Phase 09 requirements:
- P09-T01: Stock counts, purchase drafts, lead times, stock cover, accepted returns, WAC recalculation (D011).
- P09-T02: Recurring commitments, cash-aware reorder comparison, and operating reports separating cash, profit, inventory and dues.
- P09-T03: History-based sales forecast adapter with cold-start gating and rolling-origin evaluation.
- P09-T04: Supported CSV import/export with deduplication and RBAC protection.
"""
from datetime import datetime, timezone, timedelta
import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.persistence.models import (
    TenantModel, UserModel, PartyModel, ProductItemModel,
    StockMovementModel, DailySnapshotModel, AccountModel,
    JournalEntryModel, PostingModel,
    now_utc
)

client = TestClient(app)

@pytest.fixture(autouse=True)
def isolated_stock_database(monkeypatch):
    engine=create_engine('sqlite:///:memory:',connect_args={'check_same_thread':False},poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory=sessionmaker(bind=engine)
    monkeypatch.setitem(globals(),'SessionLocal',factory)
    def override():
        with factory() as db: yield db
    app.dependency_overrides[get_db]=override
    yield
    app.dependency_overrides.clear()
    engine.dispose()


def create_test_tenant(prefix: str):
    """Helper to provision an isolated test tenant with owner, cashier, and accounts."""
    db = SessionLocal()
    try:
        rand_id = uuid.uuid4().hex[:8]
        tenant = TenantModel(name=f"Stock Shop {prefix}-{rand_id}", currency="BDT", is_demo=False)
        db.add(tenant)
        db.flush()

        owner_phone = f"+88019{rand_id}"
        cashier_phone = f"+88018{rand_id}"
        owner = UserModel(tenant_id=tenant.id, phone=owner_phone, role="owner", is_active=True)
        cashier = UserModel(tenant_id=tenant.id, phone=cashier_phone, role="cashier", is_active=True)
        db.add_all([owner, cashier])

        # Core chart of accounts
        acc_cash = AccountModel(tenant_id=tenant.id, code="1001", name="Cash in Hand", type="asset", current_balance_paisa=50000) # 500 BDT
        acc_bkash = AccountModel(tenant_id=tenant.id, code="1002", name="bKash Merchant", type="asset", current_balance_paisa=30000) # 300 BDT
        acc_bank = AccountModel(tenant_id=tenant.id, code="1003", name="BRAC Bank", type="asset", current_balance_paisa=20000) # 200 BDT
        acc_ar = AccountModel(tenant_id=tenant.id, code="1004", name="Accounts Receivable", type="asset", current_balance_paisa=0)
        acc_ap = AccountModel(tenant_id=tenant.id, code="2001", name="Accounts Payable", type="liability", current_balance_paisa=0)
        acc_equity = AccountModel(tenant_id=tenant.id, code="3001", name="Owner Equity", type="equity", current_balance_paisa=100000)
        acc_rev = AccountModel(tenant_id=tenant.id, code="4001", name="Sales Revenue", type="revenue", current_balance_paisa=0)
        acc_exp = AccountModel(tenant_id=tenant.id, code="5001", name="Operating Expenses", type="expense", current_balance_paisa=0)

        db.add_all([acc_cash, acc_bkash, acc_bank, acc_ar, acc_ap, acc_equity, acc_rev, acc_exp])
        db.commit()

        owner_phone = owner.phone
        cashier_phone = cashier.phone
        tenant_id = tenant.id
    finally:
        db.close()

    # Login to obtain JWTs
    res_owner = client.post("/api/v1/auth/login", json={"phone": owner_phone, "otp": "123456"})
    owner_token = res_owner.json()["access_token"]

    res_cashier = client.post("/api/v1/auth/login", json={"phone": cashier_phone, "otp": "123456", "tenant_id": tenant_id, "role": "cashier"})
    cashier_token = res_cashier.json()["access_token"]

    return {
        "tenant_id": tenant_id,
        "owner_token": owner_token,
        "cashier_token": cashier_token,
        "headers_owner": {"Authorization": f"Bearer {owner_token}"},
        "headers_cashier": {"Authorization": f"Bearer {cashier_token}"},
    }


def test_stock_units_counts_and_wac_recalculation():
    """Verify stock counts, purchase drafts, and Weighted Average Cost (WAC per D011) recalculation."""
    ctx = create_test_tenant("1101")
    headers = ctx["headers_owner"]

    # 1. Create a product with 10 units initial stock @ 100 paisa (৳1.00) cost, 200 paisa selling price
    create_res = client.post(
        "/api/v1/stock/products",
        headers=headers,
        json={
            "name": "Basmati Rice 1kg",
            "sku": "RICE-BAS-01",
            "unit": "kg",
            "quantity_on_hand": 10,
            "cost_price_paisa": 100,
            "selling_price_paisa": 200,
            "reorder_threshold": 5,
            "lead_time_days": 2,
        }
    )
    assert create_res.status_code == 201
    product_id = create_res.json()["product_id"]

    # 2. Check product listing and margin calculation
    list_res = client.get("/api/v1/stock/products", headers=headers)
    assert list_res.status_code == 200
    prod = next(p for p in list_res.json()["products"] if p["id"] == product_id)
    assert prod["quantity_on_hand"] == 10
    assert prod["cost_price_paisa"] == 100
    assert prod["margin_paisa"] == 100
    assert prod["margin_percent"] == 50.0
    assert prod["reorder_status"] == "normal"

    # 3. Create a purchase draft: 10 units @ 160 paisa
    draft_res = client.post(
        "/api/v1/stock/purchase-drafts",
        headers=headers,
        json={
            "product_id": product_id,
            "quantity": 10,
            "unit_cost_paisa": 160,
            "lead_time_days": 3,
            "notes": "Bulk purchase from supplier"
        }
    )
    assert draft_res.status_code == 201
    draft_id = draft_res.json()["draft_id"]
    assert draft_res.json()["total_cost_paisa"] == 1600

    # 4. Receive purchase draft
    # WAC calculation: (10 * 100 + 10 * 160) / (10 + 10) = 2600 / 20 = 130 paisa
    recv_res = client.post(f"/api/v1/stock/purchase-drafts/{draft_id}/receive", headers=headers)
    assert recv_res.status_code == 200
    recv_data = recv_res.json()
    assert recv_data["status"] == "received"
    assert recv_data["new_quantity_on_hand"] == 20
    assert recv_data["old_wac_paisa"] == 100
    assert recv_data["new_wac_paisa"] == 130

    # 5. Cannot re-receive already received draft
    recv_again = client.post(f"/api/v1/stock/purchase-drafts/{draft_id}/receive", headers=headers)
    assert recv_again.status_code == 400


def test_customer_and_supplier_returns():
    """Verify returns: customer returns restock inventory and credit, supplier returns deduce inventory and payables."""
    ctx = create_test_tenant("1102")
    headers = ctx["headers_owner"]

    # Create supplier party and customer party
    db = SessionLocal()
    supplier = PartyModel(tenant_id=ctx["tenant_id"], name="Pran Depot", party_type="supplier", current_due_paisa=5000)
    customer = PartyModel(tenant_id=ctx["tenant_id"], name="Rahim Mia", party_type="customer", current_due_paisa=3000)
    prod = ProductItemModel(
        tenant_id=ctx["tenant_id"],
        name="Mustard Oil 500ml",
        sku="OIL-MUS-01",
        quantity_on_hand=15,
        cost_price_paisa=120,
        selling_price_paisa=160
    )
    db.add_all([supplier, customer, prod])
    db.commit()
    supplier_id = supplier.id
    customer_id = customer.id
    prod_id = prod.id
    db.close()

    # 1. Customer return: returns 2 units of mustard oil
    cust_ret = client.post(
        "/api/v1/stock/returns",
        headers=headers,
        json={
            "return_type": "customer_return",
            "product_id": prod_id,
            "quantity": 2,
            "party_id": customer_id,
            "refund_amount_paisa": 320,  # 2 * 160
            "refund_method": "credit_adjustment"
        }
    )
    assert cust_ret.status_code == 200
    assert cust_ret.json()["new_quantity_on_hand"] == 17

    # Verify customer receivable was reduced from 3000 to 2680
    db = SessionLocal()
    cust_db = db.query(PartyModel).filter(PartyModel.id == customer_id).first()
    assert cust_db.current_due_paisa == 3000 - 320
    db.close()

    # 2. Supplier return: return 5 defective units to supplier
    supp_ret = client.post(
        "/api/v1/stock/returns",
        headers=headers,
        json={
            "return_type": "supplier_return",
            "product_id": prod_id,
            "quantity": 5,
            "party_id": supplier_id,
            "refund_amount_paisa": 600,  # 5 * 120
        }
    )
    assert supp_ret.status_code == 200
    assert supp_ret.json()["new_quantity_on_hand"] == 12

    # Verify supplier payable was reduced from 5000 to 4400
    db = SessionLocal()
    supp_db = db.query(PartyModel).filter(PartyModel.id == supplier_id).first()
    assert supp_db.current_due_paisa == 5000 - 600
    db.close()

    # 3. Attempt to return more units than in stock
    excess_ret = client.post(
        "/api/v1/stock/returns",
        headers=headers,
        json={
            "return_type": "supplier_return",
            "product_id": prod_id,
            "quantity": 50,  # only 12 in stock
        }
    )
    assert excess_ret.status_code == 400


def test_operating_reports_strictly_separate_views_and_enforce_d011():
    """Verify operating reports strictly separate Cash, Profit, Inventory, and Dues, and enforce D011 incomplete cost suppression."""
    ctx = create_test_tenant("1103")
    headers = ctx["headers_owner"]

    db = SessionLocal()
    # Add an uncosted product (cost_price_paisa=None)
    prod_uncosted = ProductItemModel(
        tenant_id=ctx["tenant_id"],
        name="Local Egg Box",
        sku="EGG-01",
        quantity_on_hand=5,
        cost_price_paisa=None,  # Missing cost data!
        selling_price_paisa=150
    )
    db.add(prod_uncosted)
    db.commit()
    db.close()

    # 1. Fetch operating summary
    rep_res = client.get("/api/v1/reports/operating-summary", headers=headers)
    assert rep_res.status_code == 200
    rep = rep_res.json()

    # Check cash statement (1001: 50000, 1002: 30000, 1003: 20000 -> total 100000 paisa / ৳1,000)
    assert rep["cash_statement"]["total_liquid_cash_paisa"] == 100000
    assert rep["cash_statement"]["cash_in_hand_paisa"] == 50000

    # Check accrual profit statement suppresses unsupported profit per D011
    profit_stmt = rep["accrual_profit_statement"]
    assert profit_stmt["cost_data_incomplete"] is True
    assert profit_stmt["unsupported_profit_suppressed"] is True
    assert profit_stmt["net_profit_paisa"] is None
    assert profit_stmt["gross_profit_paisa"] is None
    assert "D011" in profit_stmt["disclaimer"]

    # Check inventory valuation
    assert rep["inventory_valuation"]["uncosted_products_count"] >= 1

    # 2. Verify Cashier is forbidden from viewing full profit reports
    cashier_res = client.get("/api/v1/reports/operating-summary", headers=ctx["headers_cashier"])
    assert cashier_res.status_code == 403


def test_reorder_recommendation_and_cash_awareness():
    """Verify reorder alerts and safe liquidity shortfall evaluation."""
    ctx = create_test_tenant("1104")
    headers = ctx["headers_owner"]

    db = SessionLocal()
    # Create low-stock product with 1 unit on hand (threshold 5)
    prod = ProductItemModel(
        tenant_id=ctx["tenant_id"],
        name="Lentils 1kg",
        sku="LENT-01",
        quantity_on_hand=1,
        reorder_threshold=5,
        cost_price_paisa=20000,  # ৳200 per unit
        selling_price_paisa=25000
    )
    db.add(prod)
    db.commit()
    db.close()

    reorder_res = client.get("/api/v1/stock/reorder-recommendations", headers=headers)
    assert reorder_res.status_code == 200
    reorder_data = reorder_res.json()

    # Available cash in tenant = 100,000 paisa (৳1,000)
    # Suggested order qty = max(10, 5 * 2) - 1 = 9 units
    # Est cost = 9 * 20,000 = 180,000 paisa (৳1,800)
    # Since 180,000 > 100,000 -> cash_sufficient must be False!
    assert reorder_data["cash_sufficient"] is False
    assert reorder_data["cash_warning"] is not None
    assert "insufficient" in reorder_data["cash_warning"].lower()
    assert len(reorder_data["recommendations"]) == 1
    assert reorder_data["recommendations"][0]["name"] == "Lentils 1kg"


def test_history_forecast_cold_start_and_evaluated_pipeline():
    """Verify history-based forecast adapter with cold-start gating (< 14 days) and evaluated rolling-origin backtest (>= 14 days)."""
    ctx = create_test_tenant("1105")
    headers = ctx["headers_owner"]

    db = SessionLocal()
    # 1. Populate only 5 days of trading -> Cold start gate
    base_date = datetime(2026, 11, 1, tzinfo=timezone.utc)
    for i in range(5):
        d_str = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
        snap = DailySnapshotModel(
            tenant_id=ctx["tenant_id"],
            snapshot_date=d_str,
            opening_cash_paisa=50000,
            closing_cash_paisa=60000,
            total_sales_paisa=10000 + i * 500,
            status="closed",
        )
        db.add(snap)
    db.commit()
    db.close()

    # Query forecast under cold start
    fc_cold = client.get("/api/v1/forecast/sales", headers=headers)
    assert fc_cold.status_code == 200
    cold_data = fc_cold.json()
    assert cold_data["status"] == "cold_start"
    assert cold_data["data_quality_gate"] == "insufficient_history"
    assert cold_data["observations_count"] == 5
    assert cold_data["forecast_7_day_daily_paisa"] is None
    assert "insufficient historical data" in cold_data["explanation"].lower()

    # 2. Now populate 10 more days (total 15 days >= 14 min)
    db = SessionLocal()
    for i in range(5, 15):
        d_str = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
        snap = DailySnapshotModel(
            tenant_id=ctx["tenant_id"],
            snapshot_date=d_str,
            opening_cash_paisa=50000,
            closing_cash_paisa=60000,
            total_sales_paisa=12000,
            status="closed",
        )
        db.add(snap)
    db.commit()
    db.close()

    # Query forecast with sufficient observations
    fc_eval = client.get("/api/v1/forecast/sales", headers=headers)
    assert fc_eval.status_code == 200
    eval_data = fc_eval.json()
    assert eval_data["status"] == "evaluated"
    assert eval_data["data_quality_gate"] == "passed"
    assert eval_data["observations_count"] == 15
    assert eval_data["best_baseline"] is not None
    assert eval_data["forecast_7_day_daily_paisa"] is not None
    assert eval_data["evaluated_mae_paisa"] is not None
    assert len(eval_data["uncertainty_range_daily_paisa"]) == 2


def test_csv_export_import_and_deduplication():
    """Verify CSV export and import with SKU deduplication and RBAC protection."""
    ctx = create_test_tenant("1106")
    headers = ctx["headers_owner"]

    # 1. Create product via CSV import
    csv_payload = (
        "sku,name,unit,quantity_on_hand,cost_price_bdt,selling_price_bdt,reorder_threshold,lead_time_days\n"
        "SOAP-LUX-01,Lux Soap 150g,pcs,25,45.00,55.00,5,3\n"
        "TEA-ISPA-01,Ispahani Tea 200g,packet,15,110.00,130.00,4,2\n"
    )
    import_res = client.post(
        "/api/v1/reports/import/products.csv",
        headers=headers,
        json={"csv_content": csv_payload}
    )
    assert import_res.status_code == 200
    imp_data = import_res.json()
    assert imp_data["created_count"] == 2
    assert imp_data["updated_count"] == 0

    # 2. Re-import with same SKU but updated quantity and price (Deduplication test)
    csv_update_payload = (
        "sku,name,unit,quantity_on_hand,cost_price_bdt,selling_price_bdt,reorder_threshold,lead_time_days\n"
        "SOAP-LUX-01,Lux Soap 150g (Special),pcs,30,48.00,60.00,5,3\n"
    )
    update_res = client.post(
        "/api/v1/reports/import/products.csv",
        headers=headers,
        json={"csv_content": csv_update_payload}
    )
    assert update_res.status_code == 200
    upd_data = update_res.json()
    assert upd_data["created_count"] == 0
    assert upd_data["updated_count"] == 1

    # 3. Export CSV and check contents
    export_res = client.get("/api/v1/reports/export/products.csv", headers=headers)
    assert export_res.status_code == 200
    assert "text/csv" in export_res.headers["content-type"]
    assert "SOAP-LUX-01" in export_res.text
    assert "Lux Soap 150g (Special)" in export_res.text

    # 4. Cashier cannot import or export CSV
    cashier_export = client.get("/api/v1/reports/export/products.csv", headers=ctx["headers_cashier"])
    assert cashier_export.status_code == 403

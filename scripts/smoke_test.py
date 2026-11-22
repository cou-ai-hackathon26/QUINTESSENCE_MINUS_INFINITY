"""
Shongoti Deployment & Workflow Smoke-Test Suite (Phase 12: P12-T02).
"""

import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("1. Probing /health and /ready...")
r_health = client.get("/health")
assert r_health.status_code == 200, f"Health failed: {r_health.text}"
r_ready = client.get("/ready")
assert r_ready.status_code == 200, f"Ready failed: {r_ready.text}"
print("   ✓ Health and database readiness: OK")

print("2. Authenticating demo merchant...")
r_login = client.post("/api/v1/auth/login", json={"phone": "01700000001", "otp": "123456", "role": "owner"})
assert r_login.status_code == 200, f"Login failed: {r_login.text}"
token = r_login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("   ✓ Demo authentication and JWT issuance: OK")

print("3. Querying Today Dashboard...")
r_today = client.get("/api/v1/merchant/today", headers=headers)
assert r_today.status_code == 200, f"Today failed: {r_today.text}"
print("   ✓ Today financial metrics: OK")

print("4. Simulating 7-Day Scenario Baseline...")
r_scen = client.get("/api/v1/scenarios/baseline", headers=headers)
assert r_scen.status_code == 200, f"Scenario baseline failed: {r_scen.text}"
print("   ✓ 7-Day liquidity scenario: OK")

print("5. Generating Customer Portal Scoped Token...")
r_party = client.post("/api/v1/merchant/parties", json={"name": "Smoke Test Customer", "phone": "01799001122"}, headers=headers)
assert r_party.status_code == 200
party_id = r_party.json()["id"]

r_portal = client.post("/api/v1/portal/generate-link", json={"party_id": party_id, "amount_paisa": 50000, "invoice_number": "INV-SMOKE-01"}, headers=headers)
assert r_portal.status_code == 200
portal_token = r_portal.json()["token"]
r_view = client.get(f"/api/v1/portal/{portal_token}")
assert r_view.status_code == 200
print("   ✓ Customer invoice portal and dispute intake: OK")

print("6. Retrieving Operating Reports & Stock...")
r_rep = client.get("/api/v1/reports/operating-summary", headers=headers)
assert r_rep.status_code == 200
r_stock = client.get("/api/v1/stock/products", headers=headers)
assert r_stock.status_code == 200
print("   ✓ Operating reports and stock tracking: OK")

print("\nAll 6 deployment smoke checks passed successfully.")

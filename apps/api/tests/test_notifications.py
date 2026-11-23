"""
Phase 22 Test Suite: Notifications, Voice Alerts & Actionable Inbox.
Validates:
1. Idempotent notification emission via dedup_key (no alert spam).
2. Read, snooze, and resolve lifecycle.
3. Daily executive brief generation with voice narration scripts.
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
    NotificationModel,
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


def test_idempotent_notification_emission(client, tenant_a):
    """Emitting alerts with same dedup_key updates the existing notification instead of duplicating."""
    # First emit
    res_1 = client.post(
        "/api/v1/notifications/emit",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "title": "দাবিযোগ্য ক্রেডিট সমন্বয়",
            "message": "মেঘনা বেভারেজের ৳১২০০ ক্রেডিট বাকি আছে",
            "category": "unapplied_credit",
            "priority": "medium",
            "dedup_key": "credit:meghna:123",
        },
    )
    assert res_1.status_code == 201
    id_1 = res_1.json()["id"]

    # Second emit with high priority update
    res_2 = client.post(
        "/api/v1/notifications/emit",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "title": "জরুরী: দাবিযোগ্য ক্রেডিট সমন্বয়",
            "message": "মেঘনা বেভারেজের ৳১২০০ ক্রেডিট অবিলম্বে সমন্বয় করুন",
            "category": "unapplied_credit",
            "priority": "high",
            "dedup_key": "credit:meghna:123",
        },
    )
    assert res_2.status_code == 201
    id_2 = res_2.json()["id"]

    # Must be the exact same notification record
    assert id_1 == id_2
    assert res_2.json()["priority"] == "high"


def test_snooze_and_resolve_lifecycle(client, tenant_a):
    """Snoozing hides alert from active list; resolving marks it permanently resolved."""
    emit_res = client.post(
        "/api/v1/notifications/emit",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "title": "রিটার্ন ডেডলাইন",
            "message": "প্রাণ ডেইরির নষ্ট মালের রিটার্ন মেয়াদ শেষ হবে",
            "category": "return_deadline",
            "priority": "high",
            "dedup_key": "return:pran:456",
        },
    )
    notif_id = emit_res.json()["id"]

    # Snooze for 4 hours
    snooze_res = client.post(
        f"/api/v1/notifications/{notif_id}/snooze",
        headers={"Authorization": tenant_a["Authorization"]},
        json={"hours": 4},
    )
    assert snooze_res.status_code == 200
    assert snooze_res.json()["status"] == "snoozed"

    # Active list excludes snoozed
    active_res = client.get(
        "/api/v1/notifications",
        headers={"Authorization": tenant_a["Authorization"]},
    )
    assert active_res.status_code == 200
    active_ids = [n["id"] for n in active_res.json()]
    assert notif_id not in active_ids

    # Resolve
    resolve_res = client.post(
        f"/api/v1/notifications/{notif_id}/resolve",
        headers={"Authorization": tenant_a["Authorization"]},
    )
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "resolved"


def test_daily_executive_brief(client, tenant_a):
    """Generates factual daily executive voice script."""
    res = client.get(
        "/api/v1/notifications/brief",
        headers={"Authorization": tenant_a["Authorization"]},
    )
    assert res.status_code == 200
    data = res.json()
    assert "liquid_cash_bdt" in data
    assert "voice_script_bn" in data
    assert "শুভ সকাল" in data["voice_script_bn"]


def test_cross_tenant_isolation(client, tenant_a, tenant_b):
    """Tenant B cannot see Tenant A's notifications."""
    emit_res = client.post(
        "/api/v1/notifications/emit",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "title": "Tenant A Secret Alert",
            "message": "Secret alert text",
            "category": "cash_constraint",
            "dedup_key": "secret:tenant_a",
        },
    )
    notif_id = emit_res.json()["id"]

    # Tenant B lists notifications -> notif_id not present
    b_list = client.get(
        "/api/v1/notifications",
        headers={"Authorization": tenant_b["Authorization"]},
    )
    assert b_list.status_code == 200
    b_ids = [n["id"] for n in b_list.json()]
    assert notif_id not in b_ids

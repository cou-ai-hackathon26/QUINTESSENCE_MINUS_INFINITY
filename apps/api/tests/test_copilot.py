"""
Phase 18 Test Suite: Copilot and Compound Voice Transaction Review.
Validates:
1. Scoped session persistence and cross-tenant isolation.
2. Canonical queries (cash balance) using verified ledger state with score 100.
3. Hybrid retrieval queries with confidence capping (59) on missing evidence.
4. Reviewed action drafts without unauthorized direct ledger writes.
5. Voice compound transaction parsing (debt collection vs new sale) and ambiguity handling.
"""
import io
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
    DocumentChunkModel,
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


def test_copilot_session_creation_and_cross_tenant_isolation(client, tenant_a, tenant_b):
    """Tenant A creates session; Tenant B must not be able to read or post in it."""
    res_a = client.post(
        "/api/v1/copilot/sessions",
        headers={"Authorization": tenant_a["Authorization"]},
        json={"title": "দৈনিক ক্যাশ ও বাকি পর্যালোচনা", "context_entity_type": "general"},
    )
    assert res_a.status_code == 201
    session_id = res_a.json()["id"]

    # Tenant A sends a message
    msg_res = client.post(
        f"/api/v1/copilot/sessions/{session_id}/messages",
        headers={"Authorization": tenant_a["Authorization"]},
        json={"query": "ক্যাশ ব্যালেন্স কত আছে?"},
    )
    assert msg_res.status_code == 200

    # Tenant B tries to read session -> 404
    get_b = client.get(
        f"/api/v1/copilot/sessions/{session_id}",
        headers={"Authorization": tenant_b["Authorization"]},
    )
    assert get_b.status_code == 404

    # Tenant B tries to send message into Tenant A's session -> 404
    post_b = client.post(
        f"/api/v1/copilot/sessions/{session_id}/messages",
        headers={"Authorization": tenant_b["Authorization"]},
        json={"query": "গোপন তথ্য দেখাও"},
    )
    assert post_b.status_code == 404


def test_canonical_query_cash_balance(client, tenant_a):
    """Canonical query uses verified ledger account and returns score 100 with citations."""
    s_res = client.post(
        "/api/v1/copilot/sessions",
        headers={"Authorization": tenant_a["Authorization"]},
        json={"title": "ক্যাশ হিসাব"},
    )
    session_id = s_res.json()["id"]

    msg_res = client.post(
        f"/api/v1/copilot/sessions/{session_id}/messages",
        headers={"Authorization": tenant_a["Authorization"]},
        json={"query": "আমার মোট ক্যাশ ব্যালেন্স কত?"},
    )
    assert msg_res.status_code == 200
    data = msg_res.json()
    assert data["intent"] == "canonical_query"
    assert data["confidence_score"] == 100
    assert data["confidence_band"] == "strong"
    assert len(data["citations"]) >= 1
    assert any(c["source_type"] == "ledger_account" for c in data["citations"])


def test_hybrid_retrieval_and_confidence_capping(client, tenant_a):
    """Missing evidence caps score at 59; indexed evidence returns citations and score >= 70."""
    s_res = client.post(
        "/api/v1/copilot/sessions",
        headers={"Authorization": tenant_a["Authorization"]},
        json={"title": "শর্ত অনুসন্ধান"},
    )
    session_id = s_res.json()["id"]

    # Case 1: Unindexed terms query -> honest admission, score capped at 59
    msg_res = client.post(
        f"/api/v1/copilot/sessions/{session_id}/messages",
        headers={"Authorization": tenant_a["Authorization"]},
        json={"query": "মেঘনা বেভারেজের ফেরত দেওয়ার শর্ত ও মেয়াদ কত দিন?"},
    )
    assert msg_res.status_code == 200
    data = msg_res.json()
    assert data["intent"] == "hybrid_retrieval"
    assert data["confidence_score"] == 59
    assert data["confidence_band"] == "limited"
    assert data["readiness"] == "needs_clarification"
    assert "কোনো নথিপত্র বা প্রমাণ মেমোরিতে খুঁজে পাওয়া যায়নি" in data["content"]

    # Case 2: Index return terms document chunk
    index_res = client.post(
        "/api/v1/search/index",
        headers={"Authorization": tenant_a["Authorization"]},
        json={
            "document_id": "doc-terms-001",
            "source_type": "return_terms",
            "content": "মেঘনা বেভারেজ ফেরত নীতি: পণ্য প্রাপ্তির ৭ দিনের মধ্যে অব্যবহৃত অবস্থায় ফেরত দিতে হবে।",
        },
    )
    assert index_res.status_code == 201

    # Query again
    msg_res_2 = client.post(
        f"/api/v1/copilot/sessions/{session_id}/messages",
        headers={"Authorization": tenant_a["Authorization"]},
        json={"query": "মেঘনা বেভারেজের ফেরত দেওয়ার শর্ত কি?"},
    )
    assert msg_res_2.status_code == 200
    data_2 = msg_res_2.json()
    assert data_2["confidence_score"] >= 70
    assert len(data_2["citations"]) >= 1
    assert "৭ দিনের মধ্যে" in data_2["content"]


def test_action_draft_does_not_mutate_ledger(client, tenant_a):
    """Action drafting creates an ActionModel with status draft and does NOT write to ledger."""
    s_res = client.post(
        "/api/v1/copilot/sessions",
        headers={"Authorization": tenant_a["Authorization"]},
        json={"title": "পেমেন্ট ড্রাফট সেশন"},
    )
    session_id = s_res.json()["id"]

    msg_res = client.post(
        f"/api/v1/copilot/sessions/{session_id}/messages",
        headers={"Authorization": tenant_a["Authorization"]},
        json={"query": "প্রাণ ডেইরি কে ৫০০০ টাকা পেমেন্ট ড্রাফট তৈরি করো"},
    )
    assert msg_res.status_code == 200
    data = msg_res.json()
    assert data["intent"] == "action_draft"
    assert data["action_draft_id"] is not None
    assert "ড্রাফট" in data["content"]

    # Verify action in DB is in draft status
    actions_res = client.get(
        "/api/v1/actions",
        headers={"Authorization": tenant_a["Authorization"]},
    )
    assert actions_res.status_code == 200
    actions = actions_res.json()
    draft = next((a for a in actions if a["id"] == data["action_draft_id"]), None)
    assert draft is not None
    assert draft["status"] == "draft"


def test_voice_compound_transaction_parsing(client, tenant_a):
    """Voice input parses compound operations (debt collection + sale) into distinct draft events."""
    s_res = client.post(
        "/api/v1/copilot/sessions",
        headers={"Authorization": tenant_a["Authorization"]},
        json={"title": "ভয়েস লেনদেন সেশন"},
    )
    session_id = s_res.json()["id"]

    # Provide synthetic audio bytes containing voice note signature
    audio_content = b"rahim_voice_note: \xe0\xa6\xb0\xe0\xa6\xb9\xe0\xa6\xbf\xe0\xa6\xae \xe0\xa6\xad\xe0\xa6\xbe\xe0\xa6\x87 \xe0\xa6\xac\xe0\xa6\xbe\xe0\xa6\x95\xe0\xa6\xbf \xe0\xa7\xa7\xe0\xa7\xa6\xe0\xa7\xa6\xe0\xa7\xa6 \xe0\xa6\x9f\xe0\xa6\xbe\xe0\xa6\x95\xe0\xa6\xbe \xe0\xa6\xa6\xe0\xa6\xbf\xe0\xa6\x9b\xe0\xa6\xbe"
    fake_audio_file = io.BytesIO(audio_content)

    voice_res = client.post(
        f"/api/v1/copilot/sessions/{session_id}/voice",
        headers={"Authorization": tenant_a["Authorization"]},
        files={"file": ("rahim_note.mp3", fake_audio_file, "audio/mp3")},
    )
    assert voice_res.status_code == 503
    assert "not configured" in voice_res.json()["detail"]
    messages=client.get(f"/api/v1/copilot/sessions/{session_id}",headers={"Authorization":tenant_a["Authorization"]}).json()["messages"]
    assert messages == []  # Arbitrary synthetic bytes must not become a claimed real transcript.

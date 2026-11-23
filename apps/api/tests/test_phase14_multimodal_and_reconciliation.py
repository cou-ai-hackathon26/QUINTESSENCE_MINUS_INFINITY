"""
Phase 14 Test Suite: Multimodal AI Inference Boundary, Bengali Numeral Normalization,
and Complete End-to-End Supplier Reconciliation Journey (P04/P05 Repair).
"""
import io
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.ingestion.adapters import (
    AIModelAdapter,
    NativePdfParser,
    ProviderUnavailableError,
    normalize_bengali_digits,
    parse_paisa_amount,
)
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
def owner_headers(client):
    suffix = uuid.uuid4().hex[:6]
    phone = f"0171{suffix}"
    res = client.post("/api/v1/auth/login", json={"phone": phone, "otp": "123456", "role": "owner"})
    data = res.json()
    return {"Authorization": f"Bearer {data['access_token']}", "tenant_id": data["tenant_id"]}


def test_bengali_numeral_normalization():
    """Verify transliteration of Bengali numerals to ASCII numerals."""
    assert normalize_bengali_digits("০১২৩৪৫৬৭৮৯") == "0123456789"
    assert normalize_bengali_digits("দাবি ২৫,০০০ টাকা") == "দাবি 25,000 টাকা"
    assert normalize_bengali_digits("বকেয়া ৫০০.৫০") == "বকেয়া 500.50"
    assert normalize_bengali_digits("") == ""


def test_parse_paisa_amount():
    """Verify conversion of Bengali/ASCII currency expressions to integer paisa."""
    assert parse_paisa_amount("২৫,০০০ টাকা") == 2500000
    assert parse_paisa_amount("৳ ৫০০") == 50000
    assert parse_paisa_amount("Tk. 1,250.75") == 125075
    assert parse_paisa_amount("কোন সংখ্যা নেই") is None


def test_multimodal_audio_ingestion_and_extraction(client, owner_headers):
    """Verify multimodal voice note ingestion extracts party and amount."""
    audio_content = b"RIFF....WAVEfmt rahim voice note 1000 cash paid"
    files = {"file": ("voice_memo.mp3", io.BytesIO(audio_content), "audio/mp3")}

    res = client.post("/api/v1/evidence/upload", headers=owner_headers, files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["source_type"] == "audio"
    assert data["proposed_party"] == "রহিম স্টোর"
    assert data["proposed_amount_paisa"] == 100000


def test_multimodal_image_ingestion_and_extraction(client, owner_headers):
    """Verify multimodal image upload (memo_42) extracts party and bkash payment."""
    img_content = b"\xff\xd8\xff memo_42 Al Madina Store receipt"
    files = {"file": ("memo_42.jpg", io.BytesIO(img_content), "image/jpeg")}

    res = client.post("/api/v1/evidence/upload", headers=owner_headers, files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["source_type"] == "image"
    assert data["proposed_party"] == "আল মদিনা স্টোর"
    assert data["proposed_amount_paisa"] == 1800000


def test_gemini_provider_unconfigured_vs_configured_boundary():
    """Verify that unconfigured adapter uses honest offline double, and configured with bad key raises explicit error."""
    # Offline mode (empty key)
    offline_adapter = AIModelAdapter(api_key="")
    assert offline_adapter.is_configured() is False
    res_offline = offline_adapter.parse_bangla_document("random text with no numbers")
    assert res_offline.amount_paisa is None

    # Configured mode with invalid key: should attempt API and raise ProviderUnavailableError
    live_adapter = AIModelAdapter(api_key="invalid-gemini-key-12345")
    assert live_adapter.is_configured() is True
    with pytest.raises(ProviderUnavailableError) as exc_info:
        live_adapter.parse_bangla_document("দাবি ২৫,০০০ টাকা")
    assert "Gemini" in str(exc_info.value) or "credential" in str(exc_info.value)


def test_reconciliation_evaluation_endpoint_all_hypotheses(client, owner_headers):
    """Verify /api/v1/reconciliation/evaluate returns all 4 canonical hypotheses when ambiguous."""
    payload = {
        "demand": {"invoice_id": "INV-41", "amount_paisa": 2500000},
        "eligible_payment": {"invoice_id": "INV-41", "amount_paisa": 400000},
        "accepted_return": {"invoice_id": "INV-41", "amount_paisa": 300000},
    }

    res = client.post("/api/v1/reconciliation/evaluate", headers=owner_headers, json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["expected_state"] == "unresolved"
    assert len(data["expected_payables_paisa"]) == 4
    # Payables: H4=1800000, H3=2100000, H2=2200000, H1=2500000
    assert data["expected_payables_paisa"] == [1800000, 2100000, 2200000, 2500000]
    assert len(data["hypotheses"]) == 4


def test_reconciliation_clarify_bangla_reply_and_draft_action(client, owner_headers):
    """
    Verify complete P04/P05 journey:
    1. Ambiguous demand
    2. Supplier reply in Bangla: 'পেমেন্ট পাইছি কিন্তু ফেরত বাদ দেই নাই'
    3. Resolves to REC-003: 25,000 - 3,000 = 22,000 (2,200,000 paisa)
    4. Automatically prepares draft action for owner approval
    """
    payload = {
        "case_id": "CASE-REC-HAQUE-41",
        "reply_text": "ভাই পেমেন্ট পাইছি কিন্তু ফেরত বাদ দেই নাই",
        "demand_amount_paisa": 2500000,
        "payment_amount_paisa": 400000,
        "return_amount_paisa": 300000,
        "invoice_ref": "41",
    }

    res = client.post("/api/v1/reconciliation/clarify", headers=owner_headers, json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["payment_included"] is True
    assert data["return_included"] is False
    assert data["resolved_state"] == "supported"
    # Expected payable: d - r = 2500000 - 300000 = 2200000 paisa
    assert data["resolved_payable_paisa"] == 2200000
    assert data["requires_owner_approval"] is True
    assert data["draft_action_id"] is not None

    action_id = data["draft_action_id"]

    # Verify action appears in Actions queue
    actions_res = client.get("/api/v1/actions", headers=owner_headers)
    assert actions_res.status_code == 200
    actions_list = actions_res.json()
    created_action = next((a for a in actions_list if a["id"] == action_id), None)
    assert created_action is not None
    assert created_action["status"] == "pending_approval"
    assert created_action["amount_paisa"] == 2200000

    # Owner approves the action
    approve_res = client.post(f"/api/v1/actions/{action_id}/approve", headers=owner_headers)
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "approved"


def test_reconciliation_credit_reuse_exclusion(client, owner_headers):
    """Verify attempting to reuse credit already allocated to another invoice is rejected."""
    payload = {
        "demand": {"invoice_id": "INV-41", "amount_paisa": 2500000},
        "eligible_payment": {"invoice_id": "INV-41", "amount_paisa": 400000},
        "accepted_return": {"invoice_id": "INV-41", "amount_paisa": 300000},
        "payment_included": False,
        "return_included": True,
        "attempt_reuse_event_id": "CREDIT-EVT-99",
        "unavailable_credits": {
            "CREDIT-EVT-99": {
                "amount_paisa": 300000,
                "allocated_invoice_id": "INV-38",
                "allocated_amount_paisa": 300000,
            }
        },
    }

    res = client.post("/api/v1/reconciliation/evaluate", headers=owner_headers, json=payload)
    assert res.status_code == 200
    data = res.json()
    # Credit reuse is excluded (0 paisa applied)
    assert data["applied_credits_paisa"] == 0
